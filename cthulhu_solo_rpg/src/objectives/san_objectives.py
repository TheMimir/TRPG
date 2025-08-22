"""
SAN-Integrated Objective System for Cthulhu Solo TRPG

This module implements objectives that are deeply integrated with the 
Sanity (SAN) system, providing different goals and mechanics based on
the character's mental state and cosmic horror exposure.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Callable, Union
from dataclasses import dataclass, field

from .base_objective import (
    BaseObjective, ObjectiveStatus, ObjectivePriority, ObjectiveScope,
    ObjectiveType, ObjectiveReward, ObjectiveConsequence, ObjectiveCondition,
    RewardType, FailureConsequence
)
from .layered_objectives import ShortTermObjective, MidTermObjective

logger = logging.getLogger(__name__)


class SanityState(Enum):
    """Character's current sanity state"""
    STABLE = "stable"           # 70-99 SAN: Normal mental state
    STRESSED = "stressed"       # 50-69 SAN: Under pressure, minor strain
    DISTURBED = "disturbed"     # 30-49 SAN: Significant mental distress
    UNHINGED = "unhinged"       # 10-29 SAN: Severe psychological damage
    MAD = "mad"                 # 0-9 SAN: Complete psychological breakdown
    TEMPORARILY_INSANE = "temp_insane"  # Temporary insanity state


class MadnessType(Enum):
    """Types of madness that can affect objectives"""
    PARANOIA = "paranoia"
    OBSESSION = "obsession"
    PHOBIA = "phobia"
    DELUSION = "delusion"
    COMPULSION = "compulsion"
    AMNESIA = "amnesia"
    COSMIC_AWARENESS = "cosmic_awareness"


class CosmicInsightLevel(Enum):
    """Levels of cosmic understanding"""
    IGNORANT = 0      # Blissfully unaware
    GLIMPSE = 1       # Caught a glimpse of the truth
    AWARE = 2         # Aware of cosmic horror existence
    KNOWLEDGEABLE = 3 # Understands cosmic relationships
    ENLIGHTENED = 4   # Deep cosmic understanding
    TRANSCENDENT = 5  # Beyond human comprehension


@dataclass
class SanityThreshold:
    """Defines SAN thresholds for different mental states"""
    stable_min: int = 70
    stressed_min: int = 50
    disturbed_min: int = 30
    unhinged_min: int = 10
    mad_max: int = 9


@dataclass
class MadnessEffect:
    """Effect of madness on objectives and behavior"""
    madness_type: MadnessType
    severity: int  # 1-5 scale
    duration_hours: Optional[float] = None  # None for permanent
    triggers: List[str] = field(default_factory=list)
    behavioral_changes: Dict[str, Any] = field(default_factory=dict)
    objective_modifications: Dict[str, Any] = field(default_factory=dict)


