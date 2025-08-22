"""
AI Client Factory and Utilities for Cthulhu Solo TRPG System

Provides factory functions and utilities to create and manage AI clients
with automatic provider detection and configuration.
"""

import os
import logging
from typing import Optional, Type, Dict, Any, Union
from enum import Enum

from .base_ai_client import BaseAIClient, AIConfig, AIProvider, AIResponse, ResponseStatus
from .ollama_client import OllamaClient, OllamaConfig
from .openai_client import OpenAIClient, OpenAIConfig

logger = logging.getLogger(__name__)


class AIClientFactory:
    """Factory for creating AI clients with automatic provider detection"""
    
    _clients = {
        AIProvider.OLLAMA: OllamaClient,
        AIProvider.OPENAI: OpenAIClient,
    }
    
    _configs = {
        AIProvider.OLLAMA: OllamaConfig,
        AIProvider.OPENAI: OpenAIConfig,
    }
    
    @classmethod
    def create_client(cls, provider: Union[AIProvider, str], 
                     config: Optional[AIConfig] = None, 
                     **kwargs) -> BaseAIClient:
        """
        Create an AI client for the specified provider.
        
        Args:
            provider: AI provider (enum or string)
            config: Provider-specific configuration
            **kwargs: Additional configuration parameters
            
        Returns:
            Configured AI client instance
            
        Raises:
            ValueError: If provider is not supported
        """
        # Convert string to enum if needed
        if isinstance(provider, str):
            try:
                provider = AIProvider(provider.lower())
            except ValueError:
                raise ValueError(f"Unsupported AI provider: {provider}")
        
        # Handle AUTO provider - detect available service
        if provider == AIProvider.AUTO:
            provider = cls.detect_available_provider()
            logger.info(f"Auto-detected AI provider: {provider.value}")
        
        # Get client class
        client_class = cls._clients.get(provider)
        if not client_class:
            raise ValueError(f"No client implementation for provider: {provider.value}")
        
        # Create configuration if not provided
        if config is None:
            config_class = cls._configs[provider]
            config = config_class(**kwargs)
        elif kwargs:
            # Update config with additional parameters
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # Create and return client
        client = client_class(config)
        logger.info(f"Created {provider.value} client with model: {config.model}")
        return client
    
    @classmethod
    def detect_available_provider(cls) -> AIProvider:
        """
        Automatically detect which AI provider is available.
        
        Priority order:
        1. OpenAI (if API key is configured)
        2. Ollama (if service is running)
        3. Fall back to Ollama as default
        
        Returns:
            Detected AI provider
        """
        # Check OpenAI first (API key availability)
        if os.getenv("OPENAI_API_KEY"):
            logger.debug("OpenAI API key found - selecting OpenAI provider")
            return AIProvider.OPENAI
        
        # Check Ollama service availability
        try:
            from .ollama_client import test_ollama_connection
            import asyncio
            
            # Quick async test
            async def test():
                return await test_ollama_connection()
            
            # Run the test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                is_available = loop.run_until_complete(test())
                if is_available:
                    logger.debug("Ollama service detected - selecting Ollama provider")
                    return AIProvider.OLLAMA
            finally:
                loop.close()
        except Exception as e:
            logger.debug(f"Ollama detection failed: {e}")
        
        # Default to Ollama
        logger.debug("No providers auto-detected - defaulting to Ollama")
        return AIProvider.OLLAMA
    
    @classmethod
    def get_supported_providers(cls) -> list[AIProvider]:
        """Get list of supported AI providers"""
        return list(cls._clients.keys())
    
    @classmethod
    async def test_provider(cls, provider: Union[AIProvider, str], 
                           config: Optional[AIConfig] = None) -> Dict[str, Any]:
        """
        Test if a provider is available and working.
        
        Args:
            provider: AI provider to test
            config: Optional configuration
            
        Returns:
            Test results dictionary
        """
        try:
            client = cls.create_client(provider, config)
            async with client:
                result = await client.test_connection()
                result["provider"] = provider.value if isinstance(provider, AIProvider) else provider
                return result
        except Exception as e:
            return {
                "provider": provider.value if isinstance(provider, AIProvider) else provider,
                "success": False,
                "error": str(e),
                "available": False
            }


