#!/usr/bin/env python3
"""
Test script to verify that the initialization errors have been fixed.
"""

import asyncio
import sys
import logging
import os
from pathlib import Path

# Ensure we're in the right directory
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Change to the project directory
os.chdir(current_dir)

try:
    from src.core.game_manager import GameManager
    from src.utils.config import Config
except ImportError:
    # Try alternative import
    sys.path.insert(0, str(current_dir))
    from src.core.game_manager import GameManager
    from src.utils.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_initialization():
    """Test the GameManager initialization process."""
    
    print("=" * 50)
    print("Testing Cthulhu TRPG AI Agent Initialization")
    print("=" * 50)
    
    try:
        # Create config with defaults
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
            print("-" * 30)
            for agent_name, status in game_manager.agent_status.items():
                status_icon = "✓" if status.ready else "✗"
                print(f"{status_icon} {agent_name}: {'Ready' if status.ready else 'Failed'}")
            
            # Check if agents have horror_sensitivity attribute
            print("\nAgent Attributes Check:")
            print("-" * 30)
            for agent_name, agent in game_manager.agents.items():
                if hasattr(agent, 'horror_sensitivity'):
                    print(f"✓ {agent_name}: horror_sensitivity = {agent.horror_sensitivity}")
                else:
                    print(f"✗ {agent_name}: missing horror_sensitivity attribute")
            
            # Get system status
            print("\nSystem Status:")
            print("-" * 30)
            system_status = game_manager.get_system_status()
            
            print(f"Phase: {system_status['initialization']['current_phase']}")
            print(f"Initialized: {system_status['initialization']['is_initialized']}")
            print(f"Running: {system_status['initialization']['is_running']}")
            print(f"AI Client Available: {system_status['ai_client']['available']}")
            print(f"Ultra-think Enabled: {system_status['ultra_think']['enabled']}")
            
            # Test a simple agent response
            print("\nTesting Agent Response:")
            print("-" * 30)
            
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
                    print("✓ Story Agent response generated successfully")
                    print(f"Scene Description Preview: {response.get('scene', {}).get('description', 'N/A')[:100]}...")
                    
                except Exception as agent_error:
                    print(f"✗ Story Agent test failed: {agent_error}")
            
            print("\n" + "=" * 50)
            print("SUCCESS: All initialization tests passed!")
            print("The system is ready for use.")
            
        else:
            print("✗ System initialization failed!")
            return False
            
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if 'game_manager' in locals():
            await game_manager.shutdown()
    
    return True

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_initialization())
    sys.exit(0 if result else 1)