class SanityIntegratedObjective(BaseObjective):
    """
    Base class for objectives that integrate with the SAN system.
    Provides common functionality for sanity-aware objectives.
    """
    
    def __init__(self, *args, **kwargs):
        # SAN integration parameters
        self.san_requirements: Optional[SanityThreshold] = kwargs.pop('san_requirements', None)
        self.required_sanity_state: Optional[SanityState] = kwargs.pop('required_sanity_state', None)
        self.san_risk_level: int = kwargs.pop('san_risk_level', 1)  # 1-5 scale
        self.cosmic_insight_required: int = kwargs.pop('cosmic_insight_required', 0)
        
        # Madness integration
        self.madness_effects: List[MadnessEffect] = kwargs.pop('madness_effects', [])
        self.madness_protection: bool = kwargs.pop('madness_protection', False)
        
        # SAN loss/gain tracking
        self.cumulative_san_loss: int = 0
        self.san_loss_events: List[Dict[str, Any]] = []
        self.potential_san_gain: int = kwargs.pop('potential_san_gain', 0)
        
        super().__init__(*args, **kwargs)
        
        # Add SAN-specific event tracking
        self.sanity_events: List[Dict[str, Any]] = []
        
        logger.debug(f"Created SAN-integrated objective: {self.objective_id}")
    
    def get_current_sanity_state(self, game_state: Dict[str, Any]) -> SanityState:
        """Determine current sanity state from game state"""
        current_san = game_state.get('sanity', game_state.get('san', 50))
        
        # Handle temporary insanity
        if game_state.get('temporary_insanity', False):
            return SanityState.TEMPORARILY_INSANE
        
        # Determine state based on SAN value
        thresholds = self.san_requirements or SanityThreshold()
        
        if current_san >= thresholds.stable_min:
            return SanityState.STABLE
        elif current_san >= thresholds.stressed_min:
            return SanityState.STRESSED
        elif current_san >= thresholds.disturbed_min:
            return SanityState.DISTURBED
        elif current_san >= thresholds.unhinged_min:
            return SanityState.UNHINGED
        else:
            return SanityState.MAD
    
    def can_activate(self, game_state: Dict[str, Any]) -> bool:
        """Override to include SAN requirements"""
        if not super().can_activate(game_state):
            return False
        
        # Check sanity state requirements
        if self.required_sanity_state:
            current_state = self.get_current_sanity_state(game_state)
            if current_state != self.required_sanity_state:
                return False
        
        # Check cosmic insight requirements
        current_insight = game_state.get('cosmic_insight', 0)
        if current_insight < self.cosmic_insight_required:
            return False
        
        return True
    
    def calculate_san_risk(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]] = None) -> int:
        """Calculate potential SAN loss for this objective"""
        base_risk = self.san_risk_level
        
        # Modify based on current sanity state
        current_state = self.get_current_sanity_state(game_state)
        state_modifiers = {
            SanityState.STABLE: 0,
            SanityState.STRESSED: 1,
            SanityState.DISTURBED: 2,
            SanityState.UNHINGED: 3,
            SanityState.MAD: 5,
            SanityState.TEMPORARILY_INSANE: 3
        }
        
        risk_modifier = state_modifiers.get(current_state, 0)
        total_risk = base_risk + risk_modifier
        
        # Apply madness protections
        if self.madness_protection:
            total_risk = max(1, total_risk - 2)
        
        return min(10, total_risk)  # Cap at 10
    
    def apply_san_loss(self, game_state: Dict[str, Any], loss_amount: int, reason: str = ""):
        """Apply SAN loss and track it"""
        self.cumulative_san_loss += loss_amount
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'san_loss': loss_amount,
            'reason': reason,
            'cumulative_loss': self.cumulative_san_loss,
            'sanity_before': game_state.get('sanity', 50),
            'sanity_after': max(0, game_state.get('sanity', 50) - loss_amount)
        }
        
        self.san_loss_events.append(event)
        self.sanity_events.append(event)
        
        # Update game state (in a real implementation, this would be handled by the game engine)
        game_state['sanity'] = event['sanity_after']
        
        self._log_event('san_loss_applied', event)
        logger.warning(f"SAN loss applied: {loss_amount} points - {reason}")
        
        # Check for madness threshold
        self._check_madness_threshold(game_state)
    
    def apply_san_gain(self, game_state: Dict[str, Any], gain_amount: int, reason: str = ""):
        """Apply SAN gain and track it"""
        max_san = game_state.get('max_sanity', 99)
        current_san = game_state.get('sanity', 50)
        actual_gain = min(gain_amount, max_san - current_san)
        
        if actual_gain > 0:
            event = {
                'timestamp': datetime.now().isoformat(),
                'san_gain': actual_gain,
                'reason': reason,
                'sanity_before': current_san,
                'sanity_after': current_san + actual_gain
            }
            
            self.sanity_events.append(event)
            game_state['sanity'] = event['sanity_after']
            
            self._log_event('san_gain_applied', event)
            logger.info(f"SAN restored: {actual_gain} points - {reason}")
    
    def _check_madness_threshold(self, game_state: Dict[str, Any]):
        """Check if madness effects should be triggered"""
        current_state = self.get_current_sanity_state(game_state)
        
        # Apply madness effects based on sanity state
        for effect in self.madness_effects:
            if self._should_trigger_madness(effect, current_state, game_state):
                self._apply_madness_effect(effect, game_state)
    
    def _should_trigger_madness(self, effect: MadnessEffect, current_state: SanityState, game_state: Dict[str, Any]) -> bool:
        """Determine if a madness effect should be triggered"""
        # Check if already applied
        active_madness = game_state.get('active_madness', [])
        if effect.madness_type.value in active_madness:
            return False
        
        # Check sanity state triggers
        trigger_states = {
            SanityState.DISTURBED: effect.severity >= 3,
            SanityState.UNHINGED: effect.severity >= 2,
            SanityState.MAD: True,
            SanityState.TEMPORARILY_INSANE: True
        }
        
        return trigger_states.get(current_state, False)
    
    def _apply_madness_effect(self, effect: MadnessEffect, game_state: Dict[str, Any]):
        """Apply a madness effect to the game state"""
        active_madness = game_state.setdefault('active_madness', [])
        active_madness.append(effect.madness_type.value)
        
        # Apply behavioral changes
        for behavior, change in effect.behavioral_changes.items():
            game_state[behavior] = change
        
        # Apply objective modifications
        if effect.objective_modifications:
            self._apply_objective_modifications(effect.objective_modifications)
        
        self._log_event('madness_effect_applied', {
            'madness_type': effect.madness_type.value,
            'severity': effect.severity,
            'duration': effect.duration_hours
        })
        
        logger.warning(f"Madness effect applied: {effect.madness_type.value} (severity {effect.severity})")
    
    def _apply_objective_modifications(self, modifications: Dict[str, Any]):
        """Apply madness-induced modifications to this objective"""
        for mod_type, mod_value in modifications.items():
            if mod_type == 'priority_change':
                # Adjust priority based on madness
                current_priority = self.priority.value
                new_priority = max(1, min(6, current_priority + mod_value))
                self.priority = ObjectivePriority(new_priority)
            
            elif mod_type == 'time_pressure':
                # Reduce time limit due to madness urgency
                if self.time_limit:
                    reduction = timedelta(minutes=mod_value)
                    self.time_limit = max(timedelta(minutes=1), self.time_limit - reduction)
            
            elif mod_type == 'add_compulsion':
                # Add compulsive behavior requirements
                if hasattr(self, 'required_actions'):
                    self.required_actions.add(mod_value)


