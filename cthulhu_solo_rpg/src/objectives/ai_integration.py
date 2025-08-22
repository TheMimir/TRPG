"""
AI Integration for Objective System

This module provides AI-powered dynamic objective generation, adjustment,
and management for the Cthulhu Solo TRPG system. It integrates with the
existing AI agents to create responsive and intelligent goal management.
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Callable, Union, Tuple
from dataclasses import dataclass, field
import json

from .base_objective import (
    BaseObjective, ObjectiveStatus, ObjectivePriority, ObjectiveScope,
    ObjectiveType, ObjectiveReward, ObjectiveConsequence
)
from .objective_manager import ObjectiveManager, objective_manager
from .san_objectives import SanityState, MadnessType, CosmicInsightLevel

logger = logging.getLogger(__name__)


class AIObjectiveMode(Enum):
    """Modes for AI objective generation"""
    REACTIVE = "reactive"      # React to player actions
    PROACTIVE = "proactive"    # Anticipate player needs
    ADAPTIVE = "adaptive"      # Learn from player patterns
    NARRATIVE = "narrative"    # Follow story structure
    DYNAMIC = "dynamic"        # Real-time situation response


class DifficultyLevel(Enum):
    """Difficulty levels for objective adjustment"""
    TRIVIAL = 1
    EASY = 2
    NORMAL = 3
    HARD = 4
    EXTREME = 5
    IMPOSSIBLE = 6  # For cosmic horror scenarios


class PlayerBehaviorPattern(Enum):
    """Identified player behavior patterns"""
    CAUTIOUS = "cautious"           # Prefers safe, low-risk actions
    AGGRESSIVE = "aggressive"       # Takes bold, high-risk actions
    INVESTIGATIVE = "investigative" # Focuses on discovery and knowledge
    SOCIAL = "social"              # Prefers interaction with NPCs
    SURVIVAL = "survival"          # Focuses on staying alive
    EXPLORER = "explorer"          # Likes to explore new areas
    PUZZLE_SOLVER = "puzzle_solver" # Enjoys complex challenges
    HORROR_SEEKER = "horror_seeker" # Actively seeks scary encounters


@dataclass
class AIObjectiveSuggestion:
    """AI-generated objective suggestion"""
    objective_type: str
    title: str
    description: str
    priority: ObjectivePriority
    scope: ObjectiveScope
    estimated_duration: timedelta
    confidence: float  # 0.0-1.0
    reasoning: str
    context_factors: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlayerAnalysis:
    """Analysis of player behavior and preferences"""
    primary_pattern: PlayerBehaviorPattern
    secondary_patterns: List[PlayerBehaviorPattern]
    risk_tolerance: float  # 0.0-1.0
    exploration_preference: float  # 0.0-1.0
    social_engagement: float  # 0.0-1.0
    horror_tolerance: float  # 0.0-1.0
    completion_rate: float  # 0.0-1.0
    average_session_time: float  # hours
    preferred_difficulty: DifficultyLevel
    adaptive_needs: List[str]


@dataclass
class GameContextAnalysis:
    """Analysis of current game context"""
    current_tension_level: int  # 1-5
    story_phase: str
    location_type: str
    npcs_present: List[str]
    recent_events: List[str]
    available_resources: List[str]
    time_pressure: bool
    sanity_state: SanityState
    cosmic_exposure: int
    threat_level: int


class AIObjectiveGenerator:
    """
    AI-powered objective generator that creates contextually appropriate
    objectives based on game state, player behavior, and story needs.
    """
    
    def __init__(self, ai_client=None):
        self.ai_client = ai_client
        self.generation_mode = AIObjectiveMode.ADAPTIVE
        self.player_analysis: Optional[PlayerAnalysis] = None
        self.context_history: List[GameContextAnalysis] = []
        
        # Learning parameters
        self.objective_success_history: Dict[str, List[bool]] = {}
        self.player_feedback_history: List[Dict[str, Any]] = []
        self.context_pattern_library: Dict[str, List[AIObjectiveSuggestion]] = {}
        
        # Generation settings
        self.max_suggestions_per_call = 3
        self.min_confidence_threshold = 0.6
        self.narrative_coherence_weight = 0.7
        self.player_preference_weight = 0.8
        
        logger.info("AIObjectiveGenerator initialized")
    
    async def analyze_player_behavior(self, 
                                    game_history: List[Dict[str, Any]], 
                                    objective_history: List[Dict[str, Any]]) -> PlayerAnalysis:
        """Analyze player behavior patterns from game history"""
        # Analyze action patterns
        action_counts = {}
        risk_levels = []
        exploration_actions = 0
        social_actions = 0
        completion_data = []
        
        for session in game_history:
            for action in session.get('actions', []):
                action_type = action.get('type', 'unknown')
                action_counts[action_type] = action_counts.get(action_type, 0) + 1
                
                # Analyze risk taking
                if action.get('risk_level'):
                    risk_levels.append(action['risk_level'])
                
                # Track exploration
                if 'explore' in action_type or 'investigate' in action_type:
                    exploration_actions += 1
                
                # Track social interaction
                if 'talk' in action_type or 'social' in action_type:
                    social_actions += 1
        
        # Analyze objective completion
        for obj_record in objective_history:
            completion_data.append(obj_record.get('completed', False))
        
        # Calculate metrics
        total_actions = sum(action_counts.values())
        risk_tolerance = sum(risk_levels) / len(risk_levels) if risk_levels else 0.5
        exploration_preference = exploration_actions / max(total_actions, 1)
        social_engagement = social_actions / max(total_actions, 1)
        completion_rate = sum(completion_data) / len(completion_data) if completion_data else 0.5
        
        # Determine primary pattern
        primary_pattern = self._determine_primary_pattern(action_counts, risk_tolerance, exploration_preference)
        
        # Use AI to enhance analysis if available
        if self.ai_client:
            enhanced_analysis = await self._ai_enhanced_player_analysis(
                action_counts, risk_tolerance, exploration_preference, social_engagement
            )
            if enhanced_analysis:
                primary_pattern = enhanced_analysis.get('primary_pattern', primary_pattern)
        
        return PlayerAnalysis(
            primary_pattern=primary_pattern,
            secondary_patterns=self._determine_secondary_patterns(action_counts),
            risk_tolerance=risk_tolerance,
            exploration_preference=exploration_preference,
            social_engagement=social_engagement,
            horror_tolerance=self._calculate_horror_tolerance(game_history),
            completion_rate=completion_rate,
            average_session_time=self._calculate_average_session_time(game_history),
            preferred_difficulty=self._determine_preferred_difficulty(objective_history),
            adaptive_needs=self._identify_adaptive_needs(action_counts, completion_rate)
        )
    
    def _determine_primary_pattern(self, action_counts: Dict[str, int], 
                                 risk_tolerance: float, exploration_preference: float) -> PlayerBehaviorPattern:
        """Determine the player's primary behavior pattern"""
        total_actions = sum(action_counts.values())
        
        # Calculate pattern scores
        pattern_scores = {
            PlayerBehaviorPattern.CAUTIOUS: action_counts.get('careful_action', 0) / total_actions + (1 - risk_tolerance),
            PlayerBehaviorPattern.AGGRESSIVE: action_counts.get('bold_action', 0) / total_actions + risk_tolerance,
            PlayerBehaviorPattern.INVESTIGATIVE: (action_counts.get('investigate', 0) + action_counts.get('analyze', 0)) / total_actions,
            PlayerBehaviorPattern.SOCIAL: action_counts.get('talk', 0) / total_actions,
            PlayerBehaviorPattern.EXPLORER: exploration_preference,
            PlayerBehaviorPattern.SURVIVAL: action_counts.get('flee', 0) / total_actions + action_counts.get('hide', 0) / total_actions
        }
        
        return max(pattern_scores.keys(), key=lambda k: pattern_scores[k])
    
    def _determine_secondary_patterns(self, action_counts: Dict[str, int]) -> List[PlayerBehaviorPattern]:
        """Determine secondary behavior patterns"""
        # Simplified implementation - could be enhanced with more sophisticated analysis
        return [PlayerBehaviorPattern.INVESTIGATIVE, PlayerBehaviorPattern.CAUTIOUS]
    
    def _calculate_horror_tolerance(self, game_history: List[Dict[str, Any]]) -> float:
        """Calculate player's tolerance for horror content"""
        horror_encounters = 0
        horror_completions = 0
        
        for session in game_history:
            for event in session.get('events', []):
                if event.get('type') == 'horror_encounter':
                    horror_encounters += 1
                    if event.get('completed', False):
                        horror_completions += 1
        
        return horror_completions / max(horror_encounters, 1) if horror_encounters > 0 else 0.5
    
    def _calculate_average_session_time(self, game_history: List[Dict[str, Any]]) -> float:
        """Calculate average session time in hours"""
        session_times = [session.get('duration_hours', 1.0) for session in game_history]
        return sum(session_times) / len(session_times) if session_times else 1.0
    
    def _determine_preferred_difficulty(self, objective_history: List[Dict[str, Any]]) -> DifficultyLevel:
        """Determine player's preferred difficulty level"""
        difficulty_completions = {}
        
        for obj in objective_history:
            difficulty = obj.get('difficulty', 'normal')
            completed = obj.get('completed', False)
            
            if difficulty not in difficulty_completions:
                difficulty_completions[difficulty] = {'total': 0, 'completed': 0}
            
            difficulty_completions[difficulty]['total'] += 1
            if completed:
                difficulty_completions[difficulty]['completed'] += 1
        
        # Find difficulty with best completion rate (but not too easy)
        best_difficulty = DifficultyLevel.NORMAL
        best_score = 0
        
        for difficulty, data in difficulty_completions.items():
            if data['total'] > 0:
                completion_rate = data['completed'] / data['total']
                # Prefer higher difficulties with good completion rates
                score = completion_rate * DifficultyLevel[difficulty.upper()].value
                if score > best_score:
                    best_score = score
                    best_difficulty = DifficultyLevel[difficulty.upper()]
        
        return best_difficulty
    
    def _identify_adaptive_needs(self, action_counts: Dict[str, int], completion_rate: float) -> List[str]:
        """Identify what the player might need more of"""
        needs = []
        
        if completion_rate < 0.3:
            needs.append("easier_objectives")
        elif completion_rate > 0.9:
            needs.append("harder_objectives")
        
        total_actions = sum(action_counts.values())
        if action_counts.get('social', 0) / total_actions < 0.1:
            needs.append("social_prompts")
        
        if action_counts.get('explore', 0) / total_actions < 0.2:
            needs.append("exploration_encouragement")
        
        return needs
    
    async def _ai_enhanced_player_analysis(self, action_counts: Dict[str, int], 
                                         risk_tolerance: float, exploration_preference: float,
                                         social_engagement: float) -> Optional[Dict[str, Any]]:
        """Use AI to enhance player behavior analysis"""
        if not self.ai_client:
            return None
        
        try:
            analysis_prompt = f"""
            Analyze this player's behavior pattern in a Cthulhu TRPG:
            
            Action Distribution: {action_counts}
            Risk Tolerance: {risk_tolerance:.2f} (0=cautious, 1=reckless)
            Exploration Preference: {exploration_preference:.2f}
            Social Engagement: {social_engagement:.2f}
            
            Determine the primary behavior pattern from: cautious, aggressive, investigative, social, explorer, survival, puzzle_solver, horror_seeker
            
            Provide analysis in JSON format with 'primary_pattern' and 'reasoning' fields.
            """
            
            response = await self.ai_client.generate(analysis_prompt, use_cache=True)
            if response.is_success:
                try:
                    return json.loads(response.content)
                except json.JSONDecodeError:
                    logger.warning("AI analysis response was not valid JSON")
            
        except Exception as e:
            logger.error(f"Error in AI-enhanced player analysis: {e}")
        
        return None
    
    async def generate_objective_suggestions(self, 
                                           game_state: Dict[str, Any],
                                           current_objectives: List[BaseObjective],
                                           context_analysis: GameContextAnalysis) -> List[AIObjectiveSuggestion]:
        """Generate AI-powered objective suggestions"""
        suggestions = []
        
        # Analyze current situation
        missing_objective_types = self._identify_missing_objective_types(current_objectives)
        story_needs = self._analyze_story_needs(game_state, context_analysis)
        player_needs = self._analyze_player_needs(game_state, current_objectives)
        
        # Generate suggestions based on different criteria
        for need_type, need_data in story_needs.items():
            suggestion = await self._generate_story_driven_suggestion(need_type, need_data, game_state, context_analysis)
            if suggestion and suggestion.confidence >= self.min_confidence_threshold:
                suggestions.append(suggestion)
        
        for need_type, need_data in player_needs.items():
            suggestion = await self._generate_player_driven_suggestion(need_type, need_data, game_state, context_analysis)
            if suggestion and suggestion.confidence >= self.min_confidence_threshold:
                suggestions.append(suggestion)
        
        # Fill gaps with contextual objectives
        for obj_type in missing_objective_types:
            suggestion = await self._generate_contextual_suggestion(obj_type, game_state, context_analysis)
            if suggestion and suggestion.confidence >= self.min_confidence_threshold:
                suggestions.append(suggestion)
        
        # Sort by confidence and limit
        suggestions.sort(key=lambda s: s.confidence, reverse=True)
        return suggestions[:self.max_suggestions_per_call]
    
    def _identify_missing_objective_types(self, current_objectives: List[BaseObjective]) -> List[ObjectiveType]:
        """Identify what types of objectives are missing"""
        current_types = {obj.objective_type for obj in current_objectives if obj.is_active}
        
        # Essential objective types for a balanced experience
        essential_types = {
            ObjectiveType.INVESTIGATION,
            ObjectiveType.EXPLORATION,
            ObjectiveType.SOCIAL,
            ObjectiveType.SURVIVAL
        }
        
        return list(essential_types - current_types)
    
    def _analyze_story_needs(self, game_state: Dict[str, Any], context: GameContextAnalysis) -> Dict[str, Dict[str, Any]]:
        """Analyze what the story needs for proper pacing and development"""
        needs = {}
        
        # Tension management
        if context.current_tension_level < 2:
            needs['increase_tension'] = {
                'priority': ObjectivePriority.NORMAL,
                'type': ObjectiveType.CONFRONTATION,
                'reasoning': 'Story needs more tension'
            }
        elif context.current_tension_level > 4:
            needs['reduce_tension'] = {
                'priority': ObjectivePriority.HIGH,
                'type': ObjectiveType.SURVIVAL,
                'reasoning': 'Player needs relief from high tension'
            }
        
        # Information flow
        if context.story_phase in ['investigation', 'discovery']:
            needs['information_gathering'] = {
                'priority': ObjectivePriority.HIGH,
                'type': ObjectiveType.INVESTIGATION,
                'reasoning': 'Story requires information gathering'
            }
        
        # Character development
        if len(context.npcs_present) > 0 and context.story_phase != 'action':
            needs['character_development'] = {
                'priority': ObjectivePriority.NORMAL,
                'type': ObjectiveType.SOCIAL,
                'reasoning': 'Opportunity for character interaction'
            }
        
        return needs
    
    def _analyze_player_needs(self, game_state: Dict[str, Any], current_objectives: List[BaseObjective]) -> Dict[str, Dict[str, Any]]:
        """Analyze what the player needs for engagement and progression"""
        needs = {}
        
        if not self.player_analysis:
            return needs
        
        # Adaptive needs based on player analysis
        for need in self.player_analysis.adaptive_needs:
            if need == "easier_objectives":
                needs['easier_challenge'] = {
                    'difficulty_modifier': -1,
                    'type': ObjectiveType.EXPLORATION,
                    'reasoning': 'Player needs easier objectives'
                }
            elif need == "social_prompts":
                needs['social_engagement'] = {
                    'priority': ObjectivePriority.HIGH,
                    'type': ObjectiveType.SOCIAL,
                    'reasoning': 'Player needs more social interaction'
                }
        
        # Pattern-based needs
        if self.player_analysis.primary_pattern == PlayerBehaviorPattern.INVESTIGATIVE:
            if not any(obj.objective_type == ObjectiveType.KNOWLEDGE for obj in current_objectives):
                needs['knowledge_seeking'] = {
                    'priority': ObjectivePriority.HIGH,
                    'type': ObjectiveType.KNOWLEDGE,
                    'reasoning': 'Investigative player needs knowledge objectives'
                }
        
        return needs
    
    async def _generate_story_driven_suggestion(self, 
                                              need_type: str, 
                                              need_data: Dict[str, Any],
                                              game_state: Dict[str, Any],
                                              context: GameContextAnalysis) -> Optional[AIObjectiveSuggestion]:
        """Generate suggestion based on story needs"""
        if need_type == 'increase_tension':
            return AIObjectiveSuggestion(
                objective_type="ShortTermObjective",
                title="Investigate Disturbing Sounds",
                description="Strange noises coming from nearby demand investigation",
                priority=ObjectivePriority.NORMAL,
                scope=ObjectiveScope.SHORT_TERM,
                estimated_duration=timedelta(minutes=10),
                confidence=0.8,
                reasoning="Story needs tension increase",
                context_factors=['low_tension', 'story_pacing'],
                parameters={
                    'objective_type': ObjectiveType.INVESTIGATION,
                    'tension_ramp_enabled': True,
                    'initial_tension': context.current_tension_level + 1
                }
            )
        
        elif need_type == 'information_gathering':
            return await self._generate_investigation_suggestion(game_state, context)
        
        elif need_type == 'character_development':
            return await self._generate_social_suggestion(game_state, context)
        
        return None
    
    async def _generate_player_driven_suggestion(self,
                                               need_type: str,
                                               need_data: Dict[str, Any],
                                               game_state: Dict[str, Any],
                                               context: GameContextAnalysis) -> Optional[AIObjectiveSuggestion]:
        """Generate suggestion based on player needs"""
        if need_type == 'social_engagement':
            return await self._generate_social_suggestion(game_state, context)
        
        elif need_type == 'knowledge_seeking':
            return await self._generate_knowledge_suggestion(game_state, context)
        
        return None
    
    async def _generate_contextual_suggestion(self,
                                            obj_type: ObjectiveType,
                                            game_state: Dict[str, Any],
                                            context: GameContextAnalysis) -> Optional[AIObjectiveSuggestion]:
        """Generate contextual suggestion for missing objective type"""
        if obj_type == ObjectiveType.EXPLORATION:
            return await self._generate_exploration_suggestion(game_state, context)
        elif obj_type == ObjectiveType.SOCIAL:
            return await self._generate_social_suggestion(game_state, context)
        elif obj_type == ObjectiveType.INVESTIGATION:
            return await self._generate_investigation_suggestion(game_state, context)
        elif obj_type == ObjectiveType.SURVIVAL:
            return await self._generate_survival_suggestion(game_state, context)
        
        return None
    
    async def _generate_investigation_suggestion(self, game_state: Dict[str, Any], context: GameContextAnalysis) -> AIObjectiveSuggestion:
        """Generate an investigation objective suggestion"""
        return AIObjectiveSuggestion(
            objective_type="ShortTermObjective",
            title=f"Examine {context.location_type}",
            description=f"Carefully investigate the {context.location_type} for clues",
            priority=ObjectivePriority.NORMAL,
            scope=ObjectiveScope.SHORT_TERM,
            estimated_duration=timedelta(minutes=15),
            confidence=0.7,
            reasoning="Investigation needed for story progression",
            context_factors=['location_type', 'story_phase'],
            parameters={
                'objective_type': ObjectiveType.INVESTIGATION,
                'required_discoveries': [f"examine_{context.location_type}", "find_clue"],
                'milestone_count': 2
            }
        )
    
    async def _generate_social_suggestion(self, game_state: Dict[str, Any], context: GameContextAnalysis) -> Optional[AIObjectiveSuggestion]:
        """Generate a social interaction objective suggestion"""
        if not context.npcs_present:
            return None
        
        npc = context.npcs_present[0]  # Pick first available NPC
        
        return AIObjectiveSuggestion(
            objective_type="ImmediateObjective",
            title=f"Speak with {npc}",
            description=f"Engage {npc} in conversation to gather information",
            priority=ObjectivePriority.NORMAL,
            scope=ObjectiveScope.IMMEDIATE,
            estimated_duration=timedelta(minutes=5),
            confidence=0.8,
            reasoning="NPC available for interaction",
            context_factors=['npcs_present', 'social_opportunity'],
            parameters={
                'objective_type': ObjectiveType.SOCIAL,
                'required_actions': {"initiate_conversation", "ask_questions", "conclude_conversation"},
                'metadata': {'npc_name': npc}
            }
        )
    
    async def _generate_exploration_suggestion(self, game_state: Dict[str, Any], context: GameContextAnalysis) -> AIObjectiveSuggestion:
        """Generate an exploration objective suggestion"""
        return AIObjectiveSuggestion(
            objective_type="ShortTermObjective",
            title="Explore Nearby Areas",
            description="Survey the surrounding area for points of interest",
            priority=ObjectivePriority.LOW,
            scope=ObjectiveScope.SHORT_TERM,
            estimated_duration=timedelta(minutes=12),
            confidence=0.6,
            reasoning="Exploration provides context and opportunities",
            context_factors=['location_context', 'exploration_opportunities'],
            parameters={
                'objective_type': ObjectiveType.EXPLORATION,
                'required_discoveries': {"survey_area", "identify_landmarks", "note_features"},
                'milestone_count': 3
            }
        )
    
    async def _generate_survival_suggestion(self, game_state: Dict[str, Any], context: GameContextAnalysis) -> AIObjectiveSuggestion:
        """Generate a survival objective suggestion"""
        return AIObjectiveSuggestion(
            objective_type="ShortTermObjective",
            title="Ensure Safety",
            description="Take measures to ensure your continued safety",
            priority=ObjectivePriority.HIGH,
            scope=ObjectiveScope.SHORT_TERM,
            estimated_duration=timedelta(minutes=8),
            confidence=0.9,
            reasoning="Survival is always a priority in cosmic horror",
            context_factors=['threat_level', 'safety_concerns'],
            parameters={
                'objective_type': ObjectiveType.SURVIVAL,
                'tension_ramp_enabled': True,
                'initial_tension': max(1, context.threat_level),
                'max_tension': 5
            }
        )
    
    async def _generate_knowledge_suggestion(self, game_state: Dict[str, Any], context: GameContextAnalysis) -> AIObjectiveSuggestion:
        """Generate a knowledge-seeking objective suggestion"""
        return AIObjectiveSuggestion(
            objective_type="MidTermObjective",
            title="Uncover Hidden Knowledge",
            description="Seek out forbidden knowledge related to current events",
            priority=ObjectivePriority.NORMAL,
            scope=ObjectiveScope.MID_TERM,
            estimated_duration=timedelta(minutes=30),
            confidence=0.7,
            reasoning="Knowledge objectives satisfy investigative players",
            context_factors=['cosmic_exposure', 'knowledge_opportunities'],
            parameters={
                'objective_type': ObjectiveType.KNOWLEDGE,
                'horror_revelations': ["initial_truth", "deeper_understanding"],
                'san_risk_level': 3
            }
        )


