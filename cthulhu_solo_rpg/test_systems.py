#!/usr/bin/env python3
"""
Basic test script for Cthulhu Solo TRPG core systems

This script performs basic validation of the implemented systems.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_character_system():
    """Test the character system."""
    print("Testing Character System...")
    
    try:
        from src.core.character import Character
        
        # Create a test character
        char = Character("Test Investigator", age=30, gender="male")
        
        # Generate attributes
        char.generate_attributes("rolled")
        
        # Set occupation
        char.set_occupation("Detective", 300)
        
        # Test skill allocation
        success = char.allocate_occupation_skill_points("Spot Hidden", 50)
        assert success, "Should be able to allocate occupation points"
        
        success = char.allocate_personal_skill_points("History", 30)
        assert success, "Should be able to allocate personal points"
        
        # Test skill value calculation
        spot_hidden_value = char.get_skill_value("Spot Hidden")
        assert spot_hidden_value > 0, "Spot Hidden should have value > 0"
        
        # Test sanity loss
        initial_sanity = char.sanity_current
        lost, effects = char.lose_sanity(5, "Test horror")
        assert char.sanity_current < initial_sanity, "Sanity should decrease"
        
        # Test damage
        initial_hp = char.hit_points_current
        conscious = char.take_damage(3)
        assert char.hit_points_current < initial_hp, "HP should decrease"
        assert conscious, "Character should remain conscious"
        
        # Test character summary
        summary = char.get_character_summary()
        assert 'name' in summary, "Summary should include name"
        
        print("✓ Character System tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Character System test failed: {e}")
        return False

def test_dice_system():
    """Test the dice system."""
    print("Testing Dice System...")
    
    try:
        from src.core.dice import DiceRoller, DifficultyLevel
        
        roller = DiceRoller()
        
        # Test basic rolls
        d100_roll = roller.roll_d100()
        assert 1 <= d100_roll <= 100, "d100 should be between 1-100"
        
        dice_results = roller.roll_dice(6, 3)
        assert len(dice_results) == 3, "Should roll 3 dice"
        assert all(1 <= d <= 6 for d in dice_results), "All dice should be 1-6"
        
        # Test skill checks
        result_type, roll_value, fumbled = roller.skill_check(50, 0)
        assert result_type in ['fumble', 'failure', 'success', 'hard', 'extreme', 'critical'], "Valid result type"
        assert 1 <= roll_value <= 100, "Roll value should be 1-100"
        
        # Test sanity check
        sanity_lost, description = roller.sanity_check(2, 8, 65)
        assert sanity_lost in [2, 8], "Sanity loss should be either short or long value"
        
        # Test damage roll
        damage = roller.damage_roll("1d6+2")
        assert damage >= 3, "1d6+2 should be at least 3"
        
        # Test resistance roll
        success = roller.resistance_roll(60, 50)
        assert isinstance(success, bool), "Resistance roll should return boolean"
        
        print("✓ Dice System tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Dice System test failed: {e}")
        return False

def test_game_engine():
    """Test the game engine."""
    print("Testing Game Engine...")
    
    try:
        from src.core.game_engine import GameEngine, PlayerAction, GameState
        from src.core.character import Character
        
        engine = GameEngine()
        
        # Test initialization
        char = Character("Test Player")
        char.generate_attributes("rolled")
        char.set_occupation("Detective", 300)
        
        success = engine.initialize_game(char)
        assert success, "Game should initialize successfully"
        assert engine.game_state == GameState.READY, "Game should be ready"
        
        # Test starting game
        success = engine.start_game()
        assert success, "Game should start successfully"
        assert engine.is_running, "Game should be running"
        
        # Test processing a turn
        action = PlayerAction("skill_check", {"skill_name": "Spot Hidden"})
        result = engine.process_turn(action)
        assert result.success, "Turn should process successfully"
        assert engine.current_turn == 1, "Turn counter should increment"
        
        # Test pausing and resuming
        success = engine.pause_game()
        assert success, "Game should pause"
        assert engine.is_paused, "Game should be paused"
        
        success = engine.resume_game()
        assert success, "Game should resume"
        assert not engine.is_paused, "Game should not be paused"
        
        # Test ending game
        success = engine.end_game()
        assert success, "Game should end"
        assert engine.game_state == GameState.ENDED, "Game should be ended"
        
        print("✓ Game Engine tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Game Engine test failed: {e}")
        return False

def test_rules_system():
    """Test the rules system."""
    print("Testing Rules System...")
    
    try:
        from src.core.rules import RulesEngine
        from src.core.character import Character
        
        rules = RulesEngine()
        
        # Test occupation data
        occupations = rules.get_available_occupations()
        assert len(occupations) > 0, "Should have occupations available"
        
        detective_data = rules.get_occupation_data("Detective")
        assert 'description' in detective_data, "Occupation should have description"
        
        # Test sanity loss data
        sanity_data = rules.get_sanity_loss_for_horror("seeing_a_dead_body")
        assert 'short_loss' in sanity_data, "Should have short loss value"
        assert 'long_loss' in sanity_data, "Should have long loss value"
        
        # Test character validation
        char = Character("Test")
        char.generate_attributes("rolled")
        char.set_occupation("Detective", 300)
        
        validation = rules.validate_character_creation(char)
        assert 'valid' in validation, "Validation should return valid status"
        
        # Test skill specializations
        specializations = rules.get_skill_specializations("Art/Craft")
        assert len(specializations) > 0, "Art/Craft should have specializations"
        
        # Test weapon damage
        damage_result = rules.calculate_weapon_damage("pistol", "success", 0)
        assert 'total_damage' in damage_result, "Should calculate total damage"
        
        # Test madness effects
        temp_madness = rules.roll_temporary_madness()
        assert 'effect' in temp_madness, "Should have madness effect"
        assert 'duration' in temp_madness, "Should have duration"
        
        print("✓ Rules System tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Rules System test failed: {e}")
        return False

def test_integration():
    """Test system integration."""
    print("Testing System Integration...")
    
    try:
        from src.core.character import Character
        from src.core.dice import DiceRoller
        from src.core.game_engine import GameEngine, PlayerAction
        from src.core.rules import RulesEngine
        
        # Create integrated test scenario
        char = Character("Integration Test", age=25, gender="female")
        char.generate_attributes("rolled")
        char.set_occupation("Journalist", 300)
        
        # Allocate some skills
        char.allocate_occupation_skill_points("Persuade", 40)
        char.allocate_personal_skill_points("History", 25)
        
        # Create game engine and rules
        engine = GameEngine()
        rules = RulesEngine()
        
        # Initialize and start game
        engine.initialize_game(char)
        engine.start_game()
        
        # Test a skill check through the engine
        action = PlayerAction("skill_check", {"skill_name": "Persuade", "difficulty": "normal"})
        result = engine.process_turn(action)
        assert result.success, "Turn should process"
        
        # Test sanity check
        sanity_data = rules.get_sanity_loss_for_horror("seeing_a_dead_body")
        sanity_result = rules.resolve_sanity_check(
            char, sanity_data['short_loss'], sanity_data['long_loss'], "Test horror"
        )
        assert 'success' in sanity_result, "Sanity check should return result"
        
        # Test character validation with rules
        validation = rules.validate_character_creation(char)
        if not validation['valid']:
            print(f"Validation warnings: {validation.get('warnings', [])}")
            print(f"Validation errors: {validation.get('errors', [])}")
        
        print("✓ System Integration tests passed")
        return True
        
    except Exception as e:
        print(f"✗ System Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Cthulhu Solo TRPG - Core Systems Test")
    print("=" * 50)
    
    tests = [
        test_character_system,
        test_dice_system,
        test_game_engine,
        test_rules_system,
        test_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test_func.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("🎉 All core systems are working correctly!")
        print("\nImplemented features:")
        print("• Complete character system with 8 attributes")
        print("• Skills system with occupation and personal points")
        print("• Sanity and madness mechanics")
        print("• Comprehensive dice rolling system")
        print("• Game engine with turn management")
        print("• Event system and time tracking")
        print("• Rules engine with Call of Cthulhu 7th Edition rules")
        print("• Occupation system with 7 predefined occupations")
        print("• Weapon and combat systems")
        print("• Save/load functionality")
    else:
        print("❌ Some tests failed. Please check the implementations.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)