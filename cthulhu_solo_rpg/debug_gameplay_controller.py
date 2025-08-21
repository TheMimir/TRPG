#!/usr/bin/env python3
"""
Debug GameplayController story generation workflow
"""

import asyncio
import sys
import json
import logging
from pathlib import Path

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Setup logging to see detailed information
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def debug_gameplay_controller():
    """Debug the GameplayController _generate_story_response method"""
    print("🔍 DEBUGGING GAMEPLAY CONTROLLER STORY GENERATION")
    print("=" * 70)
    
    try:
        from core.game_manager import GameManager
        from core.gameplay_controller import GameplayController
        from core.game_engine import Character
        
        # Initialize complete system
        print("🚀 Initializing game systems...")
        game_manager = GameManager()
        await game_manager.initialize()
        
        # Create character
        character = Character(name="조사관", age=30, occupation="investigator")
        character.residence = "Arkham"
        
        # Set up game engine
        game_manager.game_engine.character = character
        game_manager.game_engine.current_scene = "library_entrance"
        
        # Create gameplay controller
        controller = GameplayController(
            game_manager.game_engine,
            game_manager.agent_manager,
            scenario=None
        )
        
        print("✅ Systems initialized")
        print(f"   Agent Manager has {len(game_manager.agent_manager.agents)} agents")
        print(f"   Story Agent available: {game_manager.agent_manager.get_agent('story_agent') is not None}")
        
        # Test the _generate_story_response method directly
        print("\n🎯 Testing _generate_story_response directly...")
        
        # Create test action analysis (mimicking what _analyze_player_action would return)
        action_analysis = {
            "original_text": "미스카토닉 대학교 도서관의 오래된 책을 조사한다",
            "action_type": "investigate",
            "target": "책",
            "intent": "미스카토닉 대학교 도서관의 오래된 책을 조사한다",
            "confidence": 0.7,
            "keywords": ["미스카토닉", "도서관", "책", "조사"],
            "scene_id": "library_entrance",
            "turn_number": 1,
            "character_state": character.to_dict()
        }
        
        # Create minimal turn result
        from core.models import StoryContent, TensionLevel
        placeholder_content = StoryContent(
            text="Processing...",
            content_id="test_123",
            scene_id="library_entrance",
            tension_level=TensionLevel.CALM
        )
        
        from core.gameplay_controller import TurnResult
        turn_result = TurnResult(
            turn_number=1,
            player_action="미스카토닉 대학교 도서관의 오래된 책을 조사한다",
            story_content=placeholder_content
        )
        
        # Call _generate_story_response directly with debug output
        print("   Calling controller._generate_story_response()...")
        print(f"   Action text: {action_analysis['original_text']}")
        print(f"   Scene: {game_manager.game_engine.current_scene}")
        
        story_content = await controller._generate_story_response(
            action_analysis, turn_result, {}
        )
        
        print(f"\n📊 STORY CONTENT RESULTS:")
        print(f"   Text length: {len(story_content.text)}")
        print(f"   Text preview: {story_content.text[:120]}...")
        print(f"   Content ID: {story_content.content_id}")
        print(f"   Scene ID: {story_content.scene_id}")
        print(f"   Tension level: {story_content.tension_level}")
        print(f"   Investigation opportunities: {len(story_content.investigation_opportunities)}")
        print(f"   Metadata source: {story_content.metadata.get('source', 'unknown')}")
        
        # Check if it's fallback content
        fallback_indicators = [
            "당신의 행동이 상황에 변화를 가져왔습니다",
            "상황이 조금씩 전개되어 가고 있습니다",
            "당신은 신중하게 다음 행동을 고려해야 합니다"
        ]
        
        is_fallback = any(indicator in story_content.text for indicator in fallback_indicators)
        
        if is_fallback:
            print("❌ FALLBACK CONTENT DETECTED!")
            print(f"   Source: {story_content.metadata.get('source', 'unknown')}")
            
            # Debug why it went to fallback
            story_agent = game_manager.agent_manager.get_agent("story_agent")
            if not story_agent:
                print("   Reason: No story agent available")
            else:
                print("   Story agent is available - issue in response processing")
                
        else:
            print("✅ RICH AI CONTENT GENERATED!")
            
        await game_manager.shutdown()
        return not is_fallback
        
    except Exception as e:
        print(f"💥 Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_gameplay_controller())
    print(f"\n🎯 GameplayController AI Generation Working: {success}")
    
    if success:
        print("✅ The issue is resolved!")
    else:
        print("❌ Issue persists - need deeper investigation")