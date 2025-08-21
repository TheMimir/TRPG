"""
Tests for core game components
"""

import unittest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.character import Character
from src.core.dice import DiceRoller
from src.core.rules import RulesEngine

class TestCharacter(unittest.TestCase):
    """Test character creation and management."""
    
    def setUp(self):
        self.character = Character("Test Investigator")
    
    def test_character_creation(self):
        """Test basic character creation."""
        self.assertEqual(self.character.name, "Test Investigator")
        self.assertEqual(self.character.sanity, 99)
    
    def test_sanity_loss(self):
        """Test sanity loss mechanics."""
        initial_sanity = self.character.sanity
        self.character.lose_sanity(10)
        self.assertEqual(self.character.sanity, initial_sanity - 10)

class TestDiceRoller(unittest.TestCase):
    """Test dice rolling mechanics."""
    
    def test_d100_roll(self):
        """Test d100 roll returns value in valid range."""
        roll = DiceRoller.roll_d100()
        self.assertTrue(1 <= roll <= 100)
    
    def test_skill_check(self):
        """Test skill check mechanics."""
        success, roll = DiceRoller.skill_check(50)
        self.assertIsInstance(success, bool)
        self.assertTrue(1 <= roll <= 100)

class TestRulesEngine(unittest.TestCase):
    """Test rules engine functionality."""
    
    def setUp(self):
        self.rules = RulesEngine()
    
    def test_difficulty_levels(self):
        """Test difficulty level definitions."""
        self.assertIn('normal', self.rules.difficulty_levels)
        self.assertEqual(self.rules.difficulty_levels['normal'], 0)

if __name__ == '__main__':
    unittest.main()