class SanityDependentObjective(SanityIntegratedObjective):
    """
    Objectives that change based on sanity level.
    Different goals and methods available at different sanity states.
    """
    
    def __init__(self, *args, **kwargs):
        # State-dependent configurations
        self.state_configurations: Dict[SanityState, Dict[str, Any]] = kwargs.pop('state_configurations', {})
        self.current_configuration: Optional[Dict[str, Any]] = None
        
        super().__init__(*args, **kwargs)
    
    def update_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update progress with sanity-dependent logic"""
        if not self.is_active:
            return False
        
        # Update configuration based on current sanity state
        current_state = self.get_current_sanity_state(game_state)
        self._update_configuration_for_state(current_state)
        
        # Apply state-specific progress logic
        progress_made = self._update_state_specific_progress(current_state, game_state, action_data)
        
        # Apply SAN effects if configured
        if action_data and progress_made:
            self._apply_sanity_effects(current_state, game_state, action_data)
        
        self.last_update = datetime.now()
        return progress_made
    
    def _update_configuration_for_state(self, sanity_state: SanityState):
        """Update objective configuration based on sanity state"""
        if sanity_state in self.state_configurations:
            new_config = self.state_configurations[sanity_state]
            
            # Only update if configuration changed
            if self.current_configuration != new_config:
                self.current_configuration = new_config
                
                # Apply configuration changes
                if 'title_suffix' in new_config:
                    self.title = f"{self.title.split(' (')[0]} ({new_config['title_suffix']})"
                
                if 'description_override' in new_config:
                    self.description = new_config['description_override']
                
                if 'priority_modifier' in new_config:
                    current_priority = self.priority.value
                    new_priority = max(1, min(6, current_priority + new_config['priority_modifier']))
                    self.priority = ObjectivePriority(new_priority)
                
                self._log_event('configuration_updated', {
                    'sanity_state': sanity_state.value,
                    'new_config': new_config
                })
    
    def _update_state_specific_progress(self, sanity_state: SanityState, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]]) -> bool:
        """Update progress using state-specific logic"""
        config = self.current_configuration or {}
        
        # Different progress calculation based on sanity state
        if sanity_state == SanityState.MAD:
            return self._update_mad_progress(game_state, action_data, config)
        elif sanity_state == SanityState.UNHINGED:
            return self._update_unhinged_progress(game_state, action_data, config)
        elif sanity_state == SanityState.DISTURBED:
            return self._update_disturbed_progress(game_state, action_data, config)
        else:
            return self._update_normal_progress(game_state, action_data, config)
    
    def _update_mad_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]], config: Dict[str, Any]) -> bool:
        """Progress logic for mad characters"""
        # Mad characters have different success criteria
        if action_data and action_data.get('action_type') == 'mad_insight':
            # Mad characters can gain insight through madness
            self.progress = min(1.0, self.progress + 0.3)
            return True
        elif action_data and action_data.get('action_type') in ['random_action', 'compulsive_behavior']:
            # Mad actions sometimes accidentally succeed
            import random
            if random.random() < 0.1:  # 10% chance of accidental progress
                self.progress = min(1.0, self.progress + 0.1)
                return True
        
        return False
    
    def _update_unhinged_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]], config: Dict[str, Any]) -> bool:
        """Progress logic for unhinged characters"""
        # Unhinged characters have erratic but sometimes brilliant insights
        if action_data:
            action_type = action_data.get('action_type', '')
            
            if 'desperate' in action_type or 'reckless' in action_type:
                # Desperate actions can yield results but with risks
                advancement = 0.2
                self.progress = min(1.0, self.progress + advancement)
                
                # Apply additional SAN risk
                risk = self.calculate_san_risk(game_state, action_data)
                if risk > 3:
                    self.apply_san_loss(game_state, 1, "Desperate action while unhinged")
                
                return True
        
        return False
    
    def _update_disturbed_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]], config: Dict[str, Any]) -> bool:
        """Progress logic for disturbed characters"""
        # Disturbed characters are less efficient but can still function
        if action_data and action_data.get('action_type'):
            # Normal actions are less effective
            advancement = 0.05
            self.progress = min(1.0, self.progress + advancement)
            return True
        
        return False
    
    def _update_normal_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]], config: Dict[str, Any]) -> bool:
        """Progress logic for characters in normal sanity states"""
        # Standard progress logic
        if action_data and action_data.get('action_type'):
            advancement = 0.1
            self.progress = min(1.0, self.progress + advancement)
            return True
        
        return False
    
    def _apply_sanity_effects(self, sanity_state: SanityState, game_state: Dict[str, Any], action_data: Dict[str, Any]):
        """Apply sanity effects based on current state and actions"""
        config = self.current_configuration or {}
        
        # Apply SAN loss based on risk level and action
        if 'san_loss_multiplier' in config:
            base_risk = self.calculate_san_risk(game_state, action_data)
            adjusted_risk = int(base_risk * config['san_loss_multiplier'])
            
            if adjusted_risk > 0:
                reason = f"Action while {sanity_state.value}"
                self.apply_san_loss(game_state, adjusted_risk, reason)
        
        # Apply SAN gain for successful actions in low sanity states
        if self.progress >= 1.0 and sanity_state in [SanityState.DISTURBED, SanityState.UNHINGED]:
            if 'completion_san_bonus' in config:
                bonus = config['completion_san_bonus']
                self.apply_san_gain(game_state, bonus, "Success despite mental distress")


class CosmicInsightObjective(SanityIntegratedObjective):
    """
    Objectives that provide cosmic insight but at the cost of sanity.
    The more you learn, the more your mind suffers.
    """
    
    def __init__(self, *args, **kwargs):
        # Cosmic insight parameters
        self.insight_levels: List[Dict[str, Any]] = kwargs.pop('insight_levels', [])
        self.current_insight_level = 0
        self.revelation_thresholds: List[float] = kwargs.pop('revelation_thresholds', [0.25, 0.5, 0.75, 1.0])
        
        # Knowledge vs Sanity trade-off
        self.sanity_cost_per_insight: int = kwargs.pop('sanity_cost_per_insight', 3)
        self.insight_protection_threshold: int = kwargs.pop('insight_protection_threshold', 30)
        
        super().__init__(*args, **kwargs)
    
    def update_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update progress with cosmic insight mechanics"""
        if not self.is_active:
            return False
        
        old_progress = self.progress
        progress_made = False
        
        # Track cosmic revelations
        if action_data and 'cosmic_revelation' in action_data:
            revelation_type = action_data['cosmic_revelation']
            insight_gain = action_data.get('insight_value', 0.1)
            
            self.progress = min(1.0, self.progress + insight_gain)
            progress_made = True
            
            # Apply the cosmic insight penalty
            self._apply_cosmic_insight_penalty(game_state, revelation_type, insight_gain)
            
            self._log_event('cosmic_revelation', {
                'revelation_type': revelation_type,
                'insight_gain': insight_gain,
                'total_progress': self.progress
            })
        
        # Check for insight level progression
        if progress_made:
            self._check_insight_level_progression(game_state)
        
        self.last_update = datetime.now()
        return progress_made
    
    def _apply_cosmic_insight_penalty(self, game_state: Dict[str, Any], revelation_type: str, insight_gain: float):
        """Apply SAN loss from gaining cosmic insight"""
        current_san = game_state.get('sanity', 50)
        
        # Calculate SAN loss based on insight gain and current sanity
        base_loss = int(insight_gain * self.sanity_cost_per_insight * 10)  # Scale up
        
        # Modify based on current sanity (lower sanity = more vulnerable)
        if current_san < self.insight_protection_threshold:
            multiplier = 1.5
        elif current_san < 50:
            multiplier = 1.2
        else:
            multiplier = 1.0
        
        total_loss = int(base_loss * multiplier)
        
        # Apply protection for very low sanity
        if current_san <= 10:
            total_loss = min(total_loss, 1)  # Prevent instant death
        
        if total_loss > 0:
            reason = f"Cosmic revelation: {revelation_type}"
            self.apply_san_loss(game_state, total_loss, reason)
    
    def _check_insight_level_progression(self, game_state: Dict[str, Any]):
        """Check if character has reached a new insight level"""
        for i, threshold in enumerate(self.revelation_thresholds):
            if self.progress >= threshold and self.current_insight_level <= i:
                if i < len(self.insight_levels):
                    self.current_insight_level = i + 1
                    self._trigger_insight_level_effect(i, game_state)
                break
    
    def _trigger_insight_level_effect(self, level_index: int, game_state: Dict[str, Any]):
        """Trigger effects when reaching a new insight level"""
        if level_index >= len(self.insight_levels):
            return
        
        level_data = self.insight_levels[level_index]
        
        # Apply insight level effects
        if 'cosmic_knowledge_unlock' in level_data:
            knowledge = game_state.setdefault('cosmic_knowledge', [])
            knowledge.extend(level_data['cosmic_knowledge_unlock'])
        
        if 'sanity_threshold_change' in level_data:
            # Permanently alter sanity thresholds (some insights change you forever)
            threshold_change = level_data['sanity_threshold_change']
            max_san = game_state.get('max_sanity', 99)
            game_state['max_sanity'] = max(50, max_san + threshold_change)
        
        if 'special_ability_unlock' in level_data:
            abilities = game_state.setdefault('special_abilities', [])
            abilities.extend(level_data['special_ability_unlock'])
        
        self._log_event('insight_level_reached', {
            'level': level_index + 1,
            'effects': level_data,
            'total_insights': self.current_insight_level
        })
        
        logger.info(f"Cosmic insight level {level_index + 1} reached")


