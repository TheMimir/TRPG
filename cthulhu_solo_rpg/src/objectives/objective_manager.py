"""
Objective Manager for Cthulhu Solo TRPG

This module provides the ObjectiveManager singleton that coordinates
all objectives in the game, handles their lifecycle, and integrates
with other game systems to provide a cohesive goal-oriented experience.
"""

import asyncio
import json
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Set, Type, Callable, Union
import weakref

from .base_objective import (
    BaseObjective, ObjectiveStatus, ObjectivePriority, ObjectiveScope,
    ObjectiveType, ObjectiveReward, ObjectiveConsequence
)

logger = logging.getLogger(__name__)


class ObjectiveManagerError(Exception):
    """Custom exception for ObjectiveManager errors"""
    pass


class ObjectiveRegistry:
    """Registry for objective types and their factory functions"""
    
    def __init__(self):
        self._factories: Dict[str, Type[BaseObjective]] = {}
        self._templates: Dict[str, Dict[str, Any]] = {}
    
    def register_objective_type(self, objective_class: Type[BaseObjective], type_name: str = None):
        """Register an objective class"""
        type_name = type_name or objective_class.__name__
        self._factories[type_name] = objective_class
        logger.debug(f"Registered objective type: {type_name}")
    
    def register_template(self, template_name: str, template_data: Dict[str, Any]):
        """Register an objective template"""
        self._templates[template_name] = template_data
        logger.debug(f"Registered objective template: {template_name}")
    
    def create_objective(self, type_name: str, **kwargs) -> BaseObjective:
        """Create an objective of the specified type"""
        if type_name not in self._factories:
            raise ObjectiveManagerError(f"Unknown objective type: {type_name}")
        
        objective_class = self._factories[type_name]
        return objective_class(**kwargs)
    
    def create_from_template(self, template_name: str, **overrides) -> BaseObjective:
        """Create an objective from a template with optional overrides"""
        if template_name not in self._templates:
            raise ObjectiveManagerError(f"Unknown objective template: {template_name}")
        
        template = self._templates[template_name].copy()
        template.update(overrides)
        
        objective_type = template.pop('objective_type', 'BaseObjective')
        return self.create_objective(objective_type, **template)
    
    def get_available_types(self) -> List[str]:
        """Get list of available objective types"""
        return list(self._factories.keys())
    
    def get_available_templates(self) -> List[str]:
        """Get list of available objective templates"""
        return list(self._templates.keys())


