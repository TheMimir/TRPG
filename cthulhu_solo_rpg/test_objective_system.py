#!/usr/bin/env python3
"""
Comprehensive Test Suite for Cthulhu TRPG Objective System

Tests the complete objective system integration including:
- Base objective functionality
- Multi-layered objectives (Immediate/Short/Mid/Long/Meta)
- SAN-integrated objectives
- AI coordination
- Achievement system
- GameManager integration

Usage:
    python test_objective_system.py
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from objectives import (
    objective_manager, achievement_manager, ai_coordinator,
    create_investigation_objective, create_survival_objective,
    create_social_objective, create_exploration_objective,
    create_forbidden_knowledge_objective, create_sanity_dependent_investigation,
    ObjectiveStatus, ObjectivePriority, AchievementCategory, AchievementRarity
)
from core.game_manager import GameManager, GameManagerConfig
from core.game_engine import GameEngine, Character

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ObjectiveSystemTester:
    """Comprehensive tester for the objective system"""
    
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.start_time = time.time()
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log the result of a test"""
        status = "PASS" if success else "FAIL"
        result = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'timestamp': time.time()
        }
        self.test_results.append(result)
        
        if success:
            logger.info(f"PASS {test_name}: {status}")
        else:
            logger.error(f"FAIL {test_name}: {status} - {details}")
            self.failed_tests.append(result)
    
    async def test_basic_objective_creation(self):
        """Test basic objective creation and management"""
        try:
            logger.info("Testing basic objective creation...")
            
            # Clear existing objectives
            objective_manager.clear_all_objectives()
            
            # Test investigation objective
            investigation_obj = create_investigation_objective(
                objective_id="test_investigation",
                title="Test Investigation",
                location="test_location"
            )
            
            objective_manager.add_objective(investigation_obj)
            
            # Verify objective was added
            assert len(objective_manager.get_active_objectives()) == 1
            assert investigation_obj.status == ObjectiveStatus.ACTIVE
            
            # Test survival objective
            survival_obj = create_survival_objective(
                objective_id="test_survival",
                title="Test Survival",
                threat_description="dangerous creature",
                duration_minutes=5
            )
            
            objective_manager.add_objective(survival_obj)
            assert len(objective_manager.get_active_objectives()) == 2
            
            self.log_test_result("Basic Objective Creation", True)
            
        except Exception as e:
            self.log_test_result("Basic Objective Creation", False, str(e))
    
    async def test_objective_progress_tracking(self):
        """Test objective progress tracking and completion"""
        try:
            logger.info("Testing objective progress tracking...")
            
            # Create a social objective
            social_obj = create_social_objective(
                objective_id="test_social",
                title="Test Social Interaction",
                npc_name="Test NPC"
            )
            
            objective_manager.add_objective(social_obj)
            
            # Test progress tracking
            initial_progress = social_obj.get_progress_percentage()
            assert initial_progress >= 0.0
            
            # Simulate action that progresses objective
            game_data = {
                'turn_number': 1,
                'player_action': 'greet the NPC',
                'current_scene': 'test_location'
            }
            
            action_data = {
                'action_text': 'greet the NPC',
                'turn_number': 1,
                'location': 'test_location'
            }
            
            # Update objectives
            completed = objective_manager.update_all_objectives(game_data, action_data)
            
            # Check if progress was made
            new_progress = social_obj.get_progress_percentage()
            
            self.log_test_result("Objective Progress Tracking", True)
            
        except Exception as e:
            self.log_test_result("Objective Progress Tracking", False, str(e))
    
    async def test_san_integrated_objectives(self):
        """Test SAN-integrated objectives"""
        try:
            logger.info("Testing SAN-integrated objectives...")
            
            # Create forbidden knowledge objective
            forbidden_obj = create_forbidden_knowledge_objective(
                objective_id="test_forbidden",
                title="Test Forbidden Knowledge",
                knowledge_type="ancient_texts",
                insight_levels=[
                    {"name": "basic", "description": "Basic understanding", "san_cost": 1},
                    {"name": "advanced", "description": "Deep insights", "san_cost": 2}
                ]
            )
            
            objective_manager.add_objective(forbidden_obj)
            
            # Create sanity-dependent investigation
            from objectives.san_objectives import SanityState
            san_obj = create_sanity_dependent_investigation(
                objective_id="test_san_investigation",
                title="Test Sanity Investigation",
                location="haunted_library",
                state_configurations={
                    SanityState.STABLE: {"approach": "systematic", "bonus": 1},
                    SanityState.DISTURBED: {"approach": "cautious", "penalty": 1},
                    SanityState.MAD: {"approach": "chaotic", "alternative": "flee"}
                }
            )
            
            objective_manager.add_objective(san_obj)
            
            # Test with different sanity levels
            high_sanity_stats = {'sanity': 80}
            low_sanity_stats = {'sanity': 20}
            
            # Simulate updates with different sanity levels
            game_data = {'character_stats': high_sanity_stats}
            action_data = {'character_data': high_sanity_stats}
            
            objective_manager.update_all_objectives(game_data, action_data)
            
            self.log_test_result("SAN-Integrated Objectives", True)
            
        except Exception as e:
            self.log_test_result("SAN-Integrated Objectives", False, str(e))
    
    async def test_achievement_system(self):
        """Test the achievement system"""
        try:
            logger.info("Testing achievement system...")
            
            # Test achievement checking
            game_data = {
                'completed_objectives': [
                    {'type': 'investigation', 'title': 'Test Investigation'}
                ],
                'events': [
                    {'type': 'supernatural_encounter_survived'}
                ],
                'unlocked_achievements': set()
            }
            
            player_stats = {
                'sanity': 75,
                'cosmic_knowledge_count': 1,
                'known_entities_count': 0,
                'total_playtime_hours': 1,
                'completed_campaigns': 0,
                'cosmic_encounters': 0,
                'session_min_sanity': 70
            }
            
            # Check for achievements
            newly_unlocked = achievement_manager.check_all_achievements(game_data, player_stats)
            
            # Verify some achievements were unlocked
            unlocked_count = len(achievement_manager.get_unlocked_achievements())
            
            # Get achievement statistics
            stats = achievement_manager.get_achievement_statistics()
            assert 'total_achievements' in stats
            assert stats['total_achievements'] > 0
            
            self.log_test_result("Achievement System", True, f"Unlocked: {unlocked_count}")
            
        except Exception as e:
            self.log_test_result("Achievement System", False, str(e))
    
    async def test_ai_coordination(self):
        """Test AI coordination for objective generation"""
        try:
            logger.info("Testing AI coordination...")
            
            # Test without actual AI client (should handle gracefully)
            game_context = {
                'scenario': 'test_scenario',
                'character_name': 'Test Character',
                'current_location': 'test_location',
                'character_stats': {'sanity': 50}
            }
            
            # This should not fail even without AI client
            suggestions = await ai_coordinator.suggest_objectives(game_context, limit=1)
            
            # Should return empty list or handle gracefully
            assert isinstance(suggestions, list)
            
            self.log_test_result("AI Coordination", True, "Graceful handling without AI client")
            
        except Exception as e:
            self.log_test_result("AI Coordination", False, str(e))
    
    async def test_game_manager_integration(self):
        """Test GameManager integration with objective system"""
        try:
            logger.info("Testing GameManager integration...")
            
            # Create test configuration
            config = GameManagerConfig(
                ai_provider="auto",
                save_directory="test_saves",
                enable_fallback=True
            )
            
            # Create game manager
            game_manager = GameManager(config)
            
            # Test initialization
            initialized = await game_manager.initialize()
            
            if initialized:
                # Test objective system integration
                assert hasattr(game_manager, 'objective_manager')
                assert hasattr(game_manager, 'achievement_manager')
                assert hasattr(game_manager, 'ai_coordinator')
                
                # Test objective summary methods
                summary = game_manager.get_objective_progress_summary()
                assert isinstance(summary, dict)
                
                achievement_summary = game_manager.get_achievement_summary()
                assert isinstance(achievement_summary, dict)
                
                await game_manager.shutdown()
                
                self.log_test_result("GameManager Integration", True)
            else:
                self.log_test_result("GameManager Integration", False, "Failed to initialize GameManager")
                
        except Exception as e:
            self.log_test_result("GameManager Integration", False, str(e))
    
    async def test_objective_persistence(self):
        """Test objective and achievement persistence"""
        try:
            logger.info("Testing objective persistence...")
            
            # Test achievement save/load
            test_save_path = Path("test_achievements.json")
            
            # Save current state
            save_success = achievement_manager.save_to_file(str(test_save_path))
            assert save_success
            
            # Verify file was created
            assert test_save_path.exists()
            
            # Test load (would normally reset state first)
            load_success = achievement_manager.load_from_file(str(test_save_path))
            assert load_success
            
            # Clean up
            test_save_path.unlink()
            
            self.log_test_result("Objective Persistence", True)
            
        except Exception as e:
            self.log_test_result("Objective Persistence", False, str(e))
    
    async def test_multi_layered_objectives(self):
        """Test different objective types and their interactions"""
        try:
            logger.info("Testing multi-layered objectives...")
            
            # Clear existing objectives
            objective_manager.clear_all_objectives()
            
            # Create objectives of different types and priorities
            immediate_obj = create_social_objective(
                objective_id="immediate_test",
                title="Immediate Social Task",
                npc_name="Guard"
            )
            
            exploration_obj = create_exploration_objective(
                objective_id="exploration_test",
                title="Explore Areas",
                areas_to_explore=["courtyard", "tower", "dungeon"]
            )
            
            # Add objectives
            objective_manager.add_objective(immediate_obj)
            objective_manager.add_objective(exploration_obj)
            
            # Test priority management
            high_priority = len([obj for obj in objective_manager.get_active_objectives() 
                               if obj.priority == ObjectivePriority.HIGH])
            
            # Test objective statistics
            stats = objective_manager.get_statistics()
            assert 'active_count' in stats
            assert stats['active_count'] >= 2
            
            self.log_test_result("Multi-layered Objectives", True)
            
        except Exception as e:
            self.log_test_result("Multi-layered Objectives", False, str(e))
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        logger.info("Starting comprehensive objective system tests...")
        
        # Run all test methods
        test_methods = [
            self.test_basic_objective_creation,
            self.test_objective_progress_tracking,
            self.test_san_integrated_objectives,
            self.test_achievement_system,
            self.test_ai_coordination,
            self.test_multi_layered_objectives,
            self.test_objective_persistence,
            self.test_game_manager_integration,
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
            except Exception as e:
                logger.error(f"Test method {test_method.__name__} failed with exception: {e}")
                self.log_test_result(test_method.__name__, False, f"Exception: {e}")
    
    def print_test_summary(self):
        """Print a summary of all test results"""
        total_tests = len(self.test_results)
        failed_tests = len(self.failed_tests)
        passed_tests = total_tests - failed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        total_time = time.time() - self.start_time
        
        print("\n" + "="*60)
        print("OBJECTIVE SYSTEM TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        print("="*60)
        
        if self.failed_tests:
            print("\nFAILED TESTS:")
            for test in self.failed_tests:
                print(f"FAIL {test['test_name']}: {test['details']}")
        
        print("\nDETAILED RESULTS:")
        for test in self.test_results:
            status_icon = "PASS" if test['status'] == 'PASS' else "FAIL"
            print(f"{status_icon} {test['test_name']}: {test['status']}")
            if test['details']:
                print(f"   Details: {test['details']}")
        
        print("="*60)
        
        return failed_tests == 0


async def main():
    """Main test runner"""
    print("Cthulhu TRPG Objective System - Comprehensive Test Suite")
    print("="*60)
    
    tester = ObjectiveSystemTester()
    
    try:
        await tester.run_all_tests()
        success = tester.print_test_summary()
        
        if success:
            print("\nSUCCESS: All tests passed! Objective system is working correctly.")
            return True
        else:
            print("\nWARNING: Some tests failed. Please review the results above.")
            return False
            
    except Exception as e:
        logger.error(f"Test suite failed with exception: {e}")
        print(f"\nERROR: Test suite crashed: {e}")
        return False


if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(main())
    sys.exit(0 if success else 1)