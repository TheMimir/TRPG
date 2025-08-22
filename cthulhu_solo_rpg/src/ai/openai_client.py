"""
OpenAI Client for Cthulhu Solo TRPG System

Provides integration with OpenAI's GPT models with:
- GPT-4 and GPT-3.5 support
- Token counting and cost tracking
- Rate limiting and retry logic
- Streaming support
- Function calling capabilities
"""

import asyncio
import os
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ai.base_ai_client import BaseAIClient, AIConfig, AIResponse, ResponseStatus, AIProvider


logger = logging.getLogger(__name__)


# Model pricing (per 1K tokens) - Update as needed
MODEL_PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # 매우 경제적
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
}


@dataclass
class OpenAIConfig(AIConfig):
    """Configuration specific to OpenAI"""
    provider: AIProvider = AIProvider.OPENAI
    model: str = "gpt-4o-mini"  # Default to gpt-4o-mini for better performance
    api_key: Optional[str] = None
    organization: Optional[str] = None
    base_url: Optional[str] = None  # For Azure OpenAI or custom endpoints
    api_version: str = "v1"
    
    # OpenAI specific parameters
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None  # For tracking
    
    # Streaming
    stream: bool = False
    
    # Cost management
    warn_cost_threshold: float = 0.10  # Warn if single request costs more
    max_cost_per_request: float = 1.00  # Maximum cost per request
    track_usage: bool = True


