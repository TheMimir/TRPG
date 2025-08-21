#!/usr/bin/env python3
"""Debug import issues"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Attempting to import modules one by one...")

try:
    from core.models import GameState, Investigation, PlayerAction, StoryContent, NarrativeContext, TensionLevel, ActionType, create_basic_narrative_context
    print("✓ core.models imported successfully")
except Exception as e:
    print(f"✗ core.models failed: {e}")

try:
    from core.dice import DiceEngine, skill_check
    print("✓ core.dice imported successfully")
except Exception as e:
    print(f"✗ core.dice failed: {e}")

try:
    from core.game_manager import GameManager
    print("✓ core.game_manager imported successfully")
except Exception as e:
    print(f"✗ core.game_manager failed: {e}")

try:
    from core.game_engine import GameEngine
    print("✓ core.game_engine imported successfully")
except Exception as e:
    print(f"✗ core.game_engine failed: {e}")

try:
    from core.gameplay_controller import GameplayController
    print("✓ core.gameplay_controller imported successfully")
except Exception as e:
    print(f"✗ core.gameplay_controller failed: {e}")

try:
    from ai.ollama_client import OllamaClient
    print("✓ ai.ollama_client imported successfully")
except Exception as e:
    print(f"✗ ai.ollama_client failed: {e}")

try:
    from agents.base_agent import BaseAgent
    print("✓ agents.base_agent imported successfully")
except Exception as e:
    print(f"✗ agents.base_agent failed: {e}")

try:
    from agents.story_agent import StoryAgent
    print("✓ agents.story_agent imported successfully")
except Exception as e:
    print(f"✗ agents.story_agent failed: {e}")

try:
    from ui.gameplay_interface import GameplayInterface
    print("✓ ui.gameplay_interface imported successfully")
except Exception as e:
    print(f"✗ ui.gameplay_interface failed: {e}")

try:
    from utils.localization import LocalizationManager
    print("✓ utils.localization imported successfully")
except Exception as e:
    print(f"✗ utils.localization failed: {e}")

try:
    from data.game_data import GameData
    print("✓ data.game_data imported successfully")
except Exception as e:
    print(f"✗ data.game_data failed: {e}")

try:
    from data.save_manager import SaveManager
    print("✓ data.save_manager imported successfully")
except Exception as e:
    print(f"✗ data.save_manager failed: {e}")

try:
    from data.scenarios.miskatonic_university_library import MiskatonicUniversityLibraryScenario
    print("✓ data.scenarios.miskatonic_university_library imported successfully")
except Exception as e:
    print(f"✗ data.scenarios.miskatonic_university_library failed: {e}")

print("\nImport debugging complete!")