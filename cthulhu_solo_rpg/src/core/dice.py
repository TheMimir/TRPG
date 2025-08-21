"""
Dice System for Cthulhu Solo TRPG

Implements the Call of Cthulhu dice mechanics including:
- Basic dice rolling (d100, d6, d8, etc.)
- Skill checks with success degrees
- Luck rolls and sanity checks
- Damage rolls
- Statistical functions for game balance
"""

import random
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class SuccessLevel(Enum):
    """Success levels for skill checks"""
    CRITICAL_FAILURE = "critical_failure"
    FAILURE = "failure"
    SUCCESS = "success"
    HARD_SUCCESS = "hard_success"
    EXTREME_SUCCESS = "extreme_success"
    CRITICAL_SUCCESS = "critical_success"


@dataclass
class DiceResult:
    """Result of a dice roll with analysis"""
    total: int  # Total result
    rolls: List[int]  # Individual die results
    dice_expression: str  # Original dice expression (e.g., "2d6+3")
    success_level: Optional[SuccessLevel] = None  # For skill checks
    target_number: Optional[int] = None  # Target for skill checks
    is_pushed: bool = False  # Whether this was a pushed roll
    modifier: int = 0  # Applied modifier
    
    def __str__(self) -> str:
        """String representation of the dice result"""
        if self.success_level:
            return f"{self.dice_expression}: {self.total} ({self.success_level.value})"
        return f"{self.dice_expression}: {self.total}"