# Convenience functions for common usage patterns

def create_ollama_client(model: str = "gpt-oss:120b", 
                        base_url: str = "http://localhost:11434",
                        **kwargs) -> OllamaClient:
    """Create Ollama client with common settings"""
    config = OllamaConfig(model=model, base_url=base_url, **kwargs)
    return OllamaClient(config)


def create_openai_client(model: str = "gpt-4o-mini",
                        api_key: Optional[str] = None,
                        **kwargs) -> OpenAIClient:
    """Create OpenAI client with common settings"""
    config = OpenAIConfig(model=model, api_key=api_key, **kwargs)
    return OpenAIClient(config)


async def quick_generate(prompt: str, 
                        provider: Union[AIProvider, str] = AIProvider.AUTO,
                        system_prompt: str = "",
                        **kwargs) -> str:
    """
    Quick generation function for simple use cases.
    
    Args:
        prompt: The user prompt
        provider: AI provider to use (AUTO will detect available)
        system_prompt: Optional system prompt
        **kwargs: Additional configuration
        
    Returns:
        Generated text or empty string if failed
    """
    try:
        client = AIClientFactory.create_client(provider, **kwargs)
        async with client:
            response = await client.generate(prompt, system_prompt)
            return response.content if response.is_success else ""
    except Exception as e:
        logger.error(f"Quick generation failed: {e}")
        return ""


async def test_all_providers() -> Dict[str, Dict[str, Any]]:
    """
    Test all available AI providers.
    
    Returns:
        Dictionary of test results for each provider
    """
    results = {}
    
    for provider in AIClientFactory.get_supported_providers():
        try:
            result = await AIClientFactory.test_provider(provider)
            results[provider.value] = result
        except Exception as e:
            results[provider.value] = {
                "success": False,
                "error": str(e),
                "available": False
            }
    
    return results


# Configuration helpers

def get_ai_config_from_env(provider: AIProvider) -> AIConfig:
    """
    Create AI configuration from environment variables.
    
    Environment variables:
    - OPENAI_API_KEY: OpenAI API key
    - OLLAMA_BASE_URL: Ollama service URL (default: http://localhost:11434)
    - AI_MODEL: Model name to use
    - AI_TEMPERATURE: Temperature setting (default: 0.7)
    - AI_MAX_TOKENS: Maximum tokens (default: 4000)
    
    Args:
        provider: AI provider to create config for
        
    Returns:
        Configured AIConfig instance
    """
    common_kwargs = {
        "model": os.getenv("AI_MODEL", ""),
        "temperature": float(os.getenv("AI_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("AI_MAX_TOKENS", "4000")),
    }
    
    if provider == AIProvider.OPENAI:
        config = OpenAIConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=common_kwargs["model"] or "gpt-3.5-turbo",
            **{k: v for k, v in common_kwargs.items() if k != "model"}
        )
    elif provider == AIProvider.OLLAMA:
        config = OllamaConfig(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=common_kwargs["model"] or "gpt-oss:120b",
            **{k: v for k, v in common_kwargs.items() if k != "model"}
        )
    else:
        raise ValueError(f"No environment config support for provider: {provider.value}")
    
    return config


# Export public API
__all__ = [
    # Classes
    "AIClientFactory",
    "BaseAIClient", 
    "OllamaClient",
    "OpenAIClient",
    "AIConfig",
    "OllamaConfig", 
    "OpenAIConfig",
    "AIProvider",
    "AIResponse",
    "ResponseStatus",
    
    # Factory functions
    "create_ollama_client",
    "create_openai_client",
    
    # Utility functions
    "quick_generate",
    "test_all_providers",
    "get_ai_config_from_env",
]