class DynamicDifficultyAdjuster:
    """
    Adjusts objective difficulty based on player performance and preferences.
    """
    
    def __init__(self):
        self.target_success_rate = 0.7  # Target 70% success rate
        self.adjustment_sensitivity = 0.1
        self.recent_performance_window = 10  # Last 10 objectives
        self.difficulty_history: List[Tuple[DifficultyLevel, bool]] = []
        
    def analyze_performance(self, objective_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze recent objective completion performance"""
        recent_objectives = objective_history[-self.recent_performance_window:]
        
        if not recent_objectives:
            return {'success_rate': 0.5, 'average_difficulty': 3.0, 'trend': 0.0}
        
        successes = sum(1 for obj in recent_objectives if obj.get('completed', False))
        success_rate = successes / len(recent_objectives)
        
        difficulties = [obj.get('difficulty_level', 3) for obj in recent_objectives]
        average_difficulty = sum(difficulties) / len(difficulties)
        
        # Calculate trend (improvement/decline over time)
        if len(recent_objectives) >= 5:
            first_half = recent_objectives[:len(recent_objectives)//2]
            second_half = recent_objectives[len(recent_objectives)//2:]
            
            first_success_rate = sum(1 for obj in first_half if obj.get('completed', False)) / len(first_half)
            second_success_rate = sum(1 for obj in second_half if obj.get('completed', False)) / len(second_half)
            
            trend = second_success_rate - first_success_rate
        else:
            trend = 0.0
        
        return {
            'success_rate': success_rate,
            'average_difficulty': average_difficulty,
            'trend': trend,
            'sample_size': len(recent_objectives)
        }
    
    def calculate_difficulty_adjustment(self, performance: Dict[str, float]) -> float:
        """Calculate how much to adjust difficulty"""
        success_rate = performance['success_rate']
        trend = performance['trend']
        
        # Base adjustment based on success rate
        rate_difference = success_rate - self.target_success_rate
        base_adjustment = -rate_difference * self.adjustment_sensitivity * 2  # Negative because lower success = higher difficulty needed
        
        # Trend adjustment
        trend_adjustment = -trend * self.adjustment_sensitivity
        
        # Combined adjustment
        total_adjustment = base_adjustment + trend_adjustment
        
        # Clamp adjustment to reasonable range
        return max(-1.0, min(1.0, total_adjustment))
    
    def adjust_objective_difficulty(self, base_objective: BaseObjective, 
                                  adjustment: float, 
                                  game_context: GameContextAnalysis) -> BaseObjective:
        """Apply difficulty adjustment to an objective"""
        # Adjust time limits
        if hasattr(base_objective, 'time_limit') and base_objective.time_limit:
            if adjustment > 0:  # Make easier
                base_objective.time_limit = base_objective.time_limit * (1 + adjustment * 0.5)
            else:  # Make harder
                base_objective.time_limit = base_objective.time_limit * (1 + adjustment * 0.3)
        
        # Adjust milestone requirements
        if hasattr(base_objective, 'milestone_count'):
            if adjustment > 0:  # Make easier
                base_objective.milestone_count = max(1, int(base_objective.milestone_count * (1 - adjustment * 0.3)))
            else:  # Make harder
                base_objective.milestone_count = int(base_objective.milestone_count * (1 - adjustment * 0.2))
        
        # Adjust SAN risk
        if hasattr(base_objective, 'san_risk_level'):
            if adjustment > 0:  # Make easier (less SAN risk)
                base_objective.san_risk_level = max(1, int(base_objective.san_risk_level * (1 - adjustment * 0.4)))
            else:  # Make harder (more SAN risk)
                base_objective.san_risk_level = min(5, int(base_objective.san_risk_level * (1 - adjustment * 0.3)))
        
        # Adjust priority based on difficulty
        if adjustment < -0.5:  # Much harder
            current_priority = base_objective.priority.value
            base_objective.priority = ObjectivePriority(min(6, current_priority + 1))
        elif adjustment > 0.5:  # Much easier
            current_priority = base_objective.priority.value
            base_objective.priority = ObjectivePriority(max(1, current_priority - 1))
        
        return base_objective


class AIObjectiveCoordinator:
    """
    Coordinates AI-driven objective management with the main objective system.
    """
    
    def __init__(self, ai_client=None):
        self.ai_client = ai_client
        self.generator = AIObjectiveGenerator(ai_client)
        self.difficulty_adjuster = DynamicDifficultyAdjuster()
        
        # Integration state
        self.last_analysis_time = datetime.now()
        self.analysis_interval = timedelta(minutes=5)
        self.player_analysis: Optional[PlayerAnalysis] = None
        
        # Suggestion history
        self.suggestion_history: List[Dict[str, Any]] = []
        self.implemented_suggestions: Set[str] = set()
        
        logger.info("AIObjectiveCoordinator initialized")
    
    def set_ai_client(self, ai_client):
        """Set or update the AI client"""
        self.ai_client = ai_client
        self.generator.ai_client = ai_client
        logger.info("AI client updated in coordinator")
    
    async def update_player_analysis(self, game_history: List[Dict[str, Any]], 
                                   objective_history: List[Dict[str, Any]]):
        """Update player behavior analysis"""
        self.player_analysis = await self.generator.analyze_player_behavior(game_history, objective_history)
        self.generator.player_analysis = self.player_analysis
        logger.info(f"Player analysis updated: primary pattern = {self.player_analysis.primary_pattern.value}")
    
    async def suggest_objectives(self, game_state: Dict[str, Any], 
                               current_objectives: List[BaseObjective] = None,
                               limit: int = 5) -> List[AIObjectiveSuggestion]:
        """Get AI-generated objective suggestions"""
        if current_objectives is None:
            current_objectives = []
            
        # Create context analysis
        context = self._create_context_analysis(game_state)
        
        # Generate suggestions
        suggestions = await self.generator.generate_objective_suggestions(
            game_state, current_objectives, context
        )
        
        # Apply difficulty adjustments if we have performance data
        if hasattr(game_state, 'objective_history'):
            performance = self.difficulty_adjuster.analyze_performance(game_state['objective_history'])
            difficulty_adjustment = self.difficulty_adjuster.calculate_difficulty_adjustment(performance)
            
            # Adjust suggestion parameters based on difficulty
            for suggestion in suggestions:
                if 'estimated_duration' in suggestion.parameters:
                    duration = suggestion.estimated_duration
                    if difficulty_adjustment > 0:  # Make easier
                        suggestion.estimated_duration = duration * (1 + difficulty_adjustment * 0.3)
                    else:  # Make harder
                        suggestion.estimated_duration = duration * (1 + difficulty_adjustment * 0.2)
        
        # Store suggestion history
        self.suggestion_history.extend([{
            'timestamp': datetime.now().isoformat(),
            'suggestion': suggestion,
            'implemented': False
        } for suggestion in suggestions])
        
        return suggestions[:limit]
    
    def _create_context_analysis(self, game_state: Dict[str, Any]) -> GameContextAnalysis:
        """Create context analysis from game state"""
        return GameContextAnalysis(
            current_tension_level=game_state.get('tension_level', 2),
            story_phase=game_state.get('story_phase', 'investigation'),
            location_type=game_state.get('current_location', 'unknown'),
            npcs_present=game_state.get('npcs_present', []),
            recent_events=game_state.get('recent_events', []),
            available_resources=game_state.get('inventory', []),
            time_pressure=game_state.get('time_pressure', False),
            sanity_state=SanityState(game_state.get('sanity_state', 'stable')),
            cosmic_exposure=game_state.get('cosmic_exposure', 0),
            threat_level=game_state.get('threat_level', 1)
        )
    
    async def implement_suggestion(self, suggestion: AIObjectiveSuggestion, 
                                 game_state: Dict[str, Any]) -> Optional[BaseObjective]:
        """Implement an AI suggestion as an actual objective"""
        try:
            # Create objective using the objective manager
            objective = objective_manager.create_objective(
                suggestion.objective_type,
                f"ai_generated_{len(self.implemented_suggestions)}",
                title=suggestion.title,
                description=suggestion.description,
                objective_type=suggestion.parameters.get('objective_type', ObjectiveType.INVESTIGATION),
                scope=suggestion.scope,
                priority=suggestion.priority,
                **suggestion.parameters
            )
            
            # Track implementation
            suggestion_id = f"{suggestion.title}_{datetime.now().timestamp()}"
            self.implemented_suggestions.add(suggestion_id)
            
            # Update suggestion history
            for record in self.suggestion_history:
                if record['suggestion'] == suggestion:
                    record['implemented'] = True
                    record['objective_id'] = objective.objective_id
                    break
            
            logger.info(f"Implemented AI suggestion: {suggestion.title}")
            return objective
            
        except Exception as e:
            logger.error(f"Failed to implement AI suggestion: {e}")
            return None
    
    def get_ai_statistics(self) -> Dict[str, Any]:
        """Get statistics about AI objective management"""
        total_suggestions = len(self.suggestion_history)
        implemented_count = sum(1 for record in self.suggestion_history if record['implemented'])
        
        return {
            'total_suggestions': total_suggestions,
            'implemented_suggestions': implemented_count,
            'implementation_rate': implemented_count / max(total_suggestions, 1),
            'player_analysis': self.player_analysis.__dict__ if self.player_analysis else None,
            'last_analysis_time': self.last_analysis_time.isoformat()
        }


# Global AI coordinator instance
ai_coordinator = AIObjectiveCoordinator()