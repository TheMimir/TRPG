#!/usr/bin/env python3
"""
AI Provider Test Script for Cthulhu Solo TRPG

Tests both Ollama and OpenAI providers to ensure they work correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from ai import AIClientFactory, test_all_providers, quick_generate, AIProvider

async def test_ai_providers():
    """Test all available AI providers"""
    print("🧪 AI Provider Test Suite")
    print("=" * 50)
    
    # Test all providers
    print("\n📋 Testing all providers...")
    results = await test_all_providers()
    
    for provider, result in results.items():
        status = "✅" if result.get("success", False) else "❌"
        print(f"{status} {provider.upper()}: {result.get('error', 'Success')}")
    
    # Test specific scenarios
    print("\n🎭 Testing text generation...")
    
    # Test with auto provider
    try:
        response = await quick_generate(
            "Say 'Hello' in Korean.", 
            provider=AIProvider.AUTO
        )
        print(f"✅ Auto provider: {response[:50]}..." if response else "❌ Auto provider failed")
    except Exception as e:
        print(f"❌ Auto provider failed: {e}")
    
    # Test Ollama if available
    try:
        response = await quick_generate(
            "Say 'Hello' in Korean.", 
            provider=AIProvider.OLLAMA
        )
        print(f"✅ Ollama: {response[:50]}..." if response else "❌ Ollama failed")
    except Exception as e:
        print(f"❌ Ollama failed: {e}")
    
    # Test OpenAI if API key is available
    if os.getenv("OPENAI_API_KEY"):
        try:
            response = await quick_generate(
                "Say 'Hello' in Korean.", 
                provider=AIProvider.OPENAI
            )
            print(f"✅ OpenAI: {response[:50]}..." if response else "❌ OpenAI failed")
        except Exception as e:
            print(f"❌ OpenAI failed: {e}")
    else:
        print("⏭️  OpenAI: Skipped (no API key)")
    
    print("\n🎮 Testing game manager integration...")
    
    # Test GameManager with different providers
    try:
        from core.game_manager import GameManager, GameManagerConfig
        
        # Test with auto provider
        config = GameManagerConfig(ai_provider="auto")
        game_manager = GameManager(config)
        
        success = await game_manager.initialize()
        if success:
            stats = game_manager.get_system_statistics()
            ai_stats = stats.get("systems", {}).get("ai_client", {})
            provider = ai_stats.get("provider", "unknown")
            model = ai_stats.get("model", "unknown")
            print(f"✅ GameManager initialized with {provider} ({model})")
        else:
            print("❌ GameManager initialization failed")
        
        await game_manager.shutdown()
        
    except Exception as e:
        print(f"❌ GameManager test failed: {e}")
    
    print("\n✅ AI Provider testing complete!")

def main():
    """Main test function"""
    try:
        asyncio.run(test_ai_providers())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()