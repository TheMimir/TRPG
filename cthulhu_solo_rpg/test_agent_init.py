#!/usr/bin/env python3
"""
Simple test script to verify agent initialization
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_agent_imports():
    """Test that all agent classes can be imported."""
    print("Testing agent imports...")
    
    try:
        from src.agents.base_agent import BaseAgent
        print("✓ BaseAgent imported")
        
        from src.agents.story_agent import StoryAgent
        print("✓ StoryAgent imported")
        
        from src.agents.npc_agent import NPCAgent
        print("✓ NPCAgent imported")
        
        from src.agents.environment_agent import EnvironmentAgent
        print("✓ EnvironmentAgent imported")
        
        from src.agents.rule_agent import RuleAgent
        print("✓ RuleAgent imported")
        
        from src.agents.memory_agent import MemoryAgent
        print("✓ MemoryAgent imported")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_mock_client():
    """Test mock AI client."""
    print("\nTesting mock AI client...")
    
    try:
        from src.ai.mock_ollama_client import MockOllamaClient
        print("✓ MockOllamaClient imported")
        
        client = MockOllamaClient()
        print("✓ MockOllamaClient created")
        
        # Test basic functionality
        assert client.is_available(), "Mock client should always be available"
        print("✓ is_available() works")
        
        models = client.list_models()
        assert len(models) > 0, "Should return some models"
        print(f"✓ list_models() returned {len(models)} models")
        
        # Test generate
        response = client.generate("Test prompt", system_prompt="You are a test assistant")
        assert response.content, "Should generate content"
        print(f"✓ generate() returned {len(response.content)} characters")
        
        return True
        
    except Exception as e:
        print(f"✗ Mock client test failed: {e}")
        return False

def test_agent_creation():
    """Test creating agents with mock client."""
    print("\nTesting agent creation...")
    
    try:
        from src.ai.mock_ollama_client import MockOllamaClient
        from src.agents.story_agent import StoryAgent
        from src.agents.npc_agent import NPCAgent
        from src.agents.environment_agent import EnvironmentAgent
        from src.agents.rule_agent import RuleAgent
        from src.agents.memory_agent import MemoryAgent
        
        # Create mock client
        mock_client = MockOllamaClient()
        print("✓ Mock client created")
        
        # Test creating each agent
        agents = {}
        
        agents['story'] = StoryAgent(ollama_client=mock_client)
        print("✓ StoryAgent created")
        
        agents['npc'] = NPCAgent(ollama_client=mock_client)
        print("✓ NPCAgent created")
        
        agents['environment'] = EnvironmentAgent(ollama_client=mock_client)
        print("✓ EnvironmentAgent created")
        
        agents['rule'] = RuleAgent(ollama_client=mock_client)
        print("✓ RuleAgent created")
        
        agents['memory'] = MemoryAgent(ollama_client=mock_client)
        print("✓ MemoryAgent created")
        
        # Check horror_sensitivity attribute
        print("\nChecking horror_sensitivity attribute:")
        for name, agent in agents.items():
            if hasattr(agent, 'horror_sensitivity'):
                print(f"✓ {name} agent has horror_sensitivity = {agent.horror_sensitivity}")
            else:
                print(f"✗ {name} agent missing horror_sensitivity")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Agent Initialization Test")
    print("=" * 50)
    
    tests = [
        test_agent_imports,
        test_mock_client,
        test_agent_creation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Agent initialization is working.")
        return True
    else:
        print("❌ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)