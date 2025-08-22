"""
Layered Objective Classes for Cthulhu Solo TRPG

This module implements the multi-layered objective system that provides
different types of goals based on their time scope and complexity,
from immediate actions to meta-campaign progression.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Callable
from dataclasses import dataclass, field

from .base_objective import (
    BaseObjective, ObjectiveStatus, ObjectivePriority, ObjectiveScope,
    ObjectiveType, ObjectiveReward, ObjectiveConsequence, ObjectiveCondition
)

logger = logging.getLogger(__name__)


class ImmediateObjective(BaseObjective):
    """
    Immediate objectives that can be completed in 1-3 minutes.
    These provide instant feedback and keep players engaged.
    
    Examples:
    - Examine a specific object
    - Talk to an NPC
    - Move to a location
    - Use a skill
    """
    
    def __init__(self, *args, **kwargs):
        # Force appropriate settings for immediate objectives
        kwargs['scope'] = ObjectiveScope.IMMEDIATE
        kwargs['time_limit'] = kwargs.get('time_limit', timedelta(minutes=5))
        
        super().__init__(*args, **kwargs)
        
        # Immediate objectives have simple completion criteria
        self.required_actions: Set[str] = set(kwargs.get('required_actions', []))
        self.completed_actions: Set[str] = set()
        
        # Quick feedback settings
        self.auto_complete_on_action = kwargs.get('auto_complete_on_action', True)
        self.provide_immediate_feedback = kwargs.get('provide_immediate_feedback', True)
    
    def update_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update progress based on player actions"""
        if not self.is_active:
            return False
        
        progress_made = False
        
        # Track completed actions
        if action_data:
            action_type = action_data.get('action_type', '')
            if action_type in self.required_actions:
                self.completed_actions.add(action_type)
                progress_made = True
                
                if self.provide_immediate_feedback:
                    self._log_event('action_completed', {
                        'action': action_type,
                        'remaining': list(self.required_actions - self.completed_actions)
                    })
        
        # Update progress percentage
        if self.required_actions:
            self.progress = len(self.completed_actions) / len(self.required_actions)
        else:
            # For objectives without specific actions, use simple completion check
            self.progress = 1.0 if self._check_simple_completion(game_state) else 0.0
        
        self.last_update = datetime.now()
        
        # Auto-complete if enabled and conditions met
        if self.auto_complete_on_action and self.progress >= 1.0:
            self.complete(game_state)
        
        return progress_made
    
    def _check_simple_completion(self, game_state: Dict[str, Any]) -> bool:
        """Check for simple completion based on game state"""
        # This can be overridden for specific immediate objectives
        # For example, "be at location X" or "have item Y"
        return False
    
    def add_required_action(self, action_type: str):
        """Add a required action to complete this objective"""
        self.required_actions.add(action_type)
        # Recalculate progress
        if self.required_actions:
            self.progress = len(self.completed_actions) / len(self.required_actions)
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get display information including action checklist"""
        info = super().get_display_info()
        info.update({
            'required_actions': list(self.required_actions),
            'completed_actions': list(self.completed_actions),
            'remaining_actions': list(self.required_actions - self.completed_actions),
            'immediate_feedback': self.provide_immediate_feedback
        })
        return info


class ShortTermObjective(BaseObjective):
    """
    Short-term objectives for single scenes (5-15 minutes).
    These drive engagement within specific situations.
    
    Examples:
    - Investigate a room thoroughly
    - Conduct an interview with an NPC
    - Solve a puzzle
    - Survive a specific encounter
    """
    
    def __init__(self, *args, **kwargs):
        kwargs['scope'] = ObjectiveScope.SHORT_TERM
        kwargs['time_limit'] = kwargs.get('time_limit', timedelta(minutes=20))
        
        super().__init__(*args, **kwargs)
        
        # Short-term objectives can have sub-objectives
        self.sub_objectives: List[str] = kwargs.get('sub_objectives', [])
        self.milestone_count = kwargs.get('milestone_count', 3)
        self.milestones_completed = 0
        
        # Context tracking
        self.scene_context: Dict[str, Any] = kwargs.get('scene_context', {})
        self.required_discoveries: Set[str] = set(kwargs.get('required_discoveries', []))
        self.discoveries_made: Set[str] = set()
        
        # Intensity tracking for horror pacing
        self.tension_ramp_enabled = kwargs.get('tension_ramp_enabled', True)
        self.initial_tension = kwargs.get('initial_tension', 1)
        self.max_tension = kwargs.get('max_tension', 3)
    
    def update_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update progress with milestone and discovery tracking"""
        if not self.is_active:
            return False
        
        progress_made = False
        old_progress = self.progress
        
        # Track discoveries
        if action_data and 'discovery' in action_data:
            discovery = action_data['discovery']
            if discovery in self.required_discoveries and discovery not in self.discoveries_made:
                self.discoveries_made.add(discovery)
                progress_made = True
                self._log_event('discovery_made', {'discovery': discovery})
        
        # Track milestone completion
        if action_data and action_data.get('milestone_completed'):
            self.milestones_completed = min(self.milestones_completed + 1, self.milestone_count)
            progress_made = True
            self._log_event('milestone_completed', {
                'milestone': self.milestones_completed,
                'total': self.milestone_count
            })
        
        # Calculate progress from multiple factors
        discovery_progress = len(self.discoveries_made) / max(len(self.required_discoveries), 1)
        milestone_progress = self.milestones_completed / self.milestone_count
        
        # Weight the progress calculation
        if self.required_discoveries and self.milestone_count > 0:
            self.progress = (discovery_progress * 0.6) + (milestone_progress * 0.4)
        elif self.required_discoveries:
            self.progress = discovery_progress
        else:
            self.progress = milestone_progress
        
        # Handle tension ramping for horror effect
        if self.tension_ramp_enabled and progress_made:
            self._update_tension_level(game_state)
        
        self.last_update = datetime.now()
        return progress_made
    
    def _update_tension_level(self, game_state: Dict[str, Any]):
        """Update tension level based on progress"""
        tension_level = self.initial_tension + (self.progress * (self.max_tension - self.initial_tension))
        
        self._log_event('tension_updated', {
            'tension_level': tension_level,
            'progress': self.progress
        })
        
        # This could trigger AI to adjust narrative tone
        if 'tension_callbacks' in self.metadata:
            for callback in self.metadata['tension_callbacks']:
                try:
                    callback(tension_level, self.progress)
                except Exception as e:
                    logger.error(f"Error in tension callback: {e}")
    
    def add_milestone(self) -> bool:
        """Add a milestone completion"""
        if self.milestones_completed < self.milestone_count:
            self.milestones_completed += 1
            return True
        return False
    
    def add_discovery(self, discovery: str):
        """Add a required discovery"""
        self.required_discoveries.add(discovery)
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get display information including milestones and discoveries"""
        info = super().get_display_info()
        info.update({
            'milestones': {
                'completed': self.milestones_completed,
                'total': self.milestone_count
            },
            'discoveries': {
                'required': list(self.required_discoveries),
                'made': list(self.discoveries_made),
                'remaining': list(self.required_discoveries - self.discoveries_made)
            },
            'scene_context': self.scene_context
        })
        return info


class MidTermObjective(BaseObjective):
    """
    Mid-term objectives for complete scenarios (30-90 minutes).
    These provide structure and purpose to entire game sessions.
    
    Examples:
    - Investigate the mysterious disappearances
    - Escape from the haunted mansion
    - Uncover the cult's plans
    - Protect important NPCs from danger
    """
    
    def __init__(self, *args, **kwargs):
        kwargs['scope'] = ObjectiveScope.MID_TERM
        kwargs['time_limit'] = kwargs.get('time_limit', timedelta(hours=2))
        
        super().__init__(*args, **kwargs)
        
        # Mid-term objectives have complex progression
        self.investigation_branches: Dict[str, float] = kwargs.get('investigation_branches', {})
        self.story_beats: List[Dict[str, Any]] = kwargs.get('story_beats', [])
        self.current_beat_index = 0
        
        # Character development integration
        self.skill_challenges: Dict[str, int] = kwargs.get('skill_challenges', {})
        self.skills_tested: Dict[str, int] = {}
        
        # Horror progression
        self.san_loss_threshold = kwargs.get('san_loss_threshold', 10)
        self.accumulated_san_loss = 0
        self.horror_revelations: List[str] = kwargs.get('horror_revelations', [])
        self.revelations_unlocked: Set[str] = set()
        
        # Multiple completion paths
        self.completion_paths: Dict[str, Dict[str, Any]] = kwargs.get('completion_paths', {})
        self.active_path: Optional[str] = None
    
    def update_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update progress with complex scenario tracking"""
        if not self.is_active:
            return False
        
        progress_made = False
        
        # Track investigation branches
        if action_data and 'investigation_branch' in action_data:
            branch = action_data['investigation_branch']
            advancement = action_data.get('advancement', 0.1)
            
            if branch in self.investigation_branches:
                old_value = self.investigation_branches[branch]
                self.investigation_branches[branch] = min(1.0, old_value + advancement)
                progress_made = True
                
                self._log_event('investigation_advanced', {
                    'branch': branch,
                    'progress': self.investigation_branches[branch],
                    'advancement': advancement
                })
        
        # Track story beats
        if action_data and action_data.get('story_beat_completed'):
            if self.current_beat_index < len(self.story_beats):
                self.current_beat_index += 1
                progress_made = True
                self._log_event('story_beat_completed', {
                    'beat_index': self.current_beat_index - 1,
                    'total_beats': len(self.story_beats)
                })
        
        # Track skill challenges
        if action_data and 'skill_used' in action_data:
            skill = action_data['skill_used']
            if skill in self.skill_challenges:
                self.skills_tested[skill] = self.skills_tested.get(skill, 0) + 1
                progress_made = True
        
        # Track SAN loss for horror progression
        if action_data and 'san_loss' in action_data:
            self.accumulated_san_loss += action_data['san_loss']
            if self.accumulated_san_loss >= self.san_loss_threshold:
                self._trigger_horror_escalation(game_state)
        
        # Track horror revelations
        if action_data and 'revelation' in action_data:
            revelation = action_data['revelation']
            if revelation in self.horror_revelations and revelation not in self.revelations_unlocked:
                self.revelations_unlocked.add(revelation)
                progress_made = True
                self._log_event('horror_revelation', {'revelation': revelation})
        
        # Calculate overall progress
        self._calculate_mid_term_progress()
        
        # Check for completion path activation
        self._check_completion_paths(game_state)
        
        self.last_update = datetime.now()
        return progress_made
    
    def _calculate_mid_term_progress(self):
        """Calculate complex progress based on multiple factors"""
        progress_components = []
        
        # Investigation branches progress
        if self.investigation_branches:
            branch_progress = sum(self.investigation_branches.values()) / len(self.investigation_branches)
            progress_components.append(('investigation', branch_progress, 0.4))
        
        # Story beats progress
        if self.story_beats:
            beat_progress = self.current_beat_index / len(self.story_beats)
            progress_components.append(('story', beat_progress, 0.3))
        
        # Horror revelations progress
        if self.horror_revelations:
            revelation_progress = len(self.revelations_unlocked) / len(self.horror_revelations)
            progress_components.append(('horror', revelation_progress, 0.2))
        
        # Skill challenges progress
        if self.skill_challenges:
            completed_challenges = sum(1 for skill, required in self.skill_challenges.items()
                                     if self.skills_tested.get(skill, 0) >= required)
            skill_progress = completed_challenges / len(self.skill_challenges)
            progress_components.append(('skills', skill_progress, 0.1))
        
        # Weighted average
        if progress_components:
            total_weight = sum(weight for _, _, weight in progress_components)
            weighted_sum = sum(progress * weight for _, progress, weight in progress_components)
            self.progress = weighted_sum / total_weight
        else:
            self.progress = 0.0
    
    def _trigger_horror_escalation(self, game_state: Dict[str, Any]):
        """Trigger horror escalation when SAN loss threshold is reached"""
        self._log_event('horror_escalation', {
            'san_loss': self.accumulated_san_loss,
            'threshold': self.san_loss_threshold
        })
        
        # Reset threshold for next escalation
        self.san_loss_threshold *= 1.5
        
        # This could trigger AI to increase horror intensity
        if 'horror_callbacks' in self.metadata:
            for callback in self.metadata['horror_callbacks']:
                try:
                    callback(self.accumulated_san_loss, game_state)
                except Exception as e:
                    logger.error(f"Error in horror escalation callback: {e}")
    
    def _check_completion_paths(self, game_state: Dict[str, Any]):
        """Check if any completion paths have been activated"""
        for path_name, path_data in self.completion_paths.items():
            if self.active_path is None:  # Only activate one path
                requirements = path_data.get('requirements', {})
                if self._check_path_requirements(requirements, game_state):
                    self.active_path = path_name
                    self._log_event('completion_path_activated', {'path': path_name})
                    break
    
    def _check_path_requirements(self, requirements: Dict[str, Any], game_state: Dict[str, Any]) -> bool:
        """Check if path requirements are met"""
        for req_type, req_value in requirements.items():
            if req_type == 'min_investigation_progress':
                avg_progress = sum(self.investigation_branches.values()) / len(self.investigation_branches)
                if avg_progress < req_value:
                    return False
            elif req_type == 'required_revelations':
                if not all(rev in self.revelations_unlocked for rev in req_value):
                    return False
            elif req_type == 'min_story_beat':
                if self.current_beat_index < req_value:
                    return False
        
        return True
    
    def get_current_story_beat(self) -> Optional[Dict[str, Any]]:
        """Get the current story beat"""
        if self.current_beat_index < len(self.story_beats):
            return self.story_beats[self.current_beat_index]
        return None
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get comprehensive display information"""
        info = super().get_display_info()
        info.update({
            'investigation_branches': self.investigation_branches,
            'story_progress': {
                'current_beat': self.current_beat_index,
                'total_beats': len(self.story_beats),
                'current_beat_data': self.get_current_story_beat()
            },
            'horror_progression': {
                'san_loss': self.accumulated_san_loss,
                'revelations_unlocked': list(self.revelations_unlocked),
                'total_revelations': len(self.horror_revelations)
            },
            'skill_challenges': self.skill_challenges,
            'skills_tested': self.skills_tested,
            'active_completion_path': self.active_path
        })
        return info


class LongTermObjective(BaseObjective):
    """
    Long-term objectives spanning multiple sessions.
    These provide overarching campaign goals and character development.
    
    Examples:
    - Uncover the truth about the Whisperer in Darkness
    - Prevent the cosmic cult from completing their ritual
    - Develop resistance to mythos influence
    - Build a network of allies and knowledge
    """
    
    def __init__(self, *args, **kwargs):
        kwargs['scope'] = ObjectiveScope.LONG_TERM
        kwargs['time_limit'] = kwargs.get('time_limit', None)  # No time limit by default
        
        super().__init__(*args, **kwargs)
        
        # Campaign-spanning progression
        self.campaign_phases: List[Dict[str, Any]] = kwargs.get('campaign_phases', [])
        self.current_phase = 0
        self.phase_progress: Dict[int, float] = {}
        
        # Character development integration
        self.character_growth_goals: Dict[str, Any] = kwargs.get('character_growth_goals', {})
        self.mythos_knowledge_levels: Dict[str, int] = kwargs.get('mythos_knowledge_levels', {})
        
        # Recurring elements
        self.recurring_themes: List[str] = kwargs.get('recurring_themes', [])
        self.theme_encounters: Dict[str, int] = {}
        
        # Long-term consequences
        self.world_state_changes: List[Dict[str, Any]] = []
        self.npc_relationship_changes: Dict[str, int] = {}
        
        # Cross-scenario persistence
        self.persistent_elements: Dict[str, Any] = kwargs.get('persistent_elements', {})
    
    def update_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update long-term progress across multiple sessions"""
        if not self.is_active:
            return False
        
        progress_made = False
        
        # Track campaign phase progression
        if action_data and 'phase_advancement' in action_data:
            phase_idx = action_data.get('phase_index', self.current_phase)
            advancement = action_data['phase_advancement']
            
            old_progress = self.phase_progress.get(phase_idx, 0.0)
            self.phase_progress[phase_idx] = min(1.0, old_progress + advancement)
            
            # Check for phase completion
            if self.phase_progress[phase_idx] >= 1.0 and phase_idx == self.current_phase:
                self._complete_current_phase(game_state)
            
            progress_made = True
        
        # Track mythos knowledge accumulation
        if action_data and 'mythos_knowledge' in action_data:
            entity = action_data['mythos_knowledge']['entity']
            level_gain = action_data['mythos_knowledge'].get('level_gain', 1)
            
            old_level = self.mythos_knowledge_levels.get(entity, 0)
            self.mythos_knowledge_levels[entity] = old_level + level_gain
            
            progress_made = True
            self._log_event('mythos_knowledge_gained', {
                'entity': entity,
                'new_level': self.mythos_knowledge_levels[entity],
                'gain': level_gain
            })
        
        # Track theme encounters
        if action_data and 'theme_encounter' in action_data:
            theme = action_data['theme_encounter']
            if theme in self.recurring_themes:
                self.theme_encounters[theme] = self.theme_encounters.get(theme, 0) + 1
                progress_made = True
        
        # Track world state changes
        if action_data and 'world_change' in action_data:
            self.world_state_changes.append({
                'timestamp': datetime.now().isoformat(),
                'change': action_data['world_change'],
                'session': game_state.get('current_session', 'unknown')
            })
            progress_made = True
        
        # Track NPC relationship changes
        if action_data and 'npc_relationship' in action_data:
            npc = action_data['npc_relationship']['npc']
            change = action_data['npc_relationship']['change']
            
            old_value = self.npc_relationship_changes.get(npc, 0)
            self.npc_relationship_changes[npc] = old_value + change
            progress_made = True
        
        # Calculate overall long-term progress
        self._calculate_long_term_progress()
        
        self.last_update = datetime.now()
        return progress_made
    
    def _complete_current_phase(self, game_state: Dict[str, Any]):
        """Complete the current campaign phase"""
        if self.current_phase < len(self.campaign_phases):
            phase_data = self.campaign_phases[self.current_phase]
            
            self._log_event('campaign_phase_completed', {
                'phase': self.current_phase,
                'phase_name': phase_data.get('name', f'Phase {self.current_phase}'),
                'completion_time': datetime.now().isoformat()
            })
            
            # Advance to next phase
            self.current_phase += 1
            
            # Apply phase completion effects
            if 'completion_effects' in phase_data:
                self._apply_phase_effects(phase_data['completion_effects'], game_state)
    
    def _apply_phase_effects(self, effects: Dict[str, Any], game_state: Dict[str, Any]):
        """Apply effects from completing a campaign phase"""
        for effect_type, effect_data in effects.items():
            if effect_type == 'unlock_knowledge':
                for entity, level in effect_data.items():
                    self.mythos_knowledge_levels[entity] = max(
                        self.mythos_knowledge_levels.get(entity, 0), level
                    )
            elif effect_type == 'world_state':
                self.world_state_changes.append({
                    'timestamp': datetime.now().isoformat(),
                    'change': effect_data,
                    'source': 'phase_completion'
                })
    
    def _calculate_long_term_progress(self):
        """Calculate overall long-term objective progress"""
        progress_components = []
        
        # Campaign phases progress
        if self.campaign_phases:
            completed_phases = sum(1 for i in range(len(self.campaign_phases))
                                 if self.phase_progress.get(i, 0.0) >= 1.0)
            current_phase_progress = self.phase_progress.get(self.current_phase, 0.0)
            
            total_phase_progress = (completed_phases + current_phase_progress) / len(self.campaign_phases)
            progress_components.append(('phases', total_phase_progress, 0.5))
        
        # Character growth progress
        if self.character_growth_goals:
            growth_achievements = 0
            for goal_type, target_value in self.character_growth_goals.items():
                if goal_type == 'mythos_entities':
                    entities_known = len([e for e, level in self.mythos_knowledge_levels.items() if level > 0])
                    if entities_known >= target_value:
                        growth_achievements += 1
            
            growth_progress = growth_achievements / len(self.character_growth_goals)
            progress_components.append(('growth', growth_progress, 0.3))
        
        # Theme exploration progress
        if self.recurring_themes:
            explored_themes = len([theme for theme in self.recurring_themes
                                 if self.theme_encounters.get(theme, 0) > 0])
            theme_progress = explored_themes / len(self.recurring_themes)
            progress_components.append(('themes', theme_progress, 0.2))
        
        # Calculate weighted progress
        if progress_components:
            total_weight = sum(weight for _, _, weight in progress_components)
            weighted_sum = sum(progress * weight for _, progress, weight in progress_components)
            self.progress = weighted_sum / total_weight
        else:
            self.progress = 0.0
    
    def get_current_phase_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current campaign phase"""
        if self.current_phase < len(self.campaign_phases):
            phase = self.campaign_phases[self.current_phase].copy()
            phase['progress'] = self.phase_progress.get(self.current_phase, 0.0)
            return phase
        return None
    
    def advance_phase_progress(self, advancement: float) -> bool:
        """Advance progress in the current phase"""
        if self.current_phase < len(self.campaign_phases):
            old_progress = self.phase_progress.get(self.current_phase, 0.0)
            self.phase_progress[self.current_phase] = min(1.0, old_progress + advancement)
            return True
        return False
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get comprehensive long-term objective information"""
        info = super().get_display_info()
        info.update({
            'campaign_progression': {
                'current_phase': self.current_phase,
                'total_phases': len(self.campaign_phases),
                'current_phase_info': self.get_current_phase_info(),
                'phase_progress': self.phase_progress
            },
            'mythos_knowledge': self.mythos_knowledge_levels,
            'character_growth': self.character_growth_goals,
            'theme_encounters': self.theme_encounters,
            'world_changes': len(self.world_state_changes),
            'npc_relationships': self.npc_relationship_changes
        })
        return info


