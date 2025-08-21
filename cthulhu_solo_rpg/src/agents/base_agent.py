"""
Base Agent for Cthulhu Solo TRPG System

Provides the foundation for all AI agents with:
- Memory management with importance scoring
- Context building and pruning
- Response generation with retry logic
- Performance metrics tracking
- Fallback system for robustness
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import uuid

from core.models import AgentMemory, NarrativeContext, calculate_memory_relevance
from ai.ollama_client import OllamaClient, OllamaConfig, OllamaResponse, ResponseStatus


logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for AI agents"""
    max_memory_size: int = 1000  # Maximum number of memories to store
    memory_cleanup_threshold: float = 0.8  # When to trigger memory cleanup
    context_window_size: int = 4000  # Maximum context size in characters
    max_retries: int = 3  # Maximum retries for failed operations
    default_importance: int = 5  # Default importance for new memories
    memory_decay_hours: float = 24.0  # Hours after which memories start decaying
    enable_fallback: bool = True  # Whether to use fallback responses
    

@dataclass
class AgentResponse:
    """Response from an agent with metadata"""
    content: str
    confidence: float = 1.0
    source: str = "ai"  # "ai", "cache", "fallback"
    processing_time: float = 0.0
    memories_used: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if the response is valid"""
        return bool(self.content.strip()) and self.confidence > 0.0


class BaseAgent(ABC):
    """
    Base class for all AI agents in the Cthulhu Solo TRPG system.
    
    Provides common functionality for memory management, context building,
    and interaction with the Ollama AI service.
    """
    
    def __init__(self, agent_name: str, ollama_client: Optional[OllamaClient] = None,
                 config: Optional[AgentConfig] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Unique name for this agent
            ollama_client: Ollama client instance (will create if None)
            config: Agent configuration
        """
        self.agent_name = agent_name
        self.config = config or AgentConfig()
        self.ollama_client = ollama_client
        
        # Memory system
        self.memory: List[AgentMemory] = []
        self.memory_index: Dict[str, List[int]] = {}  # Keyword to memory indices
        
        # Performance tracking
        self.request_count = 0
        self.error_count = 0
        self.total_processing_time = 0.0
        self.last_request_time = 0.0
        
        # Response cache for identical requests
        self.response_cache: Dict[str, AgentResponse] = {}
        self.cache_timestamps: Dict[str, float] = {}
        
        logger.info(f"Initialized {self.agent_name} agent")
    
    async def initialize(self):
        """Initialize the agent (called during startup)"""
        if self.ollama_client is None:
            # Create default Ollama client
            ollama_config = OllamaConfig()
            self.ollama_client = OllamaClient(ollama_config)
            await self.ollama_client.connect()
        
        logger.info(f"{self.agent_name} agent initialized")
    
    async def shutdown(self):
        """Shutdown the agent and cleanup resources"""
        if self.ollama_client:
            await self.ollama_client.close()
        
        logger.info(f"{self.agent_name} agent shutdown")
    
    def add_memory(self, content: str, importance: int = None, 
                  memory_type: str = "general", scene_context: str = "",
                  keywords: List[str] = None) -> str:
        """
        Add a new memory to the agent's memory system.
        
        Args:
            content: Memory content
            importance: Importance score (1-10)
            memory_type: Type of memory
            scene_context: Scene where memory was created
            keywords: Relevant keywords for indexing
            
        Returns:
            Memory ID
        """
        if importance is None:
            importance = self.config.default_importance
        
        memory = AgentMemory(
            content=content,
            timestamp=time.time(),
            importance=importance,
            memory_type=memory_type,
            scene_context=scene_context,
            relevance_keywords=keywords or []
        )
        
        # Add to memory list
        memory_id = str(uuid.uuid4())
        memory.metadata["memory_id"] = memory_id
        self.memory.append(memory)
        
        # Update keyword index
        all_keywords = keywords or []
        all_keywords.extend(content.lower().split())
        
        for keyword in all_keywords:
            if keyword not in self.memory_index:
                self.memory_index[keyword] = []
            self.memory_index[keyword].append(len(self.memory) - 1)
        
        # Cleanup if necessary
        if len(self.memory) > self.config.max_memory_size * self.config.memory_cleanup_threshold:
            self._cleanup_memory()
        
        logger.debug(f"Added memory to {self.agent_name}: {content[:50]}...")
        return memory_id
    
    def get_relevant_memories(self, context: Dict[str, Any], 
                            limit: int = 10) -> List[AgentMemory]:
        """
        Retrieve memories relevant to the current context.
        
        Args:
            context: Current context information
            limit: Maximum number of memories to return
            
        Returns:
            List of relevant memories sorted by relevance
        """
        if not self.memory:
            return []
        
        # Extract keywords from context
        keywords = []
        if "keywords" in context:
            keywords.extend(context["keywords"])
        if "scene_id" in context:
            keywords.append(context["scene_id"])
        if "player_action" in context:
            keywords.extend(context["player_action"].lower().split())
        
        current_time = time.time()
        current_scene = context.get("scene_id", "")
        
        # Calculate relevance scores
        memory_scores = []
        for i, memory in enumerate(self.memory):
            relevance = calculate_memory_relevance(
                memory, keywords, current_scene, current_time
            )
            if relevance > 0:
                memory_scores.append((relevance, i, memory))
        
        # Sort by relevance and return top memories
        memory_scores.sort(reverse=True, key=lambda x: x[0])
        return [mem for _, _, mem in memory_scores[:limit]]
    
    def _cleanup_memory(self):
        """
        Clean up old and low-importance memories to stay within limits.
        
        Uses a combination of age, importance, and frequency of access
        to determine which memories to remove.
        """
        if len(self.memory) <= self.config.max_memory_size:
            return
        
        current_time = time.time()
        decay_threshold = self.config.memory_decay_hours * 3600
        
        # Calculate cleanup scores for each memory
        cleanup_candidates = []
        for i, memory in enumerate(self.memory):
            age = current_time - memory.timestamp
            age_factor = min(age / decay_threshold, 2.0)  # Cap at 2x decay
            
            # Lower scores = higher priority for removal
            cleanup_score = memory.importance * (1.0 - age_factor * 0.5)
            cleanup_candidates.append((cleanup_score, i))
        
        # Sort by cleanup score (lowest first) and remove bottom third
        cleanup_candidates.sort(key=lambda x: x[0])
        target_size = int(self.config.max_memory_size * 0.7)  # Remove to 70% capacity
        to_remove = len(self.memory) - target_size
        
        if to_remove > 0:
            remove_indices = [idx for _, idx in cleanup_candidates[:to_remove]]
            remove_indices.sort(reverse=True)  # Remove from end to avoid index shifts
            
            for idx in remove_indices:
                removed_memory = self.memory.pop(idx)
                logger.debug(f"Removed memory: {removed_memory.content[:30]}...")
            
            # Rebuild keyword index
            self._rebuild_keyword_index()
            
            logger.info(f"Cleaned up {to_remove} memories from {self.agent_name}")
    
    def _rebuild_keyword_index(self):
        """Rebuild the keyword index after memory cleanup"""
        self.memory_index.clear()
        
        for i, memory in enumerate(self.memory):
            keywords = memory.relevance_keywords + memory.content.lower().split()
            for keyword in keywords:
                if keyword not in self.memory_index:
                    self.memory_index[keyword] = []
                self.memory_index[keyword].append(i)
    
    def build_context(self, narrative_context: NarrativeContext,
                     additional_context: Dict[str, Any] = None) -> str:
        """
        Build context string for AI prompts.
        
        Args:
            narrative_context: Current narrative context
            additional_context: Additional context information
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Basic context
        context_parts.append(f"Scene: {narrative_context.scene_id}")
        context_parts.append(f"Turn: {narrative_context.turn_number}")
        context_parts.append(f"Tension Level: {narrative_context.tension_level.value}")
        
        # Character state
        if narrative_context.character_state:
            context_parts.append("Character State:")
            for key, value in narrative_context.character_state.items():
                if key in ["name", "health", "sanity", "current_location"]:
                    context_parts.append(f"  {key}: {value}")
        
        # Recent choices
        if narrative_context.choice_history:
            recent_choices = narrative_context.choice_history[-3:]
            context_parts.append("Recent Actions:")
            for choice in recent_choices:
                context_parts.append(f"  - {choice}")
        
        # Story threads
        if narrative_context.story_threads:
            context_parts.append("Active Story Threads:")
            for thread, status in narrative_context.story_threads.items():
                context_parts.append(f"  - {thread}: {status}")
        
        # Relevant memories
        if additional_context:
            memories = self.get_relevant_memories(additional_context, limit=5)
            if memories:
                context_parts.append("Relevant Memories:")
                for memory in memories:
                    context_parts.append(f"  - {memory.content[:100]}...")
        
        # Additional context
        if additional_context:
            for key, value in additional_context.items():
                if key not in ["keywords", "memories"]:
                    context_parts.append(f"{key}: {value}")
        
        context_str = "\n".join(context_parts)
        
        # Trim if too long
        if len(context_str) > self.config.context_window_size:
            context_str = context_str[:self.config.context_window_size] + "...[truncated]"
        
        return context_str
    
    async def _generate_ai_response(self, prompt: str, system_prompt: str = "") -> OllamaResponse:
        """
        Generate response using AI with error handling.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            
        Returns:
            OllamaResponse
        """
        try:
            if not self.ollama_client:
                await self.initialize()
            
            response = await self.ollama_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                use_cache=True
            )
            
            return response
            
        except Exception as e:
            logger.error(f"AI generation failed in {self.agent_name}: {e}")
            return OllamaResponse(
                content="",
                status=ResponseStatus.UNKNOWN_ERROR,
                error_message=str(e)
            )
    
    def _get_fallback_response(self, context: Dict[str, Any]) -> str:
        """
        Generate a fallback response when AI is unavailable.
        
        This should be overridden by specific agents to provide
        context-appropriate fallback responses.
        """
        fallback_responses = [
            "The situation continues to unfold before you.",
            "You sense that something important is happening.",
            "The atmosphere grows more tense as you proceed.",
            "Your actions have consequences in this mysterious place.",
            "You must decide carefully how to proceed."
        ]
        
        # Simple hash-based selection for consistency
        hash_val = hash(str(context)) % len(fallback_responses)
        return fallback_responses[hash_val]
    
    async def process_input(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Process input and generate response.
        
        This is the main interface method that subclasses should override
        to implement specific agent behavior.
        
        Args:
            context: Input context
            
        Returns:
            AgentResponse
        """
        start_time = time.time()
        self.request_count += 1
        self.last_request_time = start_time
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(context)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return cached_response
            
            # Process with retries
            for attempt in range(self.config.max_retries):
                try:
                    response = await self._process_input_impl(context)
                    
                    if response.is_valid:
                        # Cache successful response
                        self._cache_response(cache_key, response)
                        
                        # Update statistics
                        response.processing_time = time.time() - start_time
                        self.total_processing_time += response.processing_time
                        
                        return response
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed in {self.agent_name}: {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(0.5 * (attempt + 1))  # Progressive delay
                    else:
                        raise
            
            # All retries failed, use fallback
            if self.config.enable_fallback:
                fallback_content = self._get_fallback_response(context)
                return AgentResponse(
                    content=fallback_content,
                    confidence=0.3,
                    source="fallback",
                    processing_time=time.time() - start_time
                )
            else:
                raise Exception("All retries failed and fallback disabled")
                
        except Exception as e:
            self.error_count += 1
            logger.error(f"Failed to process input in {self.agent_name}: {e}")
            
            return AgentResponse(
                content="I apologize, but I'm having difficulty processing your request right now.",
                confidence=0.1,
                source="error",
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    @abstractmethod
    async def _process_input_impl(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Implementation of input processing (to be overridden by subclasses).
        
        Args:
            context: Input context
            
        Returns:
            AgentResponse
        """
        pass
    
    def _generate_cache_key(self, context: Dict[str, Any]) -> str:
        """Generate cache key for context"""
        # Create a simplified version of context for caching
        cache_context = {
            "agent": self.agent_name,
            "action": context.get("player_action", ""),
            "scene": context.get("scene_id", ""),
            "turn": context.get("turn_number", 0)
        }
        return json.dumps(cache_context, sort_keys=True)
    
    def _get_cached_response(self, cache_key: str) -> Optional[AgentResponse]:
        """Get cached response if still valid"""
        if cache_key not in self.response_cache:
            return None
        
        # Check if cache is still valid (5 minutes)
        timestamp = self.cache_timestamps.get(cache_key, 0)
        if time.time() - timestamp > 300:  # 5 minutes
            del self.response_cache[cache_key]
            del self.cache_timestamps[cache_key]
            return None
        
        return self.response_cache[cache_key]
    
    def _cache_response(self, cache_key: str, response: AgentResponse):
        """Cache a response"""
        self.response_cache[cache_key] = response
        self.cache_timestamps[cache_key] = time.time()
        
        # Limit cache size
        if len(self.response_cache) > 50:
            oldest_key = min(self.cache_timestamps.keys(), 
                           key=lambda k: self.cache_timestamps[k])
            del self.response_cache[oldest_key]
            del self.cache_timestamps[oldest_key]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this agent"""
        avg_processing_time = (self.total_processing_time / max(1, self.request_count))
        
        return {
            "agent_name": self.agent_name,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(1, self.request_count),
            "average_processing_time": avg_processing_time,
            "memory_count": len(self.memory),
            "cache_size": len(self.response_cache),
            "last_request_time": self.last_request_time,
        }
    
    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        self.cache_timestamps.clear()
    
    def clear_memory(self):
        """Clear all memories (use with caution)"""
        self.memory.clear()
        self.memory_index.clear()
        logger.warning(f"Cleared all memory for {self.agent_name}")
    
    def export_memories(self) -> List[Dict[str, Any]]:
        """Export memories for saving/backup"""
        return [
            {
                "content": mem.content,
                "timestamp": mem.timestamp,
                "importance": mem.importance,
                "memory_type": mem.memory_type,
                "scene_context": mem.scene_context,
                "relevance_keywords": mem.relevance_keywords,
                "metadata": mem.metadata
            }
            for mem in self.memory
        ]
    
    def import_memories(self, memory_data: List[Dict[str, Any]]):
        """Import memories from saved data"""
        self.memory.clear()
        self.memory_index.clear()
        
        for mem_dict in memory_data:
            memory = AgentMemory(
                content=mem_dict["content"],
                timestamp=mem_dict["timestamp"],
                importance=mem_dict["importance"],
                memory_type=mem_dict.get("memory_type", "general"),
                scene_context=mem_dict.get("scene_context", ""),
                relevance_keywords=mem_dict.get("relevance_keywords", []),
                metadata=mem_dict.get("metadata", {})
            )
            self.memory.append(memory)
        
        self._rebuild_keyword_index()
        logger.info(f"Imported {len(memory_data)} memories for {self.agent_name}")


class AgentManager:
    """
    Manager for coordinating multiple agents.
    
    Provides centralized management of agent lifecycle,
    shared resources, and inter-agent communication.
    """
    
    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        """Initialize the agent manager"""
        self.ollama_client = ollama_client
        self.agents: Dict[str, BaseAgent] = {}
        self.shared_memory: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize the agent manager and shared resources"""
        if not self.ollama_client:
            ollama_config = OllamaConfig()
            self.ollama_client = OllamaClient(ollama_config)
            await self.ollama_client.connect()
        
        logger.info("AgentManager initialized")
    
    async def shutdown(self):
        """Shutdown all agents and cleanup"""
        for agent in self.agents.values():
            await agent.shutdown()
        
        if self.ollama_client:
            await self.ollama_client.close()
        
        logger.info("AgentManager shutdown")
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the manager"""
        agent.ollama_client = self.ollama_client
        self.agents[agent.agent_name] = agent
        logger.info(f"Registered agent: {agent.agent_name}")
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(agent_name)
    
    async def initialize_all_agents(self):
        """Initialize all registered agents"""
        for agent in self.agents.values():
            await agent.initialize()
        
        logger.info(f"Initialized {len(self.agents)} agents")
    
    def get_all_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all agents"""
        return {
            agent_name: agent.get_performance_stats()
            for agent_name, agent in self.agents.items()
        }