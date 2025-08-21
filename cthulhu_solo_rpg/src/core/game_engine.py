"""
Game Engine for Cthulhu Solo TRPG System

Handles core game mechanics including:
- Character creation and management
- Skill checks and dice rolling
- Sanity and health tracking
- Investigation mechanics
- Combat system
- Experience and character progression
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import random

from .models import (
    TensionLevel, ActionType, NarrativeContext, PlayerAction, 
    GameState, Investigation, StoryContent
)
from .dice import DiceEngine, SuccessLevel, DiceResult


logger = logging.getLogger(__name__)


class CharacterCondition(Enum):
    """Character health conditions"""
    HEALTHY = "healthy"
    MINOR_INJURY = "minor_injury"
    MAJOR_INJURY = "major_injury"
    DYING = "dying"
    UNCONSCIOUS = "unconscious"
    DEAD = "dead"
    INDEFINITE_INSANITY = "indefinite_insanity"
    TEMPORARY_INSANITY = "temporary_insanity"


class SkillCategory(Enum):
    """Skill categories for organization"""
    INTERPERSONAL = "interpersonal"
    MENTAL = "mental"
    PHYSICAL = "physical"
    TECHNICAL = "technical"
    COMBAT = "combat"
    SURVIVAL = "survival"


@dataclass
class Character:
    """Represents a player character with all statistics and progression"""
    
    # Basic Information
    name: str
    age: int
    occupation: str
    residence: str = ""
    birthplace: str = ""
    
    # Core Characteristics (Call of Cthulhu 7th Edition)
    strength: int = 50
    constitution: int = 50
    power: int = 50
    dexterity: int = 50
    appearance: int = 50
    size: int = 50
    intelligence: int = 50
    education: int = 50
    
    # Derived Attributes
    hit_points: int = 0
    magic_points: int = 0
    sanity_points: int = 0
    luck_points: int = 0
    
    # Current Status
    current_hp: int = 0
    current_mp: int = 0
    current_sanity: int = 0
    current_luck: int = 0
    
    # Skills (starting values based on occupation)
    skills: Dict[str, int] = field(default_factory=dict)
    
    # Equipment and Possessions
    equipment: List[str] = field(default_factory=list)
    money: int = 0
    
    # Status Effects
    conditions: List[CharacterCondition] = field(default_factory=list)
    temporary_modifiers: Dict[str, int] = field(default_factory=dict)
    
    # Character Development
    skill_points: int = 0
    experience_points: int = 0
    
    # Background and personality
    backstory: str = ""
    motivations: List[str] = field(default_factory=list)
    fears: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate derived attributes after initialization"""
        self.calculate_derived_attributes()
    
    def calculate_derived_attributes(self):
        """Calculate hit points, magic points, sanity, etc."""
        self.hit_points = (self.constitution + self.size) // 10
        self.current_hp = self.hit_points
        
        self.magic_points = self.power // 5
        self.current_mp = self.magic_points
        
        self.sanity_points = self.power
        self.current_sanity = self.sanity_points
        
        self.luck_points = random.randint(15, 90)  # 3d6 * 5
        self.current_luck = self.luck_points
    
    def get_characteristic_modifier(self, characteristic: str) -> int:
        """Get modifier for characteristic-based rolls"""
        value = getattr(self, characteristic.lower(), 50)
        if value >= 90:
            return 20
        elif value >= 75:
            return 10
        elif value >= 25:
            return 0
        elif value >= 15:
            return -10
        else:
            return -20
    
    def is_incapacitated(self) -> bool:
        """Check if character is incapacitated"""
        return (CharacterCondition.UNCONSCIOUS in self.conditions or
                CharacterCondition.DYING in self.conditions or
                CharacterCondition.DEAD in self.conditions or
                CharacterCondition.INDEFINITE_INSANITY in self.conditions)
    
    def can_act(self) -> bool:
        """Check if character can take actions"""
        return not self.is_incapacitated()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary for saving"""
        return {
            "name": self.name,
            "age": self.age,
            "occupation": self.occupation,
            "residence": self.residence,
            "birthplace": self.birthplace,
            "strength": self.strength,
            "constitution": self.constitution,
            "power": self.power,
            "dexterity": self.dexterity,
            "appearance": self.appearance,
            "size": self.size,
            "intelligence": self.intelligence,
            "education": self.education,
            "hit_points": self.hit_points,
            "magic_points": self.magic_points,
            "sanity_points": self.sanity_points,
            "luck_points": self.luck_points,
            "current_hp": self.current_hp,
            "current_mp": self.current_mp,
            "current_sanity": self.current_sanity,
            "current_luck": self.current_luck,
            "skills": self.skills,
            "equipment": self.equipment,
            "money": self.money,
            "conditions": [c.value for c in self.conditions],
            "temporary_modifiers": self.temporary_modifiers,
            "skill_points": self.skill_points,
            "experience_points": self.experience_points,
            "backstory": self.backstory,
            "motivations": self.motivations,
            "fears": self.fears,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Create character from dictionary"""
        char = cls(
            name=data["name"],
            age=data["age"],
            occupation=data["occupation"],
            residence=data.get("residence", ""),
            birthplace=data.get("birthplace", ""),
            strength=data.get("strength", 50),
            constitution=data.get("constitution", 50),
            power=data.get("power", 50),
            dexterity=data.get("dexterity", 50),
            appearance=data.get("appearance", 50),
            size=data.get("size", 50),
            intelligence=data.get("intelligence", 50),
            education=data.get("education", 50),
        )
        
        # Restore calculated values
        char.hit_points = data.get("hit_points", char.hit_points)
        char.magic_points = data.get("magic_points", char.magic_points)
        char.sanity_points = data.get("sanity_points", char.sanity_points)
        char.luck_points = data.get("luck_points", char.luck_points)
        
        # Restore current values
        char.current_hp = data.get("current_hp", char.current_hp)
        char.current_mp = data.get("current_mp", char.current_mp)
        char.current_sanity = data.get("current_sanity", char.current_sanity)
        char.current_luck = data.get("current_luck", char.current_luck)
        
        # Restore other attributes
        char.skills = data.get("skills", {})
        char.equipment = data.get("equipment", [])
        char.money = data.get("money", 0)
        char.conditions = [CharacterCondition(c) for c in data.get("conditions", [])]
        char.temporary_modifiers = data.get("temporary_modifiers", {})
        char.skill_points = data.get("skill_points", 0)
        char.experience_points = data.get("experience_points", 0)
        char.backstory = data.get("backstory", "")
        char.motivations = data.get("motivations", [])
        char.fears = data.get("fears", [])
        
        return char


