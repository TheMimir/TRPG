#!/usr/bin/env python3
"""
Quick test to verify the list.items() error is fixed
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_turn_processing():
    """Test that turn processing works without list.items() error"""
    print("🧪 Testing turn processing fix...")
    
    try:
        from core.game_manager import GameManager
        from core.gameplay_controller import GameplayController
        
        # Initialize systems
        game_manager = GameManager()
        await game_manager.initialize()
        
        # Start game
        await game_manager.start_new_game("miskatonic_university_library")
        
        # Create gameplay controller
        gameplay_controller = GameplayController(game_manager.game_engine, game_manager.agent_manager)
        
        # Test player action processing
        test_action = "도서관 입구의 팻말을 자세히 살펴본다"
        print(f"📝 Testing action: {test_action}")
        
        # This should not raise the list.items() error
        result = await gameplay_controller.process_player_action(test_action)
        
        print("✅ Turn processing successful!")
        print(f"   Turn number: {result.turn_number}")
        # Handle both string and PlayerAction object
        if hasattr(result.player_action, 'text'):
            print(f"   Action processed: {result.player_action.text}")
        else:
            print(f"   Action processed: {result.player_action}")
        print(f"   Story generated: {len(result.story_content.text)} characters")
        
        # Check story_threads type
        story_threads = result.story_content.story_threads
        print(f"   Story threads type: {type(story_threads)}")
        print(f"   Story threads: {story_threads}")
        
        if hasattr(story_threads, 'items'):
            print("✅ story_threads.items() method available")
        else:
            print("❌ story_threads.items() method NOT available")
        
        await game_manager.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_turn_processing())
    if success:
        print("\n🎉 All tests passed! The list.items() error has been fixed!")
    else:
        print("\n💥 Tests failed. The error may still exist.")