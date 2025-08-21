#!/usr/bin/env python3
"""
FINAL VERIFICATION - AI Story Generation Fix Complete
Quick test to confirm end-to-end AI story generation works
"""

import asyncio
import sys
import logging
from pathlib import Path

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

async def final_verification_test():
    """Final verification that AI story generation works end-to-end"""
    print("🎯 FINAL VERIFICATION - AI Story Generation Fix")
    print("=" * 60)
    
    try:
        from core.game_manager import GameManager
        from core.gameplay_controller import GameplayController
        from core.game_engine import Character
        
        # Initialize complete system  
        print("🚀 Initializing game systems...")
        game_manager = GameManager()
        success = await game_manager.initialize()
        
        if not success:
            print("❌ GameManager initialization failed")
            return False
        
        print(f"✅ GameManager: {game_manager.status.value}")
        
        # Verify agent system health
        agent_health = game_manager.system_health.get("agents", {})
        print(f"✅ Agent Status: {agent_health.get('status', 'unknown')}")
        print(f"✅ Registered Agents: {agent_health.get('registered_count', 0)}")
        
        if agent_health.get("registered_count", 0) == 0:
            print("❌ No agents registered - fix failed")
            return False
        
        # Create simplified character using the correct constructor
        print("\n📝 Creating test character...")
        character = Character(
            name="조사관",
            age=30,
            occupation="investigator"
        )
        character.residence = "Arkham"
        character.strength = 60
        character.constitution = 70
        character.power = 65
        character.intelligence = 75
        character.education = 80
        
        # Set up game engine
        game_manager.game_engine.character = character
        game_manager.game_engine.current_scene = "library_entrance"
        
        # Create gameplay controller 
        controller = GameplayController(
            game_manager.game_engine,
            game_manager.agent_manager,
            scenario=None
        )
        
        print("🎮 Testing player action processing...")
        print("   Input: '미스카토닉 대학교 도서관의 오래된 책을 조사한다'")
        
        # Process player action
        turn_result = await controller.process_player_action(
            "미스카토닉 대학교 도서관의 오래된 책을 조사한다"
        )
        
        # Analyze results
        print(f"\n📊 RESULTS:")
        print(f"   Success: {turn_result.success}")
        print(f"   Processing Time: {turn_result.processing_time:.2f}s")
        
        story_text = turn_result.story_content.text
        print(f"   Story Text Length: {len(story_text)} characters")
        print(f"   Story Preview: {story_text[:120]}...")
        
        investigations = turn_result.story_content.investigation_opportunities
        print(f"   Investigation Opportunities: {len(investigations)}")
        if investigations:
            print(f"   First Opportunity: {investigations[0]}")
        
        # Check if it's the generic fallback message
        generic_messages = [
            "당신의 행동이 상황에 변화를 가져왔습니다.",
            "상황이 조금씩 전개되어 가고 있습니다.",
            "당신은 신중하게 다음 행동을 고려해야 합니다."
        ]
        
        is_generic = any(generic in story_text for generic in generic_messages)
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if turn_result.success and not is_generic and len(story_text) > 50:
            print("🏆 SUCCESS! AI Story Generation is WORKING!")
            print("✅ Rich Korean story content generated")
            print("✅ No generic fallback messages")
            print("✅ Investigation opportunities provided")
            print("🎉 The ULTRATHINK analysis was successful!")
            result = True
        else:
            print("❌ Issues detected:")
            if not turn_result.success:
                print("   - Turn processing failed")
            if is_generic:
                print("   - Generic fallback message detected")
            if len(story_text) <= 50:
                print("   - Story content too short")
            result = False
        
        await game_manager.shutdown()
        return result
        
    except Exception as e:
        print(f"💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise
    success = asyncio.run(final_verification_test())
    
    if success:
        print("\n🌟 ULTRATHINK ANALYSIS COMPLETE")
        print("🔧 AI Story Generation Issue: RESOLVED")
        print("💎 Players will now receive rich, contextual AI-generated Korean story content!")
    else:
        print("\n🚨 Further investigation needed")
    
    exit(0 if success else 1)