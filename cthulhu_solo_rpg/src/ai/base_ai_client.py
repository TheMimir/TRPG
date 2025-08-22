"""
Base AI Client for Cthulhu Solo TRPG System

Provides abstract base class for all AI service providers with:
- Unified interface for different AI providers
- Common response types and error handling
- Provider-agnostic configuration
- Standard health check and statistics
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
import time
import logging


logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    MOCK = "mock"
    AUTO = "auto"  # Automatically select available provider


class ResponseStatus(Enum):
    """Status of an AI response"""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    RATE_LIMITED = "rate_limited"
    INVALID_RESPONSE = "invalid_response"
    SERVER_ERROR = "server_error"
    AUTHENTICATION_ERROR = "authentication_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class AIResponse:
    """Unified response from any AI provider"""
    content: str
    status: ResponseStatus
    provider: AIProvider
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
            return f"AIResponse({self.provider.value}, content='{self.content[:50]}...', time={self.response_time:.2f}s)"
        return f"AIResponse({self.provider.value}, status={self.status.value}, error='{self.error_message}')"


@dataclass
class AIConfig:
    """Base configuration for AI clients"""
    provider: AIProvider = AIProvider.AUTO
    model: str = ""  # Provider-specific model name
    timeout: float = 300.0  # 5 minutes default
    max_retries: int = 3
    retry_delay: float = 2.0
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 0.9
    enable_cache: bool = True
    cache_ttl: int = 600  # Cache time-to-live in seconds
    
    # Provider-specific settings
    api_key: Optional[str] = None  # For OpenAI
    base_url: Optional[str] = None  # For Ollama or custom endpoints
    organization: Optional[str] = None  # For OpenAI
    
    # Cost management (for paid APIs)
    enable_cost_tracking: bool = True
    max_cost_per_request: Optional[float] = None
    max_cost_per_session: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }


class BaseAIClient(ABC):
    """
    Abstract base class for AI service clients.
    
    All AI providers (Ollama, OpenAI, etc.) must inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, config: Optional[AIConfig] = None):
        """Initialize the base AI client"""
        self.config = config or AIConfig()
        self.provider = self.config.provider
        
        # Statistics tracking
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.total_tokens = 0
        self.total_cost = 0.0
        
        # Cache management
        self.response_cache: Dict[str, AIResponse] = {}
        self.cache_timestamps: Dict[str, float] = {}
        
        # Health status
        self.health_status = False
        self.last_health_check = 0.0
        
        logger.info(f"Initialized {self.__class__.__name__} with provider: {self.provider.value}")
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the AI service.
        
        Returns:
            True if connection successful
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Close the connection to the AI service"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the AI service is available.
        
        Returns:
            True if service is healthy
        """
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", 
                      use_cache: bool = True, **kwargs) -> AIResponse:
        """
        Generate a response from the AI service.
        
        Args:
            prompt: The user prompt
            system_prompt: System/context prompt
            use_cache: Whether to use response caching
            **kwargs: Additional provider-specific parameters
            
        Returns:
            AIResponse with content or error information
        """
        pass
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> AIResponse:
        """
        Chat interface for conversation-style interactions.
        
        Default implementation converts to generate() call.
        Providers can override for native chat support.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
            
        Returns:
            AIResponse
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
            "provider": self.provider.value,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(1, self.request_count),
            "average_response_time": avg_response_time,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "cache_size": len(self.response_cache),
            "health_status": self.health_status,
            "model": self.config.model,
        }
    
    def clear_cache(self):
        """Clear the response cache"""
        self.response_cache.clear()
        self.cache_timestamps.clear()
        logger.info(f"{self.__class__.__name__}: Response cache cleared")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection with a simple prompt"""
        test_prompt = "Say 'Hello' in one word."
        
        start_time = time.time()
        response = await self.generate(test_prompt, use_cache=False)
        test_time = time.time() - start_time
        
        return {
            "provider": self.provider.value,
            "success": response.is_success,
            "response_time": test_time,
            "status": response.status.value,
            "response": response.content[:100] if response.content else "",
            "error": response.error_message if not response.is_success else None,
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    def _generate_cache_key(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        """Generate cache key for request"""
        import hashlib
        import json
        
        key_data = {
            "prompt": prompt,
            "system_prompt": system_prompt,
            "model": self.config.model,
            "temperature": self.config.temperature,
            "provider": self.provider.value,
            **kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[AIResponse]:
        """Get cached response if still valid"""
        if not self.config.enable_cache:
            return None
            
        if cache_key not in self.response_cache:
            return None
        
        # Check TTL
        if time.time() - self.cache_timestamps.get(cache_key, 0) > self.config.cache_ttl:
            del self.response_cache[cache_key]
            del self.cache_timestamps[cache_key]
            return None
        
        logger.debug(f"Cache hit for key: {cache_key[:8]}...")
        return self.response_cache[cache_key]
    
    def _cache_response(self, cache_key: str, response: AIResponse):
        """Cache a successful response"""
        if not self.config.enable_cache or not response.is_success:
            return
            
        self.response_cache[cache_key] = response
        self.cache_timestamps[cache_key] = time.time()
        
        # Limit cache size to 100 entries
        if len(self.response_cache) > 100:
            oldest_key = min(self.cache_timestamps.keys(), 
                           key=lambda k: self.cache_timestamps[k])
            del self.response_cache[oldest_key]
            del self.cache_timestamps[oldest_key]