class ObjectiveManager:
    """
    Singleton manager for all objectives in the game.
    
    Handles objective lifecycle, priority management, condition checking,
    and integration with the game's AI and state systems.
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Core data structures
        self.objectives: Dict[str, BaseObjective] = {}
        self.active_objectives: Dict[str, BaseObjective] = {}
        self.completed_objectives: Dict[str, BaseObjective] = {}
        self.failed_objectives: Dict[str, BaseObjective] = {}
        
        # Organization structures
        self.objectives_by_type: Dict[ObjectiveType, List[str]] = defaultdict(list)
        self.objectives_by_scope: Dict[ObjectiveScope, List[str]] = defaultdict(list)
        self.objectives_by_priority: Dict[ObjectivePriority, List[str]] = defaultdict(list)
        
        # Hierarchy tracking
        self.parent_child_map: Dict[str, List[str]] = defaultdict(list)
        self.child_parent_map: Dict[str, str] = {}
        
        # Event system
        self.event_listeners: Dict[str, List[Callable]] = defaultdict(list)
        self.recent_events: deque = deque(maxlen=100)
        
        # Registry
        self.registry = ObjectiveRegistry()
        
        # Configuration
        self.config = {
            'max_active_objectives': 20,
            'max_immediate_objectives': 5,
            'max_short_term_objectives': 10,
            'auto_cleanup_completed': True,
            'auto_cleanup_after_hours': 24,
            'enable_dynamic_priorities': True,
            'enable_ai_suggestions': True
        }
        
        # State tracking
        self.last_update = datetime.now()
        self.update_count = 0
        self.statistics = {
            'objectives_created': 0,
            'objectives_completed': 0,
            'objectives_failed': 0,
            'total_progress_updates': 0
        }
        
        # AI integration
        self.ai_suggestion_callbacks: List[Callable] = []
        self.difficulty_calculator: Optional[Callable] = None
        
        self._initialized = True
        logger.info("ObjectiveManager initialized")
    
    def register_objective_type(self, objective_class: Type[BaseObjective], type_name: str = None):
        """Register a new objective type"""
        self.registry.register_objective_type(objective_class, type_name)
    
    def register_template(self, template_name: str, template_data: Dict[str, Any]):
        """Register an objective template"""
        self.registry.register_template(template_name, template_data)
    
    def register_event_listener(self, event_type: str, callback: Callable):
        """Register a callback for objective events"""
        self.event_listeners[event_type].append(callback)
        logger.debug(f"Registered event listener for: {event_type}")
    
    def register_ai_suggestion_callback(self, callback: Callable):
        """Register a callback for AI-generated objective suggestions"""
        self.ai_suggestion_callbacks.append(callback)
    
    def create_objective(
        self,
        objective_type: str,
        objective_id: str,
        **kwargs
    ) -> BaseObjective:
        """Create a new objective"""
        if objective_id in self.objectives:
            raise ObjectiveManagerError(f"Objective with ID '{objective_id}' already exists")
        
        try:
            objective = self.registry.create_objective(objective_type, objective_id=objective_id, **kwargs)
            self.add_objective(objective)
            return objective
        except Exception as e:
            logger.error(f"Failed to create objective {objective_id}: {e}")
            raise ObjectiveManagerError(f"Failed to create objective: {e}")
    
    def create_from_template(
        self,
        template_name: str,
        objective_id: str,
        **overrides
    ) -> BaseObjective:
        """Create an objective from a template"""
        if objective_id in self.objectives:
            raise ObjectiveManagerError(f"Objective with ID '{objective_id}' already exists")
        
        try:
            objective = self.registry.create_from_template(template_name, objective_id=objective_id, **overrides)
            self.add_objective(objective)
            return objective
        except Exception as e:
            logger.error(f"Failed to create objective from template {template_name}: {e}")
            raise ObjectiveManagerError(f"Failed to create objective from template: {e}")
    
    def add_objective(self, objective: BaseObjective) -> bool:
        """Add an existing objective to the manager"""
        if objective.objective_id in self.objectives:
            return False
        
        # Add to main collection
        self.objectives[objective.objective_id] = objective
        
        # Add to organizational structures
        self.objectives_by_type[objective.objective_type].append(objective.objective_id)
        self.objectives_by_scope[objective.scope].append(objective.objective_id)
        self.objectives_by_priority[objective.priority].append(objective.objective_id)
        
        # Handle hierarchy
        if objective.parent_objective:
            self.parent_child_map[objective.parent_objective].append(objective.objective_id)
            self.child_parent_map[objective.objective_id] = objective.parent_objective
        
        for child_id in objective.child_objectives:
            self.parent_child_map[objective.objective_id].append(child_id)
            self.child_parent_map[child_id] = objective.objective_id
        
        self.statistics['objectives_created'] += 1
        self._emit_event('objective_created', {'objective_id': objective.objective_id})
        
        logger.info(f"Added objective: {objective.title}")
        return True
    
    def remove_objective(self, objective_id: str) -> bool:
        """Remove an objective from the manager"""
        if objective_id not in self.objectives:
            return False
        
        objective = self.objectives[objective_id]
        
        # Remove from collections
        del self.objectives[objective_id]
        self.active_objectives.pop(objective_id, None)
        self.completed_objectives.pop(objective_id, None)
        self.failed_objectives.pop(objective_id, None)
        
        # Remove from organizational structures
        self.objectives_by_type[objective.objective_type].remove(objective_id)
        self.objectives_by_scope[objective.scope].remove(objective_id)
        self.objectives_by_priority[objective.priority].remove(objective_id)
        
        # Handle hierarchy cleanup
        if objective_id in self.parent_child_map:
            for child_id in self.parent_child_map[objective_id]:
                self.child_parent_map.pop(child_id, None)
            del self.parent_child_map[objective_id]
        
        if objective_id in self.child_parent_map:
            parent_id = self.child_parent_map[objective_id]
            self.parent_child_map[parent_id].remove(objective_id)
            del self.child_parent_map[objective_id]
        
        self._emit_event('objective_removed', {'objective_id': objective_id})
        
        logger.info(f"Removed objective: {objective.title}")
        return True
    
    def get_objective(self, objective_id: str) -> Optional[BaseObjective]:
        """Get an objective by ID"""
        return self.objectives.get(objective_id)
    
    def get_objectives_by_status(self, status: ObjectiveStatus) -> List[BaseObjective]:
        """Get all objectives with a specific status"""
        return [obj for obj in self.objectives.values() if obj.status == status]
    
    def get_objectives_by_type(self, objective_type: ObjectiveType) -> List[BaseObjective]:
        """Get all objectives of a specific type"""
        objective_ids = self.objectives_by_type.get(objective_type, [])
        return [self.objectives[obj_id] for obj_id in objective_ids if obj_id in self.objectives]
    
    def get_objectives_by_scope(self, scope: ObjectiveScope) -> List[BaseObjective]:
        """Get all objectives of a specific scope"""
        objective_ids = self.objectives_by_scope.get(scope, [])
        return [self.objectives[obj_id] for obj_id in objective_ids if obj_id in self.objectives]
    
    def get_objectives_by_priority(self, priority: ObjectivePriority) -> List[BaseObjective]:
        """Get all objectives of a specific priority"""
        objective_ids = self.objectives_by_priority.get(priority, [])
        return [self.objectives[obj_id] for obj_id in objective_ids if obj_id in self.objectives]
    
    def get_active_objectives(self) -> List[BaseObjective]:
        """Get all currently active objectives"""
        return list(self.active_objectives.values())
    
    def get_completed_objectives(self) -> List[BaseObjective]:
        """Get all completed objectives"""
        return list(self.completed_objectives.values())
    
    def get_failed_objectives(self) -> List[BaseObjective]:
        """Get all failed objectives"""
        return list(self.failed_objectives.values())
    
    def get_available_objectives(self, game_state: Dict[str, Any]) -> List[BaseObjective]:
        """Get objectives that can be activated given current game state"""
        available = []
        for objective in self.objectives.values():
            if objective.can_activate(game_state):
                available.append(objective)
        return available
    
    def get_priority_objectives(self) -> List[BaseObjective]:
        """Get objectives sorted by priority (highest first)"""
        all_active = list(self.active_objectives.values())
        return sorted(all_active, key=lambda obj: obj.priority.value, reverse=True)
    
    def update_all_objectives(self, game_state: Dict[str, Any], action_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update all objectives with current game state"""
        update_results = {
            'activated': [],
            'updated': [],
            'completed': [],
            'failed': [],
            'expired': []
        }
        
        # Check for new objectives to activate
        available = self.get_available_objectives(game_state)
        for objective in available:
            if self._should_activate_objective(objective, game_state):
                if objective.activate(game_state):
                    self.active_objectives[objective.objective_id] = objective
                    update_results['activated'].append(objective.objective_id)
        
        # Update active objectives
        objectives_to_update = list(self.active_objectives.values())
        for objective in objectives_to_update:
            try:
                if objective.update(game_state, action_data):
                    update_results['updated'].append(objective.objective_id)
                    self.statistics['total_progress_updates'] += 1
                
                # Handle status changes
                if objective.is_completed:
                    self.completed_objectives[objective.objective_id] = objective
                    self.active_objectives.pop(objective.objective_id, None)
                    update_results['completed'].append(objective.objective_id)
                    self.statistics['objectives_completed'] += 1
                    self._emit_event('objective_completed', {'objective_id': objective.objective_id})
                
                elif objective.is_failed:
                    self.failed_objectives[objective.objective_id] = objective
                    self.active_objectives.pop(objective.objective_id, None)
                    update_results['failed'].append(objective.objective_id)
                    self.statistics['objectives_failed'] += 1
                    self._emit_event('objective_failed', {'objective_id': objective.objective_id})
                
            except Exception as e:
                logger.error(f"Error updating objective {objective.objective_id}: {e}")
                objective.fail(game_state, f"Update error: {e}")
                update_results['failed'].append(objective.objective_id)
        
        # Cleanup and maintenance
        self._cleanup_old_objectives()
        self._update_dynamic_priorities(game_state)
        
        self.last_update = datetime.now()
        self.update_count += 1
        
        return update_results
    
    def _should_activate_objective(self, objective: BaseObjective, game_state: Dict[str, Any]) -> bool:
        """Determine if an objective should be automatically activated"""
        # Check capacity limits
        active_count = len(self.active_objectives)
        if active_count >= self.config['max_active_objectives']:
            return False
        
        # Check scope-specific limits
        scope_counts = defaultdict(int)
        for active_obj in self.active_objectives.values():
            scope_counts[active_obj.scope] += 1
        
        if objective.scope == ObjectiveScope.IMMEDIATE:
            if scope_counts[ObjectiveScope.IMMEDIATE] >= self.config['max_immediate_objectives']:
                return False
        elif objective.scope == ObjectiveScope.SHORT_TERM:
            if scope_counts[ObjectiveScope.SHORT_TERM] >= self.config['max_short_term_objectives']:
                return False
        
        # Priority-based activation
        if objective.priority.value >= ObjectivePriority.HIGH.value:
            return True
        
        # Consider current context (could be enhanced with AI)
        return True
    
    def _update_dynamic_priorities(self, game_state: Dict[str, Any]):
        """Update objective priorities based on current game state"""
        if not self.config['enable_dynamic_priorities']:
            return
        
        # This is a placeholder for dynamic priority adjustment
        # Could be enhanced with AI-based priority calculation
        pass
    
    def _cleanup_old_objectives(self):
        """Clean up old completed/failed objectives"""
        if not self.config['auto_cleanup_completed']:
            return
        
        cutoff_time = datetime.now() - timedelta(hours=self.config['auto_cleanup_after_hours'])
        
        # Clean up old completed objectives
        to_remove = []
        for obj_id, objective in self.completed_objectives.items():
            if objective.completed_at and objective.completed_at < cutoff_time:
                to_remove.append(obj_id)
        
        for obj_id in to_remove:
            self.remove_objective(obj_id)
        
        # Clean up old failed objectives
        to_remove = []
        for obj_id, objective in self.failed_objectives.items():
            if objective.last_update < cutoff_time:
                to_remove.append(obj_id)
        
        for obj_id in to_remove:
            self.remove_objective(obj_id)
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to all registered listeners"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': data
        }
        
        self.recent_events.append(event)
        
        # Notify listeners
        for callback in self.event_listeners[event_type]:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event listener for {event_type}: {e}")
    
    def get_display_summary(self) -> Dict[str, Any]:
        """Get a summary for UI display"""
        active_by_priority = defaultdict(list)
        for objective in self.active_objectives.values():
            active_by_priority[objective.priority].append(objective.get_display_info())
        
        return {
            'total_objectives': len(self.objectives),
            'active_count': len(self.active_objectives),
            'completed_count': len(self.completed_objectives),
            'failed_count': len(self.failed_objectives),
            'active_by_priority': dict(active_by_priority),
            'statistics': self.statistics.copy(),
            'last_update': self.last_update.isoformat()
        }
    
    async def suggest_new_objectives(self, game_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get AI-generated objective suggestions"""
        suggestions = []
        
        for callback in self.ai_suggestion_callbacks:
            try:
                callback_suggestions = await callback(game_state, self.get_active_objectives())
                suggestions.extend(callback_suggestions)
            except Exception as e:
                logger.error(f"Error getting AI suggestions: {e}")
        
        return suggestions
    
    def save_to_file(self, file_path: Union[str, Path]) -> bool:
        """Save all objectives to a file"""
        try:
            save_data = {
                'objectives': {obj_id: obj.to_dict() for obj_id, obj in self.objectives.items()},
                'active_objectives': list(self.active_objectives.keys()),
                'completed_objectives': list(self.completed_objectives.keys()),
                'failed_objectives': list(self.failed_objectives.keys()),
                'statistics': self.statistics,
                'last_update': self.last_update.isoformat(),
                'update_count': self.update_count
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved objectives to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save objectives: {e}")
            return False
    
    def load_from_file(self, file_path: Union[str, Path]) -> bool:
        """Load objectives from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Clear current state
            self.objectives.clear()
            self.active_objectives.clear()
            self.completed_objectives.clear()
            self.failed_objectives.clear()
            
            # Load objectives (this would need concrete objective classes)
            # For now, this is a placeholder
            logger.warning("Loading objectives from file requires concrete objective classes")
            
            # Restore statistics
            self.statistics = save_data.get('statistics', {})
            self.update_count = save_data.get('update_count', 0)
            
            logger.info(f"Loaded objectives from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load objectives: {e}")
            return False
    
    def reset(self):
        """Reset the objective manager to initial state"""
        self.objectives.clear()
        self.active_objectives.clear()
        self.completed_objectives.clear()
        self.failed_objectives.clear()
        
        for objectives_list in self.objectives_by_type.values():
            objectives_list.clear()
        for objectives_list in self.objectives_by_scope.values():
            objectives_list.clear()
        for objectives_list in self.objectives_by_priority.values():
            objectives_list.clear()
        
        self.parent_child_map.clear()
        self.child_parent_map.clear()
        self.recent_events.clear()
        
        self.statistics = {
            'objectives_created': 0,
            'objectives_completed': 0,
            'objectives_failed': 0,
            'total_progress_updates': 0
        }
        
        self.last_update = datetime.now()
        self.update_count = 0
        
        logger.info("ObjectiveManager reset")
    
    def clear_all_objectives(self):
        """Clear all objectives (alias for reset method)"""
        self.reset()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            'basic_stats': self.statistics.copy(),
            'counts': {
                'total': len(self.objectives),
                'active': len(self.active_objectives),
                'completed': len(self.completed_objectives),
                'failed': len(self.failed_objectives)
            },
            'by_type': {obj_type.value: len(objectives) 
                       for obj_type, objectives in self.objectives_by_type.items()},
            'by_scope': {scope.value: len(objectives) 
                        for scope, objectives in self.objectives_by_scope.items()},
            'by_priority': {priority.value: len(objectives) 
                           for priority, objectives in self.objectives_by_priority.items()},
            'update_info': {
                'last_update': self.last_update.isoformat(),
                'update_count': self.update_count
            }
        }


# Global instance
objective_manager = ObjectiveManager()