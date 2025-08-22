"""
Achievement System for Cthulhu Solo TRPG

This module implements a comprehensive achievement system that tracks
player progress across multiple campaigns, celebrates milestones,
and provides meta-game progression elements fitting the cosmic horror theme.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Callable, Union
from dataclasses import dataclass, field
import json
from pathlib import Path

from .base_objective import ObjectiveType, ObjectiveScope, RewardType
from .san_objectives import SanityState, MadnessType, CosmicInsightLevel

logger = logging.getLogger(__name__)


class AchievementCategory(Enum):
    """Categories of achievements"""
    SURVIVAL = "survival"              # Staying alive and sane
    KNOWLEDGE = "knowledge"            # Learning mythos secrets
    INVESTIGATION = "investigation"    # Detective work
    SOCIAL = "social"                 # NPC interactions
    EXPLORATION = "exploration"       # Area discovery
    HORROR = "horror"                 # Confronting cosmic horror
    MASTERY = "mastery"               # System mastery
    NARRATIVE = "narrative"           # Story progression
    META = "meta"                     # Cross-campaign progression
    SECRET = "secret"                 # Hidden achievements


class AchievementRarity(Enum):
    """Rarity levels for achievements"""
    COMMON = 1      # Easy to obtain
    UNCOMMON = 2    # Moderate difficulty
    RARE = 3        # Challenging
    EPIC = 4        # Very difficult
    LEGENDARY = 5   # Extremely rare
    COSMIC = 6      # Almost impossible, cosmic horror themed


class AchievementTrigger(Enum):
    """What triggers achievement unlocking"""
    OBJECTIVE_COMPLETION = "objective_completion"
    STAT_THRESHOLD = "stat_threshold"
    EVENT_OCCURRENCE = "event_occurrence"
    CONDITION_MET = "condition_met"
    TIME_BASED = "time_based"
    SEQUENCE_COMPLETION = "sequence_completion"


@dataclass
class AchievementReward:
    """Reward for unlocking an achievement"""
    title: str
    description: str
    unlock_content: List[str] = field(default_factory=list)  # New content unlocked
    statistical_bonus: Dict[str, float] = field(default_factory=dict)
    cosmetic_unlocks: List[str] = field(default_factory=list)
    lore_entries: List[str] = field(default_factory=list)


@dataclass
class AchievementCriteria:
    """Criteria for unlocking an achievement"""
    trigger_type: AchievementTrigger
    target_value: Union[int, float, str, bool]
    comparison_operator: str = "eq"  # eq, gt, gte, lt, lte, in, contains
    additional_conditions: Dict[str, Any] = field(default_factory=dict)
    context_requirements: Dict[str, Any] = field(default_factory=dict)


class Achievement:
    """
    Represents a single achievement that players can unlock.
    """
    
    def __init__(
        self,
        achievement_id: str,
        title: str,
        description: str,
        category: AchievementCategory,
        rarity: AchievementRarity,
        criteria: List[AchievementCriteria],
        rewards: Optional[AchievementReward] = None,
        hidden: bool = False,
        prerequisite_achievements: Optional[List[str]] = None,
        cosmic_significance: Optional[str] = None,
        flavor_text: Optional[str] = None
    ):
        self.achievement_id = achievement_id
        self.title = title
        self.description = description
        self.category = category
        self.rarity = rarity
        self.criteria = criteria
        self.rewards = rewards or AchievementReward("Recognition", "Achievement unlocked")
        self.hidden = hidden
        self.prerequisite_achievements = prerequisite_achievements or []
        self.cosmic_significance = cosmic_significance
        self.flavor_text = flavor_text
        
        # Tracking data
        self.unlocked = False
        self.unlock_timestamp: Optional[datetime] = None
        self.progress: Dict[str, Any] = {}
        self.unlock_context: Dict[str, Any] = {}
        
        logger.debug(f"Created achievement: {achievement_id}")
    
    def check_unlock_conditions(self, game_data: Dict[str, Any], player_stats: Dict[str, Any]) -> bool:
        """Check if this achievement should be unlocked"""
        if self.unlocked:
            return False
        
        # Check prerequisites
        if self.prerequisite_achievements:
            unlocked_achievements = game_data.get('unlocked_achievements', set())
            if not all(prereq in unlocked_achievements for prereq in self.prerequisite_achievements):
                return False
        
        # Check all criteria
        for criterion in self.criteria:
            if not self._check_criterion(criterion, game_data, player_stats):
                return False
        
        return True
    
    def _check_criterion(self, criterion: AchievementCriteria, 
                        game_data: Dict[str, Any], player_stats: Dict[str, Any]) -> bool:
        """Check if a specific criterion is met"""
        if criterion.trigger_type == AchievementTrigger.STAT_THRESHOLD:
            return self._check_stat_threshold(criterion, player_stats)
        elif criterion.trigger_type == AchievementTrigger.OBJECTIVE_COMPLETION:
            return self._check_objective_completion(criterion, game_data)
        elif criterion.trigger_type == AchievementTrigger.EVENT_OCCURRENCE:
            return self._check_event_occurrence(criterion, game_data)
        elif criterion.trigger_type == AchievementTrigger.CONDITION_MET:
            return self._check_condition_met(criterion, game_data, player_stats)
        elif criterion.trigger_type == AchievementTrigger.SEQUENCE_COMPLETION:
            return self._check_sequence_completion(criterion, game_data)
        
        return False
    
    def _check_stat_threshold(self, criterion: AchievementCriteria, player_stats: Dict[str, Any]) -> bool:
        """Check statistical thresholds"""
        stat_name = criterion.additional_conditions.get('stat_name')
        if not stat_name or stat_name not in player_stats:
            return False
        
        current_value = player_stats[stat_name]
        target_value = criterion.target_value
        
        return self._compare_values(current_value, target_value, criterion.comparison_operator)
    
    def _check_objective_completion(self, criterion: AchievementCriteria, game_data: Dict[str, Any]) -> bool:
        """Check objective completion criteria"""
        completed_objectives = game_data.get('completed_objectives', [])
        
        if criterion.comparison_operator == "count":
            return len(completed_objectives) >= criterion.target_value
        elif criterion.comparison_operator == "type_count":
            objective_type = criterion.additional_conditions.get('objective_type')
            type_count = sum(1 for obj in completed_objectives 
                           if obj.get('type') == objective_type)
            return type_count >= criterion.target_value
        
        return False
    
    def _check_event_occurrence(self, criterion: AchievementCriteria, game_data: Dict[str, Any]) -> bool:
        """Check event occurrence criteria"""
        events = game_data.get('events', [])
        event_type = criterion.additional_conditions.get('event_type')
        
        if criterion.comparison_operator == "occurred":
            return any(event.get('type') == event_type for event in events)
        elif criterion.comparison_operator == "count":
            event_count = sum(1 for event in events if event.get('type') == event_type)
            return event_count >= criterion.target_value
        
        return False
    
    def _check_condition_met(self, criterion: AchievementCriteria, 
                           game_data: Dict[str, Any], player_stats: Dict[str, Any]) -> bool:
        """Check complex conditions"""
        condition_type = criterion.additional_conditions.get('condition_type')
        
        if condition_type == "sanity_state":
            current_sanity = player_stats.get('sanity', 50)
            required_state = criterion.target_value
            
            if required_state == "mad" and current_sanity <= 9:
                return True
            elif required_state == "stable" and current_sanity >= 70:
                return True
        
        elif condition_type == "cosmic_exposure":
            exposure = player_stats.get('cosmic_exposure', 0)
            return exposure >= criterion.target_value
        
        return False
    
    def _check_sequence_completion(self, criterion: AchievementCriteria, game_data: Dict[str, Any]) -> bool:
        """Check sequence completion criteria"""
        sequence_name = criterion.additional_conditions.get('sequence_name')
        completed_sequences = game_data.get('completed_sequences', [])
        
        return sequence_name in completed_sequences
    
    def _compare_values(self, current: Any, target: Any, operator: str) -> bool:
        """Compare values based on operator"""
        if operator == "eq":
            return current == target
        elif operator == "gt":
            return current > target
        elif operator == "gte":
            return current >= target
        elif operator == "lt":
            return current < target
        elif operator == "lte":
            return current <= target
        elif operator == "in":
            return current in target
        elif operator == "contains":
            return target in current
        
        return False
    
    def unlock(self, context: Dict[str, Any] = None):
        """Unlock this achievement"""
        if self.unlocked:
            return
        
        self.unlocked = True
        self.unlock_timestamp = datetime.now()
        self.unlock_context = context or {}
        
        logger.info(f"Achievement unlocked: {self.title}")
    
    def get_progress_info(self, game_data: Dict[str, Any], player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Get progress information for this achievement"""
        if self.unlocked:
            return {
                'unlocked': True,
                'unlock_timestamp': self.unlock_timestamp.isoformat() if self.unlock_timestamp else None,
                'progress': 1.0
            }
        
        # Calculate progress for criteria
        total_criteria = len(self.criteria)
        met_criteria = 0
        
        for criterion in self.criteria:
            if self._check_criterion(criterion, game_data, player_stats):
                met_criteria += 1
        
        progress = met_criteria / total_criteria if total_criteria > 0 else 0.0
        
        return {
            'unlocked': False,
            'progress': progress,
            'met_criteria': met_criteria,
            'total_criteria': total_criteria,
            'next_criterion': self._get_next_criterion_info(game_data, player_stats) if progress < 1.0 else None
        }
    
    def _get_next_criterion_info(self, game_data: Dict[str, Any], player_stats: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get information about the next unmet criterion"""
        for criterion in self.criteria:
            if not self._check_criterion(criterion, game_data, player_stats):
                return {
                    'type': criterion.trigger_type.value,
                    'description': self._describe_criterion(criterion),
                    'target_value': criterion.target_value
                }
        return None
    
    def _describe_criterion(self, criterion: AchievementCriteria) -> str:
        """Get human-readable description of criterion"""
        if criterion.trigger_type == AchievementTrigger.STAT_THRESHOLD:
            stat_name = criterion.additional_conditions.get('stat_name', 'unknown')
            return f"Reach {criterion.target_value} {stat_name}"
        elif criterion.trigger_type == AchievementTrigger.OBJECTIVE_COMPLETION:
            return f"Complete {criterion.target_value} objectives"
        elif criterion.trigger_type == AchievementTrigger.EVENT_OCCURRENCE:
            event_type = criterion.additional_conditions.get('event_type', 'event')
            return f"Experience {event_type}"
        
        return "Meet special condition"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert achievement to dictionary for serialization"""
        return {
            'achievement_id': self.achievement_id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'rarity': self.rarity.value,
            'unlocked': self.unlocked,
            'unlock_timestamp': self.unlock_timestamp.isoformat() if self.unlock_timestamp else None,
            'hidden': self.hidden,
            'cosmic_significance': self.cosmic_significance,
            'flavor_text': self.flavor_text
        }


class AchievementManager:
    """
    Manages all achievements, tracks progress, and handles unlocking.
    """
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.unlocked_achievements: Set[str] = set()
        self.achievement_categories: Dict[AchievementCategory, List[str]] = {}
        
        # Progress tracking
        self.progress_snapshots: List[Dict[str, Any]] = []
        self.unlock_history: List[Dict[str, Any]] = []
        
        # Statistics
        self.statistics = {
            'total_achievements': 0,
            'unlocked_count': 0,
            'unlock_rate': 0.0,
            'rarest_unlocked': None,
            'latest_unlock': None
        }
        
        self._initialize_default_achievements()
        logger.info("AchievementManager initialized")
    
    def _initialize_default_achievements(self):
        """Initialize default Cthulhu TRPG achievements"""
        default_achievements = [
            # Survival achievements
            Achievement(
                "first_survival",
                "The Living",
                "Survive your first supernatural encounter",
                AchievementCategory.SURVIVAL,
                AchievementRarity.COMMON,
                [AchievementCriteria(AchievementTrigger.EVENT_OCCURRENCE, True, 
                                   additional_conditions={'event_type': 'supernatural_encounter_survived'})],
                AchievementReward("Survivor's Instinct", "You've learned to recognize danger"),
                flavor_text="The first brush with the impossible leaves its mark."
            ),
            
            Achievement(
                "sanity_keeper",
                "Keeper of Reason",
                "Maintain sanity above 70 for an entire session",
                AchievementCategory.SURVIVAL,
                AchievementRarity.UNCOMMON,
                [AchievementCriteria(AchievementTrigger.STAT_THRESHOLD, 70, "gte",
                                   additional_conditions={'stat_name': 'session_min_sanity'})],
                AchievementReward("Mental Fortitude", "Resistance to madness", statistical_bonus={'sanity_resistance': 0.1}),
                flavor_text="A clear mind in a world gone mad."
            ),
            
            # Knowledge achievements
            Achievement(
                "first_truth",
                "Glimpse of Truth",
                "Gain your first piece of cosmic knowledge",
                AchievementCategory.KNOWLEDGE,
                AchievementRarity.COMMON,
                [AchievementCriteria(AchievementTrigger.STAT_THRESHOLD, 1, "gte",
                                   additional_conditions={'stat_name': 'cosmic_knowledge_count'})],
                AchievementReward("Awakened Mind", "Understanding begins", lore_entries=["cosmic_awareness_intro"]),
                flavor_text="The first step into a larger, more terrible universe."
            ),
            
            Achievement(
                "forbidden_scholar",
                "Scholar of the Forbidden",
                "Acquire knowledge of 5 different mythos entities",
                AchievementCategory.KNOWLEDGE,
                AchievementRarity.RARE,
                [AchievementCriteria(AchievementTrigger.STAT_THRESHOLD, 5, "gte",
                                   additional_conditions={'stat_name': 'known_entities_count'})],
                AchievementReward("Deep Understanding", "Profound cosmic insights", 
                                unlock_content=["advanced_lore"], statistical_bonus={'investigation_bonus': 0.15}),
                cosmic_significance="Understanding multiple cosmic entities fundamentally changes one's worldview",
                flavor_text="To know them is to invite their attention."
            ),
            
            # Investigation achievements
            Achievement(
                "first_mystery",
                "First Case",
                "Complete your first investigation objective",
                AchievementCategory.INVESTIGATION,
                AchievementRarity.COMMON,
                [AchievementCriteria(AchievementTrigger.OBJECTIVE_COMPLETION, 1, "count",
                                   additional_conditions={'objective_type': ObjectiveType.INVESTIGATION.value})],
                AchievementReward("Detective's Eye", "Enhanced observation skills"),
                flavor_text="Every great investigator starts with a single case."
            ),
            
            Achievement(
                "master_detective",
                "Master Detective",
                "Complete 25 investigation objectives",
                AchievementCategory.INVESTIGATION,
                AchievementRarity.EPIC,
                [AchievementCriteria(AchievementTrigger.OBJECTIVE_COMPLETION, 25, "count",
                                   additional_conditions={'objective_type': ObjectiveType.INVESTIGATION.value})],
                AchievementReward("Investigative Mastery", "Superior deductive abilities",
                                statistical_bonus={'investigation_success_rate': 0.2}),
                flavor_text="The threads of mystery bend to your will."
            ),
            
            # Horror achievements
            Achievement(
                "madness_embrace",
                "Embrace of Madness",
                "Continue playing while completely mad (0 SAN)",
                AchievementCategory.HORROR,
                AchievementRarity.RARE,
                [AchievementCriteria(AchievementTrigger.CONDITION_MET, "mad", 
                                   additional_conditions={'condition_type': 'sanity_state'})],
                AchievementReward("Mad Insight", "Wisdom through madness",
                                unlock_content=["madness_mechanics"], 
                                statistical_bonus={'mad_action_success': 0.3}),
                cosmic_significance="Madness can be a doorway to impossible truths",
                flavor_text="In madness, sometimes clarity is found."
            ),
            
            Achievement(
                "cosmic_witness",
                "Witness to the Cosmos",
                "Encounter 3 different cosmic entities",
                AchievementCategory.HORROR,
                AchievementRarity.LEGENDARY,
                [AchievementCriteria(AchievementTrigger.STAT_THRESHOLD, 3, "gte",
                                   additional_conditions={'stat_name': 'cosmic_encounters'})],
                AchievementReward("Cosmic Awareness", "Understanding of the infinite",
                                unlock_content=["cosmic_entities_compendium"],
                                statistical_bonus={'cosmic_resistance': 0.25}),
                cosmic_significance="To witness the cosmic entities is to understand humanity's place in the universe",
                flavor_text="You have looked upon the face of eternity."
            ),
            
            # Meta achievements
            Achievement(
                "dedicated_investigator",
                "Dedicated Investigator",
                "Play for a total of 50 hours",
                AchievementCategory.META,
                AchievementRarity.UNCOMMON,
                [AchievementCriteria(AchievementTrigger.STAT_THRESHOLD, 50, "gte",
                                   additional_conditions={'stat_name': 'total_playtime_hours'})],
                AchievementReward("Veteran Status", "Recognition of dedication",
                                cosmetic_unlocks=["veteran_title", "experience_badge"]),
                flavor_text="Dedication to the truth requires time and sacrifice."
            ),
            
            Achievement(
                "ultimate_survivor",
                "Ultimate Survivor",
                "Complete 10 different campaigns",
                AchievementCategory.META,
                AchievementRarity.LEGENDARY,
                [AchievementCriteria(AchievementTrigger.STAT_THRESHOLD, 10, "gte",
                                   additional_conditions={'stat_name': 'completed_campaigns'})],
                AchievementReward("Master Survivor", "Legendary status among investigators",
                                unlock_content=["master_difficulty", "legendary_scenarios"],
                                statistical_bonus={'all_skills': 0.1}),
                cosmic_significance="To survive so many encounters with the unknown marks you as extraordinary",
                flavor_text="You have walked through hell and emerged scarred but whole."
            ),
            
            # Secret achievements
            Achievement(
                "fourth_wall",
                "Beyond the Fourth Wall",
                "Discover the true nature of your reality",
                AchievementCategory.SECRET,
                AchievementRarity.COSMIC,
                [AchievementCriteria(AchievementTrigger.EVENT_OCCURRENCE, True,
                                   additional_conditions={'event_type': 'meta_realization'})],
                AchievementReward("True Sight", "See beyond the veil of reality",
                                unlock_content=["meta_content", "reality_mechanics"]),
                hidden=True,
                cosmic_significance="Some truths transcend even cosmic horror",
                flavor_text="The greatest horror is realizing you are just a character in someone else's story."
            )
        ]
        
        for achievement in default_achievements:
            self.add_achievement(achievement)
    
    def add_achievement(self, achievement: Achievement):
        """Add an achievement to the manager"""
        self.achievements[achievement.achievement_id] = achievement
        
        # Add to category tracking
        if achievement.category not in self.achievement_categories:
            self.achievement_categories[achievement.category] = []
        self.achievement_categories[achievement.category].append(achievement.achievement_id)
        
        self._update_statistics()
        logger.debug(f"Added achievement: {achievement.title}")
    
    def check_all_achievements(self, game_data: Dict[str, Any], player_stats: Dict[str, Any]) -> List[Achievement]:
        """Check all achievements and return newly unlocked ones"""
        newly_unlocked = []
        
        for achievement in self.achievements.values():
            if not achievement.unlocked and achievement.check_unlock_conditions(game_data, player_stats):
                achievement.unlock(game_data)
                self.unlocked_achievements.add(achievement.achievement_id)
                newly_unlocked.append(achievement)
                
                # Record unlock
                self.unlock_history.append({
                    'achievement_id': achievement.achievement_id,
                    'title': achievement.title,
                    'timestamp': achievement.unlock_timestamp.isoformat(),
                    'rarity': achievement.rarity.value,
                    'category': achievement.category.value
                })
        
        if newly_unlocked:
            self._update_statistics()
        
        return newly_unlocked
    
    def get_achievement_progress(self, achievement_id: str, 
                               game_data: Dict[str, Any], 
                               player_stats: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get progress information for a specific achievement"""
        if achievement_id not in self.achievements:
            return None
        
        achievement = self.achievements[achievement_id]
        return achievement.get_progress_info(game_data, player_stats)
    
    def get_achievements_by_category(self, category: AchievementCategory, 
                                   include_hidden: bool = False) -> List[Achievement]:
        """Get achievements by category"""
        if category not in self.achievement_categories:
            return []
        
        achievements = [self.achievements[aid] for aid in self.achievement_categories[category]]
        
        if not include_hidden:
            achievements = [ach for ach in achievements if not ach.hidden]
        
        return achievements
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements"""
        return [ach for ach in self.achievements.values() if ach.unlocked]
    
    def get_achievement_statistics(self) -> Dict[str, Any]:
        """Get comprehensive achievement statistics"""
        unlocked = self.get_unlocked_achievements()
        
        category_stats = {}
        for category in AchievementCategory:
            category_achievements = self.get_achievements_by_category(category)
            category_unlocked = [ach for ach in category_achievements if ach.unlocked]
            
            category_stats[category.value] = {
                'total': len(category_achievements),
                'unlocked': len(category_unlocked),
                'unlock_rate': len(category_unlocked) / len(category_achievements) if category_achievements else 0
            }
        
        rarity_stats = {}
        for rarity in AchievementRarity:
            rarity_achievements = [ach for ach in self.achievements.values() if ach.rarity == rarity]
            rarity_unlocked = [ach for ach in rarity_achievements if ach.unlocked]
            
            rarity_stats[rarity.value] = {
                'total': len(rarity_achievements),
                'unlocked': len(rarity_unlocked),
                'unlock_rate': len(rarity_unlocked) / len(rarity_achievements) if rarity_achievements else 0
            }
        
        return {
            'total_achievements': len(self.achievements),
            'unlocked_count': len(unlocked),
            'overall_unlock_rate': len(unlocked) / len(self.achievements) if self.achievements else 0,
            'category_breakdown': category_stats,
            'rarity_breakdown': rarity_stats,
            'recent_unlocks': self.unlock_history[-5:],  # Last 5 unlocks
            'rarest_unlocked': self._get_rarest_unlocked(),
            'completion_percentage': self._calculate_completion_percentage()
        }
    
    def _get_rarest_unlocked(self) -> Optional[Dict[str, Any]]:
        """Get the rarest unlocked achievement"""
        unlocked = self.get_unlocked_achievements()
        if not unlocked:
            return None
        
        rarest = max(unlocked, key=lambda ach: ach.rarity.value)
        return {
            'achievement_id': rarest.achievement_id,
            'title': rarest.title,
            'rarity': rarest.rarity.value
        }
    
    def _calculate_completion_percentage(self) -> float:
        """Calculate overall completion percentage"""
        if not self.achievements:
            return 0.0
        
        # Weight achievements by rarity
        total_weight = sum(ach.rarity.value for ach in self.achievements.values())
        unlocked_weight = sum(ach.rarity.value for ach in self.achievements.values() if ach.unlocked)
        
        return (unlocked_weight / total_weight) * 100 if total_weight > 0 else 0.0
    
    def _update_statistics(self):
        """Update cached statistics"""
        unlocked = self.get_unlocked_achievements()
        
        self.statistics.update({
            'total_achievements': len(self.achievements),
            'unlocked_count': len(unlocked),
            'unlock_rate': len(unlocked) / len(self.achievements) if self.achievements else 0,
            'rarest_unlocked': self._get_rarest_unlocked(),
            'latest_unlock': self.unlock_history[-1] if self.unlock_history else None
        })
    
    def save_to_file(self, file_path: str) -> bool:
        """Save achievement progress to file"""
        try:
            save_data = {
                'unlocked_achievements': list(self.unlocked_achievements),
                'unlock_history': self.unlock_history,
                'achievement_data': {aid: ach.to_dict() for aid, ach in self.achievements.items() if ach.unlocked},
                'statistics': self.statistics,
                'save_timestamp': datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Achievement progress saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save achievement progress: {e}")
            return False
    
    def load_from_file(self, file_path: str) -> bool:
        """Load achievement progress from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Restore unlocked achievements
            self.unlocked_achievements = set(save_data.get('unlocked_achievements', []))
            self.unlock_history = save_data.get('unlock_history', [])
            
            # Update achievement unlock status
            achievement_data = save_data.get('achievement_data', {})
            for achievement_id, data in achievement_data.items():
                if achievement_id in self.achievements:
                    achievement = self.achievements[achievement_id]
                    achievement.unlocked = True
                    if data.get('unlock_timestamp'):
                        achievement.unlock_timestamp = datetime.fromisoformat(data['unlock_timestamp'])
            
            self._update_statistics()
            logger.info(f"Achievement progress loaded from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load achievement progress: {e}")
            return False


# Global achievement manager instance
achievement_manager = AchievementManager()