class GameEngine:
    """
    Core game engine for the Cthulhu Solo TRPG system.
    
    Handles all game mechanics including dice rolling, skill checks,
    character management, and game state tracking.
    """
    
    def __init__(self):
        """Initialize the game engine"""
        self.dice_engine = DiceEngine()
        self.character: Optional[Character] = None
        self.current_scene: str = ""
        self.turn_number: int = 0
        self.game_flags: Dict[str, Any] = {}
        self.event_history: List[Dict[str, Any]] = []
        
        # Game rules and configurations
        self.skill_definitions = self._load_skill_definitions()
        self.occupation_skills = self._load_occupation_skills()
        self.sanity_loss_table = self._load_sanity_loss_table()
        
        logger.info("GameEngine initialized")
    
    def _load_skill_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Load skill definitions and base values"""
        return {
            # Interpersonal Skills
            "charm": {"base": 15, "category": SkillCategory.INTERPERSONAL},
            "fast_talk": {"base": 5, "category": SkillCategory.INTERPERSONAL},
            "intimidate": {"base": 15, "category": SkillCategory.INTERPERSONAL},
            "persuade": {"base": 10, "category": SkillCategory.INTERPERSONAL},
            "psychology": {"base": 10, "category": SkillCategory.MENTAL},
            
            # Mental Skills
            "accounting": {"base": 5, "category": SkillCategory.MENTAL},
            "anthropology": {"base": 1, "category": SkillCategory.MENTAL},
            "archaeology": {"base": 1, "category": SkillCategory.MENTAL},
            "history": {"base": 5, "category": SkillCategory.MENTAL},
            "library_use": {"base": 20, "category": SkillCategory.MENTAL},
            "listen": {"base": 20, "category": SkillCategory.MENTAL},
            "occult": {"base": 5, "category": SkillCategory.MENTAL},
            "science": {"base": 1, "category": SkillCategory.MENTAL},
            "spot_hidden": {"base": 25, "category": SkillCategory.MENTAL},
            
            # Physical Skills
            "climb": {"base": 20, "category": SkillCategory.PHYSICAL},
            "dodge": {"base": "dex/2", "category": SkillCategory.PHYSICAL},
            "drive_auto": {"base": 20, "category": SkillCategory.PHYSICAL},
            "jump": {"base": 20, "category": SkillCategory.PHYSICAL},
            "ride": {"base": 5, "category": SkillCategory.PHYSICAL},
            "stealth": {"base": 20, "category": SkillCategory.PHYSICAL},
            "swim": {"base": 20, "category": SkillCategory.PHYSICAL},
            "throw": {"base": 20, "category": SkillCategory.PHYSICAL},
            
            # Combat Skills
            "brawl": {"base": 25, "category": SkillCategory.COMBAT},
            "handgun": {"base": 20, "category": SkillCategory.COMBAT},
            "rifle": {"base": 25, "category": SkillCategory.COMBAT},
            "shotgun": {"base": 25, "category": SkillCategory.COMBAT},
            "submachine_gun": {"base": 15, "category": SkillCategory.COMBAT},
            
            # Technical Skills
            "electrical_repair": {"base": 10, "category": SkillCategory.TECHNICAL},
            "locksmith": {"base": 1, "category": SkillCategory.TECHNICAL},
            "mechanical_repair": {"base": 10, "category": SkillCategory.TECHNICAL},
            "operate_heavy_machinery": {"base": 1, "category": SkillCategory.TECHNICAL},
            "photography": {"base": 5, "category": SkillCategory.TECHNICAL},
            
            # Survival Skills
            "first_aid": {"base": 30, "category": SkillCategory.SURVIVAL},
            "medicine": {"base": 1, "category": SkillCategory.SURVIVAL},
            "naturalist": {"base": 10, "category": SkillCategory.SURVIVAL},
            "navigate": {"base": 10, "category": SkillCategory.SURVIVAL},
            "survival": {"base": 10, "category": SkillCategory.SURVIVAL},
            "track": {"base": 10, "category": SkillCategory.SURVIVAL},
        }
    
    def _load_occupation_skills(self) -> Dict[str, List[str]]:
        """Load occupation-specific skill bonuses"""
        return {
            "investigator": ["library_use", "spot_hidden", "psychology", "listen", "law"],
            "professor": ["library_use", "education", "psychology", "other_language", "teach"],
            "antiquarian": ["appraise", "history", "library_use", "other_language", "spot_hidden"],
            "archaeologist": ["anthropology", "archaeology", "history", "other_language", "spot_hidden"],
            "journalist": ["fast_talk", "history", "library_use", "own_language", "psychology"],
            "private_investigator": ["accounting", "fast_talk", "law", "library_use", "psychology"],
            "physician": ["first_aid", "latin", "medicine", "psychology", "science"],
            "occultist": ["history", "library_use", "occult", "other_language", "psychology"],
        }
    
    def _load_sanity_loss_table(self) -> Dict[str, str]:
        """Load sanity loss values for various encounters"""
        return {
            "minor_disturbing_sight": "1d2",
            "corpse_recent": "1d3",
            "corpse_mutilated": "1d4+1",
            "grotesque_ritual": "1d6",
            "mythos_creature_minor": "1d8",
            "mythos_creature_major": "1d10",
            "great_old_one": "2d10+5",
            "cosmic_revelation": "1d20",
            "witnessing_death": "1d4",
            "causing_death": "1d6",
            "torture": "1d8",
            "indefinite_confinement": "1d10",
        }
    
    def create_character(self, character_data: Dict[str, Any]) -> Character:
        """
        Create a new character from character data.
        
        Args:
            character_data: Dictionary with character information
            
        Returns:
            Created Character object
        """
        # Create basic character
        character = Character(
            name=character_data["name"],
            age=character_data.get("age", 25),
            occupation=character_data.get("occupation", "investigator"),
            residence=character_data.get("residence", ""),
            birthplace=character_data.get("birthplace", "")
        )
        
        # Set characteristics if provided
        if "characteristics" in character_data:
            chars = character_data["characteristics"]
            character.strength = chars.get("strength", 50)
            character.constitution = chars.get("constitution", 50)
            character.power = chars.get("power", 50)
            character.dexterity = chars.get("dexterity", 50)
            character.appearance = chars.get("appearance", 50)
            character.size = chars.get("size", 50)
            character.intelligence = chars.get("intelligence", 50)
            character.education = chars.get("education", 50)
        
        # Initialize skills based on occupation
        self._initialize_character_skills(character)
        
        # Calculate derived attributes
        character.calculate_derived_attributes()
        
        # Add starting equipment
        self._add_starting_equipment(character)
        
        self.character = character
        logger.info(f"Created character: {character.name}, {character.occupation}")
        
        return character
    
    def _initialize_character_skills(self, character: Character):
        """Initialize character skills based on occupation and characteristics"""
        # Start with base skill values
        for skill_name, skill_data in self.skill_definitions.items():
            base_value = skill_data["base"]
            
            # Handle calculated base values
            if isinstance(base_value, str):
                if base_value == "dex/2":
                    base_value = character.dexterity // 2
                else:
                    base_value = 5  # Default fallback
            
            character.skills[skill_name] = base_value
        
        # Add occupation-specific bonuses
        occupation_skills = self.occupation_skills.get(character.occupation, [])
        skill_points = character.education * 20  # Base skill points
        
        # Distribute skill points among occupation skills
        points_per_skill = skill_points // len(occupation_skills) if occupation_skills else 0
        
        for skill in occupation_skills:
            if skill in character.skills:
                character.skills[skill] += points_per_skill
            else:
                character.skills[skill] = points_per_skill
        
        # Add characteristic-based skills
        character.skills["dodge"] = character.dexterity // 2
        character.skills["language_own"] = character.education
    
    def _add_starting_equipment(self, character: Character):
        """Add starting equipment based on occupation"""
        base_equipment = ["wallet", "keys", "notebook", "pen"]
        character.equipment.extend(base_equipment)
        
        # Occupation-specific equipment
        occupation_equipment = {
            "investigator": ["magnifying_glass", "camera", "flashlight"],
            "professor": ["briefcase", "reading_glasses", "reference_books"],
            "archaeologist": ["field_notebook", "measuring_tools", "brush_set"],
            "journalist": ["typewriter", "camera", "press_credentials"],
            "physician": ["medical_bag", "stethoscope", "prescription_pad"],
        }
        
        if character.occupation in occupation_equipment:
            character.equipment.extend(occupation_equipment[character.occupation])
        
        # Starting money based on occupation
        money_ranges = {
            "investigator": (200, 500),
            "professor": (300, 800),
            "archaeologist": (150, 400),
            "journalist": (100, 300),
            "physician": (500, 1200),
        }
        
        if character.occupation in money_ranges:
            min_money, max_money = money_ranges[character.occupation]
            character.money = random.randint(min_money, max_money)
        else:
            character.money = random.randint(100, 300)
    
    def make_skill_check(self, skill_name: str, modifier: int = 0, 
                        difficulty: str = "regular") -> DiceResult:
        """
        Perform a skill check for the current character.
        
        Args:
            skill_name: Name of the skill to check
            modifier: Dice modifier
            difficulty: "regular", "hard", or "extreme"
            
        Returns:
            DiceResult with success information
        """
        if not self.character:
            raise ValueError("No character loaded")
        
        # Get skill value
        skill_value = self.character.skills.get(skill_name, 0)
        
        # Apply temporary modifiers
        temp_modifier = self.character.temporary_modifiers.get(skill_name, 0)
        skill_value += temp_modifier
        
        # Adjust for difficulty
        if difficulty == "hard":
            skill_value = skill_value // 2
        elif difficulty == "extreme":
            skill_value = skill_value // 5
        
        # Make the roll
        result = self.dice_engine.skill_check(skill_value, modifier)
        
        # Record the event
        self._record_event("skill_check", {
            "skill": skill_name,
            "value": skill_value,
            "modifier": modifier,
            "difficulty": difficulty,
            "result": result.total,
            "success": result.success_level.value if result.success_level else "unknown"
        })
        
        logger.debug(f"Skill check {skill_name} ({skill_value}): {result.total} - {result.success_level.value if result.success_level else 'unknown'}")
        
        return result
    
    def make_characteristic_check(self, characteristic: str, modifier: int = 0) -> DiceResult:
        """Make a characteristic check (STR, DEX, etc.)"""
        if not self.character:
            raise ValueError("No character loaded")
        
        char_value = getattr(self.character, characteristic.lower(), 50)
        result = self.dice_engine.skill_check(char_value, modifier)
        
        self._record_event("characteristic_check", {
            "characteristic": characteristic,
            "value": char_value,
            "modifier": modifier,
            "result": result.total,
            "success": result.success_level.value if result.success_level else "unknown"
        })
        
        return result
    
    def make_sanity_check(self, sanity_loss: str = "1d4", reason: str = "") -> Dict[str, Any]:
        """
        Perform a sanity check with potential loss.
        
        Args:
            sanity_loss: Sanity loss expression
            reason: Reason for the sanity check
            
        Returns:
            Dictionary with check results
        """
        if not self.character:
            raise ValueError("No character loaded")
        
        result = self.dice_engine.sanity_check(self.character.current_sanity, sanity_loss)
        
        # Apply sanity loss
        old_sanity = self.character.current_sanity
        self.character.current_sanity = result["new_sanity"]
        
        # Check for temporary insanity
        sanity_lost = old_sanity - self.character.current_sanity
        temporary_insanity = False
        indefinite_insanity = False
        
        if sanity_lost >= 5:
            temporary_insanity = True
            if CharacterCondition.TEMPORARY_INSANITY not in self.character.conditions:
                self.character.conditions.append(CharacterCondition.TEMPORARY_INSANITY)
        
        if self.character.current_sanity <= 0:
            indefinite_insanity = True
            if CharacterCondition.INDEFINITE_INSANITY not in self.character.conditions:
                self.character.conditions.append(CharacterCondition.INDEFINITE_INSANITY)
        
        # Record the event
        self._record_event("sanity_check", {
            "reason": reason,
            "old_sanity": old_sanity,
            "new_sanity": self.character.current_sanity,
            "sanity_lost": sanity_lost,
            "temporary_insanity": temporary_insanity,
            "indefinite_insanity": indefinite_insanity,
            "check_result": result["check_result"].success_level.value if result["check_result"].success_level else "unknown"
        })
        
        logger.info(f"Sanity check: {old_sanity} -> {self.character.current_sanity} (lost {sanity_lost})")
        
        return {
            "check_result": result["check_result"],
            "sanity_lost": sanity_lost,
            "old_sanity": old_sanity,
            "new_sanity": self.character.current_sanity,
            "temporary_insanity": temporary_insanity,
            "indefinite_insanity": indefinite_insanity
        }
    
    def apply_damage(self, damage: int, damage_type: str = "physical") -> Dict[str, Any]:
        """
        Apply damage to the character.
        
        Args:
            damage: Amount of damage
            damage_type: Type of damage (physical, mental, etc.)
            
        Returns:
            Dictionary with damage results
        """
        if not self.character:
            raise ValueError("No character loaded")
        
        old_hp = self.character.current_hp
        self.character.current_hp = max(0, self.character.current_hp - damage)
        
        # Check for unconsciousness or death
        unconscious = False
        dying = False
        dead = False
        
        if self.character.current_hp <= 0:
            dead = True
            if CharacterCondition.DEAD not in self.character.conditions:
                self.character.conditions.append(CharacterCondition.DEAD)
        elif self.character.current_hp <= self.character.hit_points // 4:
            dying = True
            if CharacterCondition.DYING not in self.character.conditions:
                self.character.conditions.append(CharacterCondition.DYING)
        elif self.character.current_hp <= self.character.hit_points // 2:
            if CharacterCondition.MAJOR_INJURY not in self.character.conditions:
                self.character.conditions.append(CharacterCondition.MAJOR_INJURY)
        
        # Record the event
        self._record_event("damage_taken", {
            "damage": damage,
            "damage_type": damage_type,
            "old_hp": old_hp,
            "new_hp": self.character.current_hp,
            "unconscious": unconscious,
            "dying": dying,
            "dead": dead
        })
        
        logger.info(f"Damage applied: {damage} {damage_type} damage, HP: {old_hp} -> {self.character.current_hp}")
        
        return {
            "damage": damage,
            "old_hp": old_hp,
            "new_hp": self.character.current_hp,
            "unconscious": unconscious,
            "dying": dying,
            "dead": dead
        }
    
    def heal_character(self, healing: int, healing_type: str = "physical") -> Dict[str, Any]:
        """
        Heal the character.
        
        Args:
            healing: Amount of healing
            healing_type: Type of healing
            
        Returns:
            Dictionary with healing results
        """
        if not self.character:
            raise ValueError("No character loaded")
        
        old_hp = self.character.current_hp
        max_hp = self.character.hit_points
        
        if healing_type == "physical":
            self.character.current_hp = min(max_hp, self.character.current_hp + healing)
        elif healing_type == "sanity":
            max_sanity = self.character.sanity_points
            self.character.current_sanity = min(max_sanity, self.character.current_sanity + healing)
        
        # Remove conditions if appropriate
        if self.character.current_hp > self.character.hit_points // 2:
            if CharacterCondition.MAJOR_INJURY in self.character.conditions:
                self.character.conditions.remove(CharacterCondition.MAJOR_INJURY)
            if CharacterCondition.DYING in self.character.conditions:
                self.character.conditions.remove(CharacterCondition.DYING)
        
        self._record_event("healing", {
            "healing": healing,
            "healing_type": healing_type,
            "old_hp": old_hp,
            "new_hp": self.character.current_hp
        })
        
        return {
            "healing": healing,
            "old_hp": old_hp,
            "new_hp": self.character.current_hp
        }
    
    def advance_time(self, hours: float = 1.0):
        """Advance game time and apply time-based effects"""
        # Natural healing over time
        if self.character and hours >= 8:  # Full rest
            healing = self.dice_engine.roll("1d3").total
            self.heal_character(healing, "physical")
        
        # Remove temporary conditions
        if self.character and hours >= 1:
            if CharacterCondition.TEMPORARY_INSANITY in self.character.conditions:
                # Roll to recover from temporary insanity
                recovery_roll = self.make_characteristic_check("power")
                if recovery_roll.success_level in [SuccessLevel.SUCCESS, SuccessLevel.HARD_SUCCESS, SuccessLevel.EXTREME_SUCCESS]:
                    self.character.conditions.remove(CharacterCondition.TEMPORARY_INSANITY)
                    logger.info("Recovered from temporary insanity")
        
        self._record_event("time_advance", {"hours": hours})
    
    def _record_event(self, event_type: str, data: Dict[str, Any]):
        """Record a game event for history tracking"""
        event = {
            "type": event_type,
            "timestamp": time.time(),
            "turn": self.turn_number,
            "scene": self.current_scene,
            "data": data
        }
        
        self.event_history.append(event)
        
        # Limit history size
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-500:]  # Keep last 500 events
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Get a summary of the current character state"""
        if not self.character:
            return {}
        
        return {
            "name": self.character.name,
            "occupation": self.character.occupation,
            "hp": f"{self.character.current_hp}/{self.character.hit_points}",
            "sanity": f"{self.character.current_sanity}/{self.character.sanity_points}",
            "luck": f"{self.character.current_luck}/{self.character.luck_points}",
            "conditions": [c.value for c in self.character.conditions],
            "can_act": self.character.can_act(),
            "skills": dict(list(self.character.skills.items())[:10])  # Top 10 skills
        }
    
    def get_game_state(self) -> GameState:
        """Get the current complete game state"""
        if not self.character:
            raise ValueError("No character loaded")
        
        narrative_context = NarrativeContext(
            scene_id=self.current_scene,
            turn_number=self.turn_number,
            character_state=self.character.to_dict(),
            narrative_flags=self.game_flags.copy()
        )
        
        return GameState(
            character_data=self.character.to_dict(),
            narrative_context=narrative_context,
            game_metadata={
                "engine_state": {
                    "current_scene": self.current_scene,
                    "turn_number": self.turn_number,
                    "game_flags": self.game_flags,
                    "event_history": self.event_history[-50:]  # Last 50 events
                }
            }
        )
    
    def load_game_state(self, game_state: GameState):
        """Load a game state"""
        # Load character
        self.character = Character.from_dict(game_state.character_data)
        
        # Load engine state
        engine_state = game_state.game_metadata.get("engine_state", {})
        self.current_scene = engine_state.get("current_scene", "")
        self.turn_number = engine_state.get("turn_number", 0)
        self.game_flags = engine_state.get("game_flags", {})
        self.event_history = engine_state.get("event_history", [])
        
        logger.info(f"Loaded game state: {self.character.name} at turn {self.turn_number}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get game engine statistics"""
        return {
            "turn_number": self.turn_number,
            "current_scene": self.current_scene,
            "character_loaded": self.character is not None,
            "character_name": self.character.name if self.character else None,
            "events_recorded": len(self.event_history),
            "game_flags": len(self.game_flags),
            "dice_statistics": self.dice_engine.get_statistics()
        }