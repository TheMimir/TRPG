"""
Ollama Client for Cthulhu Solo TRPG System

Provides a robust interface to the Ollama AI service with:
- Timeout handling and retry logic
- Error recovery and fallback systems
- Connection pooling and rate limiting
- Response parsing and validation
- Performance monitoring
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib


logger = logging.getLogger(__name__)


class ResponseStatus(Enum):
    """Status of an AI response"""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    RATE_LIMITED = "rate_limited"
    INVALID_RESPONSE = "invalid_response"
    SERVER_ERROR = "server_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class OllamaResponse:
    """Response from Ollama API with metadata"""
    content: str
    status: ResponseStatus
    response_time: float = 0.0
    model_used: str = ""
    token_count: int = 0
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_success(self) -> bool:
        """Check if the response was successful"""
        return self.status == ResponseStatus.SUCCESS and bool(self.content.strip())
    
    def __str__(self) -> str:
        if self.is_success:
            return f"OllamaResponse(content='{self.content[:50]}...', time={self.response_time:.2f}s)"
        return f"OllamaResponse(status={self.status.value}, error='{self.error_message}')"


@dataclass
class OllamaConfig:
    """Configuration for Ollama client"""
    base_url: str = "http://localhost:11434"
    model: str = "gpt-oss:120b"
    timeout: float = 300.0  # 5 minutes default
    max_retries: int = 5
    retry_delay: float = 2.0
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    seed: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for API calls"""
        return {
            "model": self.model,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "repeat_penalty": self.repeat_penalty,
                "num_predict": self.max_tokens,
                "seed": self.seed,
            }
        }


