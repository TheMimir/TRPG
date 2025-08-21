# 동적 선택지 시스템 가이드

이 문서는 새롭게 개선된 동적 선택지 생성 시스템의 사용법과 기능을 설명합니다.

## 개요

기존의 정적 선택지 배열을 동적 AI 기반 선택지 생성 시스템으로 교체하여 다음과 같은 문제를 해결했습니다:

- **반복적인 선택지**: 매번 같은 선택지가 나오는 문제
- **상황 부적합**: 현재 상황과 맞지 않는 선택지
- **AI 에이전트 오류**: AI 시스템 실패 시 적절한 대응 부족

## 주요 기능

### 1. AI 에이전트 상태 모니터링

#### 모니터링 요소
- **응답 시간**: 각 요청의 처리 시간 추적
- **성공률**: AI 에이전트의 성공/실패 비율
- **오류 추적**: 발생한 오류 종류와 빈도
- **타임아웃 감지**: 요청 타임아웃 발생 모니터링

#### 상태 분류
- `HEALTHY`: 정상 작동
- `SLOW_RESPONSE`: 응답이 느림 (10초 이상)
- `ERROR`: 오류 발생
- `TIMEOUT`: 타임아웃 발생
- `UNAVAILABLE`: 사용 불가

### 2. 컨텍스트 기반 동적 선택지

#### 고려 요소
- **현재 위치**: 입구, 실내, 위층, 지하실 등에 따른 적절한 선택지
- **캐릭터 상태**: 정신력, 체력에 따른 추가 선택지
- **긴장도**: 현재 긴장 수준에 맞는 선택지 조정
- **환경 요소**: 벽난로, 초상화, 책 등 환경에 따른 상호작용
- **발견한 단서**: 이전 발견 내용을 반영한 선택지
- **스토리 진행**: 활성 스토리 스레드와 연결된 선택지

#### 선택지 카테고리
- `investigation`: 조사 관련
- `exploration`: 탐험 관련  
- `action`: 직접 행동
- `observation`: 관찰
- `stealth`: 은밀한 행동
- `social`: NPC와 상호작용
- `safety`: 안전 확보
- `mental_health`: 정신력 관리
- `physical_health`: 체력 관리

### 3. 상황별 선택지 템플릿

#### 장소별 템플릿
- **입구**: 문 두드리기, 창문 보기, 다른 입구 찾기
- **실내**: 체계적 조사, 위층 이동, 가구 살펴보기
- **위층**: 방문 확인, 은밀한 이동, 구조 분석
- **지하실**: 철저한 수색, 빠른 탐색, 오컬트 조사
- **야외**: 지형 파악, 안전한 장소 찾기, 환경 관찰

#### 긴장도별 수정
- **극도**: 공포 극복, 즉시 도피, 진정 노력
- **높음**: 경계 유지, 조심스러운 행동
- **중간**: 불안감 무시, 상황 재평가

### 4. 사용자 피드백 시스템

#### AI 상태 정보 제공
```python
ai_status = {
    "system_health": "healthy",  # 전체 시스템 상태
    "using_ai": True,            # AI 사용 여부
    "response_time_ms": 245,     # 응답 시간
    "fallback_reason": None      # 대체 시스템 사용 이유
}
```

#### 사용자 메시지
- "AI 스토리 시스템이 정상적으로 작동하고 있습니다."
- "AI 스토리 시스템이 일부 문제를 겪고 있지만 기능하고 있습니다."
- "AI 스토리 시스템에 문제가 있어 대체 시스템을 사용하고 있습니다."

## 사용 방법

### 1. GameplayController 사용

```python
# GameplayController 초기화
controller = GameplayController(game_manager)

# 선택지 요청
character_state = {
    "sanity": 65,
    "hp": 80,
    "skills": ["Investigation", "Library Use"],
    "inventory": ["flashlight", "notebook"]
}

result = await controller.get_current_choices(character_state)

# 결과 구조
choices = result["choices"]           # 생성된 선택지 목록
ai_status = result["ai_status"]       # AI 시스템 상태
context_info = result["context_info"] # 컨텍스트 정보
```

### 2. AI 시스템 상태 확인

```python
# 전체 시스템 상태
system_status = controller.get_ai_system_status()

# 사용자 친화적 메시지
user_message = controller.get_user_feedback_message()

# 디버그 정보
debug_info = controller.get_debug_info()
```

### 3. StoryAgent 직접 사용

```python
# 향상된 선택지 생성
input_data = {
    "action_type": "choice_generation",
    "scene_id": "scene_002_inside_house",
    "turn_number": 15,
    "tension_level": "medium",
    "character_state": character_state,
    "environmental_context": {
        "location": "거실",
        "environment": ["fireplace", "portraits"],
        "npcs": ["집사"],
        "clues": ["이상한 소리", "숨겨진 문"]
    }
}

result = await story_agent.process_input(input_data)
```

## 대체 시스템 (Fallback)

AI 에이전트가 실패할 경우 다음과 같은 대체 시스템이 작동합니다:

### 1. 향상된 컨텍스트 인식 대체 시스템
- 장소에 따른 적절한 선택지 제공
- 캐릭터 상태를 반영한 추가 선택지
- 스토리 진행 상황을 고려한 선택지

### 2. 긴급 대체 선택지
- "현재 상황을 신중하게 관찰한다"
- "조심스럽게 다음 단계로 진행한다"  
- "주변에서 단서를 찾아본다"

## 성능 최적화

### 1. 응답 시간 관리
- 기본 타임아웃: 15초
- 응답 시간 추적 및 평균 계산
- 느린 응답 감지 시 경고

### 2. 메모리 효율성
- 최근 10회 응답 시간만 보관
- 중복 선택지 제거
- 우선순위 기반 선택지 정렬

### 3. 오류 처리
- 자동 재시도 없음 (무한 대기 방지)
- 즉각적인 대체 시스템 활성화
- 상세한 오류 로깅

## 확장 가능성

### 1. 새로운 장소 타입 추가
`_initialize_contextual_generators()` 함수에 새로운 생성기 추가

### 2. 추가 환경 요소
`_get_environmental_choices()` 함수에 새로운 요소 매핑 추가

### 3. 캐릭터 상태 확장
`_assess_character_condition()` 함수에 새로운 상태 평가 로직 추가

## 문제 해결

### 1. AI 응답 없음
- 대체 시스템이 자동으로 활성화됨
- 사용자에게 상황 설명 메시지 표시
- 시스템 상태는 계속 모니터링됨

### 2. 부적절한 선택지
- 컨텍스트 분석 로직 점검
- 우선순위 점수 시스템 조정
- 대체 시스템의 품질 향상

### 3. 성능 저하
- 응답 시간 모니터링으로 감지
- 타임아웃 설정 조정
- 시스템 상태에 따른 적응적 대응

이 시스템을 통해 플레이어는 항상 현재 상황에 적합하고 다양한 선택지를 제공받을 수 있으며, AI 시스템의 상태를 투명하게 확인할 수 있습니다.