"""
Gameplay Controller for Cthulhu Solo TRPG System

Manages turn-based gameplay flow and player interactions:
- Turn processing and action resolution
- Coordination between game engine and AI agents
- Free-text action processing and interpretation
- Story content generation and investigation tracking
- Game state progression and event handling
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

from core.models import (
    StoryContent, NarrativeContext, TensionLevel, ActionType,
    PlayerAction, GameState, Investigation
)
from core.game_engine import GameEngine, Character
from agents.story_agent import StoryAgent
from agents.base_agent import BaseAgent, AgentManager


logger = logging.getLogger(__name__)


class TurnPhase(Enum):
    """Phases of a game turn"""
    INPUT = "input"              # Waiting for player input
    PROCESSING = "processing"    # Processing player action
    RESOLUTION = "resolution"    # Resolving action effects
    RESPONSE = "response"        # Generating narrative response
    COMPLETION = "completion"    # Turn complete


@dataclass
class TurnResult:
    """Result of processing a complete turn"""
    turn_number: int
    player_action: str
    story_content: StoryContent
    character_updates: Dict[str, Any] = field(default_factory=dict)
    game_state_changes: Dict[str, Any] = field(default_factory=dict)
    dice_rolls: List[Dict[str, Any]] = field(default_factory=list)
    investigation_results: List[Dict[str, Any]] = field(default_factory=list)
    tension_change: Optional[TensionLevel] = None
    processing_time: float = 0.0
    success: bool = True
    error_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert turn result to dictionary"""
        return {
            "turn_number": self.turn_number,
            "player_action": self.player_action,
            "story_content": {
                "text": self.story_content.text,
                "content_id": self.story_content.content_id,
                "scene_id": self.story_content.scene_id,
                "tension_level": self.story_content.tension_level.value,
                "investigation_opportunities": self.story_content.investigation_opportunities,
                "story_threads": self.story_content.story_threads,
                "metadata": self.story_content.metadata
            },
            "character_updates": self.character_updates,
            "game_state_changes": self.game_state_changes,
            "dice_rolls": self.dice_rolls,
            "investigation_results": self.investigation_results,
            "tension_change": self.tension_change.value if self.tension_change else None,
            "processing_time": self.processing_time,
            "success": self.success,
            "error_message": self.error_message
        }