class DiceEngine:
    """
    Core dice rolling engine for the Cthulhu Solo TRPG system.
    
    Implements Call of Cthulhu 7th edition dice mechanics with
    additional features for solo play.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the dice engine with optional random seed"""
        if seed is not None:
            random.seed(seed)
        self.roll_history: List[DiceResult] = []
    
    def roll(self, dice_expression: str) -> DiceResult:
        """
        Roll dice based on standard dice notation.
        
        Supports:
        - Standard notation: "2d6", "1d100", "3d8+2"
        - Call of Cthulhu percentile: "d100", "d%"
        - Simple numbers: "20" (treated as d20)
        - Modifiers: "+3", "-2"
        
        Args:
            dice_expression: Dice expression to roll
            
        Returns:
            DiceResult with rolled values and analysis
        """
        # Clean the expression
        expr = dice_expression.strip().lower().replace(" ", "")
        
        # Handle simple number (treat as single die)
        if expr.isdigit():
            sides = int(expr)
            roll = random.randint(1, sides)
            result = DiceResult(
                total=roll,
                rolls=[roll],
                dice_expression=f"d{sides}"
            )
            self.roll_history.append(result)
            return result
        
        # Parse dice expression using regex
        pattern = r'(\d*)d(\d+|%)([\+\-]\d+)?'
        match = re.match(pattern, expr)
        
        if not match:
            raise ValueError(f"Invalid dice expression: {dice_expression}")
        
        num_dice = int(match.group(1)) if match.group(1) else 1
        sides = 100 if match.group(2) == '%' else int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        # Validate input
        if num_dice <= 0 or num_dice > 100:
            raise ValueError("Number of dice must be between 1 and 100")
        if sides <= 0 or sides > 1000:
            raise ValueError("Number of sides must be between 1 and 1000")
        
        # Roll the dice
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        
        result = DiceResult(
            total=total,
            rolls=rolls,
            dice_expression=dice_expression,
            modifier=modifier
        )
        
        self.roll_history.append(result)
        return result
    
    def skill_check(self, skill_value: int, modifier: int = 0, 
                   is_pushed: bool = False) -> DiceResult:
        """
        Perform a Call of Cthulhu skill check.
        
        Args:
            skill_value: The character's skill rating (0-100)
            modifier: Dice modifier for difficulty
            is_pushed: Whether this is a pushed roll
            
        Returns:
            DiceResult with success level analysis
        """
        # Roll d100
        roll_result = self.roll("d100")
        adjusted_roll = roll_result.total + modifier
        
        # Determine success level
        success_level = self._determine_success_level(adjusted_roll, skill_value)
        
        # Create enhanced result
        result = DiceResult(
            total=adjusted_roll,
            rolls=roll_result.rolls,
            dice_expression="d100" if modifier == 0 else f"d100{modifier:+d}",
            success_level=success_level,
            target_number=skill_value,
            is_pushed=is_pushed,
            modifier=modifier
        )
        
        # Replace in history
        self.roll_history[-1] = result
        return result
    
    def _determine_success_level(self, roll: int, skill_value: int) -> SuccessLevel:
        """Determine the success level for a skill check"""
        # Critical results
        if roll == 100:
            return SuccessLevel.CRITICAL_FAILURE
        if roll == 1:
            return SuccessLevel.CRITICAL_SUCCESS
        
        # Calculate thresholds
        hard_threshold = skill_value // 2
        extreme_threshold = skill_value // 5
        
        # Determine success level
        if roll <= extreme_threshold:
            return SuccessLevel.EXTREME_SUCCESS
        elif roll <= hard_threshold:
            return SuccessLevel.HARD_SUCCESS
        elif roll <= skill_value:
            return SuccessLevel.SUCCESS
        else:
            # Check for critical failure (96-100 for skills < 50)
            if skill_value < 50 and roll >= 96:
                return SuccessLevel.CRITICAL_FAILURE
            return SuccessLevel.FAILURE
    
    def sanity_check(self, current_sanity: int, sanity_loss: str = "1d4/1d8") -> Dict:
        """
        Perform a sanity check with potential loss.
        
        Args:
            current_sanity: Current sanity points
            sanity_loss: Loss expression (success/failure)
            
        Returns:
            Dictionary with check result and sanity loss
        """
        # Parse sanity loss (format: "success_loss/failure_loss")
        if '/' in sanity_loss:
            success_loss, failure_loss = sanity_loss.split('/')
        else:
            success_loss = failure_loss = sanity_loss
        
        # Perform sanity check
        check_result = self.skill_check(current_sanity)
        
        # Determine sanity loss
        if check_result.success_level in [SuccessLevel.SUCCESS, SuccessLevel.HARD_SUCCESS, 
                                        SuccessLevel.EXTREME_SUCCESS, SuccessLevel.CRITICAL_SUCCESS]:
            loss_roll = self.roll(success_loss.strip())
        else:
            loss_roll = self.roll(failure_loss.strip())
        
        return {
            "check_result": check_result,
            "sanity_loss": loss_roll.total,
            "new_sanity": max(0, current_sanity - loss_roll.total),
            "loss_roll": loss_roll
        }
    
    def damage_roll(self, weapon_damage: str, location: str = "general") -> DiceResult:
        """
        Roll weapon damage with location modifiers.
        
        Args:
            weapon_damage: Damage expression (e.g., "1d6+2")
            location: Hit location for modifiers
            
        Returns:
            DiceResult with damage total
        """
        base_damage = self.roll(weapon_damage)
        
        # Location modifiers (simplified)
        location_modifiers = {
            "head": 2,
            "chest": 1,
            "limb": 0,
            "general": 0
        }
        
        modifier = location_modifiers.get(location.lower(), 0)
        base_damage.total += modifier
        base_damage.modifier += modifier
        
        return base_damage
    
    def luck_check(self, luck_points: int) -> DiceResult:
        """Perform a luck check"""
        return self.skill_check(luck_points)
    
    def resistance_check(self, attacker_stat: int, defender_stat: int) -> DiceResult:
        """
        Perform a resistance table check.
        
        Args:
            attacker_stat: Attacker's relevant stat
            defender_stat: Defender's relevant stat
            
        Returns:
            DiceResult indicating success/failure
        """
        # Calculate success chance based on resistance table
        if defender_stat == 0:
            success_chance = 100
        else:
            ratio = attacker_stat / defender_stat
            if ratio >= 2.0:
                success_chance = 95
            elif ratio >= 1.5:
                success_chance = 80
            elif ratio >= 1.0:
                success_chance = 50
            elif ratio >= 0.5:
                success_chance = 20
            else:
                success_chance = 5
        
        return self.skill_check(success_chance)
    
    def pushed_roll(self, skill_value: int) -> DiceResult:
        """
        Perform a pushed skill roll (Call of Cthulhu mechanic).
        
        Pushed rolls have consequences for failure but allow a second attempt.
        """
        return self.skill_check(skill_value, is_pushed=True)
    
    def group_roll(self, dice_expression: str, count: int) -> List[DiceResult]:
        """Roll multiple dice of the same type"""
        return [self.roll(dice_expression) for _ in range(count)]
    
    def advantage_roll(self, dice_expression: str) -> DiceResult:
        """Roll with advantage (take better of two rolls)"""
        roll1 = self.roll(dice_expression)
        roll2 = self.roll(dice_expression)
        
        better_roll = roll1 if roll1.total >= roll2.total else roll2
        better_roll.dice_expression += " (advantage)"
        return better_roll
    
    def disadvantage_roll(self, dice_expression: str) -> DiceResult:
        """Roll with disadvantage (take worse of two rolls)"""
        roll1 = self.roll(dice_expression)
        roll2 = self.roll(dice_expression)
        
        worse_roll = roll1 if roll1.total <= roll2.total else roll2
        worse_roll.dice_expression += " (disadvantage)"
        return worse_roll
    
    def get_statistics(self) -> Dict:
        """Get statistics about recent rolls"""
        if not self.roll_history:
            return {"total_rolls": 0}
        
        recent_rolls = self.roll_history[-20:]  # Last 20 rolls
        totals = [r.total for r in recent_rolls]
        
        return {
            "total_rolls": len(self.roll_history),
            "recent_average": sum(totals) / len(totals),
            "recent_high": max(totals),
            "recent_low": min(totals),
            "success_rate": len([r for r in recent_rolls 
                               if r.success_level and r.success_level in [
                                   SuccessLevel.SUCCESS, SuccessLevel.HARD_SUCCESS,
                                   SuccessLevel.EXTREME_SUCCESS, SuccessLevel.CRITICAL_SUCCESS
                               ]]) / len(recent_rolls) if recent_rolls else 0
        }
    
    def clear_history(self):
        """Clear the roll history"""
        self.roll_history.clear()