class OpenAIClient(BaseAIClient):
    """
    OpenAI client implementation for GPT models.
    
    Features:
    - Supports GPT-4 and GPT-3.5 models
    - Token counting and cost estimation
    - Proper error handling for API issues
    - Response caching
    - Rate limiting
    """
    
    def __init__(self, config: Optional[OpenAIConfig] = None):
        """Initialize the OpenAI client"""
        # Use OpenAIConfig if not provided
        if config is None:
            config = OpenAIConfig()
        elif not isinstance(config, OpenAIConfig):
            # Convert base config to OpenAI config
            openai_config = OpenAIConfig()
            for key, value in config.__dict__.items():
                if hasattr(openai_config, key):
                    setattr(openai_config, key, value)
            config = openai_config
        
        super().__init__(config)
        self.config: OpenAIConfig = config
        self.client = None
        self.async_client = None
        
        # Get API key from config or environment
        if not self.config.api_key:
            self.config.api_key = os.getenv("OPENAI_API_KEY")
        
        # Usage tracking
        self.session_tokens = {"input": 0, "output": 0}
        self.session_cost = 0.0
        
        # Rate limiting
        self.last_request_time = 0.0
        self.min_request_interval = 0.1  # 100ms between requests
        
        logger.info(f"OpenAIClient initialized with model: {self.config.model}")
    
    async def connect(self) -> bool:
        """Establish connection to OpenAI service"""
        try:
            # Lazy import to avoid dependency issues if openai is not installed
            try:
                from openai import AsyncOpenAI
            except ImportError:
                logger.error("OpenAI package not installed. Run: pip install openai")
                return False
            
            if not self.config.api_key:
                logger.error("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
                return False
            
            # Create async client
            self.async_client = AsyncOpenAI(
                api_key=self.config.api_key,
                organization=self.config.organization,
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
            )
            
            # Test connection
            success = await self.health_check()
            if success:
                logger.info("Successfully connected to OpenAI service")
            else:
                logger.warning("OpenAI connection test failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI: {e}")
            return False
    
    async def close(self):
        """Close the connection to OpenAI service"""
        # OpenAI client doesn't need explicit closing
        if self.async_client:
            # Clean up if needed
            self.async_client = None
        logger.info("OpenAIClient connection closed")
    
    async def health_check(self) -> bool:
        """Check if OpenAI service is available"""
        try:
            if not self.async_client:
                return False
            
            # Try a minimal API call
            response = await self.async_client.models.list()
            self.health_status = True
            self.last_health_check = time.time()
            return True
            
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            self.health_status = False
            return False
    
    async def generate(self, prompt: str, system_prompt: str = "", 
                      use_cache: bool = True, **kwargs) -> AIResponse:
        """
        Generate response from OpenAI.
        
        Args:
            prompt: The user prompt
            system_prompt: System/context prompt
            use_cache: Whether to use response caching
            **kwargs: Additional OpenAI parameters
            
        Returns:
            AIResponse with content or error information
        """
        # Check cache first
        cache_key = self._generate_cache_key(prompt, system_prompt, **kwargs)
        if use_cache:
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
        
        # Rate limiting
        await self._rate_limit()
        
        start_time = time.time()
        
        try:
            # Ensure client is connected
            if not self.async_client:
                connected = await self.connect()
                if not connected:
                    return AIResponse(
                        content="",
                        status=ResponseStatus.CONNECTION_ERROR,
                        provider=self.provider,
                        error_message="Failed to connect to OpenAI service"
                    )
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Estimate tokens and cost
            estimated_input_tokens = self._estimate_tokens(prompt + system_prompt)
            estimated_cost = self._estimate_cost(estimated_input_tokens, 500)  # Assume 500 output tokens
            
            # Check cost limits
            if self.config.max_cost_per_request and estimated_cost > self.config.max_cost_per_request:
                return AIResponse(
                    content="",
                    status=ResponseStatus.QUOTA_EXCEEDED,
                    provider=self.provider,
                    error_message=f"Estimated cost ${estimated_cost:.4f} exceeds limit ${self.config.max_cost_per_request:.4f}"
                )
            
            # Warn about high cost
            if self.config.warn_cost_threshold and estimated_cost > self.config.warn_cost_threshold:
                logger.warning(f"High cost request: estimated ${estimated_cost:.4f}")
            
            # Make the API call
            response = await self._call_openai_api(messages, **kwargs)
            
            response_time = time.time() - start_time
            
            # Extract content
            if response and hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
                
                # Track usage
                if hasattr(response, 'usage'):
                    input_tokens = response.usage.prompt_tokens
                    output_tokens = response.usage.completion_tokens
                    total_tokens = response.usage.total_tokens
                    
                    self.session_tokens["input"] += input_tokens
                    self.session_tokens["output"] += output_tokens
                    self.total_tokens += total_tokens
                    
                    # Calculate actual cost
                    actual_cost = self._calculate_cost(input_tokens, output_tokens)
                    self.session_cost += actual_cost
                    self.total_cost += actual_cost
                else:
                    total_tokens = len(content.split())
                    actual_cost = 0.0
                
                # Update statistics
                self.request_count += 1
                self.total_response_time += response_time
                
                # Create successful response
                ai_response = AIResponse(
                    content=content,
                    status=ResponseStatus.SUCCESS,
                    provider=self.provider,
                    response_time=response_time,
                    model_used=self.config.model,
                    token_count=total_tokens,
                    metadata={
                        "input_tokens": input_tokens if hasattr(response, 'usage') else 0,
                        "output_tokens": output_tokens if hasattr(response, 'usage') else 0,
                        "cost": actual_cost,
                        "finish_reason": response.choices[0].finish_reason if response.choices else None,
                    }
                )
                
                # Cache successful response
                if use_cache:
                    self._cache_response(cache_key, ai_response)
                
                logger.debug(f"Generated response in {response_time:.2f}s, cost: ${actual_cost:.4f}")
                return ai_response
            else:
                raise ValueError("Invalid response format from OpenAI")
                
        except Exception as e:
            self.error_count += 1
            error_status, error_message = self._parse_error(e)
            
            logger.error(f"OpenAI generation failed: {error_message}")
            
            return AIResponse(
                content="",
                status=error_status,
                provider=self.provider,
                response_time=time.time() - start_time,
                error_message=error_message
            )
    
    async def _call_openai_api(self, messages: List[Dict[str, str]], **kwargs):
        """Make the actual API call to OpenAI with retry logic"""
        for attempt in range(self.config.max_retries + 1):
            try:
                # Prepare parameters
                params = {
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                    "top_p": kwargs.get("top_p", self.config.top_p),
                    "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
                    "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty),
                    "stream": self.config.stream,
                }
                
                # Add optional parameters
                if self.config.logit_bias:
                    params["logit_bias"] = self.config.logit_bias
                if self.config.user:
                    params["user"] = self.config.user
                
                # Make the API call
                response = await self.async_client.chat.completions.create(**params)
                return response
                
            except Exception as e:
                if attempt < self.config.max_retries:
                    wait_time = self.config.retry_delay * (2 ** attempt)
                    logger.warning(f"OpenAI API call failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    raise
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count"""
        # Rough estimate: 1 token ≈ 4 characters for English
        # More accurate would use tiktoken library
        return len(text) // 4
    
    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a request"""
        pricing = MODEL_PRICING.get(self.config.model, MODEL_PRICING["gpt-3.5-turbo"])
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        return input_cost + output_cost
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate actual cost for a request"""
        return self._estimate_cost(input_tokens, output_tokens)
    
    def _parse_error(self, error: Exception) -> tuple[ResponseStatus, str]:
        """Parse OpenAI error and return appropriate status and message"""
        error_str = str(error)
        
        if "rate_limit" in error_str.lower():
            return ResponseStatus.RATE_LIMITED, "Rate limit exceeded"
        elif "authentication" in error_str.lower() or "api_key" in error_str.lower():
            return ResponseStatus.AUTHENTICATION_ERROR, "Authentication failed - check API key"
        elif "quota" in error_str.lower() or "insufficient" in error_str.lower():
            return ResponseStatus.QUOTA_EXCEEDED, "API quota exceeded"
        elif "timeout" in error_str.lower():
            return ResponseStatus.TIMEOUT, "Request timed out"
        elif "connection" in error_str.lower():
            return ResponseStatus.CONNECTION_ERROR, f"Connection error: {error_str}"
        else:
            return ResponseStatus.UNKNOWN_ERROR, error_str
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get client performance statistics with cost tracking"""
        stats = super().get_statistics()
        stats.update({
            "session_cost": self.session_cost,
            "session_tokens": self.session_tokens,
            "average_cost_per_request": self.session_cost / max(1, self.request_count),
        })
        return stats
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection with a simple prompt"""
        result = await super().test_connection()
        result["api_key_configured"] = bool(self.config.api_key)
        result["model"] = self.config.model
        return result


# Mock OpenAI client for testing
class MockOpenAIClient(OpenAIClient):
    """Mock OpenAI client for testing without API calls"""
    
    def __init__(self, config: Optional[OpenAIConfig] = None):
        super().__init__(config)
        self.provider = AIProvider.MOCK
    
    async def connect(self) -> bool:
        """Mock connection always succeeds"""
        self.health_status = True
        return True
    
    async def health_check(self) -> bool:
        """Mock health check always succeeds"""
        return True
    
    async def generate(self, prompt: str, system_prompt: str = "", 
                      use_cache: bool = True, **kwargs) -> AIResponse:
        """Generate mock response"""
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Generate mock content based on prompt
        prompt_lower = prompt.lower()
        
        if any(korean_char >= '가' and korean_char <= '힣' for korean_char in prompt):
            content = "모의 응답입니다. 실제 API 연결 없이 테스트 중입니다."
        else:
            content = "This is a mock response. Testing without actual API connection."
        
        return AIResponse(
            content=content,
            status=ResponseStatus.SUCCESS,
            provider=AIProvider.MOCK,
            response_time=0.1,
            model_used="mock-gpt",
            token_count=len(content.split()),
            metadata={"mock": True}
        )