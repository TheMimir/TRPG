#!/usr/bin/env python3
"""
Test AI Story Generation Fix
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_ai_story_generation():
    """Test that AI story generation is working correctly"""
    print("🤖 Testing AI Story Generation Fix...")
    print("=" * 60)
    
    try:
        from core.game_manager import GameManager
        from core.gameplay_controller import GameplayController
        
        # Initialize systems
        print("1. Initializing game systems...")
        game_manager = GameManager()
        await game_manager.initialize()
        
        # Check system health
        print(f"   Ollama available: {game_manager.ai_available if hasattr(game_manager, 'ai_available') else 'Unknown'}")
        
        # Check agent registration
        has_agent_manager = hasattr(game_manager, 'agent_manager') and game_manager.agent_manager is not None
        print(f"   Agent manager present: {has_agent_manager}")
        
        # Start game
        print("\n2. Starting new game...")
        await game_manager.start_new_game("miskatonic_university_library")
        
        # Create gameplay controller
        gameplay_controller = GameplayController(game_manager.game_engine, game_manager.agent_manager)
        
        # Test investigation action (should trigger AI)
        test_actions = [
            "도서관 입구의 팻말과 공지사항을 확인한다",
            "접수 데스크의 사서와 대화한다",
            "도서관 내부 구조를 파악한다"
        ]
        
        for i, action in enumerate(test_actions, 1):
            print(f"\n3.{i} Testing action: '{action}'")
            
            try:
                result = await gameplay_controller.process_player_action(action)
                
                story_text = result.story_content.text
                story_length = len(story_text)
                is_fallback = "당신의 행동이 상황에 변화를 가져왔습니다" in story_text
                
                print(f"     Story length: {story_length} characters")
                print(f"     Is fallback?: {'Yes' if is_fallback else 'No'}")
                
                if is_fallback:
                    print(f"     ❌ Using fallback content: {story_text}")
                else:
                    print(f"     ✅ Rich AI content: {story_text[:100]}...")
                
                # Check metadata
                metadata = result.story_content.metadata
                source = metadata.get('source', 'unknown')
                print(f"     Content source: {source}")
                
                # Check investigation opportunities
                investigations = result.story_content.investigation_opportunities
                print(f"     Investigation opportunities: {len(investigations)}")
                for j, inv in enumerate(investigations[:2], 1):
                    print(f"       {j}. {inv}")
                
            except Exception as e:
                print(f"     ❌ Action failed: {e}")
                import traceback
                traceback.print_exc()
            
            print("-" * 60)
        
        # Test agent manager directly
        print("\n4. Direct agent manager test...")
        if game_manager.agent_manager:
            story_agent = game_manager.agent_manager.get_agent("story_agent")
            if story_agent:
                print("   ✅ StoryAgent found in manager")
                
                # Test direct agent call
                test_input = {
                    "action_type": "investigate",
                    "scene_id": "library_entrance",
                    "player_action": "도서관을 조사한다",
                    "tension_level": "uneasy"
                }
                
                try:
                    agent_response = await story_agent.process_input(test_input)
                    print(f"   ✅ Direct agent response: {len(str(agent_response))} characters")
                    print(f"   Response type: {type(agent_response)}")
                except Exception as e:
                    print(f"   ❌ Direct agent call failed: {e}")
            else:
                print("   ❌ StoryAgent NOT found in manager")
        else:
            print("   ❌ Agent manager is None")
        
        await game_manager.shutdown()
        return True
        
    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_story_generation())
    if success:
        print("\n🎉 AI Story Generation Test Complete!")
    else:
        print("\n💥 AI Story Generation Test Failed!")