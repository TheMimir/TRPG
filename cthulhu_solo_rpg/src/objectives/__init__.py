"""
Objective System for Cthulhu Solo TRPG

This module provides a comprehensive objective system that supports
the multi-layered goal structure designed for cosmic horror gaming.

Usage:
    from objectives import objective_manager, create_investigation_objective
    
    # Create an objective
    obj = create_investigation_objective(
        objective_id="investigate_library",
        title="Investigate the Miskatonic Library",
        location="library"
    )
    
    # Add to manager
    objective_manager.add_objective(obj)
    
    # Update with game state
    objective_manager.update_all_objectives(game_state, action_data)
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import timedelta

# Import all classes and enums
from .base_objective import (
    BaseObjective,
    ObjectiveStatus,
    ObjectivePriority, 
    ObjectiveScope,
    ObjectiveType,
    RewardType,
    FailureConsequence,
    ObjectiveReward,
    ObjectiveConsequence,
    ObjectiveCondition,
    # Helper functions
    create_basic_condition,
    create_location_condition,
    create_item_condition,
    create_sanity_threshold_condition,
    # Standard configurations
    KNOWLEDGE_REWARD,
    SURVIVAL_REWARD,
    SANITY_MINOR_REWARD,
    SANITY_MAJOR_REWARD,
    SAN_LOSS_MINOR,
    SAN_LOSS_MAJOR,
    ESCALATION_MINOR,
    COSMIC_ATTENTION
)

from .objective_manager import (
    ObjectiveManager,
    ObjectiveManagerError,
    ObjectiveRegistry,
    objective_manager  # Global singleton instance
)

from .layered_objectives import (
    ImmediateObjective,
    ShortTermObjective,
    MidTermObjective,
    LongTermObjective,
    MetaObjective
)

from .san_objectives import (
    SanityState,
    MadnessType,
    CosmicInsightLevel,
    SanityThreshold,
    MadnessEffect,
    SanityIntegratedObjective,
    SanityDependentObjective,
    CosmicInsightObjective,
    MadnessObjective,
    # Factory functions
    create_forbidden_knowledge_objective,
    create_sanity_dependent_investigation,
    create_madness_driven_objective
)

from .ai_integration import (
    AIObjectiveMode,
    DifficultyLevel,
    PlayerBehaviorPattern,
    AIObjectiveSuggestion,
    PlayerAnalysis,
    GameContextAnalysis,
    AIObjectiveGenerator,
    DynamicDifficultyAdjuster,
    AIObjectiveCoordinator,
    ai_coordinator  # Global instance
)

from .achievements import (
    AchievementCategory,
    AchievementRarity,
    AchievementTrigger,
    AchievementReward,
    AchievementCriteria,
    Achievement,
    AchievementManager,
    achievement_manager  # Global singleton instance
)

logger = logging.getLogger(__name__)

# Register all objective types with the global manager
objective_manager.register_objective_type(ImmediateObjective, "ImmediateObjective")
objective_manager.register_objective_type(ShortTermObjective, "ShortTermObjective") 
objective_manager.register_objective_type(MidTermObjective, "MidTermObjective")
objective_manager.register_objective_type(LongTermObjective, "LongTermObjective")
objective_manager.register_objective_type(MetaObjective, "MetaObjective")

# Register SAN-integrated objective types
objective_manager.register_objective_type(SanityIntegratedObjective, "SanityIntegratedObjective")
objective_manager.register_objective_type(SanityDependentObjective, "SanityDependentObjective")
objective_manager.register_objective_type(CosmicInsightObjective, "CosmicInsightObjective")
objective_manager.register_objective_type(MadnessObjective, "MadnessObjective")


# Convenience functions for creating common objective types

def create_investigation_objective(
    objective_id: str,
    title: str,
    location: str,
    required_discoveries: Optional[List[str]] = None,
    time_limit_minutes: int = 15,
    **kwargs
) -> ShortTermObjective:
    """Create a standard investigation objective"""
    return ShortTermObjective(
        objective_id=objective_id,
        title=title,
        description=f"Thoroughly investigate {location} to uncover its secrets",
        objective_type=ObjectiveType.INVESTIGATION,
        scope=ObjectiveScope.SHORT_TERM,
        priority=ObjectivePriority.NORMAL,
        time_limit=timedelta(minutes=time_limit_minutes),
        activation_conditions=[create_location_condition(location)],
        required_discoveries=set(required_discoveries or []),
        scene_context={"location": location},
        rewards=[KNOWLEDGE_REWARD],
        failure_consequences=[SAN_LOSS_MINOR],
        **kwargs
    )


def create_survival_objective(
    objective_id: str,
    title: str,
    threat_description: str,
    duration_minutes: int = 10,
    **kwargs
) -> ShortTermObjective:
    """Create a survival-focused objective"""
    return ShortTermObjective(
        objective_id=objective_id,
        title=title,
        description=f"Survive {threat_description}",
        objective_type=ObjectiveType.SURVIVAL,
        scope=ObjectiveScope.SHORT_TERM,
        priority=ObjectivePriority.HIGH,
        time_limit=timedelta(minutes=duration_minutes),
        rewards=[SURVIVAL_REWARD, SANITY_MINOR_REWARD],
        failure_consequences=[SAN_LOSS_MAJOR],
        tension_ramp_enabled=True,
        initial_tension=2,
        max_tension=5,
        **kwargs
    )


def create_social_objective(
    objective_id: str,
    title: str,
    npc_name: str,
    conversation_goals: Optional[List[str]] = None,
    **kwargs
) -> ImmediateObjective:
    """Create a social interaction objective"""
    required_actions = conversation_goals or ["initiate_conversation", "ask_questions", "conclude_conversation"]
    
    return ImmediateObjective(
        objective_id=objective_id,
        title=title,
        description=f"Engage with {npc_name} to gather information",
        objective_type=ObjectiveType.SOCIAL,
        scope=ObjectiveScope.IMMEDIATE,
        priority=ObjectivePriority.NORMAL,
        required_actions=set(required_actions),
        rewards=[KNOWLEDGE_REWARD],
        metadata={"npc_name": npc_name, "conversation_goals": conversation_goals},
        **kwargs
    )


def create_exploration_objective(
    objective_id: str,
    title: str,
    areas_to_explore: List[str],
    **kwargs
) -> ShortTermObjective:
    """Create an exploration objective for multiple areas"""
    return ShortTermObjective(
        objective_id=objective_id,
        title=title,
        description=f"Explore and map out the following areas: {', '.join(areas_to_explore)}",
        objective_type=ObjectiveType.EXPLORATION,
        scope=ObjectiveScope.SHORT_TERM,
        priority=ObjectivePriority.NORMAL,
        required_discoveries=set(f"explored_{area}" for area in areas_to_explore),
        milestone_count=len(areas_to_explore),
        rewards=[KNOWLEDGE_REWARD],
        failure_consequences=[SAN_LOSS_MINOR],
        **kwargs
    )


def create_knowledge_objective(
    objective_id: str,
    title: str,
    mythos_entity: str,
    knowledge_level: int = 1,
    **kwargs
) -> MidTermObjective:
    """Create a mythos knowledge acquisition objective"""
    return MidTermObjective(
        objective_id=objective_id,
        title=title,
        description=f"Learn about {mythos_entity} and its connection to current events",
        objective_type=ObjectiveType.KNOWLEDGE,
        scope=ObjectiveScope.MID_TERM,
        priority=ObjectivePriority.NORMAL,
        horror_revelations=[f"{mythos_entity}_basic", f"{mythos_entity}_advanced"],
        rewards=[KNOWLEDGE_REWARD],
        failure_consequences=[SAN_LOSS_MAJOR, COSMIC_ATTENTION],
        metadata={"mythos_entity": mythos_entity, "target_knowledge_level": knowledge_level},
        **kwargs
    )


def create_protection_objective(
    objective_id: str,
    title: str,
    protected_entity: str,
    threat_level: int = 3,
    **kwargs
) -> MidTermObjective:
    """Create an objective to protect someone or something"""
    return MidTermObjective(
        objective_id=objective_id,
        title=title,
        description=f"Keep {protected_entity} safe from harm",
        objective_type=ObjectiveType.PROTECTION,
        scope=ObjectiveScope.MID_TERM,
        priority=ObjectivePriority.HIGH,
        story_beats=[
            {"name": "identify_threat", "description": "Identify the nature of the threat"},
            {"name": "establish_protection", "description": "Set up protective measures"},
            {"name": "monitor_situation", "description": "Watch for signs of danger"},
            {"name": "respond_to_crisis", "description": "Handle direct threats"}
        ],
        rewards=[SURVIVAL_REWARD, ObjectiveReward(RewardType.ALLIANCE, 1, f"Gain trust of {protected_entity}")],
        failure_consequences=[
            ObjectiveConsequence(FailureConsequence.NPC_DEATH, 5, f"{protected_entity} is harmed or killed"),
            SAN_LOSS_MAJOR
        ],
        metadata={"protected_entity": protected_entity, "threat_level": threat_level},
        **kwargs
    )


def create_escape_objective(
    objective_id: str,
    title: str,
    location: str,
    urgency_level: int = 3,
    **kwargs
) -> ShortTermObjective:
    """Create an escape objective with escalating tension"""
    return ShortTermObjective(
        objective_id=objective_id,
        title=title,
        description=f"Escape from {location} before it's too late",
        objective_type=ObjectiveType.ESCAPE,
        scope=ObjectiveScope.SHORT_TERM,
        priority=ObjectivePriority.CRITICAL,
        time_limit=timedelta(minutes=10),
        required_discoveries={"exit_route", "clear_obstacles", "avoid_dangers"},
        tension_ramp_enabled=True,
        initial_tension=urgency_level,
        max_tension=5,
        rewards=[SURVIVAL_REWARD],
        failure_consequences=[
            ObjectiveConsequence(FailureConsequence.HP_LOSS, urgency_level, "Physical harm from failed escape"),
            ObjectiveConsequence(FailureConsequence.SAN_LOSS, urgency_level, "Terror from being trapped")
        ],
        metadata={"escape_location": location, "urgency_level": urgency_level},
        **kwargs
    )


def create_campaign_objective(
    objective_id: str,
    title: str,
    campaign_name: str,
    phases: List[Dict[str, Any]],
    **kwargs
) -> LongTermObjective:
    """Create a long-term campaign objective"""
    return LongTermObjective(
        objective_id=objective_id,
        title=title,
        description=f"Complete the {campaign_name} campaign and uncover its mysteries",
        objective_type=ObjectiveType.REVELATION,
        scope=ObjectiveScope.LONG_TERM,
        priority=ObjectivePriority.HIGH,
        campaign_phases=phases,
        recurring_themes=kwargs.get('themes', []),
        character_growth_goals={
            "mythos_entities": 5,
            "successful_investigations": 3,
            "survival_encounters": 10
        },
        rewards=[
            ObjectiveReward(RewardType.COSMIC_INSIGHT, 1, "Gain deep understanding of cosmic truth"),
            ObjectiveReward(RewardType.KNOWLEDGE, 5, "Extensive mythos knowledge")
        ],
        failure_consequences=[COSMIC_ATTENTION],
        metadata={"campaign_name": campaign_name},
        **kwargs
    )


def create_mastery_objective(
    objective_id: str,
    title: str,
    mastery_type: str,
    unlock_criteria: Dict[str, Any],
    **kwargs
) -> MetaObjective:
    """Create a meta objective for player mastery"""
    return MetaObjective(
        objective_id=objective_id,
        title=title,
        description=f"Achieve mastery in {mastery_type} across multiple campaigns",
        objective_type=ObjectiveType.KNOWLEDGE,
        scope=ObjectiveScope.META,
        priority=ObjectivePriority.LOW,
        unlock_criteria={f"{mastery_type}_mastery": unlock_criteria},
        mastery_categories={mastery_type: {}},
        rewards=[
            ObjectiveReward(RewardType.COSMIC_INSIGHT, 1, f"Master-level understanding of {mastery_type}")
        ],
        metadata={"mastery_type": mastery_type},
        **kwargs
    )


# Template registration for common objectives
def register_default_templates():
    """Register default objective templates"""
    
    # Investigation templates
    objective_manager.register_template("library_investigation", {
        "objective_type": "ShortTermObjective",
        "title": "Investigate the Library",
        "description": "Search the library for clues and forbidden knowledge",
        "objective_type": ObjectiveType.INVESTIGATION,
        "scope": ObjectiveScope.SHORT_TERM,
        "required_discoveries": ["ancient_book", "hidden_note", "strange_symbol"],
        "rewards": [KNOWLEDGE_REWARD],
        "failure_consequences": [SAN_LOSS_MINOR]
    })
    
    objective_manager.register_template("basement_exploration", {
        "objective_type": "ShortTermObjective", 
        "title": "Explore the Basement",
        "description": "Investigate the basement despite the feeling of dread",
        "objective_type": ObjectiveType.EXPLORATION,
        "scope": ObjectiveScope.SHORT_TERM,
        "tension_ramp_enabled": True,
        "initial_tension": 2,
        "max_tension": 4,
        "rewards": [KNOWLEDGE_REWARD],
        "failure_consequences": [SAN_LOSS_MAJOR]
    })
    
    objective_manager.register_template("npc_interview", {
        "objective_type": "ImmediateObjective",
        "title": "Interview NPC",
        "description": "Conduct a thorough interview to gather information",
        "objective_type": ObjectiveType.SOCIAL,
        "scope": ObjectiveScope.IMMEDIATE,
        "required_actions": {"ask_about_events", "probe_for_details", "conclude_interview"},
        "rewards": [KNOWLEDGE_REWARD]
    })
    
    objective_manager.register_template("cult_investigation", {
        "objective_type": "MidTermObjective",
        "title": "Investigate the Cult",
        "description": "Uncover the cult's plans and membership",
        "objective_type": ObjectiveType.INVESTIGATION,
        "scope": ObjectiveScope.MID_TERM,
        "investigation_branches": {
            "member_identification": 0.0,
            "ritual_discovery": 0.0,
            "location_mapping": 0.0
        },
        "horror_revelations": ["cult_purpose", "ritual_details", "cosmic_connection"],
        "rewards": [KNOWLEDGE_REWARD],
        "failure_consequences": [SAN_LOSS_MAJOR, COSMIC_ATTENTION]
    })
    
    objective_manager.register_template("survival_horror", {
        "objective_type": "ShortTermObjective",
        "title": "Survive the Encounter", 
        "description": "Survive a terrifying supernatural encounter",
        "objective_type": ObjectiveType.SURVIVAL,
        "scope": ObjectiveScope.SHORT_TERM,
        "priority": ObjectivePriority.CRITICAL,
        "tension_ramp_enabled": True,
        "initial_tension": 3,
        "max_tension": 5,
        "time_limit": timedelta(minutes=8),
        "rewards": [SURVIVAL_REWARD, SANITY_MINOR_REWARD],
        "failure_consequences": [SAN_LOSS_MAJOR]
    })
    
    logger.info("Registered default objective templates")


# Initialize default templates
register_default_templates()

# Export convenience functions for creating objectives
__all__ = [
    # Core classes
    "BaseObjective",
    "ObjectiveManager", 
    "ObjectiveManagerError",
    "objective_manager",
    
    # Enums
    "ObjectiveStatus",
    "ObjectivePriority",
    "ObjectiveScope", 
    "ObjectiveType",
    "RewardType",
    "FailureConsequence",
    
    # Data classes
    "ObjectiveReward",
    "ObjectiveConsequence", 
    "ObjectiveCondition",
    
    # Layered objectives
    "ImmediateObjective",
    "ShortTermObjective",
    "MidTermObjective", 
    "LongTermObjective",
    "MetaObjective",
    
    # SAN-integrated objectives
    "SanityState",
    "MadnessType", 
    "CosmicInsightLevel",
    "SanityThreshold",
    "MadnessEffect",
    "SanityIntegratedObjective",
    "SanityDependentObjective",
    "CosmicInsightObjective",
    "MadnessObjective",
    
    # Helper functions
    "create_basic_condition",
    "create_location_condition",
    "create_item_condition", 
    "create_sanity_threshold_condition",
    
    # Convenience factories
    "create_investigation_objective",
    "create_survival_objective",
    "create_social_objective",
    "create_exploration_objective",
    "create_knowledge_objective",
    "create_protection_objective",
    "create_escape_objective",
    "create_campaign_objective",
    "create_mastery_objective",
    
    # SAN-specific factories
    "create_forbidden_knowledge_objective",
    "create_sanity_dependent_investigation",
    "create_madness_driven_objective",
    
    # AI integration
    "AIObjectiveMode",
    "DifficultyLevel", 
    "PlayerBehaviorPattern",
    "AIObjectiveSuggestion",
    "PlayerAnalysis",
    "GameContextAnalysis",
    "AIObjectiveGenerator",
    "DynamicDifficultyAdjuster",
    "AIObjectiveCoordinator",
    "ai_coordinator",
    
    # Achievement system
    "AchievementCategory",
    "AchievementRarity",
    "AchievementTrigger",
    "AchievementReward",
    "AchievementCriteria",
    "Achievement",
    "AchievementManager",
    "achievement_manager",
    
    # Standard configurations
    "KNOWLEDGE_REWARD",
    "SURVIVAL_REWARD", 
    "SANITY_MINOR_REWARD",
    "SANITY_MAJOR_REWARD",
    "SAN_LOSS_MINOR",
    "SAN_LOSS_MAJOR",
    "ESCALATION_MINOR",
    "COSMIC_ATTENTION"
]

logger.info("Objective system initialized with all components")