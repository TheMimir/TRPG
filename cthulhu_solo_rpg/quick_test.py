#!/usr/bin/env python3
"""
Quick test of core functionality
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def quick_test():
    """Quick test of core components."""
    
    try:
        print("=== Quick TRPG System Test ===")
        
        # Test 1: Character Creation
        print("\n1. Testing Character Creation...")
        from src.core.character import Character
        
        character = Character("Test Character", age=30, gender="male")
        character.generate_attributes("rolled")
        character.set_occupation("Detective", 300)
        character.background = "A seasoned investigator"
        
        print(f"✓ Character created: {character.name}")
        print(f"  Occupation: {character.occupation}")
        print(f"  Background: {character.background}")
        print(f"  HP: {character.hit_points_maximum}")
        print(f"  Sanity: {character.sanity_maximum}")
        
        # Test 2: Game Manager Initialization
        print("\n2. Testing Game Manager...")
        from src.core.game_manager import GameManager
        from src.utils.config import Config
        
        config = Config()
        config.data = {
            'ai': {
                'use_mock_client': True,
                'model': 'mock-model',
                'ultra_think_enabled': False
            },
            'game': {
                'auto_save': False
            },
            'saves_directory': './saves'
        }
        
        game_manager = GameManager(config)
        
        print("✓ Game Manager created")
        
        # Test 3: Basic System Status
        print("\n3. Testing System Status...")
        
        try:
            success = await game_manager.initialize_systems()
            if success:
                print("✓ Systems initialized successfully")
                
                status = game_manager.get_system_status()
                print(f"  Phase: {status['initialization']['current_phase']}")
                print(f"  Running: {status['initialization']['is_running']}")
                
                agent_count = len([a for a in status['agents'].values() if a['ready']])
                print(f"  Ready Agents: {agent_count}")
                
            else:
                print("✗ System initialization failed")
                return False
                
        except Exception as e:
            print(f"✗ Initialization error: {e}")
            return False
        
        # Test 4: Character Integration
        print("\n4. Testing Character Integration...")
        
        try:
            game_success = await game_manager.start_new_game(
                character=character,
                scenario_name="Test Scenario"
            )
            
            if game_success:
                print("✓ Game started successfully")
                
                session_status = game_manager.get_system_status()
                print(f"  Character: {session_status['session']['character_name']}")
                print(f"  Scenario: {session_status['session']['scenario']}")
                
            else:
                print("✗ Game start failed")
                return False
                
        except Exception as e:
            print(f"✗ Game start error: {e}")
            return False
        
        print("\n✅ All tests passed! System is working.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if 'game_manager' in locals():
            try:
                await game_manager.shutdown()
                print("✓ Cleanup completed")
            except:
                pass

if __name__ == "__main__":
    result = asyncio.run(quick_test())
    sys.exit(0 if result else 1)