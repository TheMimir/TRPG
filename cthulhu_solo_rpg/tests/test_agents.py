"""
Tests for AI agent system
"""

import unittest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.agents.base_agent import BaseAgent
from src.agents.story_agent import StoryAgent
from src.agents.npc_agent import NPCAgent

class TestBaseAgent(unittest.TestCase):
    """Test base agent functionality."""
    
    def setUp(self):
        self.agent = BaseAgent("Test Agent", "test_role")
    
    def test_agent_creation(self):
        """Test basic agent creation."""
        self.assertEqual(self.agent.name, "Test Agent")
        self.assertEqual(self.agent.role, "test_role")
        self.assertEqual(len(self.agent.memory), 0)
    
    def test_memory_management(self):
        """Test agent memory functionality."""
        event = {"type": "test", "data": "test_data"}
        self.agent.update_memory(event)
        self.assertEqual(len(self.agent.memory), 1)
        
        self.agent.clear_memory()
        self.assertEqual(len(self.agent.memory), 0)

class TestStoryAgent(unittest.TestCase):
    """Test story agent functionality."""
    
    def setUp(self):
        self.story_agent = StoryAgent()
    
    def test_story_agent_creation(self):
        """Test story agent initialization."""
        self.assertEqual(self.story_agent.name, "Story Agent")
        self.assertEqual(self.story_agent.tension_level, 0)
    
    def test_tension_adjustment(self):
        """Test tension level adjustment."""
        self.story_agent.adjust_tension(5)
        self.assertEqual(self.story_agent.tension_level, 5)
        
        self.story_agent.adjust_tension(-10)
        self.assertEqual(self.story_agent.tension_level, 0)  # Clamped to 0

class TestNPCAgent(unittest.TestCase):
    """Test NPC agent functionality."""
    
    def setUp(self):
        self.npc_agent = NPCAgent()
    
    def test_npc_agent_creation(self):
        """Test NPC agent initialization."""
        self.assertEqual(self.npc_agent.name, "NPC Agent")
        self.assertEqual(len(self.npc_agent.active_npcs), 0)

if __name__ == '__main__':
    unittest.main()