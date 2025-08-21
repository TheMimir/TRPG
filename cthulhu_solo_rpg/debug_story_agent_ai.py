#!/usr/bin/env python3
"""
Debug StoryAgent AI generation specifically
"""

import asyncio
import sys
import logging
from pathlib import Path

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def debug_story_agent_ai():
    """Debug the StoryAgent AI generation process"""
    print("🔍 DEBUGGING STORY AGENT AI GENERATION")
    print("=" * 60)
    
    try:
        from agents.story_agent import StoryAgent
        from agents.base_agent import AgentConfig
        from ai.ollama_client import OllamaClient, OllamaConfig
        
        # Create StoryAgent with detailed logging
        print("🤖 Creating StoryAgent with Ollama client...")
        ollama_config = OllamaConfig(
            model="gpt-oss:120b",
            timeout=60.0,
            max_retries=2
        )
        ollama_client = OllamaClient(ollama_config)
        
        agent_config = AgentConfig(
            enable_fallback=True,
            max_retries=2
        )
        
        story_agent = StoryAgent(ollama_client, agent_config)
        await story_agent.initialize()
        
        print("✅ StoryAgent created and initialized")
        
        # Test context that should trigger AI generation
        test_context = {
            "player_action": "미스카토닉 대학교 도서관의 오래된 책을 조사한다",
            "scene_id": "library_entrance",
            "turn_number": 1,
            "character_state": {
                "name": "조사관",
                "current_sanity": 80,
                "sanity_points": 80,
                "occupation": "investigator"
            }
        }
        
        print(f"📝 Testing with context:")
        print(f"   Action: {test_context['player_action']}")
        print(f"   Scene: {test_context['scene_id']}")
        
        # Call process_input with detailed error catching
        print("\n🎯 Calling StoryAgent.process_input()...")
        
        response = await story_agent.process_input(test_context)
        
        print(f"\n📊 RESPONSE ANALYSIS:")
        print(f"   Valid: {response.is_valid}")
        print(f"   Source: {response.source}")
        print(f"   Confidence: {response.confidence}")
        print(f"   Processing time: {response.processing_time:.2f}s")
        
        if response.metadata:
            print(f"   Metadata: {response.metadata}")
        
        print(f"\n📄 CONTENT PREVIEW:")
        print(f"   Content length: {len(response.content)}")
        print(f"   Content: {response.content[:200]}...")
        
        if response.source == "ai":
            print("✅ AI GENERATION SUCCESSFUL!")
            
            # Try to parse the JSON content
            try:
                import json
                content_data = json.loads(response.content)
                print(f"   Story text: {content_data.get('text', 'N/A')[:100]}...")
                print(f"   Investigations: {len(content_data.get('investigation_opportunities', []))}")
            except Exception as parse_error:
                print(f"❌ JSON parsing failed: {parse_error}")
                
        elif response.source == "fallback":
            print("⚠️  USING FALLBACK - AI generation failed")
            if "reason" in response.metadata:
                print(f"   Reason: {response.metadata['reason']}")
        else:
            print(f"❓ Unknown source: {response.source}")
        
        await story_agent.shutdown()
        
        return response.source == "ai"
        
    except Exception as e:
        print(f"💥 Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_story_agent_ai())
    print(f"\n🎯 AI Generation Working: {success}")