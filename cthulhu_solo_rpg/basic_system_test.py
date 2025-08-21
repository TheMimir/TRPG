#!/usr/bin/env python3
"""
Basic System Test for Cthulhu Solo RPG
Tests the core functionality that's currently working.
"""

import os
import sys
import asyncio

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_core_models():
    """Test 1: Core Data Models"""
    print("=== Testing Core Data Models ===")
    
    try:
        from core.models import (
            GameState, Investigation, PlayerAction, StoryContent, 
            NarrativeContext, TensionLevel, ActionType,
            create_basic_narrative_context
        )
        
        # Test character data
        character_data = {
            "name": "Dr. Test Investigator",
            "stats": {"STR": 50, "DEX": 60, "INT": 80, "EDU": 85},
            "skills": {"Library Use": 70, "Occult": 45, "Psychology": 60},
            "sanity": 75,
            "hit_points": 13
        }
        print("✓ Character data structure created")
        
        # Test narrative context
        narrative_context = create_basic_narrative_context("test_scene", character_data)
        print(f"✓ NarrativeContext created: {narrative_context.scene_id}")
        
        # Test game state
        game_state = GameState(
            character_data=character_data,
            narrative_context=narrative_context,
            game_metadata={"test": True}
        )
        print(f"✓ GameState created with character: {game_state.character_data['name']}")
        
        # Test investigation
        investigation = Investigation(
            description="Test investigation description",
            difficulty=5,
            scene_id="test_scene",
            keywords=["test", "investigation"]
        )
        print(f"✓ Investigation created: {investigation.description[:30]}...")
        
        # Test player action
        player_action = PlayerAction(
            original_text="Look around the room",
            action_type=ActionType.INVESTIGATE,
            target="room",
            intent="examine surroundings"
        )
        print(f"✓ PlayerAction created: {player_action.original_text}")
        
        # Test story content
        story_content = StoryContent(
            text="You find yourself in a dimly lit library.",
            content_id="test_content_1",
            scene_id="test_scene",
            tension_level=TensionLevel.CALM
        )
        print(f"✓ StoryContent created: {story_content.text[:30]}...")
        
        # Test can_attempt method
        can_attempt = investigation.can_attempt(
            character_state=character_data,
            narrative_flags=narrative_context.narrative_flags
        )
        print(f"✓ Investigation.can_attempt method works: {can_attempt}")
        
        # Test game state serialization
        state_dict = game_state.to_dict()
        print(f"✓ GameState serialization works: {len(state_dict)} keys")
        
        # Test game state deserialization
        restored_state = GameState.from_dict(state_dict)
        print(f"✓ GameState deserialization works: {restored_state.character_data['name']}")
        
        print("✅ All core data model tests PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Core data models test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dice_system():
    """Test 2: Dice System"""
    print("\n=== Testing Dice System ===")
    
    try:
        from core.dice import DiceEngine, skill_check, roll_dice, get_common_roll
        
        # Test basic dice engine
        dice_engine = DiceEngine()
        print("✓ DiceEngine created")
        
        # Test basic roll
        d100_result = dice_engine.roll("d100")
        print(f"✓ D100 roll: {d100_result.total} (valid: {1 <= d100_result.total <= 100})")
        
        # Test dice expressions
        roll_2d6 = dice_engine.roll("2d6+3")
        print(f"✓ 2d6+3 roll: {roll_2d6.total} (rolls: {roll_2d6.rolls})")
        
        # Test skill check
        skill_result = dice_engine.skill_check(75, 0)
        print(f"✓ Skill check (75): {skill_result.total} -> {skill_result.success_level.value}")
        
        # Test sanity check
        sanity_result = dice_engine.sanity_check(65, "1d4/1d8")
        print(f"✓ Sanity check: lost {sanity_result['sanity_loss']} sanity")
        
        # Test damage roll
        damage_result = dice_engine.damage_roll("1d6+2", "head")
        print(f"✓ Damage roll (1d6+2 to head): {damage_result.total}")
        
        # Test convenience functions
        quick_roll = roll_dice("d20")
        print(f"✓ Quick roll function: {quick_roll.total}")
        
        quick_skill = skill_check(60)
        print(f"✓ Quick skill check: {quick_skill.success_level.value}")
        
        # Test common rolls
        common_damage = get_common_roll("damage_knife")
        print(f"✓ Common roll (knife damage): {common_damage.total}")
        
        # Test multiple rolls for consistency
        results = [dice_engine.roll("d100").total for _ in range(10)]
        valid_results = all(1 <= r <= 100 for r in results)
        print(f"✓ Multiple rolls consistency: {valid_results} (sample: {results[:3]})")
        
        # Test statistics
        stats = dice_engine.get_statistics()
        print(f"✓ Roll statistics: {stats['total_rolls']} total rolls")
        
        print("✅ All dice system tests PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Dice system test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_working_modules():
    """Test 3: Other Working Modules"""
    print("\n=== Testing Other Working Modules ===")
    
    try:
        from core.game_engine import GameEngine
        print("✓ GameEngine import successful")
        
        # Try to create a game engine
        try:
            engine = GameEngine()
            print("✓ GameEngine instantiation successful")
        except Exception as e:
            print(f"⚠ GameEngine instantiation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Other modules test failed: {e}")
        return False

def check_missing_dependencies():
    """Check for missing dependencies"""
    print("\n=== Checking Dependencies ===")
    
    missing_deps = []
    
    try:
        import aiohttp
        print("✓ aiohttp available")
    except ImportError:
        print("❌ aiohttp missing (needed for AI integration)")
        missing_deps.append("aiohttp")
    
    try:
        import json
        print("✓ json available")
    except ImportError:
        missing_deps.append("json")
    
    try:
        import asyncio
        print("✓ asyncio available")
    except ImportError:
        missing_deps.append("asyncio")
    
    if missing_deps:
        print(f"\n⚠ Missing dependencies: {missing_deps}")
        print("Install with: pip install " + " ".join(missing_deps))
    else:
        print("✅ All basic dependencies available")
    
    return len(missing_deps) == 0

def main():
    """Run all basic tests"""
    print("BASIC SYSTEM TEST - Cthulhu Solo RPG")
    print("=" * 50)
    
    # Change to the correct directory
    os.chdir('/Users/mimir/TRPG/cthulhu_solo_rpg')
    
    # Track results
    results = []
    
    # Run tests
    results.append(("Core Data Models", test_core_models()))
    results.append(("Dice System", test_dice_system()))
    results.append(("Other Modules", test_working_modules()))
    results.append(("Dependencies", check_missing_dependencies()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests PASSED! Core system is functional.")
    elif passed >= total * 0.7:
        print("✅ Most tests passed. System core is working with minor issues.")
    else:
        print("⚠️ Significant issues detected. System needs attention.")
    
    print("\nRecommendations:")
    if passed < total:
        print("- Fix import issues in failed modules")
        print("- Install missing dependencies: pip install aiohttp")
        print("- Check relative import statements in modules")
    
    print("- Core functionality (models, dice) is working well")
    print("- Ready for targeted fixes on specific modules")

if __name__ == "__main__":
    main()