class MetaObjective(BaseObjective):
    """
    Meta objectives that span multiple campaigns and characters.
    These track player progression and mastery of the Cthulhu mythos.
    
    Examples:
    - Master investigator (across multiple characters)
    - Mythos scholar (deep knowledge accumulation)
    - Survivor (successfully complete X scenarios)
    - Cosmic explorer (encounter diverse mythos entities)
    """
    
    def __init__(self, *args, **kwargs):
        kwargs['scope'] = ObjectiveScope.META
        kwargs['time_limit'] = None  # Meta objectives have no time limit
        
        super().__init__(*args, **kwargs)
        
        # Cross-campaign tracking
        self.campaigns_participated: Set[str] = set(kwargs.get('campaigns_participated', []))
        self.characters_used: Set[str] = set(kwargs.get('characters_used', []))
        self.total_playtime_hours = kwargs.get('total_playtime_hours', 0.0)
        
        # Mastery tracking
        self.mastery_categories: Dict[str, Dict[str, int]] = kwargs.get('mastery_categories', {})
        self.achievement_unlocks: List[Dict[str, Any]] = []
        
        # Cross-character learning
        self.learned_patterns: Set[str] = set(kwargs.get('learned_patterns', []))
        self.survival_strategies: Dict[str, int] = kwargs.get('survival_strategies', {})
        
        # Meta-game progression
        self.unlock_criteria: Dict[str, Any] = kwargs.get('unlock_criteria', {})
        self.unlocked_content: Set[str] = set(kwargs.get('unlocked_content', []))
    
    def update_progress(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update meta progression across campaigns"""
        if not self.is_active:
            return False
        
        progress_made = False
        
        # Track campaign participation
        current_campaign = game_state.get('campaign_id')
        if current_campaign and current_campaign not in self.campaigns_participated:
            self.campaigns_participated.add(current_campaign)
            progress_made = True
            self._log_event('new_campaign_participated', {'campaign': current_campaign})
        
        # Track character usage
        current_character = game_state.get('character_id')
        if current_character and current_character not in self.characters_used:
            self.characters_used.add(current_character)
            progress_made = True
        
        # Track playtime
        if action_data and 'session_duration' in action_data:
            self.total_playtime_hours += action_data['session_duration']
            progress_made = True
        
        # Track mastery progression
        if action_data and 'mastery_advancement' in action_data:
            category = action_data['mastery_advancement']['category']
            skill = action_data['mastery_advancement']['skill']
            advancement = action_data['mastery_advancement'].get('advancement', 1)
            
            if category not in self.mastery_categories:
                self.mastery_categories[category] = {}
            
            old_level = self.mastery_categories[category].get(skill, 0)
            self.mastery_categories[category][skill] = old_level + advancement
            progress_made = True
        
        # Track pattern learning
        if action_data and 'pattern_learned' in action_data:
            pattern = action_data['pattern_learned']
            if pattern not in self.learned_patterns:
                self.learned_patterns.add(pattern)
                progress_made = True
                self._log_event('pattern_learned', {'pattern': pattern})
        
        # Track survival strategies
        if action_data and 'survival_strategy' in action_data:
            strategy = action_data['survival_strategy']
            success = action_data.get('strategy_success', True)
            
            if success:
                self.survival_strategies[strategy] = self.survival_strategies.get(strategy, 0) + 1
                progress_made = True
        
        # Check for content unlocks
        if progress_made:
            self._check_content_unlocks()
        
        # Calculate meta progress
        self._calculate_meta_progress()
        
        self.last_update = datetime.now()
        return progress_made
    
    def _check_content_unlocks(self):
        """Check if any new content should be unlocked"""
        for unlock_name, criteria in self.unlock_criteria.items():
            if unlock_name not in self.unlocked_content and self._check_unlock_criteria(criteria):
                self.unlocked_content.add(unlock_name)
                self.achievement_unlocks.append({
                    'unlock': unlock_name,
                    'timestamp': datetime.now().isoformat(),
                    'criteria_met': criteria
                })
                self._log_event('content_unlocked', {'unlock': unlock_name})
    
    def _check_unlock_criteria(self, criteria: Dict[str, Any]) -> bool:
        """Check if unlock criteria are met"""
        for criterion_type, criterion_value in criteria.items():
            if criterion_type == 'min_campaigns':
                if len(self.campaigns_participated) < criterion_value:
                    return False
            elif criterion_type == 'min_characters':
                if len(self.characters_used) < criterion_value:
                    return False
            elif criterion_type == 'min_playtime':
                if self.total_playtime_hours < criterion_value:
                    return False
            elif criterion_type == 'required_patterns':
                if not all(pattern in self.learned_patterns for pattern in criterion_value):
                    return False
            elif criterion_type == 'mastery_level':
                category = criterion_value['category']
                skill = criterion_value['skill']
                min_level = criterion_value['level']
                
                if (category not in self.mastery_categories or
                    self.mastery_categories[category].get(skill, 0) < min_level):
                    return False
        
        return True
    
    def _calculate_meta_progress(self):
        """Calculate overall meta objective progress"""
        # Meta objectives use complex criteria-based progress
        if not self.unlock_criteria:
            # If no specific criteria, use simple metrics
            self.progress = min(1.0, (
                len(self.campaigns_participated) * 0.3 +
                len(self.characters_used) * 0.2 +
                len(self.learned_patterns) * 0.1 +
                min(self.total_playtime_hours / 100, 1.0) * 0.4
            ))
        else:
            # Calculate based on unlock criteria completion
            completed_unlocks = len(self.unlocked_content)
            total_unlocks = len(self.unlock_criteria)
            self.progress = completed_unlocks / max(total_unlocks, 1)
    
    def add_unlock_criteria(self, unlock_name: str, criteria: Dict[str, Any]):
        """Add new unlock criteria"""
        self.unlock_criteria[unlock_name] = criteria
    
    def get_mastery_summary(self) -> Dict[str, Any]:
        """Get a summary of mastery progression"""
        summary = {}
        for category, skills in self.mastery_categories.items():
            summary[category] = {
                'total_skills': len(skills),
                'max_level': max(skills.values()) if skills else 0,
                'skills': skills.copy()
            }
        return summary
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get comprehensive meta objective information"""
        info = super().get_display_info()
        info.update({
            'campaigns_participated': len(self.campaigns_participated),
            'characters_used': len(self.characters_used),
            'total_playtime_hours': self.total_playtime_hours,
            'mastery_summary': self.get_mastery_summary(),
            'patterns_learned': len(self.learned_patterns),
            'survival_strategies': self.survival_strategies,
            'unlocked_content': list(self.unlocked_content),
            'recent_achievements': self.achievement_unlocks[-5:],  # Last 5 achievements
            'unlock_progress': {
                unlock_name: self._check_unlock_criteria(criteria)
                for unlock_name, criteria in self.unlock_criteria.items()
                if unlock_name not in self.unlocked_content
            }
        })
        return info