# 크툴루 TRPG 선택지 동기화 문제 ULTRATHINK 분석 결과

## 🎯 **문제의 정확한 원인**

### 1. **하드코딩된 선택지 vs 동적 스토리**
**위치:** `src/agents/story_agent.py` 588-679 줄

```python
# 현재 문제 코드
if "entrance" in scene_id.lower():
    choices = [
        {
            "text": "문을 조심스럽게 두드려본다",  # 하드코딩된 선택지
            "consequences": ["소음 발생", "주의 끌기"],
        },
        # ... 다른 하드코딩된 선택지들
    ]
```

**문제:** 실제 스토리 내용과 관계없이 장면 ID만으로 고정된 선택지를 제공

### 2. **이중 폴백 시스템의 불일치**
**위치A:** `src/ui/gameplay_interface.py` 340-359 줄
**위치B:** `src/core/gameplay_controller.py` 570-618 줄

- GameplayInterface: 턴 수 기반 폴백
- GameplayController: 장면 ID 기반 폴백
- **결과:** 서로 다른 선택지 세트 생성

### 3. **데이터 타입 변환 불일치**
**위치:** `src/core/gameplay_controller.py` 464-471 줄

```python
# 선택지 텍스트 변환 로직이 여러 곳에 분산
if isinstance(choice_text, list):
    choice_text = ' '.join(choice_text)
```

**문제:** DisplayManager와 GameplayController에서 서로 다른 변환 규칙 적용

---

## 🛠 **완벽한 해결책**

### **즉시 적용 가능한 수정 사항들**

#### A. StoryAgent 선택지 생성 통일

**파일:** `src/agents/story_agent.py`
**수정 위치:** 564-738 줄

```python
async def _generate_choices(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate choices with perfect text synchronization."""
    
    # 1. 컨텍스트 정보 추출
    scene_id = input_data.get("scene_id", "unknown")
    turn_number = input_data.get("turn_number", 1)
    current_story_text = input_data.get("current_story_text", "")  # 추가!
    
    # 2. 실제 스토리 내용 기반 선택지 생성
    story_based_choices = self._extract_choices_from_story(current_story_text)
    
    # 3. 장면별 기본 선택지와 통합
    scene_choices = self._get_scene_template_choices(scene_id)
    
    # 4. 중복 제거하여 최종 선택지 결정
    final_choices = self._merge_and_validate_choices(story_based_choices, scene_choices)
    
    return {"choices": final_choices}
```

#### B. GameplayInterface 선택지 처리 단순화

**파일:** `src/ui/gameplay_interface.py`  
**수정 위치:** 318-338 줄, 437-502 줄

```python
async def _get_current_choices(self) -> List[str]:
    """Get choices with guaranteed string format."""
    
    # GameplayController를 통해 검증된 선택지만 사용
    choice_objects = await self.gameplay_controller.get_current_choices(character_state)
    
    if choice_objects:
        # Choice 객체에서 이미 검증된 텍스트만 추출
        self._current_choice_objects = choice_objects
        display_texts = []
        
        for i, choice in enumerate(choice_objects):
            # 추가 안전성 검사
            text = getattr(choice, 'text', f'선택지 {i+1}')
            if not isinstance(text, str):
                text = str(text)
            text = text.strip()
            display_texts.append(text)
            
        logger.info(f"Extracted {len(display_texts)} validated choice texts")
        return display_texts
```

#### C. DisplayManager 안전장치 강화

**파일:** `src/ui/display_manager.py`
**수정 위치:** 314-327 줄

```python
def create_choice_menu(self, choices, title="행동을 선택하세요"):
    """Create choice menu with enhanced validation."""
    
    table = Table(title=title, box=box.ROUNDED, title_style=self.styles['title'])
    table.add_column("옵션", style=self.styles['cosmic'])
    table.add_column("행동", style=Style(color=self.colors['bone_white']))
    
    for i, choice in enumerate(choices, 1):
        # 강화된 텍스트 검증
        if choice is None:
            safe_choice = f"선택지 {i}"
        elif isinstance(choice, str):
            safe_choice = choice.strip()
        elif isinstance(choice, (list, tuple)):
            safe_choice = ' '.join(str(x) for x in choice if x)
        else:
            safe_choice = str(choice)
        
        # 문제 문자 제거
        safe_choice = safe_choice.replace('\x00', '').replace('\n', ' ').replace('\r', ' ')
        safe_choice = ' '.join(safe_choice.split())  # 연속 공백 제거
        
        # 빈 텍스트 방지
        if not safe_choice.strip():
            safe_choice = f"선택지 {i}"
            
        table.add_row(f"[{i}]", safe_choice)
        
        # 디버깅용 로그
        logger.debug(f"Choice {i} display text: '{safe_choice}' (length: {len(safe_choice)})")
    
    return Panel(table, border_style=self.styles['mystery'])
```

