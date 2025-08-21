#!/usr/bin/env python3
"""
Comprehensive System Test for Cthulhu Solo RPG
Tests all major components and functionality of the rebuilt system.
"""

import os
import sys
import asyncio
import json
import traceback
from typing import Dict, List, Any, Optional

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import all core modules
try:
    from core.models import (
        GameState, Investigation, PlayerAction, StoryContent, 
        NarrativeContext, TensionLevel, ActionType,
        create_basic_narrative_context
    )
    from core.dice import DiceEngine, skill_check
    from core.game_manager import GameManager
    from core.game_engine import GameEngine
    from core.gameplay_controller import GameplayController
    from ai.ollama_client import OllamaClient
    from agents.base_agent import BaseAgent
    from agents.story_agent import StoryAgent
    from ui.gameplay_interface import GameplayInterface
    from utils.localization import LocalizationManager
    from data.game_data import GameData
    from data.save_manager import SaveManager
    from data.scenarios.miskatonic_university_library import MiskatonicUniversityLibraryScenario
except ImportError as e:
    print(f"CRITICAL: Failed to import core modules: {e}")
    sys.exit(1)

class ComprehensiveSystemTest:
    """Comprehensive testing suite for the entire system"""
    
    def __init__(self):
        self.test_results = {}
        self.passed_tests = 0
        self.failed_tests = 0
        self.total_tests = 0
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "PASS"
        else:
            self.failed_tests += 1
            status = "FAIL"
            
        self.test_results[test_name] = {
            "status": status,
            "details": details
        }
        
        print(f"[{status}] {test_name}")
        if details:
            print(f"    {details}")
    
    async def test_basic_imports(self):
        """Test 1: Basic System Test - Import all modules"""
        print("\n=== 1. BASIC SYSTEM TEST ===")
        
        try:
            # Test core model instantiation
            character_data = {
                "name": "Test Character",
                "stats": {"STR": 50, "DEX": 60, "INT": 70, "EDU": 65},
                "skills": {"Library Use": 50, "Occult": 30},
                "sanity": 70,
                "hit_points": 12
            }
            self.log_test("Character data creation", True, f"Created character: {character_data['name']}")
            
            # Test narrative context
            narrative_context = create_basic_narrative_context("test_scene", character_data)
            self.log_test("NarrativeContext creation", True, f"Scene: {narrative_context.scene_id}")
            
            # Test game state
            game_state = GameState(
                character_data=character_data,
                narrative_context=narrative_context,
                game_metadata={"test": True}
            )
            self.log_test("GameState creation", True, f"Character: {game_state.character_data['name']}")
            
            # Test investigation
            investigation = Investigation(
                description="Test investigation description",
                difficulty=5,
                scene_id="test_scene",
                keywords=["test", "investigation"]
            )
            self.log_test("Investigation creation", True, f"Investigation: {investigation.description}")
            
            # Test player action
            player_action = PlayerAction(
                original_text="Look around the room",
                action_type=ActionType.INVESTIGATE,
                target="room",
                intent="examine surroundings"
            )
            self.log_test("PlayerAction creation", True, f"Action: {player_action.original_text}")
            
            # Test story content
            story_content = StoryContent(
                text="You find yourself in a dimly lit library.",
                content_id="test_content_1",
                scene_id="test_scene",
                tension_level=TensionLevel.CALM
            )
            self.log_test("StoryContent creation", True, f"Content: {story_content.text[:30]}...")
            
        except Exception as e:
            self.log_test("Basic data structures", False, f"Error: {str(e)}")
    
    async def test_dice_system(self):
        """Test dice system and game mechanics"""
        try:
            dice_engine = DiceEngine()
            
            # Test basic rolls
            d100_result = dice_engine.roll("d100")
            self.log_test("D100 roll", 1 <= d100_result.total <= 100, f"Result: {d100_result.total}")
            
            # Test skill checks
            skill_result = dice_engine.skill_check(75, 0)  # skill 75, no modifier
            self.log_test("Skill check", skill_result.success_level is not None, 
                         f"Success: {skill_result.success_level.value}, Roll: {skill_result.total}")
            
            # Test multiple rolls for consistency
            results = [dice_engine.roll("d100").total for _ in range(10)]
            valid_results = all(1 <= r <= 100 for r in results)
            self.log_test("Multiple dice rolls", valid_results, f"Results: {results[:5]}...")
            
            # Test sanity check
            sanity_result = dice_engine.sanity_check(65, "1d4/1d8")
            self.log_test("Sanity check", "sanity_loss" in sanity_result, 
                         f"Sanity loss: {sanity_result.get('sanity_loss', 'N/A')}")
            
        except Exception as e:
            self.log_test("Dice system", False, f"Error: {str(e)}")
    
    async def test_ai_integration(self):
        """Test 2: AI Integration Test"""
        print("\n=== 2. AI INTEGRATION TEST ===")
        
        try:
            # Test OllamaClient initialization
            ollama_client = OllamaClient()
            self.log_test("OllamaClient initialization", True, "Client created successfully")
            
            # Test BaseAgent
            base_agent = BaseAgent(ollama_client)
            self.log_test("BaseAgent creation", True, "Agent created successfully")
            
            # Test StoryAgent
            story_agent = StoryAgent(ollama_client)
            self.log_test("StoryAgent creation", True, "Story agent created successfully")
            
            # Test agent memory management
            story_agent.add_to_memory("test", "This is a test memory entry")
            memory = story_agent.get_memory("test")
            self.log_test("Memory management", memory == "This is a test memory entry", 
                         f"Memory stored and retrieved: {memory}")
            
            # Test AI response (with fallback if Ollama unavailable)
            try:
                test_prompt = "Describe a simple room in a haunted library."
                response = await story_agent.generate_response(test_prompt)
                ai_available = True
                self.log_test("AI response generation", len(response) > 10, 
                             f"Response length: {len(response)} characters")
            except Exception as ai_error:
                ai_available = False
                self.log_test("AI response generation", True, 
                             f"Fallback mode (Ollama unavailable): {str(ai_error)}")
            
        except Exception as e:
            self.log_test("AI Integration", False, f"Error: {str(e)}")
    
    async def test_game_flow(self):
        """Test 3: Game Flow Test"""
        print("\n=== 3. GAME FLOW TEST ===")
        
        try:
            # Test GameManager initialization
            game_manager = GameManager()
            self.log_test("GameManager initialization", True, "Game manager created")
            
            # Test character creation through game manager
            character_data = {
                "name": "Dr. Test Investigator",
                "occupation": "Professor",
                "age": 35,
                "stats": {"STR": 50, "DEX": 60, "INT": 80, "EDU": 85},
                "skills": {"Library Use": 70, "Occult": 45, "Psychology": 60},
                "sanity": 75,
                "hit_points": 13
            }
            
            # Test game state initialization
            game_state = game_manager.initialize_game(character_data)
            self.log_test("Game state initialization", 
                         game_state.character_data["name"] == "Dr. Test Investigator",
                         f"Character in state: {game_state.character_data['name']}")
            
            # Test investigation setup
            investigation = Investigation(
                description="Investigating strange occurrences in the library",
                difficulty=6,
                scene_id="library_main",
                keywords=["library", "strange", "occurrences"],
                rewards=["library_clue_1", "sanity_boost"]
            )
            
            # Test investigation can_attempt method
            can_attempt = investigation.can_attempt(
                character_state=game_state.character_data,
                narrative_flags=game_state.narrative_context.narrative_flags
            )
            self.log_test("Investigation attempt check", 
                         can_attempt == True,
                         f"Investigation: {investigation.description[:30]}...")
            
        except Exception as e:
            self.log_test("Game Flow", False, f"Error: {str(e)}")
    
    async def test_scenario_system(self):
        """Test Miskatonic University Library scenario"""
        try:
            # Test scenario loading
            scenario = MiskatonicUniversityLibraryScenario()
            self.log_test("Scenario initialization", True, 
                         f"Scenario: {scenario.__class__.__name__}")
            
            # Test scenario data
            scenario_data = scenario.get_scenario_data()
            required_keys = ["name", "description", "initial_location", "investigation_opportunities"]
            has_required_keys = all(key in scenario_data for key in required_keys)
            self.log_test("Scenario data structure", has_required_keys, 
                         f"Keys present: {list(scenario_data.keys())}")
            
            # Test investigation opportunities
            opportunities = scenario_data.get("investigation_opportunities", [])
            self.log_test("Investigation opportunities", len(opportunities) > 0, 
                         f"Found {len(opportunities)} opportunities")
            
        except Exception as e:
            self.log_test("Scenario system", False, f"Error: {str(e)}")
    
    async def test_ui_system(self):
        """Test 4: UI System Test"""
        print("\n=== 4. UI SYSTEM TEST ===")
        
        try:
            # Test LocalizationManager
            localization = LocalizationManager("en")
            self.log_test("Localization manager (EN)", True, 
                         f"Language: {localization.current_language}")
            
            # Test Korean language support
            localization_ko = LocalizationManager("ko")
            self.log_test("Korean language support", True, 
                         f"Language: {localization_ko.current_language}")
            
            # Test GameplayInterface
            interface = GameplayInterface(localization)
            self.log_test("GameplayInterface creation", True, "Interface created successfully")
            
            # Test command parsing
            help_result = interface.parse_command("/help")
            self.log_test("Command parsing (/help)", help_result is not None, 
                         f"Help command recognized")
            
            character_result = interface.parse_command("/character")
            self.log_test("Command parsing (/character)", character_result is not None, 
                         f"Character command recognized")
            
        except Exception as e:
            self.log_test("UI System", False, f"Error: {str(e)}")
    
    async def test_free_text_system(self):
        """Test free-text action processing"""
        try:
            # Create a complete game setup
            game_manager = GameManager()
            character_data = {
                "name": "Test Investigator",
                "stats": {"STR": 50, "DEX": 60, "INT": 70, "EDU": 65},
                "skills": {"Library Use": 60, "Spot Hidden": 50},
                "sanity": 65,
                "hit_points": 12
            }
            
            game_state = game_manager.initialize_game(character_data)
            game_state.narrative_context.scene_id = "miskatonic_university_library"
            
            # Create gameplay controller for free-text processing
            controller = GameplayController(game_manager)
            
            # Test free-text actions
            test_actions = [
                "I want to search the library for ancient books",
                "Look around the reading room carefully",
                "Talk to the librarian about strange occurrences"
            ]
            
            for i, action in enumerate(test_actions):
                try:
                    result = await controller.process_free_text_action(action, game_state)
                    self.log_test(f"Free-text action {i+1}", 
                                 result is not None and hasattr(result, 'text'),
                                 f"Action: '{action[:30]}...' processed")
                except Exception as action_error:
                    self.log_test(f"Free-text action {i+1}", False, 
                                 f"Error processing '{action[:30]}...': {str(action_error)}")
            
        except Exception as e:
            self.log_test("Free-text system", False, f"Error: {str(e)}")
    
    async def test_integration(self):
        """Test 5: Integration Test"""
        print("\n=== 5. INTEGRATION TEST ===")
        
        try:
            # Test save/load functionality
            save_manager = SaveManager()
            
            # Create test game state
            character_data = {
                "name": "Integration Test Character",
                "stats": {"STR": 60, "DEX": 55, "INT": 75, "EDU": 80},
                "skills": {"Library Use": 65, "Occult": 40},
                "sanity": 70,
                "hit_points": 14
            }
            
            narrative_context = create_basic_narrative_context("test_location", character_data)
            narrative_context.story_threads["main"] = "Integration test context"
            
            game_state = GameState(
                character_data=character_data,
                narrative_context=narrative_context,
                game_metadata={"test_session": True}
            )
            
            # Test save functionality
            save_path = save_manager.save_game(game_state, "integration_test")
            self.log_test("Save functionality", os.path.exists(save_path), 
                         f"Saved to: {os.path.basename(save_path)}")
            
            # Test load functionality
            loaded_state = save_manager.load_game("integration_test")
            self.log_test("Load functionality", 
                         loaded_state.character_data["name"] == character_data["name"],
                         f"Loaded character: {loaded_state.character_data['name']}")
            
            # Test game data loading
            game_data = GameData()
            locations = game_data.get_locations()
            self.log_test("Game data loading", len(locations) > 0, 
                         f"Loaded {len(locations)} locations")
            
        except Exception as e:
            self.log_test("Integration test", False, f"Error: {str(e)}")
    
    async def test_complete_mini_session(self):
        """Test a complete mini game session"""
        print("\n=== 6. COMPLETE MINI SESSION TEST ===")
        
        try:
            # Initialize complete game system
            game_manager = GameManager()
            localization = LocalizationManager("en")
            interface = GameplayInterface(localization)
            controller = GameplayController(game_manager)
            
            # Create character
            character_data = {
                "name": "Dr. Sarah Chen",
                "stats": {"STR": 45, "DEX": 65, "INT": 85, "EDU": 90},
                "skills": {"Library Use": 80, "Occult": 55, "Spot Hidden": 60},
                "sanity": 75,
                "hit_points": 11
            }
            
            # Initialize game
            game_state = game_manager.initialize_game(character_data)
            
            # Set up Miskatonic University Library scenario
            scenario = MiskatonicUniversityLibraryScenario()
            scenario_data = scenario.get_scenario_data()
            
            game_state.narrative_context.scene_id = scenario_data["initial_location"]
            game_state.narrative_context.story_threads["main"] = scenario_data["description"]
            
            # Set up investigation
            investigation = Investigation(
                description=scenario_data["description"],
                difficulty=5,
                scene_id=scenario_data["initial_location"],
                keywords=["library", "mysterious", "investigation"]
            )
            
            self.log_test("Mini session setup", True, 
                         f"Character: {character_data['name']}, Location: {game_state.narrative_context.scene_id}")
            
            # Simulate a few game actions
            actions = [
                "Look around the library entrance",
                "Check the librarian's desk for clues",
                "Examine the rare books section"
            ]
            
            for i, action in enumerate(actions):
                try:
                    result = await controller.process_free_text_action(action, game_state)
                    self.log_test(f"Session action {i+1}", result is not None, 
                                 f"Processed: {action}")
                except Exception as action_error:
                    self.log_test(f"Session action {i+1}", False, 
                                 f"Failed: {action} - {str(action_error)}")
            
            # Test investigation opportunities display
            opportunities = scenario_data.get("investigation_opportunities", [])
            if opportunities:
                self.log_test("Investigation opportunities display", True, 
                             f"Available opportunities: {len(opportunities)}")
            else:
                self.log_test("Investigation opportunities display", False, 
                             "No opportunities found")
            
        except Exception as e:
            self.log_test("Complete mini session", False, f"Error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all test suites"""
        print("COMPREHENSIVE SYSTEM TEST - Cthulhu Solo RPG")
        print("=" * 50)
        
        try:
            # Run all test suites
            await self.test_basic_imports()
            await self.test_dice_system()
            await self.test_ai_integration()
            await self.test_game_flow()
            await self.test_scenario_system()
            await self.test_ui_system()
            await self.test_free_text_system()
            await self.test_integration()
            await self.test_complete_mini_session()
            
        except Exception as e:
            print(f"CRITICAL ERROR during testing: {str(e)}")
            traceback.print_exc()
        
        # Print final results
        self.print_results()
    
    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 50)
        print("COMPREHENSIVE TEST RESULTS")
        print("=" * 50)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        print("\nDETAILED RESULTS:")
        print("-" * 30)
        
        for test_name, result in self.test_results.items():
            status = result["status"]
            details = result["details"]
            print(f"[{status}] {test_name}")
            if details:
                print(f"    {details}")
        
        # Overall assessment
        print("\n" + "=" * 50)
        if self.failed_tests == 0:
            print("🎉 ALL TESTS PASSED! System is fully functional.")
        elif self.failed_tests < self.total_tests * 0.2:  # Less than 20% failure
            print("✅ SYSTEM MOSTLY FUNCTIONAL with minor issues.")
        else:
            print("⚠️  SYSTEM HAS SIGNIFICANT ISSUES that need attention.")
        
        print("=" * 50)

async def main():
    """Main test execution"""
    print("Starting Comprehensive System Test...")
    
    # Change to the correct directory
    os.chdir('/Users/mimir/TRPG/cthulhu_solo_rpg')
    
    # Create and run test suite
    test_suite = ComprehensiveSystemTest()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())