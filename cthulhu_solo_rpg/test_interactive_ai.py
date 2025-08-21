#!/usr/bin/env python3
"""
Interactive Test for AI Story Generation
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_interactive_ai():
    """Test interactive AI story generation"""
    print("🎮 Interactive AI Story Generation Test")
    print("=" * 60)
    
    try:
        from core.game_manager import GameManager
        from core.gameplay_controller import GameplayController
        from ui.gameplay_interface import GameplayInterface
        
        # Initialize systems
        print("Initializing game systems...")
        game_manager = GameManager()
        await game_manager.initialize()
        
        # Start game with character data
        print("Starting new game...")
        default_character = {
            "name": "테스트 조사관",
            "occupation": "investigator", 
            "age": 28,
            "stats": {
                "STR": 10, "CON": 12, "POW": 14,
                "DEX": 11, "APP": 10, "SIZ": 13, 
                "INT": 16, "EDU": 18
            },
            "skills": {
                "도서관 이용": 70,
                "탐지": 60,
                "교육": 80
            }
        }
        
        game_started = await game_manager.start_new_game(default_character, "miskatonic_university_library")
        if not game_started:
            print("❌ Failed to start game")
            return False
        
        # Create gameplay controller with scenario
        current_scenario = getattr(game_manager, 'current_scenario', None)
        if hasattr(GameplayController.__init__, '__code__') and 'current_scenario' in GameplayController.__init__.__code__.co_varnames:
            gameplay_controller = GameplayController(game_manager.game_engine, game_manager.agent_manager, current_scenario)
        else:
            gameplay_controller = GameplayController(game_manager.game_engine, game_manager.agent_manager)
        
        print("\nSystem ready! Testing investigation actions...")
        print("Current scene:", game_manager.game_engine.current_scene)
        print("Current turn:", game_manager.game_engine.turn_number)
        
        # Test the exact investigation actions from the menu
        test_actions = [
            "도서관 입구의 팻말과 공지사항을 확인한다"
        ]
        
        for action in test_actions:
            print(f"\n🔍 Processing action: '{action}'")
            print("-" * 40)
            
            try:
                # Process the action
                result = await gameplay_controller.process_player_action(action)
                
                print(f"✅ Turn {result.turn_number} completed")
                print(f"📖 Story content ({len(result.story_content.text)} chars):")
                print(f"   {result.story_content.text}")
                
                print(f"🏷️  Content metadata:")
                for key, value in result.story_content.metadata.items():
                    print(f"   {key}: {value}")
                
                print(f"🔬 Investigation opportunities:")
                for i, inv in enumerate(result.story_content.investigation_opportunities, 1):
                    print(f"   {i}. {inv}")
                
                # Check if this is AI generated or fallback
                source = result.story_content.metadata.get('source', 'unknown')
                if source == 'ai':
                    print("🤖 ✅ AI-generated content detected!")
                elif source == 'fallback':
                    print("⚠️  Fallback content used")
                elif source == 'error_fallback':
                    print("❌ Error fallback content used")
                else:
                    print(f"ℹ️  Content source: {source}")
                
            except Exception as e:
                print(f"❌ Action failed: {e}")
                import traceback
                traceback.print_exc()
        
        await game_manager.shutdown()
        return True
        
    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_interactive_ai())
    if success:
        print("\n🎉 Interactive AI test complete!")
    else:
        print("\n💥 Interactive AI test failed!")