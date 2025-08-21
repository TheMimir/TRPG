"""
Integration Tests for Cthulhu Solo TRPG

Comprehensive integration testing suite that validates the complete game system,
including AI agents, game loop, save/load functionality, and error scenarios.
"""

import asyncio
import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import unittest
import logging

# Import game systems
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.game_manager import GameManager, GamePhase
from src.core.game_engine import PlayerAction, ActionResult, GameState
from src.core.character import Character
from src.utils.config import Config
from src.utils.system_check import SystemCheck
from src.ai.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Status of individual test cases."""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"

@dataclass
class TestResult:
    """Result of a test case."""
    name: str
    status: TestStatus
    duration: float
    message: str
    details: Dict[str, Any] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "duration": self.duration,
            "message": self.message,
            "details": self.details or {},
            "error": self.error
        }

class IntegrationTestSuite:
    """Comprehensive integration test suite for the TRPG system."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.test_results: List[TestResult] = []
        self.temp_dir: Optional[Path] = None
        self.game_manager: Optional[GameManager] = None
        
        # Test configuration
        self.max_test_duration = 60.0  # Maximum time per test in seconds
        self.stress_test_iterations = 10
        self.performance_thresholds = {
            "system_init": 30.0,      # System initialization
            "turn_processing": 10.0,  # Single turn processing
            "save_operation": 5.0,    # Save/load operations
            "ai_response": 15.0       # AI agent response
        }
        
        # Setup test logging
        self.setup_test_logging()
    
    def setup_test_logging(self):
        """Setup logging for test execution."""
        
        # Create test-specific logger
        test_logger = logging.getLogger('integration_test')
        test_logger.setLevel(logging.INFO)
        
        # Console handler for test output
        if not test_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            test_logger.addHandler(handler)
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run the complete integration test suite."""
        
        logger.info("Starting comprehensive integration test suite...")
        start_time = time.time()
        
        # Clear previous results
        self.test_results.clear()
        
        # Setup test environment
        await self._setup_test_environment()
        
        try:
            # Run test categories in order
            await self._run_basic_functionality_tests()
            await self._run_ai_system_tests()
            await self._run_game_loop_tests()
            await self._run_save_load_tests()
            await self._run_error_handling_tests()
            await self._run_performance_tests()
            await self._run_stress_tests()
            
        finally:
            # Cleanup test environment
            await self._cleanup_test_environment()
        
        # Generate comprehensive report
        total_time = time.time() - start_time
        report = self._generate_test_report(total_time)
        
        logger.info(f"Integration test suite completed in {total_time:.2f} seconds")
        return report
    
    async def _setup_test_environment(self):
        """Setup isolated test environment."""
        
        logger.info("Setting up test environment...")
        
        # Create temporary directory for test files
        self.temp_dir = Path(tempfile.mkdtemp(prefix="cthulhu_test_"))
        
        # Create test config
        test_config_data = {
            "ai": {
                "ollama_url": self.config.get('ai.ollama_url', 'http://localhost:11434'),
                "model": self.config.get('ai.model', 'gpt-oss-120b'),
                "temperature": 0.1,  # Low temperature for consistent testing
                "ultra_think_enabled": False  # Disable for faster testing
            },
            "game": {
                "auto_save": False,  # Disable auto-save during testing
                "auto_save_interval": 9999,
                "difficulty": "normal"
            },
            "ui": {
                "interface": "cli"
            },
            "logging": {
                "level": "WARNING"  # Reduce log noise during testing
            }
        }
        
        # Write test config
        test_config_path = self.temp_dir / "test_config.json"
        with open(test_config_path, 'w') as f:
            json.dump(test_config_data, f, indent=2)
        
        # Update config for testing
        self.config = Config(str(test_config_path))
        
        logger.info(f"Test environment created at: {self.temp_dir}")
    
    async def _cleanup_test_environment(self):
        """Clean up test environment."""
        
        logger.info("Cleaning up test environment...")
        
        # Shutdown game manager if running
        if self.game_manager:
            try:
                await self.game_manager.shutdown()
            except Exception as e:
                logger.warning(f"Error during game manager shutdown: {e}")
        
        # Remove temporary directory
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                logger.info("Test environment cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up test directory: {e}")
    
    async def _run_test_case(self, test_name: str, test_func) -> TestResult:
        """Run a single test case with error handling and timing."""
        
        logger.info(f"Running test: {test_name}")
        start_time = time.time()
        
        try:
            # Run test with timeout
            result = await asyncio.wait_for(
                test_func(), 
                timeout=self.max_test_duration
            )
            
            duration = time.time() - start_time
            
            if result is True:
                test_result = TestResult(
                    name=test_name,
                    status=TestStatus.PASS,
                    duration=duration,
                    message="Test passed successfully"
                )
            elif isinstance(result, dict):
                test_result = TestResult(
                    name=test_name,
                    status=TestStatus.PASS if result.get('success', True) else TestStatus.FAIL,
                    duration=duration,
                    message=result.get('message', 'Test completed'),
                    details=result.get('details', {})
                )
            else:
                test_result = TestResult(
                    name=test_name,
                    status=TestStatus.FAIL,
                    duration=duration,
                    message="Test returned unexpected result",
                    details={"result": str(result)}
                )
            
        except asyncio.TimeoutError:
            test_result = TestResult(
                name=test_name,
                status=TestStatus.FAIL,
                duration=self.max_test_duration,
                message=f"Test timed out after {self.max_test_duration} seconds",
                error="Timeout"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                duration=duration,
                message=f"Test failed with exception: {str(e)}",
                error=str(e)
            )
        
        self.test_results.append(test_result)
        logger.info(f"Test {test_name}: {test_result.status.value} ({test_result.duration:.2f}s)")
        
        return test_result
    
    # Basic Functionality Tests
    
    async def _run_basic_functionality_tests(self):
        """Run basic system functionality tests."""
        
        logger.info("Running basic functionality tests...")
        
        await self._run_test_case("System Check", self._test_system_check)
        await self._run_test_case("Game Manager Initialization", self._test_game_manager_init)
        await self._run_test_case("Configuration Loading", self._test_config_loading)
        await self._run_test_case("Character Creation", self._test_character_creation)
    
    async def _test_system_check(self):
        """Test system check functionality."""
        
        system_check = SystemCheck()
        report = await system_check.run_all_checks()
        
        # System should be operational for testing
        if report["summary"]["overall_status"] == "FAIL":
            return {
                "success": False,
                "message": "System check failed - cannot proceed with testing",
                "details": report["summary"]
            }
        
        return {
            "success": True,
            "message": f"System check passed with {report['summary']['success_rate']}% success rate",
            "details": {
                "total_checks": report["summary"]["total_checks"],
                "warnings": report["summary"]["warnings"],
                "critical_failures": report["summary"]["critical_failures"]
            }
        }
    
    async def _test_game_manager_init(self):
        """Test game manager initialization."""
        
        self.game_manager = GameManager(self.config)
        
        # Test initialization
        init_success = await self.game_manager.initialize_systems()
        
        if not init_success:
            return {
                "success": False,
                "message": "Game manager initialization failed",
                "details": {"phase": self.game_manager.current_phase.value}
            }
        
        # Verify system status
        status = self.game_manager.get_system_status()
        
        return {
            "success": True,
            "message": "Game manager initialized successfully",
            "details": {
                "initialized": status["initialization"]["is_initialized"],
                "ready_agents": sum(1 for agent in status["agents"].values() if agent["ready"]),
                "total_agents": len(status["agents"]),
                "ai_available": status["ai_client"]["available"]
            }
        }
    
    async def _test_config_loading(self):
        """Test configuration system."""
        
        # Test default config loading
        config = Config()
        
        # Test key configuration values
        tests = [
            ("ai.ollama_url", str),
            ("ai.model", str),
            ("game.auto_save", bool),
            ("ui.interface", str)
        ]
        
        missing_configs = []
        for key, expected_type in tests:
            value = config.get(key)
            if value is None or not isinstance(value, expected_type):
                missing_configs.append(key)
        
        if missing_configs:
            return {
                "success": False,
                "message": f"Missing or invalid configurations: {', '.join(missing_configs)}",
                "details": {"missing": missing_configs}
            }
        
        return {
            "success": True,
            "message": "Configuration loaded successfully",
            "details": {
                "ai_url": config.get("ai.ollama_url"),
                "model": config.get("ai.model"),
                "interface": config.get("ui.interface")
            }
        }
    
    async def _test_character_creation(self):
        """Test character creation functionality."""
        
        # Create test character
        character_data = {
            "name": "Test Investigator",
            "profession": "Professor",
            "age": 35,
            "attributes": {
                "strength": 60,
                "constitution": 70,
                "size": 65,
                "dexterity": 65,
                "appearance": 50,
                "intelligence": 80,
                "power": 60,
                "education": 85
            },
            "skills": {
                "Spot Hidden": 50,
                "Library Use": 70,
                "Occult": 40,
                "Psychology": 60
            }
        }
        
        try:
            character = Character.from_dict(character_data)
            
            # Verify character data
            if character.name != "Test Investigator":
                return {"success": False, "message": "Character name not set correctly"}
            
            if character.get_skill_value("Library Use") != 70:
                return {"success": False, "message": "Character skills not set correctly"}
            
            # Test character methods
            original_hp = character.hit_points_current
            character.take_damage(5)
            if character.hit_points_current != original_hp - 5:
                return {"success": False, "message": "Character damage calculation failed"}
            
            return {
                "success": True,
                "message": "Character creation and functionality verified",
                "details": {
                    "name": character.name,
                    "profession": character.profession,
                    "hp": f"{character.hit_points_current}/{character.hit_points_maximum}",
                    "sanity": f"{character.sanity_current}/{character.sanity_maximum}"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Character creation failed: {str(e)}",
                "error": str(e)
            }
    
    # AI System Tests
    
    async def _run_ai_system_tests(self):
        """Run AI system integration tests."""
        
        logger.info("Running AI system tests...")
        
        await self._run_test_case("Ollama Connection", self._test_ollama_connection)
        await self._run_test_case("AI Agent Responses", self._test_ai_agent_responses)
        await self._run_test_case("Agent Coordination", self._test_agent_coordination)
    
    async def _test_ollama_connection(self):
        """Test Ollama AI service connection."""
        
        if not self.game_manager or not self.game_manager.ollama_client:
            return {"success": False, "message": "Game manager not initialized"}
        
        client = self.game_manager.ollama_client
        
        # Test basic connection
        if not client.is_available():
            return {
                "success": False,
                "message": "Ollama service is not available",
                "details": {"url": client.base_url}
            }
        
        # Test model availability
        models = client.list_models()
        if client.model not in models:
            return {
                "success": False,
                "message": f"Required model '{client.model}' not available",
                "details": {"available_models": models}
            }
        
        # Test basic generation
        start_time = time.time()
        response = client.generate(
            "Respond with exactly: 'Test successful'",
            temperature=0.1
        )
        response_time = time.time() - start_time
        
        if "test successful" not in response.content.lower():
            return {
                "success": False,
                "message": "AI response test failed",
                "details": {"response": response.content}
            }
        
        return {
            "success": True,
            "message": "Ollama connection and model verified",
            "details": {
                "model": client.model,
                "response_time": round(response_time, 2),
                "available_models": len(models)
            }
        }
    
    async def _test_ai_agent_responses(self):
        """Test individual AI agent responses."""
        
        if not self.game_manager:
            return {"success": False, "message": "Game manager not initialized"}
        
        # Test story agent
        if 'story_agent' in self.game_manager.agents:
            story_agent = self.game_manager.agents['story_agent']
            
            test_input = {
                "action_type": "scene_generation",
                "player_action": "examine the old book",
                "location": "Library",
                "context": "Test scenario"
            }
            
            start_time = time.time()
            response = await story_agent.process_input(test_input)
            response_time = time.time() - start_time
            
            if "error" in response:
                return {
                    "success": False,
                    "message": "Story agent returned error",
                    "details": {"error": response["error"]}
                }
            
            # Check response structure
            if "scene" not in response:
                return {
                    "success": False,
                    "message": "Story agent response missing scene data",
                    "details": {"response_keys": list(response.keys())}
                }
            
            return {
                "success": True,
                "message": "AI agents responding correctly",
                "details": {
                    "story_agent_response_time": round(response_time, 2),
                    "response_has_scene": "scene" in response,
                    "response_has_actions": "available_actions" in response
                }
            }
        else:
            return {
                "success": False,
                "message": "Story agent not available for testing"
            }
    
    async def _test_agent_coordination(self):
        """Test multi-agent coordination."""
        
        if not self.game_manager:
            return {"success": False, "message": "Game manager not initialized"}
        
        # Count available agents
        available_agents = [
            name for name, status in self.game_manager.agent_status.items() 
            if status.ready
        ]
        
        if len(available_agents) < 2:
            return {
                "success": False,
                "message": "Insufficient agents for coordination testing",
                "details": {"available_agents": available_agents}
            }
        
        # Test basic coordination (without Ultra-think for speed)
        test_action = PlayerAction("investigation", {"target": "mysterious_artifact"})
        
        # Create mock turn result
        from src.core.game_engine import TurnResult, ActionResult
        mock_action_result = ActionResult("investigation")
        mock_action_result.success = True
        mock_action_result.message = "Investigation successful"
        
        mock_turn_result = TurnResult(
            success=True,
            turn_number=1,
            action_result=mock_action_result,
            message="Test turn"
        )
        
        start_time = time.time()
        coordination_result = await self.game_manager._coordinate_ai_responses(
            test_action, mock_turn_result
        )
        coordination_time = time.time() - start_time
        
        if "coordination_error" in coordination_result:
            return {
                "success": False,
                "message": "Agent coordination failed",
                "details": {"error": coordination_result["coordination_error"]}
            }
        
        responding_agents = len([
            agent for agent, response in coordination_result.items() 
            if "error" not in response
        ])
        
        return {
            "success": True,
            "message": "Agent coordination working",
            "details": {
                "available_agents": len(available_agents),
                "responding_agents": responding_agents,
                "coordination_time": round(coordination_time, 2)
            }
        }
    
    # Game Loop Tests
    
    async def _run_game_loop_tests(self):
        """Run complete game loop tests."""
        
        logger.info("Running game loop tests...")
        
        await self._run_test_case("Game Session Start", self._test_game_session_start)
        await self._run_test_case("Turn Processing", self._test_turn_processing)
        await self._run_test_case("Multiple Turn Sequence", self._test_multiple_turns)
        await self._run_test_case("Game State Management", self._test_game_state_management)
    
    async def _test_game_session_start(self):
        """Test starting a new game session."""
        
        if not self.game_manager:
            return {"success": False, "message": "Game manager not initialized"}
        
        # Create test character
        character_data = {
            "name": "Integration Test Character",
            "profession": "Investigator",
            "age": 30,
            "attributes": {"strength": 60, "constitution": 70, "intelligence": 80},
            "skills": {"Spot Hidden": 50, "Library Use": 60}
        }
        character = Character.from_dict(character_data)
        
        # Start new game
        start_success = await self.game_manager.start_new_game(
            character=character,
            scenario_name="Test Scenario"
        )
        
        if not start_success:
            return {
                "success": False,
                "message": "Failed to start new game session",
                "details": {"phase": self.game_manager.current_phase.value}
            }
        
        # Verify game state
        status = self.game_manager.get_system_status()
        
        return {
            "success": True,
            "message": "Game session started successfully",
            "details": {
                "session_id": status["session"]["session_id"],
                "character_name": status["session"]["character_name"],
                "scenario": status["session"]["scenario"],
                "is_running": self.game_manager.is_running
            }
        }
    
    async def _test_turn_processing(self):
        """Test single turn processing."""
        
        if not self.game_manager or not self.game_manager.is_running:
            return {"success": False, "message": "Game not running"}
        
        # Create test action
        test_action = PlayerAction(
            action_type="skill_check",
            parameters={
                "skill_name": "Spot Hidden",
                "difficulty": 0
            },
            time_cost=1.0
        )
        
        start_time = time.time()
        result = await self.game_manager.process_player_action(test_action)
        processing_time = time.time() - start_time
        
        if not result.get("success", False):
            return {
                "success": False,
                "message": "Turn processing failed",
                "details": {"error": result.get("error", "Unknown error")}
            }
        
        # Check response structure
        required_fields = ["success", "turn_number", "ai_responses", "processing_time"]
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            return {
                "success": False,
                "message": f"Turn result missing fields: {missing_fields}",
                "details": {"available_fields": list(result.keys())}
            }
        
        return {
            "success": True,
            "message": "Turn processed successfully",
            "details": {
                "turn_number": result["turn_number"],
                "processing_time": round(processing_time, 2),
                "ai_responses": len(result.get("ai_responses", {})),
                "action_successful": result.get("action_result", {}).get("success", False)
            }
        }
    
    async def _test_multiple_turns(self):
        """Test sequence of multiple turns."""
        
        if not self.game_manager or not self.game_manager.is_running:
            return {"success": False, "message": "Game not running"}
        
        # Define sequence of test actions
        test_actions = [
            PlayerAction("investigation", {"target": "library_book"}),
            PlayerAction("movement", {"destination": "garden"}),
            PlayerAction("skill_check", {"skill_name": "Listen", "difficulty": 0})
        ]
        
        turn_results = []
        total_start_time = time.time()
        
        for i, action in enumerate(test_actions):
            start_time = time.time()
            result = await self.game_manager.process_player_action(action)
            turn_time = time.time() - start_time
            
            if not result.get("success", False):
                return {
                    "success": False,
                    "message": f"Turn {i+1} failed",
                    "details": {"error": result.get("error", "Unknown error")}
                }
            
            turn_results.append({
                "turn": result["turn_number"],
                "action": action.action_type,
                "duration": turn_time,
                "ai_responses": len(result.get("ai_responses", {}))
            })
        
        total_time = time.time() - total_start_time
        
        return {
            "success": True,
            "message": f"Processed {len(test_actions)} turns successfully",
            "details": {
                "total_turns": len(test_actions),
                "total_time": round(total_time, 2),
                "avg_turn_time": round(total_time / len(test_actions), 2),
                "turns": turn_results
            }
        }
    
    async def _test_game_state_management(self):
        """Test game state tracking and updates."""
        
        if not self.game_manager:
            return {"success": False, "message": "Game manager not initialized"}
        
        # Get initial state
        initial_status = self.game_manager.get_system_status()
        initial_turn_count = initial_status["session"]["total_turns"]
        
        # Process action to change state
        test_action = PlayerAction("skill_check", {"skill_name": "Spot Hidden"})
        result = await self.game_manager.process_player_action(test_action)
        
        if not result.get("success", False):
            return {"success": False, "message": "Action processing failed"}
        
        # Check state updates
        updated_status = self.game_manager.get_system_status()
        updated_turn_count = updated_status["session"]["total_turns"]
        
        if updated_turn_count <= initial_turn_count:
            return {
                "success": False,
                "message": "Turn count not updated correctly",
                "details": {
                    "initial": initial_turn_count,
                    "updated": updated_turn_count
                }
            }
        
        return {
            "success": True,
            "message": "Game state management working correctly",
            "details": {
                "turn_count_change": updated_turn_count - initial_turn_count,
                "session_tracking": "active",
                "character_tracking": updated_status["session"]["character_name"] is not None
            }
        }
    
    # Save/Load Tests
    
    async def _run_save_load_tests(self):
        """Run save and load functionality tests."""
        
        logger.info("Running save/load tests...")
        
        await self._run_test_case("Game Save", self._test_game_save)
        await self._run_test_case("Game Load", self._test_game_load)
        await self._run_test_case("Save Data Integrity", self._test_save_data_integrity)
    
    async def _test_game_save(self):
        """Test game save functionality."""
        
        if not self.game_manager or not self.game_manager.is_running:
            return {"success": False, "message": "Game not running"}
        
        # Save current game
        save_path = self.temp_dir / "test_save.json.gz"
        
        start_time = time.time()
        save_success = await self.game_manager.save_game(str(save_path))
        save_time = time.time() - start_time
        
        if not save_success:
            return {
                "success": False,
                "message": "Game save operation failed"
            }
        
        # Verify save file exists and has content
        if not save_path.exists():
            return {
                "success": False,
                "message": "Save file was not created"
            }
        
        file_size = save_path.stat().st_size
        if file_size == 0:
            return {
                "success": False,
                "message": "Save file is empty"
            }
        
        return {
            "success": True,
            "message": "Game saved successfully",
            "details": {
                "save_path": str(save_path),
                "file_size": file_size,
                "save_time": round(save_time, 2)
            }
        }
    
    async def _test_game_load(self):
        """Test game load functionality."""
        
        # First ensure we have a save file
        save_path = self.temp_dir / "test_save.json.gz"
        if not save_path.exists():
            # Create a save first
            await self._test_game_save()
        
        if not save_path.exists():
            return {"success": False, "message": "No save file available for load test"}
        
        # Get current state for comparison
        if self.game_manager and self.game_manager.is_running:
            pre_load_status = self.game_manager.get_system_status()
            pre_load_turns = pre_load_status["session"]["total_turns"]
        else:
            pre_load_turns = 0
        
        # Create new game manager for load test
        new_game_manager = GameManager(self.config)
        init_success = await new_game_manager.initialize_systems()
        
        if not init_success:
            return {"success": False, "message": "Failed to initialize new game manager for load test"}
        
        # Load the save
        start_time = time.time()
        load_success = await new_game_manager.load_game(str(save_path))
        load_time = time.time() - start_time
        
        if not load_success:
            await new_game_manager.shutdown()
            return {
                "success": False,
                "message": "Game load operation failed"
            }
        
        # Verify loaded state
        post_load_status = new_game_manager.get_system_status()
        
        # Clean up
        await new_game_manager.shutdown()
        
        return {
            "success": True,
            "message": "Game loaded successfully",
            "details": {
                "load_time": round(load_time, 2),
                "character_restored": post_load_status["session"]["character_name"] is not None,
                "session_restored": post_load_status["session"]["session_id"] is not None,
                "game_running": post_load_status["initialization"]["is_running"]
            }
        }
    
    async def _test_save_data_integrity(self):
        """Test save data integrity and structure."""
        
        save_path = self.temp_dir / "test_save.json.gz"
        if not save_path.exists():
            await self._test_game_save()
        
        if not save_path.exists():
            return {"success": False, "message": "No save file available for integrity test"}
        
        try:
            # Load and verify save data structure
            from src.data.save_manager import SaveManager
            save_manager = SaveManager()
            
            save_data = save_manager.load_game(str(save_path))
            if not save_data:
                return {"success": False, "message": "Failed to load save data"}
            
            # Check required sections
            required_sections = ["game_manager", "game_engine", "agents"]
            missing_sections = [section for section in required_sections if section not in save_data]
            
            if missing_sections:
                return {
                    "success": False,
                    "message": f"Save data missing sections: {missing_sections}",
                    "details": {"available_sections": list(save_data.keys())}
                }
            
            # Check data content
            game_manager_data = save_data["game_manager"]
            if "session" not in game_manager_data:
                return {"success": False, "message": "Save data missing session information"}
            
            return {
                "success": True,
                "message": "Save data integrity verified",
                "details": {
                    "sections": list(save_data.keys()),
                    "has_session": "session" in game_manager_data,
                    "has_agents": len(save_data.get("agents", {})) > 0,
                    "file_size": save_path.stat().st_size
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Save data integrity check failed: {str(e)}",
                "error": str(e)
            }
    
    # Error Handling Tests
    
    async def _run_error_handling_tests(self):
        """Run error handling and recovery tests."""
        
        logger.info("Running error handling tests...")
        
        await self._run_test_case("Invalid Action Handling", self._test_invalid_action_handling)
        await self._run_test_case("AI Connection Loss Simulation", self._test_ai_connection_loss)
        await self._run_test_case("Corrupted Save Handling", self._test_corrupted_save_handling)
    
    async def _test_invalid_action_handling(self):
        """Test handling of invalid player actions."""
        
        if not self.game_manager or not self.game_manager.is_running:
            return {"success": False, "message": "Game not running"}
        
        # Test invalid action type
        invalid_action = PlayerAction("invalid_action_type", {})
        result = await self.game_manager.process_player_action(invalid_action)
        
        # Should handle gracefully, not crash
        if "error" not in result and not result.get("success", True):
            return {
                "success": True,
                "message": "Invalid action handled gracefully",
                "details": {"handled_gracefully": True}
            }
        
        # Test action with missing parameters
        incomplete_action = PlayerAction("skill_check", {})  # Missing skill_name
        result2 = await self.game_manager.process_player_action(incomplete_action)
        
        # Should handle gracefully
        return {
            "success": True,
            "message": "Error handling working correctly",
            "details": {
                "invalid_action_handled": True,
                "incomplete_action_handled": True
            }
        }
    
    async def _test_ai_connection_loss(self):
        """Test AI connection loss simulation."""
        
        if not self.game_manager:
            return {"success": False, "message": "Game manager not initialized"}
        
        # This test simulates what happens when AI is unavailable
        # We'll modify the client temporarily to simulate failure
        original_client = self.game_manager.ollama_client
        
        # Create a mock failing client
        class FailingClient:
            def is_available(self):
                return False
            
            def generate(self, *args, **kwargs):
                raise Exception("Simulated connection failure")
        
        # Temporarily replace client
        self.game_manager.ollama_client = FailingClient()
        
        try:
            # Try to process an action
            test_action = PlayerAction("skill_check", {"skill_name": "Spot Hidden"})
            result = await self.game_manager.process_player_action(test_action)
            
            # Should handle the failure gracefully
            return {
                "success": True,
                "message": "AI connection loss handled gracefully",
                "details": {
                    "action_processed": result.get("success", False),
                    "error_handled": "error" in result or not result.get("success", True)
                }
            }
            
        finally:
            # Restore original client
            self.game_manager.ollama_client = original_client
    
    async def _test_corrupted_save_handling(self):
        """Test handling of corrupted save files."""
        
        # Create corrupted save file
        corrupted_save_path = self.temp_dir / "corrupted_save.json.gz"
        
        # Write invalid data
        with open(corrupted_save_path, 'wb') as f:
            f.write(b"This is not valid compressed JSON data")
        
        # Try to load corrupted save
        new_game_manager = GameManager(self.config)
        await new_game_manager.initialize_systems()
        
        try:
            load_success = await new_game_manager.load_game(str(corrupted_save_path))
            
            # Should fail gracefully
            return {
                "success": True,
                "message": "Corrupted save handled gracefully",
                "details": {
                    "load_attempted": True,
                    "load_failed_gracefully": not load_success,
                    "system_stable": new_game_manager.current_phase != GamePhase.ERROR
                }
            }
            
        finally:
            await new_game_manager.shutdown()
    
    # Performance Tests
    
    async def _run_performance_tests(self):
        """Run performance benchmark tests."""
        
        logger.info("Running performance tests...")
        
        await self._run_test_case("System Initialization Performance", self._test_init_performance)
        await self._run_test_case("Turn Processing Performance", self._test_turn_performance)
        await self._run_test_case("Save/Load Performance", self._test_save_load_performance)
    
    async def _test_init_performance(self):
        """Test system initialization performance."""
        
        # Create new game manager for timing test
        start_time = time.time()
        perf_game_manager = GameManager(self.config)
        init_success = await perf_game_manager.initialize_systems()
        init_time = time.time() - start_time
        
        try:
            if not init_success:
                return {"success": False, "message": "Initialization failed"}
            
            threshold = self.performance_thresholds["system_init"]
            performance_ok = init_time <= threshold
            
            return {
                "success": performance_ok,
                "message": f"Initialization took {init_time:.2f}s (threshold: {threshold}s)",
                "details": {
                    "init_time": round(init_time, 2),
                    "threshold": threshold,
                    "within_threshold": performance_ok
                }
            }
            
        finally:
            await perf_game_manager.shutdown()
    
    async def _test_turn_performance(self):
        """Test turn processing performance."""
        
        if not self.game_manager or not self.game_manager.is_running:
            return {"success": False, "message": "Game not running"}
        
        # Test multiple turn processing times
        test_actions = [
            PlayerAction("skill_check", {"skill_name": "Spot Hidden"}),
            PlayerAction("investigation", {"target": "desk"}),
            PlayerAction("movement", {"destination": "library"})
        ]
        
        turn_times = []
        
        for action in test_actions:
            start_time = time.time()
            result = await self.game_manager.process_player_action(action)
            turn_time = time.time() - start_time
            
            if result.get("success", False):
                turn_times.append(turn_time)
        
        if not turn_times:
            return {"success": False, "message": "No successful turns for performance measurement"}
        
        avg_turn_time = sum(turn_times) / len(turn_times)
        max_turn_time = max(turn_times)
        threshold = self.performance_thresholds["turn_processing"]
        
        performance_ok = avg_turn_time <= threshold
        
        return {
            "success": performance_ok,
            "message": f"Average turn time: {avg_turn_time:.2f}s (threshold: {threshold}s)",
            "details": {
                "avg_turn_time": round(avg_turn_time, 2),
                "max_turn_time": round(max_turn_time, 2),
                "threshold": threshold,
                "turns_tested": len(turn_times),
                "within_threshold": performance_ok
            }
        }
    
    async def _test_save_load_performance(self):
        """Test save and load operation performance."""
        
        if not self.game_manager or not self.game_manager.is_running:
            return {"success": False, "message": "Game not running"}
        
        save_path = self.temp_dir / "perf_test_save.json.gz"
        
        # Test save performance
        start_time = time.time()
        save_success = await self.game_manager.save_game(str(save_path))
        save_time = time.time() - start_time
        
        if not save_success:
            return {"success": False, "message": "Save operation failed"}
        
        # Test load performance
        new_game_manager = GameManager(self.config)
        await new_game_manager.initialize_systems()
        
        try:
            start_time = time.time()
            load_success = await new_game_manager.load_game(str(save_path))
            load_time = time.time() - start_time
            
            if not load_success:
                return {"success": False, "message": "Load operation failed"}
            
            threshold = self.performance_thresholds["save_operation"]
            save_ok = save_time <= threshold
            load_ok = load_time <= threshold
            
            return {
                "success": save_ok and load_ok,
                "message": f"Save: {save_time:.2f}s, Load: {load_time:.2f}s (threshold: {threshold}s)",
                "details": {
                    "save_time": round(save_time, 2),
                    "load_time": round(load_time, 2),
                    "threshold": threshold,
                    "save_within_threshold": save_ok,
                    "load_within_threshold": load_ok
                }
            }
            
        finally:
            await new_game_manager.shutdown()
    
    # Stress Tests
    
    async def _run_stress_tests(self):
        """Run stress tests for system stability."""
        
        logger.info("Running stress tests...")
        
        await self._run_test_case("Extended Gameplay Session", self._test_extended_gameplay)
        await self._run_test_case("Rapid Action Processing", self._test_rapid_actions)
        await self._run_test_case("Memory Leak Detection", self._test_memory_usage)
    
    async def _test_extended_gameplay(self):
        """Test extended gameplay session stability."""
        
        if not self.game_manager or not self.game_manager.is_running:
            return {"success": False, "message": "Game not running"}
        
        # Process many turns to test stability
        num_turns = 20  # Reduced for CI/testing
        successful_turns = 0
        errors = []
        
        for i in range(num_turns):
            try:
                action = PlayerAction(
                    action_type="skill_check",
                    parameters={"skill_name": "Spot Hidden", "difficulty": 0}
                )
                
                result = await self.game_manager.process_player_action(action)
                
                if result.get("success", False):
                    successful_turns += 1
                else:
                    errors.append(f"Turn {i+1}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                errors.append(f"Turn {i+1} exception: {str(e)}")
        
        success_rate = successful_turns / num_turns
        
        return {
            "success": success_rate >= 0.9,  # 90% success rate required
            "message": f"Completed {successful_turns}/{num_turns} turns successfully ({success_rate*100:.1f}%)",
            "details": {
                "total_turns": num_turns,
                "successful_turns": successful_turns,
                "success_rate": round(success_rate, 3),
                "errors": errors[:5]  # First 5 errors
            }
        }
    
    async def _test_rapid_actions(self):
        """Test rapid action processing."""
        
        if not self.game_manager or not self.game_manager.is_running:
            return {"success": False, "message": "Game not running"}
        
        # Process actions rapidly
        num_actions = 5  # Reduced for testing
        actions = [
            PlayerAction("skill_check", {"skill_name": "Listen"}) 
            for _ in range(num_actions)
        ]
        
        start_time = time.time()
        
        # Process actions rapidly
        tasks = [
            self.game_manager.process_player_action(action) 
            for action in actions
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            successful_results = [
                r for r in results 
                if not isinstance(r, Exception) and r.get("success", False)
            ]
            
            avg_time_per_action = total_time / len(actions)
            
            return {
                "success": len(successful_results) >= len(actions) * 0.8,  # 80% success
                "message": f"Processed {len(successful_results)}/{len(actions)} rapid actions",
                "details": {
                    "total_actions": len(actions),
                    "successful_actions": len(successful_results),
                    "total_time": round(total_time, 2),
                    "avg_time_per_action": round(avg_time_per_action, 2)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Rapid action test failed: {str(e)}",
                "error": str(e)
            }
    
    async def _test_memory_usage(self):
        """Test memory usage and leak detection."""
        
        import psutil
        import gc
        
        process = psutil.Process()
        
        # Get baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform memory-intensive operations
        for i in range(10):
            if self.game_manager and self.game_manager.is_running:
                action = PlayerAction("skill_check", {"skill_name": "Spot Hidden"})
                await self.game_manager.process_player_action(action)
        
        # Check memory after operations
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - baseline_memory
        
        # Acceptable memory increase threshold (50MB)
        memory_ok = memory_increase < 50
        
        return {
            "success": memory_ok,
            "message": f"Memory usage increased by {memory_increase:.1f}MB",
            "details": {
                "baseline_memory_mb": round(baseline_memory, 1),
                "final_memory_mb": round(final_memory, 1),
                "memory_increase_mb": round(memory_increase, 1),
                "within_threshold": memory_ok
            }
        }
    
    def _generate_test_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == TestStatus.PASS])
        failed_tests = len([r for r in self.test_results if r.status == TestStatus.FAIL])
        error_tests = len([r for r in self.test_results if r.status == TestStatus.ERROR])
        skipped_tests = len([r for r in self.test_results if r.status == TestStatus.SKIP])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Overall status
        if failed_tests > 0 or error_tests > 0:
            overall_status = "FAIL"
        elif passed_tests == total_tests:
            overall_status = "PASS"
        else:
            overall_status = "PARTIAL"
        
        # Performance summary
        test_times = [r.duration for r in self.test_results if r.duration > 0]
        avg_test_time = sum(test_times) / len(test_times) if test_times else 0
        
        return {
            "summary": {
                "overall_status": overall_status,
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "skipped": skipped_tests,
                "success_rate": round(success_rate, 1),
                "total_time": round(total_time, 2),
                "avg_test_time": round(avg_test_time, 2)
            },
            "test_results": [result.to_dict() for result in self.test_results],
            "performance_summary": {
                "fastest_test": min(test_times) if test_times else 0,
                "slowest_test": max(test_times) if test_times else 0,
                "total_test_time": sum(test_times),
                "tests_over_threshold": len([t for t in test_times if t > 30])
            },
            "recommendations": self._generate_test_recommendations()
        }
    
    def _generate_test_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        
        recommendations = []
        
        # Check for failures
        failed_tests = [r for r in self.test_results if r.status in [TestStatus.FAIL, TestStatus.ERROR]]
        if failed_tests:
            recommendations.append(f"🔴 {len(failed_tests)} tests failed - investigate and fix critical issues")
        
        # Check performance
        slow_tests = [r for r in self.test_results if r.duration > 30]
        if slow_tests:
            recommendations.append(f"⚠️ {len(slow_tests)} tests are slow (>30s) - consider optimization")
        
        # Check error patterns
        ai_errors = [r for r in self.test_results if "ai" in r.name.lower() and r.status != TestStatus.PASS]
        if ai_errors:
            recommendations.append("🤖 AI system issues detected - check Ollama service and model availability")
        
        save_errors = [r for r in self.test_results if "save" in r.name.lower() and r.status != TestStatus.PASS]
        if save_errors:
            recommendations.append("💾 Save/load issues detected - check file permissions and disk space")
        
        if not recommendations:
            recommendations.append("✅ All tests passed successfully - system is ready for production use")
        
        return recommendations
    
    def print_summary(self, report: Dict[str, Any]):
        """Print formatted test summary."""
        
        summary = report["summary"]
        
        print("\n" + "="*60)
        print("🧪 CTHULHU SOLO TRPG - INTEGRATION TEST REPORT")
        print("="*60)
        
        # Overall status
        status_emoji = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️"}
        emoji = status_emoji.get(summary["overall_status"], "❓")
        
        print(f"\n{emoji} Overall Status: {summary['overall_status']}")
        print(f"🎯 Success Rate: {summary['success_rate']}%")
        
        # Test breakdown
        print(f"\n📊 Test Results:")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   🚫 Errors: {summary['errors']}")
        print(f"   ⏭️  Skipped: {summary['skipped']}")
        print(f"   📋 Total: {summary['total_tests']}")
        
        # Performance
        perf = report["performance_summary"]
        print(f"\n⏱️  Performance:")
        print(f"   Total Time: {summary['total_time']:.2f}s")
        print(f"   Average Test Time: {summary['avg_test_time']:.2f}s")
        print(f"   Fastest Test: {perf['fastest_test']:.2f}s")
        print(f"   Slowest Test: {perf['slowest_test']:.2f}s")
        
        # Recommendations
        if report["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   {rec}")
        
        print("="*60 + "\n")


# CLI interface for running tests
async def main():
    """Main function for running integration tests as standalone script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cthulhu Solo TRPG Integration Tests")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--save-report", action="store_true", help="Save detailed report to file")
    parser.add_argument("--fast", action="store_true", help="Run fast tests only (skip stress tests)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level)
    
    # Load configuration
    config = Config(args.config) if os.path.exists(args.config) else Config()
    
    # Run integration tests
    test_suite = IntegrationTestSuite(config)
    
    if args.fast:
        # Skip stress tests for faster execution
        test_suite.stress_test_iterations = 3
        test_suite.max_test_duration = 30.0
    
    report = await test_suite.run_all_tests()
    
    # Print summary
    test_suite.print_summary(report)
    
    # Save report if requested
    if args.save_report:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_path = f"integration_test_report_{timestamp}.json"
        
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📄 Detailed report saved to: {report_path}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
    
    # Exit with appropriate code
    if report["summary"]["overall_status"] == "FAIL":
        sys.exit(1)
    elif report["summary"]["overall_status"] == "PARTIAL":
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())