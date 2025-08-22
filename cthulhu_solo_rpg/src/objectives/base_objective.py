"""
Base Objective System for Cthulhu Solo TRPG

This module provides the foundation for the game's objective system,
implementing the core classes and enums that support the multi-layered
goal structure designed for cosmic horror gaming.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Callable, Union
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ObjectiveStatus(Enum):
    """Current status of an objective"""
    INACTIVE = "inactive"          # Not yet activated
    ACTIVE = "active"              # Currently available to pursue
    IN_PROGRESS = "in_progress"    # Player is actively working on this
    COMPLETED = "completed"        # Successfully completed
    FAILED = "failed"              # Failed to complete
    EXPIRED = "expired"            # Time limit exceeded
    SUSPENDED = "suspended"        # Temporarily disabled
    ABANDONED = "abandoned"        # Player chose to abandon


class ObjectivePriority(Enum):
    """Priority level of objectives"""
    TRIVIAL = 1      # Optional flavor objectives
    LOW = 2          # Side objectives
    NORMAL = 3       # Standard objectives
    HIGH = 4         # Important story objectives
    CRITICAL = 5     # Essential survival objectives
    COSMIC = 6       # Reality-threatening situations


class ObjectiveType(Enum):
    """Type classification of objectives"""
    EXPLORATION = "exploration"        # Investigate locations
    INVESTIGATION = "investigation"    # Gather clues and evidence
    SOCIAL = "social"                 # Interact with NPCs
    SURVIVAL = "survival"             # Stay alive and sane
    KNOWLEDGE = "knowledge"           # Learn about the mythos
    RITUAL = "ritual"                 # Perform supernatural actions
    ESCAPE = "escape"                 # Flee from danger
    CONFRONTATION = "confrontation"   # Face cosmic horror
    PROTECTION = "protection"         # Protect others
    REVELATION = "revelation"         # Uncover truth


class ObjectiveScope(Enum):
    """Time scope of objectives"""
    IMMEDIATE = "immediate"    # 1-2 actions (1-3 minutes)
    SHORT_TERM = "short_term"  # Single scene (5-15 minutes)
    MID_TERM = "mid_term"      # Session/scenario (30-90 minutes)
    LONG_TERM = "long_term"    # Campaign arc (multiple sessions)
    META = "meta"              # Cross-campaign progression


class RewardType(Enum):
    """Types of rewards for completing objectives"""
    NONE = "none"                      # No reward (horror theme)
    KNOWLEDGE = "knowledge"            # Gain mythos knowledge
    SKILL_IMPROVEMENT = "skill"        # Improve character skills
    ITEM = "item"                      # Acquire useful item
    ALLIANCE = "alliance"              # Gain NPC ally
    SAFETY = "safety"                  # Temporary safety
    SANITY_RESTORATION = "sanity"      # Restore some SAN
    REVELATION = "revelation"          # Major story revelation
    SURVIVAL = "survival"              # Simply staying alive
    COSMIC_INSIGHT = "cosmic_insight"  # Understand cosmic truth


class FailureConsequence(Enum):
    """Types of consequences for failing objectives"""
    NONE = "none"                      # No immediate consequence
    SAN_LOSS = "san_loss"             # Lose sanity points
    HP_LOSS = "hp_loss"               # Physical harm
    RESOURCE_LOSS = "resource_loss"    # Lose items/allies
    TIME_PRESSURE = "time_pressure"    # Increase urgency
    NEW_THREAT = "new_threat"          # Spawn new danger
    REVELATION_LOST = "revelation_lost" # Miss important truth
    NPC_DEATH = "npc_death"           # Important NPC dies
    ESCALATION = "escalation"          # Situation worsens
    COSMIC_ATTENTION = "cosmic_attention" # Attract otherworldly notice


@dataclass
class ObjectiveReward:
    """Represents a reward for completing an objective"""
    reward_type: RewardType
    value: int = 0
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        if self.description:
            return f"{self.reward_type.value}: {self.description}"
        return f"{self.reward_type.value} ({self.value})"


@dataclass
class ObjectiveConsequence:
    """Represents a consequence for failing an objective"""
    consequence_type: FailureConsequence
    severity: int = 1  # 1-5 scale
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        if self.description:
            return f"{self.consequence_type.value}: {self.description}"
        return f"{self.consequence_type.value} (severity {self.severity})"


@dataclass
class ObjectiveCondition:
    """Represents a condition that must be met for objective activation/completion"""
    condition_id: str
    description: str
    check_function: Optional[Callable[..., bool]] = None
    required_value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(self, game_state: Dict[str, Any]) -> bool:
        """Evaluate if this condition is met"""
        if self.check_function:
            try:
                return self.check_function(game_state, self.required_value, self.metadata)
            except Exception as e:
                logger.error(f"Error evaluating condition {self.condition_id}: {e}")
                return False
        
        # Simple value check
        if self.condition_id in game_state:
            return game_state[self.condition_id] == self.required_value
        
        return False


class BaseObjective(ABC):
    """
    Abstract base class for all objectives in the Cthulhu Solo TRPG system.
    
    This class encapsulates the core functionality needed to represent
    goals, track progress, handle completion/failure, and integrate with
    the cosmic horror theme of the game.
    """
    
    def __init__(
        self,
        objective_id: str,
        title: str,
        description: str,
        objective_type: ObjectiveType,
        scope: ObjectiveScope,
        priority: ObjectivePriority = ObjectivePriority.NORMAL,
        time_limit: Optional[timedelta] = None,
        activation_conditions: Optional[List[ObjectiveCondition]] = None,
        completion_conditions: Optional[List[ObjectiveCondition]] = None,
        rewards: Optional[List[ObjectiveReward]] = None,
        failure_consequences: Optional[List[ObjectiveConsequence]] = None,
        parent_objective: Optional[str] = None,
        child_objectives: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a base objective"""
        self.objective_id = objective_id
        self.uuid = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.objective_type = objective_type
        self.scope = scope
        self.priority = priority
        
        # Status tracking
        self.status = ObjectiveStatus.INACTIVE
        self.progress = 0.0  # 0.0 to 1.0
        self.created_at = datetime.now()
        self.activated_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.time_limit = time_limit
        
        # Conditions and requirements
        self.activation_conditions = activation_conditions or []
        self.completion_conditions = completion_conditions or []
        
        # Rewards and consequences
        self.rewards = rewards or []
        self.failure_consequences = failure_consequences or []
        
        # Hierarchy
        self.parent_objective = parent_objective
        self.child_objectives = child_objectives or []
        
        # Additional data
        self.metadata = metadata or {}
        self.attempt_count = 0
        self.last_update = datetime.now()
        
        # Event tracking
        self.events: List[Dict[str, Any]] = []
        
        logger.debug(f"Created objective: {self.objective_id} ({self.title})")
    
    @property
    def is_active(self) -> bool:
        """Check if objective is currently active"""
        return self.status in [ObjectiveStatus.ACTIVE, ObjectiveStatus.IN_PROGRESS]
    
    @property
    def is_completed(self) -> bool:
        """Check if objective is completed"""
        return self.status == ObjectiveStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if objective has failed"""
        return self.status in [ObjectiveStatus.FAILED, ObjectiveStatus.EXPIRED, ObjectiveStatus.ABANDONED]
    
    @property
    def time_remaining(self) -> Optional[timedelta]:
        """Get remaining time for this objective"""
        if not self.time_limit or not self.activated_at:
            return None
        
        elapsed = datetime.now() - self.activated_at
        remaining = self.time_limit - elapsed
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    
    @property
    def is_expired(self) -> bool:
        """Check if objective has expired"""
        if not self.time_limit or not self.activated_at:
            return False
        
        return datetime.now() > (self.activated_at + self.time_limit)
    
    def can_activate(self, game_state: Dict[str, Any]) -> bool:
        """Check if this objective can be activated given current game state"""
        if self.status != ObjectiveStatus.INACTIVE:
            return False
        
        # Check activation conditions
        for condition in self.activation_conditions:
            if not condition.evaluate(game_state):
                return False
        
        return True
    
    def activate(self, game_state: Dict[str, Any]) -> bool:
        """Activate this objective if conditions are met"""
        if not self.can_activate(game_state):
            return False
        
        self.status = ObjectiveStatus.ACTIVE
        self.activated_at = datetime.now()
        self.last_update = datetime.now()
        
        self._log_event("activated", {"game_state_snapshot": self._capture_relevant_state(game_state)})
        
        logger.info(f"Objective activated: {self.title}")
        return True
    
    def start_progress(self) -> bool:
        """Mark objective as in progress"""
        if self.status != ObjectiveStatus.ACTIVE:
            return False
        
        self.status = ObjectiveStatus.IN_PROGRESS
        self.last_update = datetime.now()
        self._log_event("progress_started")
        
        logger.info(f"Objective progress started: {self.title}")
        return True
    
    @abstractmethod
    def update_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update objective progress based on game state and player actions.
        Must be implemented by subclasses.
        
        Args:
            game_state: Current game state
            action_data: Data about the player's recent action
            
        Returns:
            True if progress was updated, False otherwise
        """
        pass
    
    def check_completion(self, game_state: Dict[str, Any]) -> bool:
        """Check if objective is completed based on current game state"""
        if not self.is_active:
            return False
        
        # Check completion conditions
        for condition in self.completion_conditions:
            if not condition.evaluate(game_state):
                return False
        
        # If we have explicit completion conditions and they're all met, complete
        if self.completion_conditions:
            return self.complete(game_state)
        
        # Otherwise, use progress-based completion
        return self.progress >= 1.0
    
    def complete(self, game_state: Dict[str, Any]) -> bool:
        """Mark objective as completed and apply rewards"""
        if not self.is_active:
            return False
        
        self.status = ObjectiveStatus.COMPLETED
        self.progress = 1.0
        self.completed_at = datetime.now()
        self.last_update = datetime.now()
        
        # Apply rewards
        applied_rewards = self._apply_rewards(game_state)
        
        self._log_event("completed", {
            "completion_time": self.completed_at.isoformat(),
            "final_progress": self.progress,
            "rewards_applied": applied_rewards
        })
        
        logger.info(f"Objective completed: {self.title}")
        return True
    
    def fail(self, game_state: Dict[str, Any], reason: str = "") -> bool:
        """Mark objective as failed and apply consequences"""
        if self.is_completed:
            return False
        
        self.status = ObjectiveStatus.FAILED
        self.last_update = datetime.now()
        
        # Apply failure consequences
        applied_consequences = self._apply_consequences(game_state)
        
        self._log_event("failed", {
            "reason": reason,
            "final_progress": self.progress,
            "consequences_applied": applied_consequences
        })
        
        logger.warning(f"Objective failed: {self.title} - {reason}")
        return True
    
    def abandon(self) -> bool:
        """Abandon this objective (player choice)"""
        if self.is_completed:
            return False
        
        self.status = ObjectiveStatus.ABANDONED
        self.last_update = datetime.now()
        
        self._log_event("abandoned")
        
        logger.info(f"Objective abandoned: {self.title}")
        return True
    
    def suspend(self) -> bool:
        """Temporarily suspend this objective"""
        if not self.is_active:
            return False
        
        self.status = ObjectiveStatus.SUSPENDED
        self.last_update = datetime.now()
        
        self._log_event("suspended")
        
        logger.info(f"Objective suspended: {self.title}")
        return True
    
    def resume(self) -> bool:
        """Resume a suspended objective"""
        if self.status != ObjectiveStatus.SUSPENDED:
            return False
        
        self.status = ObjectiveStatus.ACTIVE
        self.last_update = datetime.now()
        
        self._log_event("resumed")
        
        logger.info(f"Objective resumed: {self.title}")
        return True
    
    def update(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Main update method called each game loop.
        Handles expiration, progress updates, and completion checks.
        """
        # Check for expiration
        if self.is_expired and self.is_active:
            self.status = ObjectiveStatus.EXPIRED
            self._apply_consequences(game_state)
            self._log_event("expired")
            logger.warning(f"Objective expired: {self.title}")
            return True
        
        # Update progress if active
        if self.is_active:
            progress_updated = self.update_progress(game_state, action_data)
            
            # Check for completion
            if self.check_completion(game_state):
                self.complete(game_state)
                return True
            
            return progress_updated
        
        return False
    
    def _apply_rewards(self, game_state: Dict[str, Any]) -> List[str]:
        """Apply rewards for completing this objective"""
        applied_rewards = []
        
        for reward in self.rewards:
            try:
                # This would be implemented by the reward system
                # For now, just log what would be applied
                applied_rewards.append(str(reward))
                logger.info(f"Applied reward: {reward}")
            except Exception as e:
                logger.error(f"Failed to apply reward {reward}: {e}")
        
        return applied_rewards
    
    def _apply_consequences(self, game_state: Dict[str, Any]) -> List[str]:
        """Apply consequences for failing this objective"""
        applied_consequences = []
        
        for consequence in self.failure_consequences:
            try:
                # This would be implemented by the consequence system
                # For now, just log what would be applied
                applied_consequences.append(str(consequence))
                logger.warning(f"Applied consequence: {consequence}")
            except Exception as e:
                logger.error(f"Failed to apply consequence {consequence}: {e}")
        
        return applied_consequences
    
    def _log_event(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        """Log an event for this objective"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "objective_id": self.objective_id,
            "status": self.status.value,
            "progress": self.progress,
            "data": data or {}
        }
        
        self.events.append(event)
        
        # Keep only last 50 events to prevent memory bloat
        if len(self.events) > 50:
            self.events = self.events[-50:]
    
    def _capture_relevant_state(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Capture relevant parts of game state for this objective"""
        # Override in subclasses to capture specific state relevant to the objective type
        relevant_keys = ["location", "san", "hp", "time", "npcs_met", "items_found"]
        return {key: game_state.get(key) for key in relevant_keys if key in game_state}
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get information for UI display"""
        time_info = None
        if self.time_remaining:
            time_info = {
                "remaining": str(self.time_remaining),
                "expired": self.is_expired
            }
        
        return {
            "id": self.objective_id,
            "title": self.title,
            "description": self.description,
            "type": self.objective_type.value,
            "scope": self.scope.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "progress": self.progress,
            "time_info": time_info,
            "rewards": [str(r) for r in self.rewards],
            "consequences": [str(c) for c in self.failure_consequences]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert objective to dictionary for serialization"""
        return {
            "objective_id": self.objective_id,
            "uuid": self.uuid,
            "title": self.title,
            "description": self.description,
            "objective_type": self.objective_type.value,
            "scope": self.scope.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "time_limit": self.time_limit.total_seconds() if self.time_limit else None,
            "parent_objective": self.parent_objective,
            "child_objectives": self.child_objectives,
            "metadata": self.metadata,
            "attempt_count": self.attempt_count,
            "events": self.events[-10:]  # Only save last 10 events
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseObjective':
        """Create objective from dictionary (for deserialization)"""
        # This would need to be implemented by concrete subclasses
        # as they need to know their specific constructor parameters
        raise NotImplementedError("Subclasses must implement from_dict method")
    
    def __str__(self) -> str:
        return f"{self.title} ({self.status.value}, {self.progress:.1%})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id='{self.objective_id}', status='{self.status.value}', progress={self.progress:.2f})>"


# Helper functions for common objective operations

def create_basic_condition(condition_id: str, description: str, required_value: Any) -> ObjectiveCondition:
    """Create a basic condition that checks game state value"""
    return ObjectiveCondition(
        condition_id=condition_id,
        description=description,
        required_value=required_value
    )

def create_location_condition(location_name: str) -> ObjectiveCondition:
    """Create a condition that checks if player is at a specific location"""
    return ObjectiveCondition(
        condition_id="current_location",
        description=f"Must be at {location_name}",
        required_value=location_name
    )

def create_item_condition(item_name: str) -> ObjectiveCondition:
    """Create a condition that checks if player has a specific item"""
    def check_item(game_state: Dict[str, Any], item: str, metadata: Dict[str, Any]) -> bool:
        inventory = game_state.get("inventory", [])
        return item in inventory
    
    return ObjectiveCondition(
        condition_id="has_item",
        description=f"Must have {item_name}",
        check_function=check_item,
        required_value=item_name
    )

def create_sanity_threshold_condition(min_san: int) -> ObjectiveCondition:
    """Create a condition that checks minimum sanity level"""
    def check_sanity(game_state: Dict[str, Any], threshold: int, metadata: Dict[str, Any]) -> bool:
        current_san = game_state.get("sanity", 0)
        return current_san >= threshold
    
    return ObjectiveCondition(
        condition_id="sanity_check",
        description=f"Must have at least {min_san} SAN",
        check_function=check_sanity,
        required_value=min_san
    )


# Standard reward configurations
KNOWLEDGE_REWARD = ObjectiveReward(RewardType.KNOWLEDGE, 1, "Gain insight into the mythos")
SURVIVAL_REWARD = ObjectiveReward(RewardType.SURVIVAL, 1, "Successfully survive the encounter")
SANITY_MINOR_REWARD = ObjectiveReward(RewardType.SANITY_RESTORATION, 1, "Restore 1d3 SAN")
SANITY_MAJOR_REWARD = ObjectiveReward(RewardType.SANITY_RESTORATION, 2, "Restore 1d6 SAN")

# Standard consequence configurations
SAN_LOSS_MINOR = ObjectiveConsequence(FailureConsequence.SAN_LOSS, 1, "Lose 1d3 SAN")
SAN_LOSS_MAJOR = ObjectiveConsequence(FailureConsequence.SAN_LOSS, 3, "Lose 1d6 SAN")
ESCALATION_MINOR = ObjectiveConsequence(FailureConsequence.ESCALATION, 1, "Situation becomes more dangerous")
COSMIC_ATTENTION = ObjectiveConsequence(FailureConsequence.COSMIC_ATTENTION, 5, "Something vast and terrible notices you")