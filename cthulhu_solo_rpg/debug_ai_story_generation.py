#!/usr/bin/env python3
"""
ULTRATHINK ANALYSIS - Debug AI Story Generation Issue
Critical investigation to determine exactly what's broken and how to fix it.
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

async def debug_complete_ai_story_system():
    """
    LAYER 4 - CRITICAL EVALUATION
    Comprehensive analysis of the AI story generation system.
    """
    print("🔍 ULTRATHINK LAYER 4 - CRITICAL EVALUATION")
    print("=" * 70)
    print("Analyzing AI Story Generation System...")
    print()
    
    results = {
        "ollama_connection": False,
        "story_agent_creation": False,
        "ai_generation": False,
        "agent_registration": False,
        "full_workflow": False,
        "errors": []
    }
    
    # TEST 1: Ollama Connection
    print("📡 TEST 1: Ollama Connection")
    print("-" * 30)
    try:
        from ai.ollama_client import OllamaClient, OllamaConfig
        
        config = OllamaConfig(
            base_url="http://localhost:11434",
            model="gpt-oss:120b",
            timeout=30.0
        )
        
        ollama_client = OllamaClient(config)
        await ollama_client.connect()
        
        # Test health check
        health = await ollama_client.health_check()
        if health:
            print("✅ Ollama service is available")
            results["ollama_connection"] = True
        else:
            print("❌ Ollama service health check failed")
            results["errors"].append("Ollama health check failed")
            
        await ollama_client.close()
        
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        results["errors"].append(f"Ollama connection: {e}")
    
    print()
    
    # TEST 2: StoryAgent Creation and Basic Function
    print("🤖 TEST 2: StoryAgent Creation")
    print("-" * 30)
    try:
        from agents.story_agent import StoryAgent
        from agents.base_agent import AgentConfig
        from ai.ollama_client import OllamaClient, OllamaConfig
        
        # Create StoryAgent with Ollama client
        ollama_config = OllamaConfig()
        ollama_client = OllamaClient(ollama_config)
        await ollama_client.connect()
        
        agent_config = AgentConfig()
        story_agent = StoryAgent(ollama_client, agent_config)
        
        await story_agent.initialize()
        
        print("✅ StoryAgent created successfully")
        print(f"   Agent name: {story_agent.agent_name}")
        print(f"   Memory count: {len(story_agent.memory)}")
        
        results["story_agent_creation"] = True
        
        # Test basic input processing
        print("\n🧪 Testing StoryAgent.process_input()")
        test_context = {
            "player_action": "도서관에서 오래된 책을 조사한다",
            "scene_id": "library_entrance", 
            "turn_number": 1,
            "character_state": {
                "name": "조사관",
                "current_sanity": 80,
                "sanity_points": 80
            }
        }
        
        # Call the actual method that GameplayController uses
        response = await story_agent.process_input(test_context)
        
        print(f"📄 Response received:")
        print(f"   Valid: {response.is_valid}")
        print(f"   Source: {response.source}")
        print(f"   Confidence: {response.confidence}")
        print(f"   Content preview: {response.content[:100]}...")
        
        if response.is_valid and "text" in response.content:
            results["ai_generation"] = True
            print("✅ AI story generation successful!")
        else:
            print("❌ AI story generation failed")
            results["errors"].append("AI generation produced invalid response")
            
        await ollama_client.close()
        
    except Exception as e:
        print(f"❌ StoryAgent test failed: {e}")
        results["errors"].append(f"StoryAgent test: {e}")
    
    print()
    
    # TEST 3: Agent Registration Process 
    print("📋 TEST 3: Proper Agent Registration")
    print("-" * 30)
    try:
        from agents.base_agent import AgentManager
        from agents.story_agent import StoryAgent
        from ai.ollama_client import OllamaClient, OllamaConfig
        
        # Create proper agent manager
        ollama_config = OllamaConfig() 
        ollama_client = OllamaClient(ollama_config)
        
        agent_manager = AgentManager(ollama_client)
        await agent_manager.initialize()
        
        # Create and register story agent
        story_agent = StoryAgent()
        agent_manager.register_agent(story_agent)
        await agent_manager.initialize_all_agents()
        
        # Test retrieval
        retrieved_agent = agent_manager.get_agent("story_agent")
        
        if retrieved_agent and isinstance(retrieved_agent, StoryAgent):
            print("✅ Agent registration and retrieval successful")
            print(f"   Registered agents: {len(agent_manager.agents)}")
            print(f"   Retrieved agent: {retrieved_agent.agent_name}")
            results["agent_registration"] = True
        else:
            print("❌ Agent registration failed")
            results["errors"].append("Agent registration/retrieval failed")
            
        await agent_manager.shutdown()
        
    except Exception as e:
        print(f"❌ Agent registration test failed: {e}")
        results["errors"].append(f"Agent registration: {e}")
    
    print()
    
    # TEST 4: Complete Workflow Simulation
    print("🎮 TEST 4: Complete Workflow Simulation")
    print("-" * 30)
    try:
        from core.game_manager import GameManager
        
        # This will test the current (broken) GameManager
        game_manager = GameManager()
        success = await game_manager.initialize()
        
        if success:
            print(f"✅ GameManager initialized successfully")
            print(f"   Status: {game_manager.status.value}")
            
            # Check agent manager
            if game_manager.agent_manager:
                agent_count = len(game_manager.agent_manager.agents)
                print(f"   Registered agents: {agent_count}")
                
                if agent_count == 0:
                    print("⚠️  No agents registered (this is the problem!)")
                    results["errors"].append("GameManager registered 0 agents")
                else:
                    results["full_workflow"] = True
            else:
                print("❌ No agent manager in GameManager")
                results["errors"].append("No agent manager in GameManager")
        else:
            print("❌ GameManager initialization failed")
            results["errors"].append("GameManager initialization failed")
            
        await game_manager.shutdown()
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        results["errors"].append(f"Workflow test: {e}")
    
    print()
    print("🎯 CRITICAL EVALUATION SUMMARY")
    print("=" * 50)
    
    print("System Component Status:")
    for component, status in results.items():
        if component != "errors":
            emoji = "✅" if status else "❌"
            print(f"   {emoji} {component.replace('_', ' ').title()}: {status}")
    
    print(f"\nErrors Found ({len(results['errors'])}):")
    for i, error in enumerate(results['errors'], 1):
        print(f"   {i}. {error}")
    
    print("\n🏁 CONCLUSION:")
    if results["ollama_connection"] and results["story_agent_creation"] and results["ai_generation"]:
        print("✅ CORE AI FUNCTIONALITY WORKS!")
        print("❌ PROBLEM: GameManager doesn't register agents")
        print("💡 SOLUTION: Fix GameManager._register_core_agents()")
    else:
        print("❌ DEEPER ISSUES FOUND - Multiple system failures")
    
    return results

if __name__ == "__main__":
    asyncio.run(debug_complete_ai_story_system())