#!/usr/bin/env python3
"""
Test Numbered Investigation Input System
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_numbered_input():
    """Test that numbered investigation input works correctly"""
    print("🔢 Testing Numbered Investigation Input System...")
    print("=" * 60)
    
    try:
        from core.game_manager import GameManager
        from core.gameplay_controller import GameplayController
        from ui.gameplay_interface import GameplayInterface
        
        # Initialize systems
        print("1. Initializing game systems...")
        game_manager = GameManager()
        await game_manager.initialize()
        
        # Start game with character data
        default_character = {
            "name": "테스트 탐사자",
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
        
        # Create gameplay controller
        current_scenario = getattr(game_manager, 'current_scenario', None)
        if hasattr(GameplayController.__init__, '__code__') and 'current_scenario' in GameplayController.__init__.__code__.co_varnames:
            gameplay_controller = GameplayController(game_manager.game_engine, game_manager.agent_manager, current_scenario)
        else:
            gameplay_controller = GameplayController(game_manager.game_engine, game_manager.agent_manager)
        
        # Create interface
        interface = GameplayInterface(gameplay_controller)
        
        # Get initial story content to have investigation opportunities
        initial_story = await gameplay_controller.get_current_story_content()
        interface.current_story_content = initial_story
        
        print(f"2. Current investigation opportunities:")
        if initial_story.investigation_opportunities:
            for i, opp in enumerate(initial_story.investigation_opportunities, 1):
                print(f"   {i}. {opp}")
        else:
            print("   No investigation opportunities available")
        
        # Test conversion of numbered inputs
        print(f"\n3. Testing numbered input conversion...")
        
        test_inputs = ["1", "2", "3", "99", "abc", "도서관을 조사한다"]
        
        for test_input in test_inputs:
            print(f"\n   Testing input: '{test_input}'")
            
            # Test the conversion method directly
            converted = interface._convert_investigation_number(test_input)
            
            if converted != test_input:
                print(f"   ✅ Converted to: '{converted}'")
            elif test_input.isdigit():
                print(f"   ❌ Number not converted (likely invalid)")
            else:
                print(f"   ✅ Text input passed through: '{converted}'")
        
        # Test actual gameplay processing with numbered input
        print(f"\n4. Testing actual gameplay with numbered input...")
        
        if initial_story.investigation_opportunities:
            # Try processing the first investigation opportunity by number
            print(f"   Processing input: '1'")
            
            try:
                # This should convert "1" to the first investigation opportunity and process it
                result = await gameplay_controller.process_player_action("1")  # Direct call, bypassing UI conversion
                
                # Let's simulate what the UI would do
                converted_action = interface._convert_investigation_number("1")
                if converted_action:
                    print(f"   🔍 UI would convert '1' to: '{converted_action}'")
                    result = await gameplay_controller.process_player_action(converted_action)
                    
                    print(f"   ✅ Action processed successfully")
                    print(f"   📖 Generated story: {result.story_content.text[:100]}...")
                    print(f"   🏷️  Content source: {result.story_content.metadata.get('source', 'unknown')}")
                    
            except Exception as e:
                print(f"   ❌ Processing failed: {e}")
        
        await game_manager.shutdown()
        return True
        
    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_numbered_input())
    if success:
        print("\n🎉 Numbered input test complete!")
    else:
        print("\n💥 Numbered input test failed!")