# Convenience functions
def roll_dice(expression: str) -> DiceResult:
    """Quick dice roll function"""
    engine = DiceEngine()
    return engine.roll(expression)


def skill_check(skill_value: int, modifier: int = 0) -> DiceResult:
    """Quick skill check function"""
    engine = DiceEngine()
    return engine.skill_check(skill_value, modifier)


def sanity_loss_check(current_sanity: int, loss_expression: str = "1d4/1d8") -> Dict:
    """Quick sanity check function"""
    engine = DiceEngine()
    return engine.sanity_check(current_sanity, loss_expression)


# Predefined common rolls for Cthulhu games
COMMON_ROLLS = {
    "idea": "d100",  # Idea roll (against INT*5)
    "know": "d100",  # Knowledge roll (against EDU*5)
    "luck": "d100",  # Luck roll
    "sanity": "d100",  # Sanity check
    "damage_punch": "1d3",  # Unarmed damage
    "damage_knife": "1d4+1",  # Knife damage
    "damage_pistol": "1d10",  # Pistol damage
    "damage_rifle": "2d6+4",  # Rifle damage
    "hp_human": "3d6",  # Human hit points
    "hp_tough": "4d6",  # Tough human
    "san_minor": "1d4",  # Minor sanity loss
    "san_major": "1d8",  # Major sanity loss
    "san_extreme": "1d20",  # Extreme sanity loss
}


def get_common_roll(roll_name: str) -> DiceResult:
    """Get a predefined common roll"""
    if roll_name not in COMMON_ROLLS:
        raise ValueError(f"Unknown common roll: {roll_name}")
    
    engine = DiceEngine()
    return engine.roll(COMMON_ROLLS[roll_name])