---

## 🔧 **즉시 적용할 핵심 수정사항**

### 1. **GameplayController에 통합 검증 추가**

**파일:** `src/core/gameplay_controller.py`
**위치:** 438-490 줄 `_get_agent_choices` 메서드

```python
# 현재 코드의 464-471 줄을 다음과 같이 수정:
for i, choice_data in enumerate(response['choices']):
    # 강화된 텍스트 검증
    choice_text = choice_data.get('text', f'선택지 {i+1}')
    
    # 확실한 문자열 변환
    if isinstance(choice_text, list):
        choice_text = ' '.join(str(x) for x in choice_text if x)
    elif not isinstance(choice_text, str):
        choice_text = str(choice_text)
    
    # 텍스트 정규화
    choice_text = choice_text.strip()
    choice_text = ' '.join(choice_text.split())  # 연속 공백 제거
    
    # 빈 텍스트 방지
    if not choice_text:
        choice_text = f'선택지 {i+1}'
        
    # 디버깅 로그 추가
    logger.info(f"Choice {i+1} validated: '{choice_text}'")
```

### 2. **StoryAgent에 현재 스토리 텍스트 전달**

**파일:** `src/core/gameplay_controller.py`  
**위치:** 446-455 줄

```python
# agent_input에 현재 스토리 추가
agent_input = {
    'action_type': 'choice_generation',
    'scene_id': context.scene_id,
    'turn_number': context.turn_number,
    'story_threads': context.story_threads,
    'tension_level': context.tension_level.value,
    'previous_choices': context.choice_history,
    'character_state': context.character_state,
    'narrative_flags': context.narrative_flags,
    'current_story_text': context.story_state.get('current_story_text', '')  # 추가!
}
```

---

## 🎯 **테스트 및 검증 방법**

### 1. **로그 기반 디버깅**

다음 로그를 활성화하여 문제를 추적:

```python
# src/ui/gameplay_interface.py 에 추가
logger.debug(f"Generated choices: {[type(c).__name__ + ': ' + str(c)[:50] for c in choices]}")

# src/ui/display_manager.py 에 추가  
logger.debug(f"Displaying choice {i}: '{safe_choice}' (original: {repr(choice)})")

# src/core/gameplay_controller.py 에 추가
logger.info(f"Agent returned {len(response.get('choices', []))} choices")
```

### 2. **런타임 검증**

```python
# GameplayInterface._display_choices_and_get_input 메서드에 추가
def _display_choices_and_get_input(self, choices: List[str]) -> int:
    # 검증 코드 추가
    for i, choice in enumerate(choices):
        if not isinstance(choice, str):
            logger.error(f"Choice {i} is not string: {type(choice)} = {repr(choice)}")
            
        if len(choice.strip()) == 0:
            logger.error(f"Choice {i} is empty or whitespace only")
```

---

## 📋 **최종 해결 확인 체크리스트**

- [ ] StoryAgent가 일관된 텍스트 형식으로 선택지 반환
- [ ] GameplayController가 모든 선택지를 문자열로 검증
- [ ] GameplayInterface가 표시 텍스트와 처리 객체 동기화
- [ ] DisplayManager가 안전한 텍스트 표시
- [ ] 로그에서 선택지 타입 불일치 오류 제거
- [ ] 실제 게임에서 "옵션 내용 상이" 메시지 해결

---

## 🚀 **즉시 시도할 수 있는 간단한 수정**

가장 빠른 해결을 위해 다음 하나의 파일만 수정:

**파일:** `src/core/gameplay_controller.py`  
**라인:** 463 줄 근처

```python
# 기존
choice_text = choice_data.get('text', '')

# 수정 후
choice_text = choice_data.get('text', f'선택지 {i+1}')
# 확실한 문자열 보장
if isinstance(choice_text, (list, tuple)):
    choice_text = ' '.join(str(x) for x in choice_text)
elif not isinstance(choice_text, str):
    choice_text = str(choice_text)
choice_text = choice_text.strip()
if not choice_text:
    choice_text = f'선택지 {i+1}'
```

이 수정만으로도 대부분의 선택지 불일치 문제가 해결될 것입니다.