class GameplayController:
    """
    Coordinates turn-based gameplay flow.
    
    Manages the complete turn cycle from player input to narrative response,
    integrating game mechanics, AI agents, and story progression.
    """
    
    def __init__(self, game_engine: GameEngine, agent_manager: AgentManager, scenario=None):
        """
        Initialize the gameplay controller.
        
        Args:
            game_engine: Game engine instance
            agent_manager: Agent manager for AI coordination
            scenario: Optional scenario object for content generation
        """
        self.game_engine = game_engine
        self.agent_manager = agent_manager
        self.current_scenario = scenario
        
        # Controller state
        self.current_phase = TurnPhase.INPUT
        self.active_investigations: List[Investigation] = []
        self.turn_history: List[TurnResult] = []
        
        # Performance tracking
        self.total_turns_processed = 0
        self.average_turn_time = 0.0
        self.error_count = 0
        
        # Configuration
        self.max_turn_time = 60.0  # Maximum time per turn
        self.auto_save_frequency = 5  # Auto-save every N turns
        
        logger.info("GameplayController initialized")
    
    async def process_player_action(self, player_action: str, 
                                  context: Optional[Dict[str, Any]] = None) -> TurnResult:
        """
        Process a complete player action and return the result.
        
        Args:
            player_action: Free-text player input
            context: Additional context for processing
            
        Returns:
            TurnResult with complete turn outcome
        """
        start_time = time.time()
        self.current_phase = TurnPhase.PROCESSING
        
        # Initialize turn result with placeholder story content
        # Story content will be generated and updated later in the process
        current_scene = self.game_engine.current_scene or "unknown_scene"
        placeholder_story_content = StoryContent(
            text="Processing your action...",
            content_id=f"placeholder_{int(time.time())}",
            scene_id=current_scene,
            tension_level=TensionLevel.CALM,
            metadata={"source": "placeholder", "processing": True}
        )
        
        turn_result = TurnResult(
            turn_number=self.game_engine.turn_number + 1,
            player_action=player_action,
            story_content=placeholder_story_content
        )
        
        try:
            logger.info(f"Processing turn {turn_result.turn_number}: {player_action[:50]}...")
            
            # Phase 1: Analyze and validate action
            action_analysis = await self._analyze_player_action(player_action, context)
            
            # Phase 2: Check for skill requirements and rolls
            skill_results = await self._handle_skill_checks(action_analysis, context)
            turn_result.dice_rolls.extend(skill_results)
            
            # Phase 3: Process investigations if applicable
            investigation_results = await self._handle_investigations(action_analysis, context)
            turn_result.investigation_results = investigation_results
            
            # Phase 4: Apply game mechanics and state changes
            mechanics_results = await self._apply_game_mechanics(action_analysis, skill_results, context)
            turn_result.character_updates = mechanics_results.get("character_updates", {})
            turn_result.game_state_changes = mechanics_results.get("state_changes", {})
            
            # Phase 5: Generate narrative response
            story_content = await self._generate_story_response(action_analysis, turn_result, context)
            turn_result.story_content = story_content
            
            # Phase 6: Update game state
            await self._update_game_state(turn_result, context)
            
            # Complete turn processing
            turn_result.processing_time = time.time() - start_time
            turn_result.success = True
            
            # Update statistics
            self.total_turns_processed += 1
            self.average_turn_time = ((self.average_turn_time * (self.total_turns_processed - 1) + 
                                     turn_result.processing_time) / self.total_turns_processed)
            
            # Add to history
            self.turn_history.append(turn_result)
            if len(self.turn_history) > 100:  # Keep last 100 turns
                self.turn_history = self.turn_history[-100:]
            
            self.current_phase = TurnPhase.COMPLETION
            
            logger.info(f"Turn {turn_result.turn_number} completed in {turn_result.processing_time:.2f}s")
            return turn_result
            
        except Exception as e:
            # Handle turn processing error
            self.error_count += 1
            turn_result.success = False
            turn_result.error_message = str(e)
            turn_result.processing_time = time.time() - start_time
            
            # Generate error fallback response
            turn_result.story_content = await self._generate_error_fallback(player_action, str(e))
            
            logger.error(f"Turn processing failed: {e}")
            return turn_result
    
    async def _analyze_player_action(self, player_action: str, 
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze player action to understand intent and requirements.
        
        Args:
            player_action: Player's input
            context: Additional context
            
        Returns:
            Action analysis with type, target, and requirements
        """
        # Get story agent for action analysis
        story_agent = self.agent_manager.get_agent("story_agent")
        
        if story_agent and isinstance(story_agent, StoryAgent):
            # Use story agent's action analysis
            action_analysis = story_agent._analyze_action_type(player_action)
        else:
            # Fallback analysis
            action_analysis = {
                "action_type": ActionType.OTHER.value,
                "target": "",
                "intent": player_action,
                "confidence": 0.5,
                "keywords": player_action.lower().split()
            }
        
        # Add context information
        action_analysis.update({
            "original_text": player_action,
            "scene_id": self.game_engine.current_scene,
            "turn_number": self.game_engine.turn_number + 1,
            "character_state": self.game_engine.character.to_dict() if self.game_engine.character else {}
        })
        
        return action_analysis
    
    async def _handle_skill_checks(self, action_analysis: Dict[str, Any], 
                                 context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Determine and execute any required skill checks.
        
        Args:
            action_analysis: Analysis of player action
            context: Additional context
            
        Returns:
            List of skill check results
        """
        skill_results = []
        action_type = action_analysis.get("action_type", "other")
        target = action_analysis.get("target", "")
        
        # Determine required skills based on action type
        required_skills = self._determine_required_skills(action_type, target, action_analysis)
        
        for skill_info in required_skills:
            skill_name = skill_info["skill"]
            difficulty = skill_info.get("difficulty", "regular")
            modifier = skill_info.get("modifier", 0)
            
            try:
                # Perform skill check
                dice_result = self.game_engine.make_skill_check(skill_name, modifier, difficulty)
                
                skill_result = {
                    "skill": skill_name,
                    "difficulty": difficulty,
                    "modifier": modifier,
                    "roll": dice_result.total,
                    "target": dice_result.target_number,
                    "success_level": dice_result.success_level.value if dice_result.success_level else "unknown",
                    "success": dice_result.success_level.value in ["success", "hard_success", "extreme_success", "critical_success"] if dice_result.success_level else False
                }
                
                skill_results.append(skill_result)
                
                logger.debug(f"Skill check {skill_name}: {dice_result.total} vs {dice_result.target_number} - {skill_result['success_level']}")
                
            except Exception as e:
                logger.warning(f"Failed to perform skill check {skill_name}: {e}")
                # Add failed skill check to results
                skill_results.append({
                    "skill": skill_name,
                    "error": str(e),
                    "success": False
                })
        
        return skill_results
    
    def _determine_required_skills(self, action_type: str, target: str, 
                                 action_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Determine what skills are required for this action.
        
        Args:
            action_type: Type of action being performed
            target: Target of the action
            action_analysis: Full action analysis
            
        Returns:
            List of required skill checks
        """
        required_skills = []
        
        # Map action types to skill requirements
        action_skill_map = {
            "investigate": [
                {"skill": "spot_hidden", "difficulty": "regular"},
                {"skill": "library_use", "difficulty": "regular", "conditional": "book" in target.lower()},
            ],
            "movement": [
                {"skill": "climb", "difficulty": "regular", "conditional": any(word in action_analysis.get("keywords", []) 
                                                                              for word in ["climb", "올라", "기어"])},
                {"skill": "stealth", "difficulty": "regular", "conditional": any(word in action_analysis.get("keywords", []) 
                                                                               for word in ["sneak", "조용", "몰래"])}
            ],
            "interact": [
                {"skill": "psychology", "difficulty": "regular", "conditional": "talk" in action_analysis.get("keywords", [])},
                {"skill": "persuade", "difficulty": "regular", "conditional": any(word in action_analysis.get("keywords", []) 
                                                                                 for word in ["convince", "설득"])},
            ]
        }
        
        # Get base skills for action type
        if action_type in action_skill_map:
            for skill_info in action_skill_map[action_type]:
                # Check if skill is required unconditionally or meets condition
                if "conditional" not in skill_info or skill_info["conditional"]:
                    required_skills.append({
                        "skill": skill_info["skill"],
                        "difficulty": skill_info.get("difficulty", "regular"),
                        "modifier": skill_info.get("modifier", 0)
                    })
        
        # Add context-specific skills
        current_scene = self.game_engine.current_scene
        if "horror" in current_scene.lower() or "occult" in current_scene.lower():
            # Add sanity check for horror scenes
            required_skills.append({
                "skill": "sanity",
                "difficulty": "regular",
                "modifier": 0,
                "special": "sanity_check"
            })
        
        return required_skills
    
    async def _handle_investigations(self, action_analysis: Dict[str, Any], 
                                   context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Handle investigation actions and opportunities.
        
        Args:
            action_analysis: Player action analysis
            context: Additional context
            
        Returns:
            List of investigation results
        """
        investigation_results = []
        
        # Check if this is an investigation action
        if action_analysis.get("action_type") == "investigate":
            # Create investigation from player action
            investigation = Investigation(
                description=action_analysis.get("intent", ""),
                difficulty=5,  # Base difficulty
                scene_id=self.game_engine.current_scene,
                keywords=action_analysis.get("keywords", [])
            )
            
            # Check if character can attempt this investigation
            character_state = self.game_engine.character.to_dict() if self.game_engine.character else {}
            narrative_flags = self.game_engine.game_flags
            
            if investigation.can_attempt(character_state, narrative_flags):
                # Attempt the investigation
                result = await self._perform_investigation(investigation, action_analysis)
                investigation_results.append(result)
            else:
                investigation_results.append({
                    "investigation": investigation.description,
                    "success": False,
                    "reason": "Character cannot attempt this investigation",
                    "requirements_not_met": True
                })
        
        return investigation_results
    
    async def _perform_investigation(self, investigation: Investigation, 
                                   action_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a specific investigation.
        
        Args:
            investigation: Investigation to perform
            action_analysis: Player action analysis
            
        Returns:
            Investigation result
        """
        # Base investigation result
        result = {
            "investigation": investigation.description,
            "success": False,
            "discoveries": [],
            "clues": [],
            "story_impact": ""
        }
        
        try:
            # Perform skill check for investigation
            skill_check = self.game_engine.make_skill_check("spot_hidden", 0, "regular")
            
            # Determine success based on skill check
            success = skill_check.success_level.value in ["success", "hard_success", "extreme_success", "critical_success"]
            result["success"] = success
            result["skill_check"] = {
                "roll": skill_check.total,
                "target": skill_check.target_number,
                "success_level": skill_check.success_level.value
            }
            
            if success:
                # Generate discoveries based on scene and action
                discoveries = await self._generate_investigation_discoveries(investigation, action_analysis)
                result["discoveries"] = discoveries
                
                # Add to active investigations if ongoing
                if not investigation.one_time:
                    self.active_investigations.append(investigation)
            
        except Exception as e:
            logger.error(f"Investigation failed: {e}")
            result["error"] = str(e)
        
        return result
    
    async def _generate_investigation_discoveries(self, investigation: Investigation, 
                                                action_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate discoveries for a successful investigation.
        
        Args:
            investigation: The investigation being performed
            action_analysis: Player action analysis
            
        Returns:
            List of discoveries/clues
        """
        # This would ideally use an AI agent to generate contextual discoveries
        # For now, provide basic discoveries based on scene and action
        
        scene_id = self.game_engine.current_scene
        discoveries = []
        
        # Scene-based discoveries
        if "library" in scene_id.lower():
            discoveries.extend([
                "오래된 책에서 이상한 기호를 발견했습니다",
                "한 페이지가 찢어져 나간 것을 확인했습니다",
                "책장 뒤에 숨겨진 문서를 찾았습니다"
            ])
        elif "room" in scene_id.lower():
            discoveries.extend([
                "바닥에 이상한 얼룩을 발견했습니다",
                "벽에 작은 균열이 있습니다",
                "창문 근처에서 낡은 편지를 찾았습니다"
            ])
        else:
            discoveries.extend([
                "주변에서 미묘한 변화를 감지했습니다",
                "이전에 놓쳤던 세부사항을 발견했습니다",
                "새로운 단서를 찾아냈습니다"
            ])
        
        # Return 1-3 random discoveries
        import random
        num_discoveries = random.randint(1, 3)
        return random.sample(discoveries, min(num_discoveries, len(discoveries)))
    
    async def _apply_game_mechanics(self, action_analysis: Dict[str, Any], 
                                  skill_results: List[Dict[str, Any]], 
                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Apply game mechanics based on action and skill results.
        
        Args:
            action_analysis: Player action analysis
            skill_results: Results of skill checks
            context: Additional context
            
        Returns:
            Mechanics results with character and state updates
        """
        mechanics_results = {
            "character_updates": {},
            "state_changes": {},
            "special_effects": []
        }
        
        # Check for sanity effects
        for skill_result in skill_results:
            if skill_result.get("skill") == "sanity" or "sanity" in skill_result.get("special", ""):
                if not skill_result.get("success", False):
                    # Apply sanity loss
                    sanity_result = self.game_engine.make_sanity_check("1d4", "Horror encounter")
                    mechanics_results["character_updates"]["sanity_loss"] = sanity_result
        
        # Check for damage or healing
        action_type = action_analysis.get("action_type", "")
        if action_type == "combat":
            # Combat mechanics would go here
            pass
        elif action_type == "rest":
            # Healing mechanics
            healing_result = self.game_engine.heal_character(1, "physical")
            mechanics_results["character_updates"]["healing"] = healing_result
        
        # Time advancement
        self.game_engine.advance_time(0.25)  # 15 minutes per action
        mechanics_results["state_changes"]["time_advanced"] = 0.25
        
        return mechanics_results
    
    async def _generate_story_response(self, action_analysis: Dict[str, Any], 
                                     turn_result: TurnResult, 
                                     context: Optional[Dict[str, Any]] = None) -> StoryContent:
        """
        Generate narrative response to player action.
        
        Args:
            action_analysis: Player action analysis
            turn_result: Current turn result
            context: Additional context
            
        Returns:
            Generated story content
        """
        # Get story agent
        story_agent = self.agent_manager.get_agent("story_agent")
        
        if story_agent:
            # Build context for story generation
            story_context = {
                "player_action": action_analysis["original_text"],
                "scene_id": self.game_engine.current_scene,
                "turn_number": turn_result.turn_number,
                "character_state": self.game_engine.character.to_dict() if self.game_engine.character else {},
                "skill_results": turn_result.dice_rolls,
                "investigation_results": turn_result.investigation_results,
                "narrative_context": self._build_narrative_context()
            }
            
            # Generate story response
            agent_response = await story_agent.process_input(story_context)
            
            if agent_response.is_valid:
                # Parse story content from agent response
                story_data = json.loads(agent_response.content)
                
                story_content = StoryContent(
                    text=story_data.get("text", ""),
                    content_id=story_data.get("content_id", f"content_{int(time.time())}"),
                    scene_id=story_data.get("scene_id", self.game_engine.current_scene),
                    tension_level=TensionLevel(story_data.get("tension_level", "calm")),
                    metadata=story_data.get("metadata", {}),
                    investigation_opportunities=story_data.get("investigation_opportunities", []),
                    story_threads=story_data.get("story_threads", {})
                )
                
                return story_content
        
        # Fallback story generation
        return await self._generate_fallback_story_content(action_analysis, turn_result)
    
    def _build_narrative_context(self) -> NarrativeContext:
        """Build current narrative context"""
        character_state = self.game_engine.character.to_dict() if self.game_engine.character else {}
        
        # Get recent action history
        recent_actions = [turn.player_action for turn in self.turn_history[-5:]]
        
        return NarrativeContext(
            scene_id=self.game_engine.current_scene,
            turn_number=self.game_engine.turn_number,
            character_state=character_state,
            choice_history=recent_actions,
            narrative_flags=self.game_engine.game_flags.copy(),
            tension_level=TensionLevel.CALM  # This would be tracked properly in a full implementation
        )
    
    async def _generate_fallback_story_content(self, action_analysis: Dict[str, Any], 
                                             turn_result: TurnResult) -> StoryContent:
        """Generate fallback story content when AI is unavailable"""
        action_type = action_analysis.get("action_type", "other")
        
        fallback_texts = {
            "investigate": "당신의 조사는 흥미로운 결과를 가져왔습니다.",
            "movement": "새로운 장소로 이동했습니다.",
            "interact": "상호작용을 통해 상황이 발전했습니다.",
            "other": "당신의 행동이 상황에 변화를 가져왔습니다."
        }
        
        fallback_text = fallback_texts.get(action_type, fallback_texts["other"])
        
        # Ensure scene_id is never empty
        current_scene = self.game_engine.current_scene or "library_entrance"
        
        return StoryContent(
            text=fallback_text,
            content_id=f"fallback_{int(time.time())}",
            scene_id=current_scene,
            tension_level=TensionLevel.CALM,
            metadata={"source": "fallback", "controller": "gameplay_controller"},
            investigation_opportunities=["주변을 더 자세히 살펴본다", "다른 접근 방법을 시도한다"],
            story_threads={}
        )
    
    async def _generate_error_fallback(self, player_action: str, error_msg: str) -> StoryContent:
        """Generate error fallback story content"""
        # Ensure scene_id is never empty
        current_scene = self.game_engine.current_scene or "library_entrance"
        
        return StoryContent(
            text="예상치 못한 문제가 발생했지만, 상황은 계속 진행됩니다.",
            content_id=f"error_fallback_{int(time.time())}",
            scene_id=current_scene,
            tension_level=TensionLevel.CALM,
            metadata={"source": "error_fallback", "error": error_msg},
            investigation_opportunities=["상황을 다시 살펴본다"],
            story_threads={}
        )
    
    async def _update_game_state(self, turn_result: TurnResult, 
                               context: Optional[Dict[str, Any]] = None):
        """
        Update game state after turn processing.
        
        Args:
            turn_result: Completed turn result
            context: Additional context
        """
        # Update turn number
        self.game_engine.turn_number = turn_result.turn_number
        
        # Update tension level if changed
        if turn_result.tension_change:
            # This would update the narrative context tension level
            pass
        
        # Apply any character updates
        if turn_result.character_updates:
            # Character updates are already applied by game engine
            # This is where we'd handle any additional state synchronization
            pass
        
        # Update story threads and flags
        if hasattr(turn_result.story_content, 'story_threads'):
            # Ensure story_threads is a dictionary before calling .items()
            story_threads = turn_result.story_content.story_threads
            if isinstance(story_threads, dict):
                for thread, status in story_threads.items():
                    self.game_engine.game_flags[f"story_thread_{thread}"] = status
            elif isinstance(story_threads, list):
                # Handle legacy list format for compatibility
                logger.warning("story_threads is a list, converting to dict format")
                for i, thread in enumerate(story_threads):
                    self.game_engine.game_flags[f"story_thread_{thread}"] = "active"
            else:
                logger.error(f"story_threads has unexpected type: {type(story_threads)}")
    
    async def get_current_story_content(self, context: Optional[Dict[str, Any]] = None) -> StoryContent:
        """
        Get current story content without processing an action.
        
        Args:
            context: Optional context for content generation
            
        Returns:
            Current story content
        """
        # Check if we have a valid scene ID
        current_scene = self.game_engine.current_scene
        if not current_scene:
            # If no scene is set, default to library entrance for Miskatonic scenario
            current_scene = "library_entrance"
            self.game_engine.current_scene = current_scene
            logger.warning("No current scene set, defaulting to library_entrance")
        
        # Try to get content from scenario first
        if self.current_scenario:
            try:
                scenario_content = self.current_scenario.get_scene_initial_content(current_scene)
                if scenario_content:
                    logger.info(f"Using scenario content for scene: {current_scene}")
                    return scenario_content
            except Exception as e:
                logger.warning(f"Failed to get scenario content: {e}")
        
        # Fallback: Generate basic story content based on current scene
        scene_descriptions = {
            "library_entrance": "미스카토닉 대학교 도서관의 웅장한 입구에 서 있습니다. 거대한 참나무 문과 고딕 양식의 아치가 인상적입니다.",
            "main_reading_room": "도서관의 메인 열람실에 들어섰습니다. 높은 천장과 거대한 창문들이 있는 웅장한 공간입니다.",
            "restricted_section": "드디어 도서관의 제한 구역에 들어왔습니다. 이곳은 메인 열람실과는 완전히 다른 분위기입니다."
        }
        
        scene_text = scene_descriptions.get(current_scene, f"당신은 {current_scene}에 있습니다.")
        
        return StoryContent(
            text=f"{scene_text} 주변을 둘러보며 다음 행동을 결정하세요.",
            content_id=f"current_{int(time.time())}",
            scene_id=current_scene,
            tension_level=TensionLevel.CALM,
            metadata={"source": "fallback_content"},
            investigation_opportunities=[
                "주변을 자세히 관찰한다",
                "이동할 수 있는 곳을 찾는다",
                "상호작용할 수 있는 것들을 확인한다"
            ],
            story_threads={}
        )
    
    def get_controller_statistics(self) -> Dict[str, Any]:
        """Get gameplay controller statistics"""
        return {
            "total_turns_processed": self.total_turns_processed,
            "average_turn_time": self.average_turn_time,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(1, self.total_turns_processed),
            "current_phase": self.current_phase.value,
            "active_investigations": len(self.active_investigations),
            "turn_history_size": len(self.turn_history),
            "current_scene": self.game_engine.current_scene,
            "current_turn": self.game_engine.turn_number
        }