class MadnessObjective(SanityIntegratedObjective):
    """
    Objectives that can only be completed while experiencing madness.
    These represent actions that only make sense to a disturbed mind.
    """
    
    def __init__(self, *args, **kwargs):
        # Madness requirements
        self.required_madness_types: Set[MadnessType] = set(kwargs.pop('required_madness_types', []))
        self.min_madness_severity: int = kwargs.pop('min_madness_severity', 1)
        
        # Madness-specific mechanics
        self.madness_progress_multiplier: float = kwargs.pop('madness_progress_multiplier', 2.0)
        self.sanity_recovery_on_completion: int = kwargs.pop('sanity_recovery_on_completion', 5)
        
        super().__init__(*args, **kwargs)
        
        # Force high priority for madness objectives
        if self.priority.value < ObjectivePriority.HIGH.value:
            self.priority = ObjectivePriority.HIGH
    
    def can_activate(self, game_state: Dict[str, Any]) -> bool:
        """Only activate if character has appropriate madness"""
        if not super().can_activate(game_state):
            return False
        
        # Check for required madness types
        active_madness = set(game_state.get('active_madness', []))
        if self.required_madness_types:
            if not self.required_madness_types.intersection(active_madness):
                return False
        
        # Check minimum madness severity
        madness_severity = game_state.get('madness_severity', 0)
        if madness_severity < self.min_madness_severity:
            return False
        
        return True
    
    def update_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update progress with madness-enhanced logic"""
        if not self.is_active:
            return False
        
        # Check if still in appropriate madness state
        if not self._is_madness_appropriate(game_state):
            # Lose progress if madness is no longer appropriate
            self.progress = max(0.0, self.progress - 0.1)
            self._log_event('madness_progress_lost', {
                'reason': 'Inappropriate madness state',
                'progress_lost': 0.1
            })
            return True
        
        # Enhanced progress while in madness
        if action_data and action_data.get('action_type'):
            action_type = action_data['action_type']
            
            # Madness-driven actions are more effective for these objectives
            if any(madness in action_type for madness in ['compulsive', 'obsessive', 'paranoid', 'delusional']):
                advancement = 0.1 * self.madness_progress_multiplier
                self.progress = min(1.0, self.progress + advancement)
                
                self._log_event('madness_enhanced_progress', {
                    'action_type': action_type,
                    'advancement': advancement,
                    'multiplier': self.madness_progress_multiplier
                })
                
                return True
        
        return False
    
    def _is_madness_appropriate(self, game_state: Dict[str, Any]) -> bool:
        """Check if current madness state is appropriate for this objective"""
        active_madness = set(game_state.get('active_madness', []))
        
        # If specific madness types are required, check for them
        if self.required_madness_types:
            return bool(self.required_madness_types.intersection(active_madness))
        
        # Otherwise, just check for any significant madness
        return len(active_madness) > 0 or game_state.get('madness_severity', 0) >= self.min_madness_severity
    
    def complete(self, game_state: Dict[str, Any]) -> bool:
        """Complete madness objective with sanity recovery"""
        if super().complete(game_state):
            # Completing a madness objective can provide some sanity recovery
            # (confronting and working through madness can be therapeutic)
            if self.sanity_recovery_on_completion > 0:
                self.apply_san_gain(
                    game_state, 
                    self.sanity_recovery_on_completion,
                    "Completing madness-driven objective"
                )
            
            return True
        return False


# Factory functions for creating SAN-integrated objectives

def create_forbidden_knowledge_objective(
    objective_id: str,
    title: str,
    knowledge_type: str,
    insight_levels: List[Dict[str, Any]],
    **kwargs
) -> CosmicInsightObjective:
    """Create an objective for gaining forbidden knowledge"""
    return CosmicInsightObjective(
        objective_id=objective_id,
        title=title,
        description=f"Learn the terrible truth about {knowledge_type}",
        objective_type=ObjectiveType.KNOWLEDGE,
        scope=ObjectiveScope.MID_TERM,
        priority=ObjectivePriority.HIGH,
        san_risk_level=4,
        insight_levels=insight_levels,
        sanity_cost_per_insight=3,
        rewards=[
            ObjectiveReward(RewardType.COSMIC_INSIGHT, 1, f"Deep understanding of {knowledge_type}"),
            ObjectiveReward(RewardType.KNOWLEDGE, 3, "Forbidden knowledge gained")
        ],
        failure_consequences=[
            ObjectiveConsequence(FailureConsequence.SAN_LOSS, 5, "Failed to comprehend cosmic truth"),
            ObjectiveConsequence(FailureConsequence.COSMIC_ATTENTION, 3, "Noticed by cosmic entities")
        ],
        **kwargs
    )


def create_sanity_dependent_investigation(
    objective_id: str,
    title: str,
    location: str,
    state_configurations: Dict[SanityState, Dict[str, Any]],
    **kwargs
) -> SanityDependentObjective:
    """Create an investigation that changes based on sanity state"""
    return SanityDependentObjective(
        objective_id=objective_id,
        title=title,
        description=f"Investigate {location} - methods depend on mental state",
        objective_type=ObjectiveType.INVESTIGATION,
        scope=ObjectiveScope.SHORT_TERM,
        priority=ObjectivePriority.NORMAL,
        state_configurations=state_configurations,
        san_risk_level=2,
        rewards=[ObjectiveReward(RewardType.KNOWLEDGE, 1, "Information gathered")],
        failure_consequences=[ObjectiveConsequence(FailureConsequence.SAN_LOSS, 2, "Disturbing findings")],
        **kwargs
    )


def create_madness_driven_objective(
    objective_id: str,
    title: str,
    required_madness: List[MadnessType],
    **kwargs
) -> MadnessObjective:
    """Create an objective that requires madness to complete"""
    return MadnessObjective(
        objective_id=objective_id,
        title=title,
        description="An action that only makes sense to a disturbed mind",
        objective_type=ObjectiveType.RITUAL,
        scope=ObjectiveScope.SHORT_TERM,
        priority=ObjectivePriority.HIGH,
        required_madness_types=set(required_madness),
        madness_progress_multiplier=2.0,
        sanity_recovery_on_completion=3,
        rewards=[
            ObjectiveReward(RewardType.SANITY_RESTORATION, 3, "Confronting madness provides clarity"),
            ObjectiveReward(RewardType.REVELATION, 1, "Madness reveals hidden truth")
        ],
        **kwargs
    )