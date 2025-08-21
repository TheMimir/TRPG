#!/usr/bin/env python3
"""
Test script for Ultra-think integration in Cthulhu Horror TRPG

Tests the integration of Ultra-think functionality across all agents
and validates the coordination system.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ai.ultra_think import UltraThink, ThinkingMode
from src.ai.ultra_think_coordinator import UltraThinkCoordinator, AnalysisPriority
from src.ai.gm_brain import GMBrain, GameContext, GamePhase, ActionType
from src.ai.ollama_client import OllamaClient

# Import agents
from src.agents.story_agent import StoryAgent
from src.agents.npc_agent import NPCAgent
from src.agents.environment_agent import EnvironmentAgent
from src.agents.rule_agent import RuleAgent
from src.agents.memory_agent import MemoryAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockOllamaClient:
    """Mock Ollama client for testing without actual LLM calls."""
    
    async def generate_response(self, prompt: str, model: str = "llama2", **kwargs):
        """Mock response generation."""
        class MockResponse:
            def __init__(self):
                self.success = True
                self.content = f"Mock response for: {prompt[:50]}..."
                self.processing_time = 0.1
        
        await asyncio.sleep(0.1)  # Simulate processing time
        return MockResponse()

class UltraThinkIntegrationTester:
    """Test Ultra-think integration across the TRPG system."""
    
    def __init__(self):
        self.ollama_client = MockOllamaClient()
        self.ultra_think = UltraThink(self.ollama_client)
        self.coordinator = UltraThinkCoordinator(self.ultra_think)
        
        # Initialize agents with Ultra-think
        self.agents = {
            "story_agent": StoryAgent(self.ollama_client, self.ultra_think, self.coordinator),
            "npc_agent": NPCAgent(self.ollama_client, self.ultra_think, self.coordinator),
            "environment_agent": EnvironmentAgent(self.ollama_client, self.ultra_think, self.coordinator),
            "rule_agent": RuleAgent(self.ollama_client, self.ultra_think, self.coordinator),
            "memory_agent": MemoryAgent(self.ollama_client, self.ultra_think, self.coordinator)
        }
        
        # Initialize GM Brain
        self.gm_brain = GMBrain(
            ollama_client=self.ollama_client,
            agents=self.agents,
            ultra_think=self.ultra_think,
            coordinator=self.coordinator
        )
        
        self.test_results = {}
    
    async def run_all_tests(self):
        """Run all Ultra-think integration tests."""
        
        logger.info("Starting Ultra-think integration tests...")
        
        tests = [
            ("Basic Ultra-think Functionality", self.test_basic_ultra_think),
            ("Coordinator Functionality", self.test_coordinator),
            ("Story Agent Ultra-think", self.test_story_agent_ultra_think),
            ("NPC Agent Ultra-think", self.test_npc_agent_ultra_think),
            ("Environment Agent Ultra-think", self.test_environment_agent_ultra_think),
            ("GMBrain Coordination", self.test_gm_brain_coordination),
            ("Complex Scenario Integration", self.test_complex_scenario),
            ("Performance and Caching", self.test_performance_caching)
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"Running test: {test_name}")
                result = await test_func()
                self.test_results[test_name] = {"status": "PASS", "details": result}
                logger.info(f"✓ {test_name} PASSED")
            except Exception as e:
                self.test_results[test_name] = {"status": "FAIL", "error": str(e)}
                logger.error(f"✗ {test_name} FAILED: {e}")
        
        self.print_test_summary()
    
    async def test_basic_ultra_think(self):
        """Test basic Ultra-think functionality."""
        
        situation_data = {
            "scenario": "Player discovers ancient tome",
            "context": "library investigation",
            "complexity": "high supernatural elements"
        }
        
        result = self.ultra_think.analyze_situation(
            situation_data, 
            ThinkingMode.MYTHOS_INTEGRATION,
            depth=3
        )
        
        assert result is not None, "Ultra-think should return a result"
        assert result.confidence_level > 0, "Result should have confidence level"
        assert len(result.primary_analysis) > 0, "Should have primary analysis"
        
        return f"Analysis confidence: {result.confidence_level:.2f}, length: {len(result.primary_analysis)}"
    
    async def test_coordinator(self):
        """Test Ultra-think coordinator functionality."""
        
        situation_data = {
            "scenario": "Cosmic horror revelation",
            "multiple_agents_needed": True,
            "complexity": "critical situation"
        }
        
        coordinated_result = await self.coordinator.request_coordinated_analysis(
            requesting_agent="test",
            situation_data=situation_data,
            thinking_mode=ThinkingMode.MYTHOS_INTEGRATION,
            priority=AnalysisPriority.HIGH,
            participating_agents=["story_agent", "npc_agent", "environment_agent"]
        )
        
        assert coordinated_result is not None, "Coordinator should return result"
        assert coordinated_result.consensus_confidence > 0, "Should have consensus confidence"
        assert len(coordinated_result.unified_recommendations) > 0, "Should have recommendations"
        
        return f"Consensus confidence: {coordinated_result.consensus_confidence:.2f}, participating agents: {len(coordinated_result.agent_contributions)}"
    
    async def test_story_agent_ultra_think(self):
        """Test Story Agent Ultra-think integration."""
        
        # Test complex scene generation
        input_data = {
            "action_type": "scene_generation",
            "player_action": "Confront the cosmic entity",
            "location": "Ancient temple",
            "tension_level": "maximum",
            "cosmic_revelation": 85
        }
        
        # Access the Story Agent's internal Ultra-think method
        story_agent = self.agents["story_agent"]
        
        # Set up complex conditions to trigger Ultra-think
        story_agent.current_tension = story_agent.TensionLevel.OVERWHELMING
        story_agent.cosmic_revelation_level = 85
        story_agent.sanity_pressure = 0.9
        
        # Test should_use_ultra_think
        should_use = story_agent._should_use_ultra_think(input_data, "scene_generation")
        assert should_use, "Story agent should use Ultra-think for complex scenarios"
        
        # Test thinking mode selection
        thinking_mode = story_agent._select_thinking_mode(input_data, "scene_generation")
        assert thinking_mode is not None, "Should select appropriate thinking mode"
        
        return f"Ultra-think triggered: {should_use}, mode: {thinking_mode.value}"
    
    async def test_npc_agent_ultra_think(self):
        """Test NPC Agent Ultra-think integration."""
        
        # Create a complex NPC first
        npc_creation_data = {
            "action_type": "create_npc",
            "npc_type": "occultist",
            "location": "Forbidden library",
            "purpose": "Complex psychological manipulation",
            "context": "Multiple supernatural elements"
        }
        
        npc_agent = self.agents["npc_agent"]
        
        # Test should_use_ultra_think for complex NPC creation
        should_use = npc_agent._should_use_ultra_think(npc_creation_data, "create_npc")
        assert should_use, "NPC agent should use Ultra-think for complex NPCs"
        
        # Test dialogue complexity
        dialogue_data = {
            "action_type": "dialogue",
            "player_input": "Tell me about the ancient rituals and cosmic truths",
            "npc_id": "test_npc",
            "psychological_complexity": True
        }
        
        should_use_dialogue = npc_agent._should_use_ultra_think(dialogue_data, "dialogue")
        
        return f"NPC creation Ultra-think: {should_use}, dialogue Ultra-think: {should_use_dialogue}"
    
    async def test_environment_agent_ultra_think(self):
        """Test Environment Agent Ultra-think integration."""
        
        env_agent = self.agents["environment_agent"]
        
        # Set up complex environmental conditions
        env_agent.global_horror_level = 0.8
        env_agent.environmental_tension = 0.9
        env_agent.supernatural_saturation = 0.7
        
        input_data = {
            "action_type": "describe_location",
            "location_type": "occult",
            "atmosphere": "complex supernatural manifestations",
            "multiple_sensory_layers": True
        }
        
        should_use = env_agent._should_use_ultra_think(input_data, "describe_location")
        assert should_use, "Environment agent should use Ultra-think for complex atmospheric scenarios"
        
        thinking_mode = env_agent._select_thinking_mode(input_data, "describe_location")
        assert thinking_mode == ThinkingMode.HORROR_ATMOSPHERE, "Should select horror atmosphere mode"
        
        return f"Environmental Ultra-think triggered: {should_use}, mode: {thinking_mode.value}"
    
    async def test_gm_brain_coordination(self):
        """Test GMBrain Ultra-think coordination."""
        
        # Create complex game context
        game_context = GameContext(
            phase=GamePhase.CLIMAX,
            location="Ancient city of R'lyeh",
            characters_present=["investigator"],
            investigation_progress={"main_mystery": 0.9},
            sanity_levels={"investigator": 45},
            known_clues=["tome", "ritual", "star_alignment", "ancient_seal", "cosmic_truth"],
            active_threats=["awakening_entity", "cultists", "reality_distortion"],
            atmosphere_level=0.95,
            mythos_exposure=0.85,
            session_time=4.5,
            player_stress_level=0.8
        )
        
        player_action = "Attempt to perform the counter-ritual to prevent cosmic catastrophe"
        
        # Test Ultra-think necessity evaluation
        needs_ultra_think, thinking_mode, priority = await self.gm_brain.evaluate_ultra_think_necessity(
            player_action, game_context
        )
        
        assert needs_ultra_think, "GMBrain should recognize need for Ultra-think in critical scenarios"
        assert priority == AnalysisPriority.CRITICAL, "Should assign critical priority"
        assert thinking_mode is not None, "Should select appropriate thinking mode"
        
        # Test agent selection
        situation_data = {"context": game_context, "action": player_action}
        selected_agents = self.gm_brain._select_optimal_agents_for_situation(situation_data, thinking_mode)
        
        assert len(selected_agents) > 0, "Should select multiple agents for complex scenario"
        assert "story_agent" in selected_agents, "Should include story agent for narrative coherence"
        
        return f"Ultra-think needed: {needs_ultra_think}, priority: {priority.name}, agents: {len(selected_agents)}, mode: {thinking_mode.value}"
    
    async def test_complex_scenario(self):
        """Test complex multi-agent scenario."""
        
        scenario_data = {
            "scenario": "The investigators discover that their trusted professor has been corrupted by an ancient entity",
            "elements": {
                "story": "Major plot revelation and betrayal",
                "npc": "Professor's psychological transformation",
                "environment": "University becomes eldritch nightmare",
                "rules": "Sanity loss and new supernatural threats",
                "memory": "Recontextualizing past events"
            },
            "complexity": "Maximum - affects all game aspects",
            "thinking_mode": "MYTHOS_INTEGRATION"
        }
        
        # Test coordinated analysis
        coordinated_result = await self.coordinator.request_coordinated_analysis(
            requesting_agent="test_scenario",
            situation_data=scenario_data,
            thinking_mode=ThinkingMode.MYTHOS_INTEGRATION,
            priority=AnalysisPriority.CRITICAL,
            participating_agents=list(self.agents.keys())
        )
        
        assert coordinated_result is not None, "Complex scenario should produce coordinated result"
        assert len(coordinated_result.agent_contributions) >= 3, "Should have multiple agent contributions"
        assert coordinated_result.consensus_confidence > 0.5, "Should have reasonable consensus"
        
        # Test GM Brain application of insights
        base_response = "The professor reveals his transformation..."
        enhanced_response = await self.gm_brain.apply_coordinated_insights(
            coordinated_result, base_response
        )
        
        assert enhanced_response != base_response, "Response should be enhanced"
        assert len(enhanced_response) > len(base_response), "Enhanced response should be more detailed"
        
        return f"Coordinated agents: {len(coordinated_result.agent_contributions)}, consensus: {coordinated_result.consensus_confidence:.2f}, enhanced: {len(enhanced_response) > len(base_response)}"
    
    async def test_performance_caching(self):
        """Test performance and caching features."""
        
        # Test caching by making similar requests
        situation_data = {
            "test": "caching scenario",
            "repeated_elements": True
        }
        
        # First request
        start_time = asyncio.get_event_loop().time()
        result1 = await self.coordinator.request_coordinated_analysis(
            requesting_agent="cache_test_1",
            situation_data=situation_data,
            thinking_mode=ThinkingMode.NARRATIVE_FLOW,
            priority=AnalysisPriority.MEDIUM,
            participating_agents=["story_agent", "memory_agent"]
        )
        first_time = asyncio.get_event_loop().time() - start_time
        
        # Second similar request (should potentially use cache)
        start_time = asyncio.get_event_loop().time()
        result2 = await self.coordinator.request_coordinated_analysis(
            requesting_agent="cache_test_2",
            situation_data=situation_data,
            thinking_mode=ThinkingMode.NARRATIVE_FLOW,
            priority=AnalysisPriority.MEDIUM,
            participating_agents=["story_agent", "memory_agent"]
        )
        second_time = asyncio.get_event_loop().time() - start_time
        
        # Test coordination statistics
        stats = self.coordinator.get_coordination_stats()
        
        assert stats["total_requests"] > 0, "Should track coordination requests"
        assert "agent_participation" in stats, "Should track agent participation"
        
        return f"First request: {first_time:.2f}s, second: {second_time:.2f}s, total requests: {stats['total_requests']}"
    
    def print_test_summary(self):
        """Print summary of all test results."""
        
        print("\n" + "="*80)
        print("ULTRA-THINK INTEGRATION TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
        total = len(self.test_results)
        
        print(f"Overall Result: {passed}/{total} tests passed")
        print()
        
        for test_name, result in self.test_results.items():
            status_symbol = "✓" if result["status"] == "PASS" else "✗"
            print(f"{status_symbol} {test_name}: {result['status']}")
            
            if result["status"] == "PASS" and "details" in result:
                print(f"   Details: {result['details']}")
            elif result["status"] == "FAIL":
                print(f"   Error: {result['error']}")
            print()
        
        # Print coordination statistics
        if hasattr(self, 'coordinator'):
            print("COORDINATION STATISTICS:")
            stats = self.coordinator.get_coordination_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
            print()
        
        print("="*80)
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Ultra-think integration is working correctly.")
        else:
            print(f"⚠️  {total - passed} tests failed. Please review the errors above.")
        
        print("="*80)

async def main():
    """Main test runner."""
    
    print("Cthulhu Horror TRPG - Ultra-think Integration Test Suite")
    print("="*60)
    
    tester = UltraThinkIntegrationTester()
    await tester.run_all_tests()
    
    return tester.test_results

if __name__ == "__main__":
    # Run the tests
    try:
        results = asyncio.run(main())
        
        # Exit with appropriate code
        failed_tests = sum(1 for result in results.values() if result["status"] == "FAIL")
        sys.exit(failed_tests)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        sys.exit(1)