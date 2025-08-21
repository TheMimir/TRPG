"""
Game Manager for Cthulhu Solo TRPG System

Central orchestrator that coordinates all game systems:
- System initialization and teardown
- Agent lifecycle management
- State coordination between components
- Error recovery and fallback handling
- Save/load game management
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path

from core.models import GameState, NarrativeContext, TensionLevel
from core.game_engine import GameEngine, Character
from agents.base_agent import AgentManager, BaseAgent
from ai.ollama_client import OllamaClient, OllamaConfig, test_ollama_connection
from data.scenarios.miskatonic_university_library import create_miskatonic_library_scenario


logger = logging.getLogger(__name__)


class GameStatus(Enum):
    """Current status of the game session"""
    NOT_INITIALIZED = "not_initialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    SAVING = "saving"
    LOADING = "loading"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class GameManagerConfig:
    """Configuration for the Game Manager"""
    # AI Configuration
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "gpt-oss:120b"
    ollama_timeout: float = 300.0
    
    # Save System
    save_directory: str = "saves"
    auto_save_interval: int = 5  # turns
    max_save_files: int = 20
    
    # Performance
    enable_caching: bool = True
    max_turn_time: float = 30.0  # maximum time per turn
    
    # Error Handling
    enable_fallback: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Logging
    log_level: str = "INFO"
    enable_debug_mode: bool = False


class GameManager:
    """
    Central game manager that orchestrates all systems.
    
    Responsibilities:
    - Initialize and manage all subsystems
    - Coordinate between game engine, agents, and UI
    - Handle save/load operations
    - Manage error recovery and fallbacks
    - Provide unified API for game operations
    """
    
    def __init__(self, config: Optional[GameManagerConfig] = None):
        """Initialize the game manager"""
        self.config = config or GameManagerConfig()
        self.status = GameStatus.NOT_INITIALIZED
        
        # Core systems
        self.game_engine: Optional[GameEngine] = None
        self.agent_manager: Optional[AgentManager] = None
        self.ollama_client: Optional[OllamaClient] = None
        self.current_scenario = None
        
        # Game state
        self.current_save_file: Optional[str] = None
        self.last_auto_save: int = 0
        self.error_count: int = 0
        self.start_time: float = 0.0
        
        # System health monitoring
        self.system_health: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, float] = {}
        
        logger.info("GameManager created")
    
    async def initialize(self) -> bool:
        """
        Initialize all game systems.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.status = GameStatus.INITIALIZING
            self.start_time = time.time()
            
            logger.info("Initializing GameManager...")
            
            # 1. Test Ollama connection
            await self._initialize_ollama()
            
            # 2. Initialize game engine
            await self._initialize_game_engine()
            
            # 3. Initialize agent manager
            await self._initialize_agent_manager()
            
            # 4. Setup save system
            await self._initialize_save_system()
            
            # 5. Register agents (placeholder - will be implemented with specific agents)
            await self._register_core_agents()
            
            # 6. System health check
            await self._perform_system_health_check()
            
            self.status = GameStatus.READY
            initialization_time = time.time() - self.start_time
            
            logger.info(f"GameManager initialized successfully in {initialization_time:.2f}s")
            return True
            
        except Exception as e:
            self.status = GameStatus.ERROR
            logger.error(f"Failed to initialize GameManager: {e}")
            await self._cleanup_on_error()
            return False
    
    async def _initialize_ollama(self):
        """Initialize Ollama client with connection testing"""
        logger.info("Initializing Ollama client...")
        
        # Test connection first
        is_connected = await test_ollama_connection(self.config.ollama_url)
        
        if not is_connected:
            logger.warning("Ollama service not available - will use fallback mode")
            if not self.config.enable_fallback:
                raise ConnectionError("Ollama not available and fallback disabled")
        
        # Create Ollama client
        ollama_config = OllamaConfig(
            base_url=self.config.ollama_url,
            model=self.config.ollama_model,
            timeout=self.config.ollama_timeout,
            max_retries=self.config.max_retries
        )
        
        self.ollama_client = OllamaClient(ollama_config)
        await self.ollama_client.connect()
        
        # Test with simple query
        test_result = await self.ollama_client.test_connection()
        self.system_health["ollama"] = {
            "status": "healthy" if test_result["success"] else "degraded",
            "response_time": test_result["response_time"],
            "last_check": time.time()
        }
        
        logger.info(f"Ollama client initialized - Status: {self.system_health['ollama']['status']}")
    
    async def _initialize_game_engine(self):
        """Initialize the game engine"""
        logger.info("Initializing game engine...")
        
        self.game_engine = GameEngine()
        
        self.system_health["game_engine"] = {
            "status": "healthy",
            "last_check": time.time()
        }
        
        logger.info("Game engine initialized")
    
    async def _initialize_agent_manager(self):
        """Initialize the agent manager"""
        logger.info("Initializing agent manager...")
        
        self.agent_manager = AgentManager(self.ollama_client)
        await self.agent_manager.initialize()
        
        self.system_health["agent_manager"] = {
            "status": "healthy",
            "last_check": time.time()
        }
        
        logger.info("Agent manager initialized")
    
    async def _initialize_save_system(self):
        """Initialize the save system"""
        logger.info("Initializing save system...")
        
        # Create save directory if it doesn't exist
        save_path = Path(self.config.save_directory)
        save_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        for subdir in ["autosaves", "quicksaves", "user_saves", "campaigns"]:
            (save_path / subdir).mkdir(exist_ok=True)
        
        self.system_health["save_system"] = {
            "status": "healthy",
            "save_directory": str(save_path.absolute()),
            "last_check": time.time()
        }
        
        logger.info(f"Save system initialized at: {save_path.absolute()}")
    
    async def _register_core_agents(self):
        """Register core AI agents for the game system"""
        logger.info("Registering core agents...")
        
        try:
            # Import agents
            from agents.story_agent import StoryAgent
            from agents.base_agent import AgentConfig
            
            registered_count = 0
            
            # Create and register Story Agent
            logger.info("Creating StoryAgent...")
            agent_config = AgentConfig(
                enable_fallback=True,
                max_retries=3,
                context_window_size=4000
            )
            
            story_agent = StoryAgent(self.ollama_client, agent_config)
            self.agent_manager.register_agent(story_agent)
            registered_count += 1
            logger.info("✅ StoryAgent registered successfully")
            
            # Initialize all registered agents
            await self.agent_manager.initialize_all_agents()
            
            # Update system health
            self.system_health["agents"] = {
                "status": "healthy",
                "registered_count": registered_count,
                "last_check": time.time(),
                "agents": list(self.agent_manager.agents.keys())
            }
            
            logger.info(f"✅ Core agents registration complete - {registered_count} agents registered")
            
        except Exception as e:
            logger.error(f"Failed to register core agents: {e}")
            self.system_health["agents"] = {
                "status": "error",
                "registered_count": 0,
                "last_check": time.time(),
                "error": str(e)
            }
            raise
    
    async def _perform_system_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        logger.info("Performing system health check...")
        
        health_report = {
            "timestamp": time.time(),
            "overall_status": "healthy",
            "systems": self.system_health.copy(),
            "performance": {}
        }
        
        # Check each system
        failed_systems = []
        
        for system_name, system_info in self.system_health.items():
            if system_info["status"] != "healthy":
                failed_systems.append(system_name)
        
        if failed_systems:
            health_report["overall_status"] = "degraded"
            logger.warning(f"Systems with issues: {failed_systems}")
        
        # Performance metrics
        initialization_time = time.time() - self.start_time
        health_report["performance"]["initialization_time"] = initialization_time
        
        self.system_health["overall"] = health_report
        
        logger.info(f"System health check complete - Status: {health_report['overall_status']}")
        return health_report
    
    async def _cleanup_on_error(self):
        """Cleanup resources when initialization fails"""
        logger.info("Cleaning up after initialization error...")
        
        if self.agent_manager:
            try:
                await self.agent_manager.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down agent manager: {e}")
        
        if self.ollama_client:
            try:
                await self.ollama_client.close()
            except Exception as e:
                logger.error(f"Error closing Ollama client: {e}")
    
    async def _load_scenario(self, scenario_name: str):
        """Load a scenario by name"""
        try:
            logger.info(f"Loading scenario: {scenario_name}")
            
            if scenario_name == "miskatonic_university_library":
                scenario = create_miskatonic_library_scenario()
                logger.info(f"Loaded scenario: {scenario.title}")
                return scenario
            else:
                logger.warning(f"Unknown scenario: {scenario_name}, using default")
                return create_miskatonic_library_scenario()
                
        except Exception as e:
            logger.error(f"Failed to load scenario {scenario_name}: {e}")
            return None
    
    async def start_new_game(self, character_data: Dict[str, Any], scenario_name: str = "miskatonic_university_library") -> bool:
        """
        Start a new game with the provided character and scenario.
        
        Args:
            character_data: Character creation data
            scenario_name: Name of the scenario to load
            
        Returns:
            True if game started successfully
        """
        try:
            if self.status != GameStatus.READY:
                raise RuntimeError(f"Cannot start game - Status: {self.status}")
            
            logger.info(f"Starting new game with scenario: {scenario_name}...")
            self.status = GameStatus.RUNNING
            
            # Load scenario
            self.current_scenario = await self._load_scenario(scenario_name)
            
            # Create character in game engine
            character = self.game_engine.create_character(character_data)
            
            # Get initial scene from scenario
            if self.current_scenario:
                initial_scene = "library_entrance"  # Default starting scene for Miskatonic Library
                self.current_scenario.advance_to_scene(initial_scene)
            else:
                initial_scene = "library_entrance"  # Fallback
            
            # Initialize narrative context
            narrative_context = NarrativeContext(
                scene_id=initial_scene,
                turn_number=1,
                character_state=character.to_dict(),
                tension_level=TensionLevel.CALM
            )
            
            # Set game engine state
            self.game_engine.current_scene = initial_scene
            self.game_engine.turn_number = 1
            
            # Set scenario-specific flags
            if self.current_scenario:
                self.game_engine.game_flags["scenario"] = scenario_name
                self.game_engine.game_flags["scenario_title"] = self.current_scenario.title
            
            # Reset auto-save counter
            self.last_auto_save = 0
            
            # Create initial auto-save
            await self._auto_save()
            
            logger.info(f"New game started with character: {character.name} in scene: {initial_scene}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start new game: {e}")
            self.status = GameStatus.ERROR
            return False
    
    async def load_game(self, save_file: str) -> bool:
        """
        Load a saved game.
        
        Args:
            save_file: Path to save file
            
        Returns:
            True if loaded successfully
        """
        try:
            if self.status not in [GameStatus.READY, GameStatus.RUNNING]:
                raise RuntimeError(f"Cannot load game - Status: {self.status}")
            
            logger.info(f"Loading game from: {save_file}")
            self.status = GameStatus.LOADING
            
            # Load game state
            save_path = Path(self.config.save_directory) / save_file
            
            if not save_path.exists():
                raise FileNotFoundError(f"Save file not found: {save_path}")
            
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Create game state from save data
            game_state = GameState.from_dict(save_data)
            
            # Load into game engine
            self.game_engine.load_game_state(game_state)
            
            # Update current save file
            self.current_save_file = save_file
            
            self.status = GameStatus.RUNNING
            logger.info(f"Game loaded successfully from: {save_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            self.status = GameStatus.ERROR
            return False
    
    async def save_game(self, save_name: str, save_type: str = "user_saves") -> bool:
        """
        Save the current game.
        
        Args:
            save_name: Name for the save file
            save_type: Type of save (user_saves, quicksaves, campaigns)
            
        Returns:
            True if saved successfully
        """
        try:
            if self.status != GameStatus.RUNNING:
                raise RuntimeError(f"Cannot save game - Status: {self.status}")
            
            logger.info(f"Saving game: {save_name}")
            self.status = GameStatus.SAVING
            
            # Get current game state
            game_state = self.game_engine.get_game_state()
            
            # Add manager metadata
            game_state.game_metadata.update({
                "save_name": save_name,
                "save_type": save_type,
                "manager_version": "1.0.0",
                "character_name": self.game_engine.character.name if self.game_engine.character else "Unknown"
            })
            
            # Determine save path
            save_dir = Path(self.config.save_directory) / save_type
            save_path = save_dir / f"{save_name}.json"
            
            # Ensure unique filename
            counter = 1
            while save_path.exists():
                save_path = save_dir / f"{save_name}_{counter}.json"
                counter += 1
            
            # Save to file
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(game_state.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Update current save file
            self.current_save_file = str(save_path.relative_to(self.config.save_directory))
            
            self.status = GameStatus.RUNNING
            logger.info(f"Game saved to: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            self.status = GameStatus.RUNNING  # Return to running state
            return False
    
    async def _auto_save(self) -> bool:
        """Perform automatic save"""
        if not self.game_engine or not self.game_engine.character:
            return False
        
        turn_number = self.game_engine.turn_number
        character_name = self.game_engine.character.name
        
        save_name = f"auto_save_{int(time.time())}"
        return await self.save_game(save_name, "autosaves")
    
    async def process_turn(self, player_action: str) -> Dict[str, Any]:
        """
        Process a complete game turn.
        
        Args:
            player_action: Player's input action
            
        Returns:
            Turn result with story content and game state updates
        """
        try:
            if self.status != GameStatus.RUNNING:
                raise RuntimeError(f"Cannot process turn - Status: {self.status}")
            
            turn_start_time = time.time()
            
            # Increment turn counter
            self.game_engine.turn_number += 1
            current_turn = self.game_engine.turn_number
            
            logger.info(f"Processing turn {current_turn}: {player_action[:50]}...")
            
            # This will be expanded when we implement agents and controllers
            # For now, return a basic structure
            
            result = {
                "turn_number": current_turn,
                "player_action": player_action,
                "story_content": {
                    "text": f"Turn {current_turn}: Processing your action '{player_action}'",
                    "scene_id": self.game_engine.current_scene,
                    "tension_level": "calm",
                    "investigation_opportunities": [],
                },
                "character_state": self.game_engine.get_character_summary(),
                "game_state": {
                    "can_continue": True,
                    "scene_id": self.game_engine.current_scene,
                    "turn_number": current_turn
                },
                "processing_time": time.time() - turn_start_time
            }
            
            # Auto-save check
            if current_turn - self.last_auto_save >= self.config.auto_save_interval:
                await self._auto_save()
                self.last_auto_save = current_turn
            
            # Update performance metrics
            self.performance_metrics["last_turn_time"] = result["processing_time"]
            
            logger.info(f"Turn {current_turn} processed in {result['processing_time']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process turn: {e}")
            self.error_count += 1
            
            return {
                "error": True,
                "error_message": str(e),
                "turn_number": self.game_engine.turn_number if self.game_engine else 0,
                "processing_time": time.time() - turn_start_time if 'turn_start_time' in locals() else 0
            }
    
    async def shutdown(self):
        """Shutdown the game manager and all subsystems"""
        logger.info("Shutting down GameManager...")
        
        try:
            self.status = GameStatus.SHUTDOWN
            
            # Auto-save before shutdown
            if (self.status == GameStatus.RUNNING and 
                self.game_engine and 
                self.game_engine.character):
                await self._auto_save()
            
            # Shutdown subsystems
            if self.agent_manager:
                await self.agent_manager.shutdown()
            
            if self.ollama_client:
                await self.ollama_client.close()
            
            # Clear references
            self.game_engine = None
            self.agent_manager = None
            self.ollama_client = None
            
            shutdown_time = time.time() - self.start_time
            logger.info(f"GameManager shutdown complete (ran for {shutdown_time:.1f}s)")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current game manager status"""
        return {
            "status": self.status.value,
            "uptime": time.time() - self.start_time if self.start_time > 0 else 0,
            "current_save": self.current_save_file,
            "error_count": self.error_count,
            "turn_number": self.game_engine.turn_number if self.game_engine else 0,
            "character_name": (self.game_engine.character.name 
                             if self.game_engine and self.game_engine.character else None),
            "system_health": self.system_health,
            "performance_metrics": self.performance_metrics
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get detailed performance statistics"""
        stats = {
            "manager": {
                "uptime": time.time() - self.start_time if self.start_time > 0 else 0,
                "error_count": self.error_count,
                "turns_processed": self.game_engine.turn_number if self.game_engine else 0,
            },
            "systems": {}
        }
        
        # Add system-specific stats
        if self.game_engine:
            stats["systems"]["game_engine"] = self.game_engine.get_statistics()
        
        if self.agent_manager:
            stats["systems"]["agents"] = self.agent_manager.get_all_performance_stats()
        
        if self.ollama_client:
            stats["systems"]["ollama"] = self.ollama_client.get_statistics()
        
        return stats
    
    def get_current_scenario_content(self):
        """Get current story content from the loaded scenario"""
        if self.current_scenario and self.game_engine:
            return self.current_scenario.get_scene_initial_content()
        return None
    
    def list_save_files(self, save_type: str = "user_saves") -> List[Dict[str, Any]]:
        """
        List available save files.
        
        Args:
            save_type: Type of saves to list
            
        Returns:
            List of save file information
        """
        save_dir = Path(self.config.save_directory) / save_type
        save_files = []
        
        if not save_dir.exists():
            return save_files
        
        for save_file in save_dir.glob("*.json"):
            try:
                stat = save_file.stat()
                
                # Try to read save metadata
                metadata = {"character_name": "Unknown", "turn_number": 0}
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    if "game_metadata" in save_data:
                        metadata.update(save_data["game_metadata"])
                    
                    if "character_data" in save_data:
                        metadata["character_name"] = save_data["character_data"].get("name", "Unknown")
                    
                except Exception:
                    pass  # Use default metadata
                
                save_files.append({
                    "filename": save_file.name,
                    "path": str(save_file.relative_to(self.config.save_directory)),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "character_name": metadata.get("character_name", "Unknown"),
                    "turn_number": metadata.get("turn_number", 0),
                    "save_type": save_type
                })
                
            except Exception as e:
                logger.warning(f"Error reading save file {save_file}: {e}")
        
        # Sort by modification time (newest first)
        save_files.sort(key=lambda x: x["modified"], reverse=True)
        
        return save_files
    
    async def cleanup_old_saves(self):
        """Clean up old auto-save files"""
        try:
            autosaves = self.list_save_files("autosaves")
            
            if len(autosaves) > self.config.max_save_files:
                # Remove oldest files
                to_remove = autosaves[self.config.max_save_files:]
                
                for save_info in to_remove:
                    save_path = Path(self.config.save_directory) / save_info["path"]
                    try:
                        save_path.unlink()
                        logger.debug(f"Removed old auto-save: {save_info['filename']}")
                    except Exception as e:
                        logger.warning(f"Failed to remove old save {save_path}: {e}")
                
                logger.info(f"Cleaned up {len(to_remove)} old auto-saves")
                
        except Exception as e:
            logger.error(f"Error cleaning up old saves: {e}")


# Convenience functions for external use
async def create_game_manager(config: Optional[GameManagerConfig] = None) -> GameManager:
    """Create and initialize a game manager"""
    manager = GameManager(config)
    
    if await manager.initialize():
        return manager
    else:
        await manager.shutdown()
        raise RuntimeError("Failed to initialize GameManager")


async def quick_game_session(character_data: Dict[str, Any], 
                           config: Optional[GameManagerConfig] = None) -> GameManager:
    """Create a game manager and start a new game in one call"""
    manager = await create_game_manager(config)
    
    if await manager.start_new_game(character_data):
        return manager
    else:
        await manager.shutdown()
        raise RuntimeError("Failed to start new game")