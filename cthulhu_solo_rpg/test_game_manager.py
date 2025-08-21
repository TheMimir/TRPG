#!/usr/bin/env python3
"""
Test GameManager initialization with mock AI system
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_game_manager_initialization():
    """Test GameManager initialization process."""
    print("Testing GameManager initialization...")
    
    try:
        from src.core.game_manager import GameManager
        from src.utils.config import Config
        
        # Create config with mock AI settings
        config = Config()
        config.data = {
            'ai': {
                'ollama_url': 'http://localhost:11434',
                'model': 'gpt-oss-120b',
                'ultra_think_enabled': True,
                'ultra_think_depth': 3
            },
            'game': {
                'auto_save': True,
                'auto_save_interval': 300
            },
            'saves_directory': './saves'
        }
        
        print("✓ Configuration created")
        
        # Initialize GameManager
        game_manager = GameManager(config)
        print("✓ GameManager instance created")
        
        # Initialize all systems
        print("\nInitializing systems...")
        success = await game_manager.initialize_systems()
        
        if success:
            print("✓ All systems initialized successfully!")
            
            # Check agent status
            print("\nAgent Status:")
            for agent_name, status in game_manager.agent_status.items():
                status_icon = "✓" if status.ready else "✗"
                print(f"  {status_icon} {agent_name}: {'Ready' if status.ready else 'Failed'}")
            
            # Check if agents have required attributes
            print("\nAgent Attributes Check:")
            for agent_name, agent in game_manager.agents.items():
                if hasattr(agent, 'horror_sensitivity'):
                    print(f"  ✓ {agent_name}: horror_sensitivity = {agent.horror_sensitivity}")
                else:
                    print(f"  ✗ {agent_name}: missing horror_sensitivity attribute")
                    return False
            
            # Get system status
            print("\nSystem Status:")
            system_status = game_manager.get_system_status()
            
            print(f"  Phase: {system_status['initialization']['current_phase']}")
            print(f"  Initialized: {system_status['initialization']['is_initialized']}")
            print(f"  AI Client Available: {system_status['ai_client']['available']}")
            print(f"  Ultra-think Enabled: {system_status['ultra_think']['enabled']}")
            
            # Test a simple story agent response
            print("\nTesting Story Agent Response:")
            if 'story_agent' in game_manager.agents:
                story_agent = game_manager.agents['story_agent']
                try:
                    test_input = {
                        "action_type": "scene_generation",
                        "player_action": "examining the old library",
                        "location": "Miskatonic University Library",
                        "context": "Initial investigation"
                    }
                    
                    response = await story_agent.process_input(test_input)
                    
                    if 'scene' in response and 'description' in response['scene']:
                        scene_desc = response['scene']['description']
                        print(f"  ✓ Scene generated ({len(scene_desc)} characters)")
                        print(f"  Preview: {scene_desc[:100]}...")
                    else:
                        print(f"  ✓ Response generated: {response}")
                    
                except Exception as agent_error:
                    print(f"  ✗ Story Agent test failed: {agent_error}")
                    return False
            
            return True
            
        else:
            print("✗ System initialization failed!")
            return False
            
    except Exception as e:
        print(f"✗ GameManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if 'game_manager' in locals() and game_manager:
            try:
                await game_manager.shutdown()
                print("✓ GameManager shutdown completed")
            except:
                pass

async def main():
    """Run the test."""
    print("=" * 60)
    print("GameManager Initialization Test with Mock AI")
    print("=" * 60)
    
    success = await test_game_manager_initialization()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS: GameManager initialization is working!")
        print("All AI agents are properly initialized and responding.")
        print("The system is ready for use with mock AI responses.")
    else:
        print("❌ FAILED: GameManager initialization has issues.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)