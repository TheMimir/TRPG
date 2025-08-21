"""
Story Agent for Cthulhu Solo TRPG System

Specialized AI agent for narrative generation including:
- Scene generation based on context
- Player action interpretation and responses
- Investigation opportunities generation
- Tension management and horror atmosphere
- Story thread tracking and development
- Dynamic narrative adaptation
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
import re
import random

from agents.base_agent import BaseAgent, AgentResponse, AgentConfig
from core.models import (
    StoryContent, NarrativeContext, TensionLevel, ActionType, 
    PlayerAction, Investigation
)
from ai.ollama_client import OllamaClient, OllamaResponse, ResponseStatus


logger = logging.getLogger(__name__)


class StoryAgent(BaseAgent):
    """
    Specialized agent for narrative generation and story management.
    
    Handles all aspects of storytelling including scene descriptions,
    action responses, investigation opportunities, and maintaining
    narrative consistency and horror atmosphere.
    """
    
    def __init__(self, ollama_client: Optional[OllamaClient] = None,
                 config: Optional[AgentConfig] = None):
        """Initialize the Story Agent"""
        super().__init__("story_agent", ollama_client, config)
        
        # Story-specific configuration
        self.tension_escalation_rate = 0.1  # How quickly tension builds
        self.investigation_frequency = 0.7  # Probability of generating investigations
        self.narrative_consistency_weight = 0.8  # How much to weigh consistency
        
        # Action classification patterns (Korean and English)
        self.action_patterns = self._initialize_action_patterns()
        
        # Investigation templates and opportunities
        self.investigation_templates = self._initialize_investigation_templates()
        
        # Fallback narrative elements
        self.fallback_responses = self._initialize_fallback_responses()
        
        logger.info("StoryAgent initialized")
    
    def _initialize_action_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for action type classification"""
        return {
            ActionType.INVESTIGATE.value: [
                # Korean patterns
                r'조사.*?다', r'살펴.*?다', r'확인.*?다', r'찾.*?다', r'검사.*?다',
                r'탐색.*?다', r'뒤져.*?다', r'관찰.*?다', r'점검.*?다', r'분석.*?다',
                # English patterns
                r'investigate', r'examine', r'search', r'look', r'inspect',
                r'study', r'analyze', r'observe', r'check', r'explore'
            ],
            ActionType.MOVEMENT.value: [
                # Korean patterns
                r'이동.*?다', r'가.*?다', r'들어.*?다', r'나.*?다', r'올라.*?다',
                r'내려.*?다', r'따라.*?다', r'돌아.*?다', r'향.*?다', r'접근.*?다',
                # English patterns
                r'go', r'move', r'enter', r'exit', r'climb', r'descend',
                r'approach', r'return', r'follow', r'head'
            ],
            ActionType.INTERACT.value: [
                # Korean patterns
                r'대화.*?다', r'말.*?다', r'물.*?다', r'답.*?다', r'소통.*?다',
                r'이야기.*?다', r'질문.*?다', r'요청.*?다', r'부탁.*?다',
                # English patterns
                r'talk', r'speak', r'ask', r'tell', r'communicate',
                r'question', r'request', r'discuss', r'converse'
            ],
            ActionType.DIALOGUE.value: [
                # Korean patterns
                r'\".*?\"', r'\'.*?\'', r'라고.*?다', r'하고.*?다',
                # English patterns
                r'".*?"', r"'.*?'", r'say', r'shout', r'whisper'
            ]
        }
    
    def _initialize_investigation_templates(self) -> Dict[str, List[str]]:
        """Initialize templates for generating investigation opportunities"""
        return {
            "general": [
                "주변을 자세히 살펴본다",
                "바닥에 떨어진 것들을 확인한다", 
                "벽면을 점검한다",
                "숨겨진 통로나 문을 찾는다",
                "이상한 냄새의 근원을 추적한다"
            ],
            "indoor": [
                "가구 아래를 들여다본다",
                "서랍이나 캐비닛을 뒤진다",
                "책장이나 책들을 조사한다",
                "창문 밖을 관찰한다",
                "조명이나 전기 시설을 확인한다"
            ],
            "outdoor": [
                "발자국이나 흔적을 추적한다",
                "주변 식물이나 나무를 관찰한다",
                "하늘이나 날씨 변화를 주시한다",
                "근처 건물들을 살펴본다",
                "소음의 방향을 파악한다"
            ],
            "social": [
                "상대방의 표정과 몸짓을 관찰한다",
                "대화 중 거짓말의 징후를 찾는다",
                "상대방의 소지품을 주시한다",
                "주변 사람들의 반응을 살핀다",
                "사회적 관계와 위계를 파악한다"
            ],
            "horror": [
                "불가사의한 현상의 원인을 탐구한다",
                "오컬트적 상징이나 기호를 해독한다",
                "이상한 소리의 패턴을 분석한다",
                "초자연적 존재의 흔적을 추적한다",
                "고대 지식이나 금서를 연구한다"
            ]
        }
    
    def _initialize_fallback_responses(self) -> Dict[str, List[str]]:
        """Initialize fallback responses for when AI is unavailable"""
        return {
            "general": [
                "당신의 행동은 주변 환경에 미묘한 변화를 가져옵니다.",
                "상황이 조금씩 전개되어 가고 있습니다.",
                "당신은 신중하게 다음 행동을 고려해야 합니다.",
                "무언가 중요한 일이 일어나려 하고 있습니다."
            ],
            "investigation": [
                "조사 결과, 흥미로운 단서를 발견합니다.",
                "자세히 살펴보니 이전에 놓쳤던 세부사항이 보입니다.",
                "탐색을 통해 새로운 정보를 얻었습니다.",
                "조사는 예상치 못한 발견으로 이어집니다."
            ],
            "movement": [
                "새로운 장소로 이동했습니다.",
                "다른 지역에 도착하여 주변을 둘러봅니다.",
                "이동 중에 여러 가지를 관찰할 수 있었습니다.",
                "새로운 환경이 당신을 맞이합니다."
            ],
            "interaction": [
                "상호작용을 통해 새로운 정보를 얻었습니다.",
                "대화가 예상과 다른 방향으로 흘러갑니다.",
                "상대방의 반응이 흥미롭습니다.",
                "소통을 통해 상황을 더 잘 이해하게 되었습니다."
            ]
        }
    
    async def _process_input_impl(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Process story-related input and generate narrative response.
        
        Args:
            context: Input context with player action and game state
            
        Returns:
            AgentResponse with story content
        """
        start_time = time.time()
        
        # Extract relevant information from context
        player_action = context.get("player_action", "")
        narrative_context = context.get("narrative_context")
        scene_id = context.get("scene_id", "unknown")
        tension_level = context.get("tension_level", TensionLevel.CALM)
        
        # Classify the player action
        action_analysis = self._analyze_action_type(player_action)
        
        # Build context for AI prompt
        story_context = self._build_story_context(context, action_analysis)
        
        # Generate AI response
        ai_response = await self._generate_story_response(story_context, player_action)
        
        if ai_response.is_success:
            # Parse and structure the AI response
            story_content = self._parse_ai_response(ai_response.content, context)
            
            # Add memory of this interaction
            self.add_memory(
                content=f"Player action: {player_action} -> {story_content['text'][:100]}...",
                importance=7,
                memory_type="story_interaction",
                scene_context=scene_id,
                keywords=[action_analysis["action_type"], scene_id]
            )
            
            return AgentResponse(
                content=json.dumps(story_content, ensure_ascii=False),
                confidence=0.9,
                source="ai",
                processing_time=time.time() - start_time,
                metadata={
                    "action_analysis": action_analysis,
                    "scene_id": scene_id,
                    "tension_level": tension_level.value if hasattr(tension_level, 'value') else str(tension_level)
                }
            )
        else:
            # Use fallback response
            return self._generate_fallback_story_response(context, action_analysis)
    
    def _analyze_action_type(self, action_text: str) -> Dict[str, Any]:
        """
        Analyze player action to determine type and extract key information.
        
        Args:
            action_text: Raw player input
            
        Returns:
            Dictionary with action analysis
        """
        action_lower = action_text.lower()
        
        # Initialize analysis result
        analysis = {
            "action_type": ActionType.OTHER.value,
            "target": "",
            "intent": action_text,
            "confidence": 0.5,
            "keywords": []
        }
        
        # Check against patterns
        best_match_score = 0
        for action_type, patterns in self.action_patterns.items():
            match_score = 0
            
            for pattern in patterns:
                if re.search(pattern, action_lower):
                    match_score += 1
            
            if match_score > best_match_score:
                best_match_score = match_score
                analysis["action_type"] = action_type
                analysis["confidence"] = min(1.0, match_score * 0.3)
        
        # Extract target/object (simple keyword extraction)
        # This could be improved with more sophisticated NLP
        common_targets = [
            "문", "창문", "책", "상자", "서랍", "벽", "바닥", "천장",
            "door", "window", "book", "box", "drawer", "wall", "floor", "ceiling"
        ]
        
        for target in common_targets:
            if target in action_lower:
                analysis["target"] = target
                break
        
        # Extract keywords for memory and context
        words = action_text.split()
        analysis["keywords"] = [word.lower() for word in words if len(word) > 2]
        
        return analysis
    
    def _build_story_context(self, context: Dict[str, Any], 
                           action_analysis: Dict[str, Any]) -> str:
        """
        Build comprehensive context for story generation.
        
        Args:
            context: Game context
            action_analysis: Analysis of player action
            
        Returns:
            Formatted context string for AI prompt
        """
        context_parts = []
        
        # System prompt for horror atmosphere
        context_parts.append("""당신은 H.P. 러브크래프트의 크툴루 신화를 바탕으로 한 공포 TRPG의 게임 마스터입니다.
플레이어의 행동에 대해 몰입감 있고 분위기 있는 반응을 생성해야 합니다.

중요한 지침:
1. 한국어로 응답하세요
2. 공포와 미스터리 분위기를 유지하세요
3. 플레이어의 행동에 논리적으로 반응하세요
4. 조사 기회를 자연스럽게 제공하세요
5. 서서히 긴장감을 높여가세요""")
        
        # Current scene and tension
        scene_id = context.get("scene_id", "unknown")
        tension_level = context.get("tension_level", TensionLevel.CALM)
        
        context_parts.append(f"현재 장면: {scene_id}")
        context_parts.append(f"긴장도: {tension_level.value if hasattr(tension_level, 'value') else tension_level}")
        
        # Character state
        if "character_state" in context:
            char_state = context["character_state"]
            context_parts.append(f"캐릭터: {char_state.get('name', 'Unknown')}")
            context_parts.append(f"직업: {char_state.get('occupation', 'Unknown')}")
            
            # Health and sanity (if available)
            if "current_hp" in char_state and "hit_points" in char_state:
                hp_ratio = char_state["current_hp"] / max(1, char_state["hit_points"])
                if hp_ratio < 0.5:
                    context_parts.append("캐릭터는 부상을 입었습니다")
            
            if "current_sanity" in char_state and "sanity_points" in char_state:
                sanity_ratio = char_state["current_sanity"] / max(1, char_state["sanity_points"])
                if sanity_ratio < 0.7:
                    context_parts.append("캐릭터의 정신 상태가 불안정합니다")
        
        # Recent story context from memories
        relevant_memories = self.get_relevant_memories(
            {"keywords": action_analysis["keywords"], "scene_id": scene_id},
            limit=3
        )
        
        if relevant_memories:
            context_parts.append("최근 상황:")
            for memory in relevant_memories:
                context_parts.append(f"- {memory.content[:100]}...")
        
        # Action analysis
        context_parts.append(f"플레이어 행동 유형: {action_analysis['action_type']}")
        if action_analysis["target"]:
            context_parts.append(f"행동 대상: {action_analysis['target']}")
        
        return "\n".join(context_parts)
    
    async def _generate_story_response(self, story_context: str, 
                                     player_action: str) -> OllamaResponse:
        """
        Generate story response using AI.
        
        Args:
            story_context: Context for story generation
            player_action: Player's action
            
        Returns:
            OllamaResponse with generated content
        """
        prompt = f"""
{story_context}

플레이어 행동: "{player_action}"

위 상황과 플레이어의 행동을 바탕으로 다음 형식으로 응답해주세요:

STORY_TEXT: [플레이어의 행동에 대한 결과와 새로운 상황 설명 (2-3문장)]

INVESTIGATION_OPPORTUNITIES: [플레이어가 할 수 있는 조사 기회들 (3-5개)]
- [조사 기회 1]
- [조사 기회 2]
- [조사 기회 3]

TENSION_CHANGE: [calm/uneasy/tense/terrifying/cosmic_horror 중 하나]

STORY_THREADS: [진행 중인 스토리 요소들]
- [스토리 요소 1]: [상태]
- [스토리 요소 2]: [상태]

반드시 STORY_TEXT로 시작하고 각 섹션을 명확히 구분해주세요.
"""
        
        return await self._generate_ai_response(prompt, story_context)
    
    def _parse_ai_response(self, ai_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse AI response into structured story content.
        
        Args:
            ai_content: Raw AI response
            context: Original context
            
        Returns:
            Structured story content
        """
        # Initialize default values
        story_content = {
            "text": "",
            "investigation_opportunities": [],
            "tension_level": "calm",
            "story_threads": {},
            "scene_id": context.get("scene_id", "unknown"),
            "content_id": f"story_{int(time.time())}",
            "metadata": {"source": "ai", "agent": "story_agent"}
        }
        
        # Parse sections from AI response
        sections = {
            "STORY_TEXT": "",
            "INVESTIGATION_OPPORTUNITIES": [],
            "TENSION_CHANGE": "calm",
            "STORY_THREADS": {}
        }
        
        current_section = None
        for line in ai_content.split('\n'):
            line = line.strip()
            
            if line.startswith('STORY_TEXT:'):
                current_section = 'STORY_TEXT'
                sections[current_section] = line.replace('STORY_TEXT:', '').strip()
            elif line.startswith('INVESTIGATION_OPPORTUNITIES:'):
                current_section = 'INVESTIGATION_OPPORTUNITIES'
            elif line.startswith('TENSION_CHANGE:'):
                current_section = 'TENSION_CHANGE'
                sections[current_section] = line.replace('TENSION_CHANGE:', '').strip()
            elif line.startswith('STORY_THREADS:'):
                current_section = 'STORY_THREADS'
            elif line.startswith('-') and current_section == 'INVESTIGATION_OPPORTUNITIES':
                opportunity = line.replace('-', '').strip()
                if opportunity:
                    sections[current_section].append(opportunity)
            elif line.startswith('-') and current_section == 'STORY_THREADS':
                if ':' in line:
                    thread_part = line.replace('-', '').strip()
                    if ':' in thread_part:
                        thread_name, thread_status = thread_part.split(':', 1)
                        sections[current_section][thread_name.strip()] = thread_status.strip()
            elif current_section == 'STORY_TEXT' and line:
                sections[current_section] += " " + line
        
        # Build final story content
        story_content["text"] = sections["STORY_TEXT"] or self._get_fallback_text(context)
        story_content["investigation_opportunities"] = sections["INVESTIGATION_OPPORTUNITIES"]
        
        # Validate and set tension level
        try:
            story_content["tension_level"] = TensionLevel(sections["TENSION_CHANGE"]).value
        except ValueError:
            story_content["tension_level"] = TensionLevel.CALM.value
        
        story_content["story_threads"] = sections["STORY_THREADS"]
        
        # Generate investigation opportunities if none provided
        if not story_content["investigation_opportunities"]:
            story_content["investigation_opportunities"] = self._generate_investigation_opportunities(context)
        
        return story_content
    
    def _generate_investigation_opportunities(self, context: Dict[str, Any]) -> List[str]:
        """
        Generate contextual investigation opportunities.
        
        Args:
            context: Game context
            
        Returns:
            List of investigation opportunities
        """
        opportunities = []
        scene_id = context.get("scene_id", "unknown")
        
        # Determine context type
        context_type = "general"
        if "indoor" in scene_id.lower() or "room" in scene_id.lower() or "house" in scene_id.lower():
            context_type = "indoor"
        elif "outdoor" in scene_id.lower() or "street" in scene_id.lower() or "forest" in scene_id.lower():
            context_type = "outdoor"
        elif "social" in scene_id.lower() or "conversation" in scene_id.lower():
            context_type = "social"
        elif any(horror_word in scene_id.lower() for horror_word in ["horror", "ritual", "occult", "mystery"]):
            context_type = "horror"
        
        # Get base opportunities
        base_opportunities = self.investigation_templates.get(context_type, self.investigation_templates["general"])
        
        # Add some general opportunities
        general_opportunities = self.investigation_templates["general"]
        
        # Combine and randomize
        all_opportunities = base_opportunities + general_opportunities
        random.shuffle(all_opportunities)
        
        # Select 3-5 opportunities
        num_opportunities = random.randint(3, 5)
        opportunities = all_opportunities[:num_opportunities]
        
        return opportunities
    
    def _generate_fallback_story_response(self, context: Dict[str, Any], 
                                        action_analysis: Dict[str, Any]) -> AgentResponse:
        """
        Generate fallback response when AI is unavailable.
        
        Args:
            context: Game context
            action_analysis: Player action analysis
            
        Returns:
            AgentResponse with fallback content
        """
        action_type = action_analysis.get("action_type", "other")
        
        # Select appropriate fallback response
        fallback_category = action_type if action_type in self.fallback_responses else "general"
        fallback_texts = self.fallback_responses[fallback_category]
        
        fallback_text = random.choice(fallback_texts)
        
        # Create basic story content
        story_content = {
            "text": fallback_text,
            "investigation_opportunities": self._generate_investigation_opportunities(context),
            "tension_level": context.get("tension_level", TensionLevel.CALM).value,
            "story_threads": {},
            "scene_id": context.get("scene_id", "unknown"),
            "content_id": f"fallback_{int(time.time())}",
            "metadata": {"source": "fallback", "agent": "story_agent"}
        }
        
        return AgentResponse(
            content=json.dumps(story_content, ensure_ascii=False),
            confidence=0.3,
            source="fallback",
            metadata={"reason": "ai_unavailable"}
        )
    
    def _get_fallback_text(self, context: Dict[str, Any]) -> str:
        """Get fallback text when AI response parsing fails"""
        return random.choice(self.fallback_responses["general"])
    
    def _get_fallback_response(self, context: Dict[str, Any]) -> str:
        """Override base class fallback for story-specific fallbacks"""
        action_text = context.get("player_action", "")
        action_analysis = self._analyze_action_type(action_text)
        
        response = self._generate_fallback_story_response(context, action_analysis)
        return response.content
    
    async def generate_scene(self, scene_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a new scene description.
        
        Args:
            scene_context: Context for scene generation
            
        Returns:
            Scene description and setup
        """
        scene_id = scene_context.get("scene_id", "unknown")
        tension_level = scene_context.get("tension_level", TensionLevel.CALM)
        
        # Build scene generation prompt
        scene_prompt = f"""
새로운 장면을 설정해주세요.

장면 ID: {scene_id}
긴장도: {tension_level.value if hasattr(tension_level, 'value') else tension_level}

크툴루 신화 스타일의 공포 분위기로 장면을 묘사해주세요.
다음 형식으로 응답해주세요:

SCENE_DESCRIPTION: [장면에 대한 자세한 묘사 (3-4문장)]

INITIAL_INVESTIGATIONS: [이 장면에서 가능한 초기 조사 기회들]
- [조사 기회 1]
- [조사 기회 2]
- [조사 기회 3]

ATMOSPHERE: [분위기나 특별한 요소들]

한국어로 응답해주세요.
"""
        
        ai_response = await self._generate_ai_response(scene_prompt)
        
        if ai_response.is_success:
            # Parse scene response similar to story response
            scene_data = self._parse_scene_response(ai_response.content, scene_context)
        else:
            # Fallback scene generation
            scene_data = self._generate_fallback_scene(scene_context)
        
        # Add memory of scene generation
        self.add_memory(
            content=f"Generated scene: {scene_id} - {scene_data.get('description', '')[:100]}...",
            importance=8,
            memory_type="scene_generation",
            scene_context=scene_id,
            keywords=[scene_id, "scene_generation"]
        )
        
        return scene_data
    
    def _parse_scene_response(self, ai_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response for scene generation"""
        scene_data = {
            "scene_id": context.get("scene_id", "unknown"),
            "description": "",
            "investigation_opportunities": [],
            "atmosphere": "",
            "metadata": {"source": "ai", "generated_by": "story_agent"}
        }
        
        # Simple parsing (could be enhanced)
        lines = ai_content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('SCENE_DESCRIPTION:'):
                current_section = 'description'
                scene_data["description"] = line.replace('SCENE_DESCRIPTION:', '').strip()
            elif line.startswith('INITIAL_INVESTIGATIONS:'):
                current_section = 'investigations'
            elif line.startswith('ATMOSPHERE:'):
                current_section = 'atmosphere'
                scene_data["atmosphere"] = line.replace('ATMOSPHERE:', '').strip()
            elif line.startswith('-') and current_section == 'investigations':
                opportunity = line.replace('-', '').strip()
                if opportunity:
                    scene_data["investigation_opportunities"].append(opportunity)
            elif current_section == 'description' and line:
                scene_data["description"] += " " + line
            elif current_section == 'atmosphere' and line:
                scene_data["atmosphere"] += " " + line
        
        # Fallback values if parsing failed
        if not scene_data["description"]:
            scene_data["description"] = f"{context.get('scene_id', '알 수 없는 장소')}에 도착했습니다. 주변은 신비롭고 불안한 분위기로 가득합니다."
        
        if not scene_data["investigation_opportunities"]:
            scene_data["investigation_opportunities"] = self._generate_investigation_opportunities(context)
        
        return scene_data
    
    def _generate_fallback_scene(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback scene when AI is unavailable"""
        scene_id = context.get("scene_id", "unknown")
        
        fallback_descriptions = [
            f"{scene_id}에 도착했습니다. 이곳은 평범해 보이지만 무언가 이상한 기운이 감돕니다.",
            f"새로운 장소 {scene_id}가 당신 앞에 펼쳐집니다. 주변은 고요하지만 긴장감이 흐릅니다.",
            f"{scene_id}의 분위기는 묘하게 불안합니다. 여기서 무슨 일이 일어났을까요?"
        ]
        
        return {
            "scene_id": scene_id,
            "description": random.choice(fallback_descriptions),
            "investigation_opportunities": self._generate_investigation_opportunities(context),
            "atmosphere": "신비롭고 불안한 분위기",
            "metadata": {"source": "fallback", "generated_by": "story_agent"}
        }
    
    def get_story_statistics(self) -> Dict[str, Any]:
        """Get statistics about story generation"""
        base_stats = self.get_performance_stats()
        
        # Add story-specific statistics
        story_memories = [m for m in self.memory if m.memory_type == "story_interaction"]
        scene_memories = [m for m in self.memory if m.memory_type == "scene_generation"]
        
        base_stats.update({
            "story_interactions": len(story_memories),
            "scenes_generated": len(scene_memories),
            "investigation_frequency": self.investigation_frequency,
            "tension_escalation_rate": self.tension_escalation_rate
        })
        
        return base_stats