class OllamaClient:
    """
    Robust Ollama client with comprehensive error handling.
    
    Features:
    - Async operations with configurable timeouts
    - Automatic retry with exponential backoff
    - Response caching for performance
    - Connection pooling
    - Health monitoring
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        """Initialize the Ollama client"""
        self.config = config or OllamaConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.response_cache: Dict[str, OllamaResponse] = {}
        self.cache_ttl: Dict[str, float] = {}
        self.request_count = 0
        self.total_response_time = 0.0
        self.error_count = 0
        self.last_error_time = 0.0
        self.health_status = True
        
        # Rate limiting
        self.last_request_time = 0.0
        self.min_request_interval = 0.1  # Minimum 100ms between requests
        
        logger.info(f"OllamaClient initialized with model: {self.config.model}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def connect(self):
        """Establish connection to Ollama service"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Test connection
            try:
                await self.health_check()
                logger.info("Successfully connected to Ollama service")
            except Exception as e:
                logger.warning(f"Initial health check failed: {e}")
                self.health_status = False
    
    async def close(self):
        """Close the connection"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("OllamaClient connection closed")
    
    async def health_check(self) -> bool:
        """Check if Ollama service is available"""
        try:
            if not self.session:
                await self.connect()
            
            async with self.session.get(f"{self.config.base_url}/api/tags") as response:
                if response.status == 200:
                    self.health_status = True
                    return True
                else:
                    self.health_status = False
                    return False
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            self.health_status = False
            return False
    
    def _generate_cache_key(self, prompt: str, **kwargs) -> str:
        """Generate cache key for request"""
        key_data = {
            "prompt": prompt,
            "model": self.config.model,
            "temperature": self.config.temperature,
            **kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[OllamaResponse]:
        """Get cached response if still valid"""
        if cache_key not in self.response_cache:
            return None
        
        # Check TTL (cache for 10 minutes)
        if time.time() - self.cache_ttl.get(cache_key, 0) > 600:
            del self.response_cache[cache_key]
            del self.cache_ttl[cache_key]
            return None
        
        return self.response_cache[cache_key]
    
    def _cache_response(self, cache_key: str, response: OllamaResponse):
        """Cache a successful response"""
        if response.is_success:
            self.response_cache[cache_key] = response
            self.cache_ttl[cache_key] = time.time()
            
            # Limit cache size
            if len(self.response_cache) > 100:
                oldest_key = min(self.cache_ttl.keys(), key=lambda k: self.cache_ttl[k])
                del self.response_cache[oldest_key]
                del self.cache_ttl[oldest_key]
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    async def generate(self, prompt: str, system_prompt: str = "", 
                      use_cache: bool = True, **kwargs) -> OllamaResponse:
        """
        Generate response from Ollama with full error handling.
        
        Args:
            prompt: The user prompt
            system_prompt: System/context prompt
            use_cache: Whether to use response caching
            **kwargs: Additional parameters
            
        Returns:
            OllamaResponse with content or error information
        """
        # Check cache first
        cache_key = self._generate_cache_key(prompt, system_prompt=system_prompt, **kwargs)
        if use_cache:
            cached = self._get_cached_response(cache_key)
            if cached:
                logger.debug(f"Cache hit for prompt: {prompt[:50]}...")
                return cached
        
        # Rate limiting
        await self._rate_limit()
        
        start_time = time.time()
        last_exception = None
        
        # Retry logic
        for attempt in range(self.config.max_retries + 1):
            try:
                if not self.session:
                    await self.connect()
                
                if not self.health_status:
                    await self.health_check()
                    if not self.health_status:
                        logger.warning("Ollama service appears to be down")
                
                # Prepare request
                request_data = self.config.to_dict()
                
                # Combine prompts
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
                
                request_data["prompt"] = full_prompt
                request_data["stream"] = False
                
                # Add any additional options
                request_data["options"].update(kwargs)
                
                # Make the request
                async with self.session.post(
                    f"{self.config.base_url}/api/generate",
                    json=request_data
                ) as response:
                    
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validate response
                        if "response" not in data:
                            raise ValueError("Invalid response format: missing 'response' field")
                        
                        content = data["response"].strip()
                        if not content:
                            raise ValueError("Empty response from Ollama")
                        
                        # Create successful response
                        ollama_response = OllamaResponse(
                            content=content,
                            status=ResponseStatus.SUCCESS,
                            response_time=response_time,
                            model_used=self.config.model,
                            token_count=len(content.split()),  # Rough estimate
                            metadata={
                                "prompt_length": len(prompt),
                                "system_length": len(system_prompt),
                                "eval_count": data.get("eval_count", 0),
                                "eval_duration": data.get("eval_duration", 0),
                            }
                        )
                        
                        # Update statistics
                        self.request_count += 1
                        self.total_response_time += response_time
                        
                        # Cache successful response
                        if use_cache:
                            self._cache_response(cache_key, ollama_response)
                        
                        logger.debug(f"Generated response in {response_time:.2f}s: {content[:100]}...")
                        return ollama_response
                    
                    elif response.status == 429:
                        # Rate limited
                        logger.warning(f"Rate limited on attempt {attempt + 1}")
                        status = ResponseStatus.RATE_LIMITED
                        wait_time = self.config.retry_delay * (2 ** attempt)
                        await asyncio.sleep(wait_time)
                        
                    elif response.status >= 500:
                        # Server error
                        logger.warning(f"Server error {response.status} on attempt {attempt + 1}")
                        status = ResponseStatus.SERVER_ERROR
                        
                    else:
                        # Other HTTP error
                        error_text = await response.text()
                        logger.error(f"HTTP {response.status}: {error_text}")
                        status = ResponseStatus.UNKNOWN_ERROR
                        
            except asyncio.TimeoutError as e:
                logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                status = ResponseStatus.TIMEOUT
                last_exception = e
                
            except aiohttp.ClientError as e:
                logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                status = ResponseStatus.CONNECTION_ERROR
                last_exception = e
                self.health_status = False
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                status = ResponseStatus.UNKNOWN_ERROR
                last_exception = e
            
            # Wait before retry (with exponential backoff)
            if attempt < self.config.max_retries:
                wait_time = self.config.retry_delay * (2 ** attempt)
                logger.info(f"Retrying in {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
        
        # All retries failed
        self.error_count += 1
        self.last_error_time = time.time()
        
        error_response = OllamaResponse(
            content="",
            status=status,
            response_time=time.time() - start_time,
            error_message=str(last_exception) if last_exception else "All retries failed"
        )
        
        logger.error(f"Failed to generate response after {self.config.max_retries + 1} attempts")
        return error_response
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> OllamaResponse:
        """
        Chat interface (converts to single prompt for compatibility).
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
            
        Returns:
            OllamaResponse
        """
        # Convert chat format to single prompt
        prompt_parts = []
        system_prompt = ""
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                system_prompt = content
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n".join(prompt_parts)
        return await self.generate(prompt, system_prompt, **kwargs)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get client performance statistics"""
        avg_response_time = (self.total_response_time / self.request_count 
                           if self.request_count > 0 else 0)
        
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(1, self.request_count),
            "average_response_time": avg_response_time,
            "cache_size": len(self.response_cache),
            "health_status": self.health_status,
            "last_error_time": self.last_error_time,
            "model": self.config.model,
        }
    
    def clear_cache(self):
        """Clear the response cache"""
        self.response_cache.clear()
        self.cache_ttl.clear()
        logger.info("Response cache cleared")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection with a simple prompt"""
        test_prompt = "Say 'Hello' in one word."
        
        start_time = time.time()
        response = await self.generate(test_prompt, use_cache=False)
        test_time = time.time() - start_time
        
        return {
            "success": response.is_success,
            "response_time": test_time,
            "status": response.status.value,
            "response": response.content[:100] if response.content else "",
            "error": response.error_message if not response.is_success else None,
        }


# Convenience functions
async def quick_generate(prompt: str, system_prompt: str = "", 
                        config: Optional[OllamaConfig] = None) -> str:
    """Quick generation function for simple use cases"""
    client_config = config or OllamaConfig()
    
    async with OllamaClient(client_config) as client:
        response = await client.generate(prompt, system_prompt)
        return response.content if response.is_success else ""


async def test_ollama_connection(base_url: str = "http://localhost:11434") -> bool:
    """Test if Ollama is available"""
    config = OllamaConfig(base_url=base_url)
    
    try:
        async with OllamaClient(config) as client:
            result = await client.test_connection()
            return result["success"]
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


# Mock client for testing without Ollama
class MockOllamaClient:
    """Mock client for testing and development"""
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.request_count = 0
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> OllamaResponse:
        """Mock generation - returns a simple response"""
        self.request_count += 1
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Generate mock response based on prompt
        mock_content = self._generate_mock_content(prompt, system_prompt)
        
        return OllamaResponse(
            content=mock_content,
            status=ResponseStatus.SUCCESS,
            response_time=0.1,
            model_used="mock-model",
            token_count=len(mock_content.split()),
        )
    
    def _generate_mock_content(self, prompt: str, system_prompt: str = "") -> str:
        """Generate appropriate mock content based on the prompt"""
        prompt_lower = prompt.lower()
        
        # Korean responses for Korean prompts
        if any(korean_char >= '가' and korean_char <= '힣' for korean_char in prompt):
            if "조사" in prompt_lower or "살펴" in prompt_lower:
                return "당신은 조심스럽게 주변을 살펴보았습니다. 어둠 속에서 무언가 움직이는 것 같습니다."
            elif "이동" in prompt_lower or "가다" in prompt_lower:
                return "당신은 조용히 앞으로 나아갔습니다. 발걸음 소리가 텅 빈 복도에 메아리칩니다."
            elif "대화" in prompt_lower or "말하다" in prompt_lower:
                return "상대방이 당신을 바라보며 천천히 입을 열었습니다. 그의 눈에는 두려움이 어려 있습니다."
            else:
                return "당신의 행동에 따라 상황이 변화합니다. 신중하게 다음 행동을 선택하세요."
        
        # English responses
        if "investigate" in prompt_lower or "examine" in prompt_lower:
            return "You carefully examine the area. In the dim light, you notice something unsettling."
        elif "move" in prompt_lower or "go" in prompt_lower:
            return "You move forward cautiously. Your footsteps echo in the empty corridor."
        elif "talk" in prompt_lower or "speak" in prompt_lower:
            return "The person looks at you with fear in their eyes and begins to speak slowly."
        else:
            return "The situation unfolds before you. Choose your next action carefully."
    
    async def health_check(self) -> bool:
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "request_count": self.request_count,
            "error_count": 0,
            "error_rate": 0.0,
            "average_response_time": 0.1,
            "cache_size": 0,
            "health_status": True,
            "model": "mock-model",
        }