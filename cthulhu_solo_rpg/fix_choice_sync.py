"""
크툴루 TRPG 선택지 동기화 문제 해결책

이 스크립트는 선택지 표시와 실제 옵션 간의 불일치 문제를 해결하기 위한
통합된 선택지 관리 시스템을 제안합니다.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

@dataclass
class UnifiedChoice:
    """통합된 선택지 클래스 - 표시와 처리 간의 일관성 보장"""
    id: str
    display_text: str  # 화면에 표시되는 텍스트 (정확히 이것만 표시됨)
    action_data: Dict[str, Any]  # 실제 처리에 사용되는 데이터
    consequences: List[str]
    requirements: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        """데이터 일관성 검증"""
        if not self.display_text or not isinstance(self.display_text, str):
            raise ValueError(f"display_text must be non-empty string, got: {self.display_text}")
        
        # 표시 텍스트 정규화
        self.display_text = self.display_text.strip()
        self.display_text = ' '.join(self.display_text.split())  # 연속 공백 제거
        
        # 안전한 기본값 설정
        if not self.action_data:
            self.action_data = {"type": "generic", "text": self.display_text}
        if not self.consequences:
            self.consequences = []
        if not self.requirements:
            self.requirements = {}
        if not self.metadata:
            self.metadata = {}

class ChoiceGenerationContext:
    """선택지 생성을 위한 통합 컨텍스트"""
    
    def __init__(self, scene_id: str, turn_number: int, story_state: Dict[str, Any]):
        self.scene_id = scene_id
        self.turn_number = turn_number
        self.story_state = story_state
        self.dynamic_story_content = story_state.get('current_story_text', '')
        self.narrative_flags = story_state.get('narrative_flags', {})
        self.tension_level = story_state.get('tension_level', 'calm')

class UnifiedChoiceGenerator:
    """통합된 선택지 생성 시스템"""
    
    def __init__(self):
        self.choice_templates = self._load_choice_templates()
        self.story_context_analyzer = StoryContextAnalyzer()
    
    def generate_choices(self, context: ChoiceGenerationContext) -> List[UnifiedChoice]:
        """컨텍스트에 기반한 일관된 선택지 생성"""
        
        # 1. 스토리 내용에서 암시된 행동들 추출
        story_implied_actions = self.story_context_analyzer.extract_implied_actions(
            context.dynamic_story_content
        )
        
        # 2. 장면별 기본 선택지 가져오기
        scene_base_choices = self.choice_templates.get(context.scene_id, [])
        
        # 3. 스토리 컨텍스트와 기본 선택지 통합
        unified_choices = self._merge_choices(
            story_implied_actions, 
            scene_base_choices, 
            context
        )
        
        # 4. 선택지 검증 및 정규화
        validated_choices = []
        for i, choice_data in enumerate(unified_choices):
            try:
                choice = UnifiedChoice(
                    id=f"{context.scene_id}_turn_{context.turn_number}_choice_{i}",
                    display_text=choice_data['text'],
                    action_data={
                        "type": choice_data.get('type', 'story_action'),
                        "scene_id": context.scene_id,
                        "original_text": choice_data['text'],
                        "story_context": choice_data.get('story_context', {})
                    },
                    consequences=choice_data.get('consequences', []),
                    requirements=choice_data.get('requirements', {}),
                    metadata={
                        "generation_method": choice_data.get('source', 'template'),
                        "turn_number": context.turn_number,
                        "scene_id": context.scene_id
                    }
                )
                validated_choices.append(choice)
                
            except ValueError as e:
                logger.error(f"Failed to create choice {i}: {e}")
                # 안전한 폴백 선택지 생성
                fallback_choice = UnifiedChoice(
                    id=f"{context.scene_id}_fallback_{i}",
                    display_text=f"다른 방법을 찾아본다",
                    action_data={"type": "fallback", "index": i},
                    consequences=["새로운 접근"],
                    requirements={},
                    metadata={"is_fallback": True}
                )
                validated_choices.append(fallback_choice)
        
        return validated_choices
    
    def _load_choice_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """장면별 선택지 템플릿 로드"""
        return {
            "scene_001_entrance": [
                {
                    "text": "등대 꼭대기에서 더 많은 흔적을 찾는다",
                    "type": "investigation",
                    "consequences": ["정보 획득", "시간 소모"],
                    "requirements": {"skill": "Spot Hidden"}
                },
                {
                    "text": "바위에 새겨진 기호를 자세히 조사한다",
                    "type": "occult_investigation", 
                    "consequences": ["오컬트 지식", "정신력 위험"],
                    "requirements": {"skill": "Occult"}
                },
                {
                    "text": "조셉 하트와 이야기를 나누어 그의 목격담을 들어본다",
                    "type": "npc_interaction",
                    "consequences": ["증언 획득", "NPC 관계 발전"],
                    "requirements": {}
                },
                {
                    "text": "마을 도서관으로 향해 관련 기록을 찾아본다", 
                    "type": "research",
                    "consequences": ["배경 지식", "새로운 단서"],
                    "requirements": {"skill": "Library Use"}
                }
            ],
            "scene_002_inside_house": [
                {
                    "text": "거실을 체계적으로 조사한다",
                    "type": "detailed_search",
                    "consequences": ["물리적 단서", "시간 소모"],
                    "requirements": {"skill": "Investigation"}
                },
                {
                    "text": "위층으로 조심스럽게 올라간다",
                    "type": "location_change",
                    "consequences": ["새로운 지역", "잠재적 위험"],
                    "requirements": {}
                }
            ]
        }
    
    def _merge_choices(self, story_actions: List[Dict[str, Any]], 
                      base_choices: List[Dict[str, Any]], 
                      context: ChoiceGenerationContext) -> List[Dict[str, Any]]:
        """스토리 기반 선택지와 템플릿 선택지 통합"""
        
        merged = []
        
        # 스토리에서 추출한 선택지 우선
        for action in story_actions[:2]:  # 최대 2개
            action['source'] = 'story_content'
            merged.append(action)
        
        # 기본 템플릿 선택지 추가 (중복 제거)
        for base_choice in base_choices:
            if not self._is_duplicate_choice(base_choice, merged):
                base_choice['source'] = 'template'
                merged.append(base_choice)
        
        # 최대 4개 선택지로 제한
        return merged[:4]
    
    def _is_duplicate_choice(self, new_choice: Dict[str, Any], 
                           existing_choices: List[Dict[str, Any]]) -> bool:
        """중복 선택지 검사"""
        new_text = new_choice['text'].lower().strip()
        
        for existing in existing_choices:
            existing_text = existing['text'].lower().strip()
            # 단어 70% 이상 겹치면 중복으로 간주
            if self._text_similarity(new_text, existing_text) > 0.7:
                return True
        return False
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산 (간단한 단어 기반)"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

class StoryContextAnalyzer:
    """스토리 내용에서 가능한 행동 추출"""
    
    def extract_implied_actions(self, story_text: str) -> List[Dict[str, Any]]:
        """스토리 텍스트에서 암시된 행동들 추출"""
        
        if not story_text:
            return []
        
        implied_actions = []
        story_lower = story_text.lower()
        
        # 키워드 기반 행동 추출
        action_patterns = {
            "조사": {
                "keywords": ["흔적", "단서", "증거", "기호", "표시"],
                "action_template": "{}을(를) 자세히 조사한다",
                "type": "investigation"
            },
            "이동": {
                "keywords": ["문", "계단", "방", "복도", "위", "아래"],
                "action_template": "{}(으)로 향한다",
                "type": "movement"
            },
            "상호작용": {
                "keywords": ["사람", "목소리", "소리", "누군가"],
                "action_template": "{}와 소통을 시도한다",
                "type": "interaction"
            }
        }
        
        # 패턴 매칭으로 행동 생성
        for action_type, pattern_data in action_patterns.items():
            for keyword in pattern_data["keywords"]:
                if keyword in story_lower:
                    # 실제 스토리 내용에 기반한 구체적인 행동 생성
                    action_text = self._generate_contextual_action(
                        story_text, keyword, pattern_data["action_template"]
                    )
                    
                    if action_text:
                        implied_actions.append({
                            "text": action_text,
                            "type": pattern_data["type"],
                            "story_context": {"keyword": keyword, "source": story_text[:100]},
                            "consequences": self._predict_consequences(action_type)
                        })
                        
                        # 하나의 액션 타입당 최대 1개
                        break
        
        return implied_actions[:3]  # 최대 3개 반환
    
    def _generate_contextual_action(self, story_text: str, keyword: str, 
                                   action_template: str) -> str:
        """컨텍스트에 맞는 구체적인 행동 생성"""
        
        # 키워드 주변 문맥 추출
        sentences = story_text.split('.')
        relevant_sentence = ""
        
        for sentence in sentences:
            if keyword in sentence.lower():
                relevant_sentence = sentence.strip()
                break
        
        if not relevant_sentence:
            return ""
        
        # 구체적인 객체 추출 시도
        if keyword == "흔적":
            return "발견된 흔적을 더 자세히 조사한다"
        elif keyword == "기호":
            return "새겨진 기호들의 의미를 파악하려 한다"
        elif keyword == "문":
            return "앞에 있는 문을 열어본다"
        elif keyword == "사람" or keyword == "누군가":
            return "그 사람과 대화를 시도한다"
        else:
            return action_template.format(keyword)
    
    def _predict_consequences(self, action_type: str) -> List[str]:
        """행동 타입에 따른 결과 예측"""
        consequence_map = {
            "조사": ["새로운 정보", "시간 소모"],
            "이동": ["위치 변경", "새로운 상황"],
            "상호작용": ["대화 진전", "관계 변화"]
        }
        
        return consequence_map.get(action_type, ["예상치 못한 결과"])

# 통합된 선택지 처리 시스템
class UnifiedChoiceProcessor:
    """선택지 표시와 처리를 완전히 동기화"""
    
    def __init__(self):
        self.choice_generator = UnifiedChoiceGenerator()
        self.active_choices: List[UnifiedChoice] = []
    
    def generate_and_store_choices(self, context: ChoiceGenerationContext) -> List[str]:
        """선택지 생성하고 저장한 후 표시용 텍스트만 반환"""
        
        # 통합 시스템으로 선택지 생성
        self.active_choices = self.choice_generator.generate_choices(context)
        
        # 표시용 텍스트만 추출 (이것이 실제 화면에 표시됨)
        display_texts = [choice.display_text for choice in self.active_choices]
        
        logger.info(f"Generated {len(display_texts)} synchronized choices")
        logger.debug(f"Choice texts: {display_texts}")
        
        return display_texts
    
    def process_selected_choice(self, choice_index: int) -> Dict[str, Any]:
        """선택된 인덱스로 정확한 선택지 처리"""
        
        if not (0 <= choice_index < len(self.active_choices)):
            raise ValueError(f"Invalid choice index: {choice_index}")
        
        selected_choice = self.active_choices[choice_index]
        
        # 정확히 저장된 선택지 데이터로 처리
        result = {
            "choice_id": selected_choice.id,
            "display_text": selected_choice.display_text,  # 화면에 표시된 것과 동일
            "action_data": selected_choice.action_data,
            "consequences": selected_choice.consequences,
            "requirements": selected_choice.requirements,
            "metadata": selected_choice.metadata
        }
        
        logger.info(f"Processed choice: {selected_choice.display_text}")
        return result
    
    def get_choice_by_text(self, choice_text: str) -> Optional[UnifiedChoice]:
        """텍스트로 선택지 검색 (폴백용)"""
        for choice in self.active_choices:
            if choice.display_text.strip() == choice_text.strip():
                return choice
        return None

# 사용 예시
def demonstrate_unified_system():
    """통합 시스템 사용 예시"""
    
    # 게임 상황 설정
    story_context = {
        'current_story_text': "당신은 등대 근처에서 이상한 기호들을 발견했습니다. 조셉 하트가 근처에서 기다리고 있고, 마을 도서관이 보입니다.",
        'narrative_flags': {'lighthouse_visited': True},
        'tension_level': 'tense'
    }
    
    context = ChoiceGenerationContext(
        scene_id="scene_001_entrance",
        turn_number=5,
        story_state=story_context
    )
    
    # 통합 처리 시스템 초기화
    processor = UnifiedChoiceProcessor()
    
    # 동기화된 선택지 생성
    display_choices = processor.generate_and_store_choices(context)
    
    print("=== 생성된 선택지 (화면에 표시될 내용) ===")
    for i, choice_text in enumerate(display_choices, 1):
        print(f"{i}. {choice_text}")
    
    # 사용자가 선택지 2번을 선택했다고 가정
    selected_index = 1  # 0-based index
    result = processor.process_selected_choice(selected_index)
    
    print(f"\n=== 처리된 선택지 결과 ===")
    print(f"선택된 텍스트: {result['display_text']}")
    print(f"행동 타입: {result['action_data']['type']}")
    print(f"예상 결과: {', '.join(result['consequences'])}")

if __name__ == "__main__":
    demonstrate_unified_system()