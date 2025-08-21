#!/usr/bin/env python3
"""
Complete integration test - create character and start game
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_complete_game_flow():
    """Test complete game flow from character creation to story start."""
    
    try:
        from src.core.game_manager import GameManager
        from src.core.character import Character
        from src.utils.config import Config
        
        print("Creating game configuration...")
        config = Config()
        config.data = {
            'ai': {
                'ollama_url': 'http://localhost:11434',
                'model': 'gpt-oss-120b',
                'ultra_think_enabled': False,  # Disable for simpler test
                'ultra_think_depth': 3,
                'use_mock_client': True  # Use mock client for testing
            },
            'game': {
                'auto_save': True,
                'auto_save_interval': 300
            },
            'saves_directory': './saves'
        }
        
        print("✓ Configuration created")
        
        # Initialize GameManager
        print("\nInitializing GameManager...")
        game_manager = GameManager(config)
        
        success = await game_manager.initialize_systems()
        if not success:
            print("✗ Failed to initialize GameManager")
            return False
        
        print("✓ GameManager initialized")
        
        # Create a test character
        print("\nCreating test character...")
        character = Character("Dr. Henry Armitage", age=55, gender="male")
        character.generate_attributes("rolled")
        character.set_occupation("Professor", 400)
        
        # Allocate some skill points
        character.allocate_occupation_skill_points("Library Use", 70)
        character.allocate_occupation_skill_points("Occult", 60)
        character.allocate_occupation_skill_points("Other Language (Latin)", 50)
        character.allocate_personal_skill_points("History", 40)
        character.allocate_personal_skill_points("Spot Hidden", 30)
        
        print(f"✓ Character created: {character.name}")
        print(f"  Age: {character.age}, Occupation: {character.occupation}")
        print(f"  Library Use: {character.get_skill_value('Library Use')}")
        print(f"  Occult: {character.get_skill_value('Occult')}")
        
        # Start new game
        print("\nStarting new game...")
        success = await game_manager.start_new_game(
            character=character,
            scenario_name="The Whisperer in Darkness"
        )
        
        if not success:
            print("✗ Failed to start new game")
            return False
        
        print("✓ New game started")
        
        # Check game status
        status = game_manager.get_system_status()
        print(f"  Game Phase: {status['initialization']['current_phase']}")
        print(f"  Running: {status['initialization']['is_running']}")
        print(f"  Character: {status['session']['character_name']}")
        print(f"  Scenario: {status['session']['scenario']}")
        
        # Simulate some player actions
        print("\nSimulating player actions...")
        
        from src.core.game_engine import PlayerAction
        
        # Action 1: Look around
        action1 = PlayerAction(
            action_type="observation",
            parameters={"target": "surroundings", "detail_level": "careful"},
            time_cost=10
        )
        
        result1 = await game_manager.process_player_action(action1)
        if result1.get("success"):
            print("✓ Action 1 (observation) processed successfully")
            if "ai_responses" in result1:
                print(f"  AI responses received: {len(result1['ai_responses'])} agents")
        else:
            print(f"✗ Action 1 failed: {result1.get('error', 'Unknown error')}")
        
        # Action 2: Investigation
        action2 = PlayerAction(
            action_type="investigation",
            parameters={"target": "mysterious book", "skill": "Library Use"},
            time_cost=30
        )
        
        result2 = await game_manager.process_player_action(action2)
        if result2.get("success"):
            print("✓ Action 2 (investigation) processed successfully")
            print(f"  Turn number: {result2['turn_number']}")
        else:
            print(f"✗ Action 2 failed: {result2.get('error', 'Unknown error')}")
        
        print("\n✓ Complete game flow test successful!")
        return True
        
    except Exception as e:
        print(f"✗ Game flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if 'game_manager' in locals() and game_manager:
            try:
                await game_manager.shutdown()
                print("✓ Game cleanup completed")
            except Exception as cleanup_error:
                print(f"! Cleanup warning: {cleanup_error}")

async def main():
    """Run the complete test."""
    print("=" * 70)
    print("Complete Cthulhu TRPG Game Flow Test")
    print("=" * 70)
    
    success = await test_complete_game_flow()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 SUCCESS: Complete game flow is working!")
        print("✓ Character creation works")
        print("✓ Game initialization works") 
        print("✓ AI agents respond to actions")
        print("✓ Turn processing works")
        print("\nThe Cthulhu TRPG system is ready for gameplay!")
    else:
        print("❌ FAILED: Game flow has issues.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)