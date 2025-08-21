#!/usr/bin/env python3
"""
ULTRATHINK LAYER 5 - SYNTHESIS VERIFICATION
Test the comprehensive AI story generation fix.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_complete_ai_story_fix():
    """
    Test the complete AI story generation workflow after the fix.
    This should now work end-to-end without fallback messages.
    """
    print("🚀 ULTRATHINK LAYER 5 - SYNTHESIS VERIFICATION")
    print("=" * 70)
    print("Testing Complete AI Story Generation Fix...")
    print()
    
    success_count = 0
    total_tests = 4
    
    # TEST 1: GameManager with Fixed Agent Registration
    print("🎮 TEST 1: GameManager with Fixed Agent Registration")
    print("-" * 50)
    try:
        from core.game_manager import GameManager
        
        game_manager = GameManager()
        success = await game_manager.initialize()
        
        if success:
            print(f"✅ GameManager initialized successfully")
            print(f"   Status: {game_manager.status.value}")
            
            # Check agent system health
            agent_health = game_manager.system_health.get("agents", {})
            print(f"   Agent status: {agent_health.get('status', 'unknown')}")
            print(f"   Registered agents: {agent_health.get('registered_count', 0)}")
            
            if agent_health.get("registered_count", 0) > 0:
                print(f"   Agent names: {agent_health.get('agents', [])}")
                success_count += 1
                print("✅ AGENTS SUCCESSFULLY REGISTERED!")
            else:
                print("❌ No agents registered")
                
            # Verify story agent is accessible
            if game_manager.agent_manager:
                story_agent = game_manager.agent_manager.get_agent("story_agent")
                if story_agent:
                    print("✅ StoryAgent is accessible via AgentManager")
                else:
                    print("❌ StoryAgent not accessible via AgentManager")
        else:
            print("❌ GameManager initialization failed")
            
        await game_manager.shutdown()
        
    except Exception as e:
        print(f"❌ GameManager test failed: {e}")
    
    print()
    
    # TEST 2: End-to-End GameplayController Test
    print("🎯 TEST 2: End-to-End GameplayController Test")
    print("-" * 50)
    try:
        from core.game_manager import GameManager
        from core.gameplay_controller import GameplayController
        from core.game_engine import GameEngine, Character
        
        # Initialize complete system
        game_manager = GameManager()
        await game_manager.initialize()
        
        # Create character and start game engine
        character = Character(
            name="조사관",
            age=30,
            occupation="investigator",
            residence="Arkham, Massachusetts",
            characteristics={
                "strength": 60, "constitution": 70, "power": 65,
                "dexterity": 55, "appearance": 50, "size": 60,
                "intelligence": 75, "education": 80
            }
        )
        
        game_manager.game_engine.character = character
        game_manager.game_engine.current_scene = "library_entrance"
        
        # Create gameplay controller
        controller = GameplayController(
            game_manager.game_engine,
            game_manager.agent_manager,
            scenario=None
        )
        
        # Test player action processing
        print("   Testing player action: '오래된 책을 조사한다'")
        
        turn_result = await controller.process_player_action("오래된 책을 조사한다")
        
        print(f"   Turn success: {turn_result.success}")
        print(f"   Story text: {turn_result.story_content.text[:100]}...")
        print(f"   Investigation opportunities: {len(turn_result.story_content.investigation_opportunities)}")
        
        # Check if it's NOT the generic fallback message
        generic_fallback = "당신의 행동이 상황에 변화를 가져왔습니다."
        if generic_fallback not in turn_result.story_content.text:
            success_count += 1
            print("✅ RICH AI STORY CONTENT GENERATED (NOT FALLBACK)!")
        else:
            print("❌ Still getting generic fallback message")
            
        await game_manager.shutdown()
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # TEST 3: Multiple Story Generation Test
    print("📚 TEST 3: Multiple Story Generation Test")
    print("-" * 50)
    try:
        from core.game_manager import GameManager
        from core.gameplay_controller import GameplayController
        from core.game_engine import Character
        
        game_manager = GameManager()
        await game_manager.initialize()
        
        character = Character(
            name="조사관", age=30, occupation="investigator",
            residence="Arkham", characteristics={
                "strength": 60, "constitution": 70, "power": 65,
                "dexterity": 55, "appearance": 50, "size": 60,
                "intelligence": 75, "education": 80
            }
        )
        
        game_manager.game_engine.character = character
        game_manager.game_engine.current_scene = "library_entrance"
        
        controller = GameplayController(
            game_manager.game_engine, game_manager.agent_manager
        )
        
        test_actions = [
            "책장을 자세히 살펴본다",
            "바닥에 떨어진 종이를 조사한다",
            "창문 밖을 관찰한다"
        ]
        
        ai_responses = 0
        
        for i, action in enumerate(test_actions, 1):
            print(f"   Action {i}: {action}")
            result = await controller.process_player_action(action)
            
            # Check if response is AI-generated (not fallback)
            fallback_messages = [
                "당신의 행동이 상황에 변화를 가져왔습니다.",
                "상황이 조금씩 전개되어 가고 있습니다.",
                "당신은 신중하게 다음 행동을 고려해야 합니다."
            ]
            
            is_ai_response = not any(fallback in result.story_content.text for fallback in fallback_messages)
            
            if is_ai_response:
                ai_responses += 1
                print(f"   ✅ AI Response: {result.story_content.text[:60]}...")
            else:
                print(f"   ❌ Fallback: {result.story_content.text}")
        
        if ai_responses == len(test_actions):
            success_count += 1
            print("✅ ALL ACTIONS GENERATED RICH AI CONTENT!")
        else:
            print(f"❌ Only {ai_responses}/{len(test_actions)} generated AI content")
            
        await game_manager.shutdown()
        
    except Exception as e:
        print(f"❌ Multiple story test failed: {e}")
    
    print()
    
    # TEST 4: Investigation Opportunity Generation
    print("🔍 TEST 4: Investigation Opportunity Generation")
    print("-" * 50)
    try:
        from core.game_manager import GameManager
        from core.gameplay_controller import GameplayController
        from core.game_engine import Character
        
        game_manager = GameManager()
        await game_manager.initialize()
        
        character = Character(
            name="조사관", age=30, occupation="investigator",
            residence="Arkham", characteristics={
                "strength": 60, "constitution": 70, "power": 65,
                "dexterity": 55, "appearance": 50, "size": 60,
                "intelligence": 75, "education": 80
            }
        )
        
        game_manager.game_engine.character = character
        game_manager.game_engine.current_scene = "library_entrance"
        
        controller = GameplayController(
            game_manager.game_engine, game_manager.agent_manager
        )
        
        result = await controller.process_player_action("미스카토닉 대학교 도서관에 들어간다")
        
        print(f"   Generated {len(result.story_content.investigation_opportunities)} investigation opportunities:")
        for i, opportunity in enumerate(result.story_content.investigation_opportunities[:3], 1):
            print(f"   {i}. {opportunity}")
        
        if len(result.story_content.investigation_opportunities) >= 3:
            success_count += 1
            print("✅ INVESTIGATION OPPORTUNITIES GENERATED!")
        else:
            print("❌ Insufficient investigation opportunities")
            
        await game_manager.shutdown()
        
    except Exception as e:
        print(f"❌ Investigation test failed: {e}")
    
    print()
    print("🎯 SYNTHESIS VERIFICATION SUMMARY")
    print("=" * 50)
    print(f"Successful Tests: {success_count}/{total_tests}")
    print()
    
    if success_count == total_tests:
        print("🎉 COMPLETE SUCCESS!")
        print("✅ AI Story Generation System FULLY OPERATIONAL")
        print("✅ No more generic fallback messages")
        print("✅ Rich Korean story content being generated")
        print("✅ Investigation opportunities working")
        print()
        print("🏆 THE ULTRATHINK ANALYSIS WAS SUCCESSFUL!")
        print("🔧 The AI story generation issue has been RESOLVED!")
    elif success_count > 0:
        print("⚠️  Partial Success - Some components working")
        print(f"   Fixed: {success_count} components")
        print(f"   Remaining issues: {total_tests - success_count} components")
    else:
        print("🚨 All tests failed - Further investigation needed")
    
    return success_count == total_tests

if __name__ == "__main__":
    asyncio.run(test_complete_ai_story_fix())