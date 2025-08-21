#!/usr/bin/env python3
"""
Example Ultra-think Scenario for Cthulhu Horror TRPG

Demonstrates how Ultra-think is used in complex gaming scenarios
across multiple agents for enhanced storytelling.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ai.ultra_think import UltraThink, ThinkingMode
from src.ai.ultra_think_coordinator import UltraThinkCoordinator, AnalysisPriority
from src.ai.gm_brain import GMBrain, GameContext, GamePhase
from src.ai.ollama_client import OllamaClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockOllamaClient:
    """Mock Ollama client that generates realistic responses for demo."""
    
    async def generate_response(self, prompt: str, model: str = "llama2", **kwargs):
        """Generate mock responses based on prompt content."""
        
        class MockResponse:
            def __init__(self, content):
                self.success = True
                self.content = content
                self.processing_time = 0.2
        
        await asyncio.sleep(0.2)  # Simulate processing
        
        # Generate contextual responses based on prompt keywords
        if "mythos" in prompt.lower() or "cosmic" in prompt.lower():
            content = """The ancient knowledge revealed through this analysis suggests multiple layers of cosmic horror:
            
            The protagonist's investigation has led them to a threshold moment where humanity's insignificance 
            becomes terrifyingly apparent. The entity they face represents forces beyond mortal comprehension,
            existing in dimensions where human concepts of time and space lose all meaning.
            
            Key insights:
            - This revelation will permanently alter the character's worldview
            - Sanity loss should reflect not just fear, but existential dissolution
            - The knowledge gained cannot be unlearned or forgotten
            - Reality itself becomes suspect after this encounter
            
            Recommended approach: Layer the horror gradually, allowing the full implications to dawn slowly
            rather than delivering them as exposition."""
            
        elif "character" in prompt.lower() or "psychology" in prompt.lower():
            content = """Character psychology analysis reveals complex emotional and mental dynamics:
            
            The character stands at a psychological crossroads where their fundamental beliefs about reality
            are being challenged. Their training and education become both an asset and a liability - 
            providing analytical tools while making acceptance of the impossible more difficult.
            
            Psychological factors:
            - Cognitive dissonance between evidence and worldview
            - Professional pride conflicting with growing terror
            - Isolation from normal human support systems
            - Progressive erosion of mental defenses
            
            Character development opportunities:
            - Moments of vulnerability showing human side
            - Desperate attempts to rationalize the irrational
            - Small acts of courage in the face of cosmic terror"""
            
        elif "atmosphere" in prompt.lower() or "environment" in prompt.lower():
            content = """Environmental atmosphere analysis for maximum horror impact:
            
            The setting should reflect the growing wrongness of the situation through subtle environmental cues
            that accumulate to create an overwhelming sense of dread and unnaturalness.
            
            Atmospheric elements:
            - Light sources that cast impossible shadows
            - Sounds that don't quite match their sources
            - Air that feels thick and oppressive
            - Geometric patterns that hurt to perceive directly
            - Temperature fluctuations without apparent cause
            
            Sensory details:
            - The metallic taste of fear in the air
            - Whispers in languages that predate humanity
            - Visual distortions at the edge of perception
            - Textures that feel wrong under touch"""
            
        else:
            content = f"""Analysis of the presented situation reveals multiple considerations requiring careful attention.
            
            The complexity of this scenario demands a nuanced approach that balances multiple factors:
            player agency, narrative coherence, horror pacing, and mechanical fairness.
            
            Key recommendations:
            - Maintain tension while providing clear player options
            - Ensure consequences feel earned rather than arbitrary
            - Layer information to build understanding gradually
            - Preserve mystery while advancing the plot
            
            This situation represents a critical juncture that will significantly impact the ongoing narrative."""
        
        return MockResponse(content)

class UltraThinkScenarioDemo:
    """Demonstrates Ultra-think in action with a complete horror scenario."""
    
    def __init__(self):
        self.ollama_client = MockOllamaClient()
        self.ultra_think = UltraThink(self.ollama_client)
        self.coordinator = UltraThinkCoordinator(self.ultra_think)
        
        print("🧠 Ultra-think System Initialized")
        print("🎭 Coordination System Active")
        print("📚 Cthulhu Horror Context Loaded")
        print()

    async def run_scenario_demo(self):
        """Run complete scenario demonstration."""
        
        print("="*80)
        print("CTHULHU HORROR TRPG - ULTRA-THINK SCENARIO DEMONSTRATION")
        print("="*80)
        print()
        
        print("📖 SCENARIO: 'The Whispering Gallery'")
        print("-" * 40)
        print("The investigators have discovered that the university's new acoustic research lab")
        print("has been recording sounds that shouldn't exist - whispers in pre-human languages")
        print("that seem to be coming from the building's structure itself.")
        print()
        
        print("🎯 PLAYER ACTION:")
        print("'I want to analyze the recordings using the latest audio equipment while")
        print("cross-referencing the whispered words with ancient linguistic databases.'")
        print()
        
        # Scenario 1: Initial Analysis
        await self.demonstrate_initial_analysis()
        
        # Scenario 2: Coordinated Multi-Agent Analysis
        await self.demonstrate_coordinated_analysis()
        
        # Scenario 3: Critical Decision Point
        await self.demonstrate_critical_decision()
        
        print("="*80)
        print("DEMONSTRATION COMPLETE")
        print("="*80)
        print()
        print("This demonstration shows how Ultra-think enhances complex horror scenarios by:")
        print("• Providing deep analysis of multi-layered situations")
        print("• Coordinating insights across specialized AI agents")
        print("• Maintaining horror atmosphere while ensuring narrative coherence")
        print("• Balancing player agency with cosmic horror themes")
        print()

    async def demonstrate_initial_analysis(self):
        """Demonstrate initial Ultra-think analysis."""
        
        print("🔍 PHASE 1: INITIAL ULTRA-THINK ANALYSIS")
        print("-" * 50)
        
        situation_data = {
            "player_action": "Analyze recordings and cross-reference with linguistic databases",
            "location": "University acoustic research lab",
            "context": {
                "investigation_progress": 0.6,
                "sanity_level": 65,
                "known_clues": ["strange_recordings", "architectural_anomalies", "staff_disappearances"],
                "atmospheric_tension": 0.7,
                "mythos_exposure": 0.4
            },
            "complexity_factors": [
                "Ancient linguistic elements",
                "Supernatural audio phenomena", 
                "Academic setting with hidden horrors",
                "Progressive revelation of cosmic truth"
            ]
        }
        
        print("Initiating Ultra-think analysis...")
        print("Mode: MYTHOS_INTEGRATION")
        print("Depth: 4 (Deep analysis for complex revelation)")
        print()
        
        # Perform analysis
        result = self.ultra_think.analyze_situation(
            situation_data,
            ThinkingMode.MYTHOS_INTEGRATION,
            depth=4
        )
        
        print("📋 ULTRA-THINK ANALYSIS COMPLETE")
        print(f"Confidence Level: {result.confidence_level:.1%}")
        print(f"Processing Depth: {result.processing_depth}")
        print()
        
        print("🎯 PRIMARY ANALYSIS:")
        print(self._format_text(result.primary_analysis))
        print()
        
        print("🔀 ALTERNATIVE PERSPECTIVES:")
        for i, perspective in enumerate(result.alternative_perspectives[:2], 1):
            print(f"{i}. {self._format_text(perspective, indent=3)}")
        print()
        
        print("⚡ RECOMMENDED ACTIONS:")
        for i, action in enumerate(result.recommended_actions[:3], 1):
            print(f"{i}. {action}")
        print()

    async def demonstrate_coordinated_analysis(self):
        """Demonstrate coordinated multi-agent analysis."""
        
        print("🤝 PHASE 2: COORDINATED MULTI-AGENT ANALYSIS")
        print("-" * 50)
        
        situation_data = {
            "scenario": "Linguistic analysis reveals Pre-Sumerian origins",
            "revelation": "The whispers are not recordings but active communications",
            "implications": {
                "story": "Major plot advancement - building is alive/conscious",
                "character": "Sanity challenge from impossible knowledge",
                "environment": "Lab becomes increasingly hostile",
                "rules": "New supernatural mechanics needed",
                "memory": "Recontextualizes all previous campus encounters"
            },
            "coordination_required": True,
            "priority": "HIGH"
        }
        
        print("Requesting coordinated analysis across specialized agents...")
        print("Participating Agents: Story, NPC, Environment, Rule, Memory")
        print("Thinking Mode: MYTHOS_INTEGRATION")
        print("Priority: HIGH")
        print()
        
        # Simulate coordinated analysis
        coordinated_result = await self.coordinator.request_coordinated_analysis(
            requesting_agent="gm_brain",
            situation_data=situation_data,
            thinking_mode=ThinkingMode.MYTHOS_INTEGRATION,
            priority=AnalysisPriority.HIGH,
            participating_agents=["story_agent", "npc_agent", "environment_agent", "rule_agent", "memory_agent"]
        )
        
        print("🎯 COORDINATED SYNTHESIS:")
        print(self._format_text(coordinated_result.synthesis))
        print()
        
        print("⭐ PRIORITY INSIGHTS:")
        for insight in coordinated_result.priority_insights:
            print(f"• {insight}")
        print()
        
        print("📋 UNIFIED RECOMMENDATIONS:")
        for i, rec in enumerate(coordinated_result.unified_recommendations, 1):
            print(f"{i}. {rec}")
        print()
        
        print("📊 COORDINATION METADATA:")
        print(f"Consensus Confidence: {coordinated_result.consensus_confidence:.1%}")
        print(f"Contributing Agents: {len(coordinated_result.agent_contributions)}")
        print(f"Processing Time: {coordinated_result.processing_time:.2f}s")
        print()

    async def demonstrate_critical_decision(self):
        """Demonstrate Ultra-think for critical decision points."""
        
        print("⚠️  PHASE 3: CRITICAL DECISION POINT")
        print("-" * 50)
        
        print("NARRATIVE DEVELOPMENT:")
        print("The analysis reveals that the building itself is a massive acoustic resonator,")
        print("designed to amplify and transmit messages across dimensional boundaries.")
        print("The 'whispers' are actually communications from entities trapped between")
        print("dimensions, and the research has been slowly weakening the barriers.")
        print()
        
        print("PLAYER DECISION:")
        print("The player must choose: Shut down the equipment immediately (safe but loses")
        print("valuable information) or continue the analysis to learn more (dangerous but")
        print("potentially crucial for stopping a larger threat).")
        print()
        
        critical_situation = {
            "decision_point": "Continue dangerous research vs. immediate safety",
            "stakes": "Individual sanity vs. potential cosmic catastrophe",
            "time_pressure": "Entity breakthrough imminent",
            "information_state": "Partial knowledge is most dangerous",
            "character_factors": {
                "sanity": 58,
                "academic_curiosity": "high", 
                "fear_level": "mounting",
                "sense_of_responsibility": "strong"
            },
            "environmental_factors": {
                "building_instability": "increasing",
                "dimensional_barriers": "weakening",
                "supernatural_manifestations": "escalating"
            }
        }
        
        print("Analyzing critical decision with CONSEQUENCE_ANALYSIS mode...")
        print()
        
        consequence_result = self.ultra_think.analyze_situation(
            critical_situation,
            ThinkingMode.CONSEQUENCE_ANALYSIS,
            depth=5
        )
        
        print("🎯 CONSEQUENCE ANALYSIS:")
        print(self._format_text(consequence_result.primary_analysis))
        print()
        
        print("⚖️  DECISION OUTCOMES:")
        for i, outcome in enumerate(consequence_result.alternative_perspectives, 1):
            print(f"Option {i}: {self._format_text(outcome, indent=2)}")
        print()
        
        print("🎲 GM GUIDANCE:")
        for guidance in consequence_result.recommended_actions[:3]:
            print(f"• {guidance}")
        print()

    def _format_text(self, text: str, width: int = 70, indent: int = 0) -> str:
        """Format text for better display."""
        
        import textwrap
        
        # Clean up the text
        text = text.strip()
        
        # Wrap the text
        wrapped = textwrap.fill(text, width=width-indent)
        
        # Add indentation if specified
        if indent > 0:
            indent_str = " " * indent
            wrapped = "\n".join(indent_str + line for line in wrapped.split("\n"))
        
        return wrapped

async def main():
    """Main demonstration runner."""
    
    print("🎮 Cthulhu Horror TRPG - Ultra-think Integration Demo")
    print("🧠 Demonstrating AI-enhanced horror storytelling")
    print()
    
    demo = UltraThinkScenarioDemo()
    await demo.run_scenario_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error during demo: {e}")
        import traceback
        traceback.print_exc()