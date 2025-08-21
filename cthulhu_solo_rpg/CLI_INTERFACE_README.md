# 크툴루 솔로 TRPG - CLI 인터페이스

Rich 라이브러리를 활용한 몰입감 있는 호러 테마 CLI 인터페이스가 구현되었습니다.

## 🎭 주요 기능

### 구현된 파일들

1. **`src/ui/display_manager.py`** - 시각적 효과 및 스타일링
   - 크툴루 호러 테마 색상 스킴
   - 아스키 아트 및 시각적 요소
   - 캐릭터 상태 표시 바
   - 주사위 굴리기 애니메이션
   - 정신력 손실 효과
   - 호러 분위기 연출 효과

2. **`src/ui/menu_system.py`** - 메뉴 시스템 및 네비게이션
   - 메인 메뉴 (새 게임, 불러오기, 설정 등)
   - 캐릭터 생성 마법사
     - 속성 생성 (포인트 바이, 랜덤, 표준 배열)
     - 직업 선택
     - 기술 할당
   - 시나리오 선택 메뉴
   - 인게임 메뉴 (캐릭터 시트, 인벤토리, 저장/불러오기)
   - 설정 메뉴

3. **`src/ui/gameplay_interface.py`** - 턴 기반 게임플레이
   - 실시간 레이아웃 업데이트
   - 스토리 텍스트 표시
   - 선택지 메뉴
   - 주사위 굴리기 시스템
   - 정신력 체크
   - 게임 로그
   - 키보드 단축키 (M/I/C/Q)

4. **`src/ui/cli_interface.py`** - 메인 CLI 통합
   - 모든 컴포넌트 통합
   - 상태 관리
   - 오류 처리 (호러 테마)
   - 긴급 저장
   - 우아한 종료

## 🌟 호러 테마 요소

### 색상 스킴
- **Blood Red** (`#8B0000`) - 위험, 정신력 손실
- **Deep Purple** (`#301934`) - 신비, 미스터리  
- **Eldritch Green** (`#355E3B`) - 성공, 건강
- **Cosmic Blue** (`#0F0F23`) - 우주적 공포
- **Bone White** (`#F8F8FF`) - 일반 텍스트
- **Shadow Gray** (`#2F2F2F`) - 속삭임, 부차적 정보
- **Madness Yellow** (`#DAA520`) - 광기, 경고
- **Sanity Loss** (`#FF4500`) - 정신력 손실

### 시각적 효과
- 아스키 아트 로고
- 상태 표시 바 (HP, 정신력, MP)
- 주사위 애니메이션
- 깜빡임 효과 (공포 장면)
- 타이핑 애니메이션 (optional)
- 광기 상징들

### 분위기 연출
- 정신력에 따른 화면 효과
- 공포 레벨별 텍스트 스타일
- 로보크래프트 인용구
- 호러 테마 오류 메시지
- 드라마틱한 페어웰 메시지

## 🚀 실행 방법

### 1. 의존성 설치
```bash
# 가상 환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Rich 라이브러리 설치
pip install rich
```

### 2. 데모 실행
```bash
# 데모 스크립트 실행
python demo_cli.py

# 또는 직접 실행
python -c "from src.ui.cli_interface import create_cli_interface; create_cli_interface().run()"
```

### 3. 모듈별 테스트
```bash
# 디스플레이 매니저 테스트
python -c "from src.ui.display_manager import DisplayManager; dm = DisplayManager(); print('Display Manager ready!')"

# 메뉴 시스템 테스트  
python -c "from src.ui.menu_system import MenuSystem; ms = MenuSystem(); print('Menu System ready!')"
```

## 🎮 사용 방법

### 메인 메뉴
1. **New Game** - 새로운 게임 시작
2. **Load Game** - 저장된 게임 불러오기
3. **Character Generator** - 캐릭터 생성 마법사
4. **Settings** - 게임 설정
5. **About** - 게임 정보
6. **Exit** - 게임 종료

### 캐릭터 생성
- **포인트 바이**: 460 포인트를 속성에 직접 배분
- **랜덤 생성**: 주사위로 속성 결정
- **표준 배열**: 미리 정의된 값들을 속성에 할당

### 게임플레이 단축키
- **M** - 게임 메뉴 열기
- **I** - 인벤토리 확인
- **C** - 캐릭터 시트 보기
- **Q** - 게임 종료
- **1-4** - 선택지 선택

### 호러 효과
- 정신력이 낮아질수록 화면 효과 증가
- 공포 상황에서 텍스트 스타일 변화
- 주사위 굴리기 시 긴장감 있는 애니메이션
- 정신력 손실 시 드라마틱한 효과

## 🔧 기술적 특징

### Rich 라이브러리 활용
- `Panel` - 정보 박스 및 테두리
- `Table` - 캐릭터 시트, 상태 표시
- `Layout` - 화면 분할 레이아웃
- `Progress` - 로딩 효과, 상태 바
- `Text` - 색상 및 스타일링
- `Live` - 실시간 애니메이션

### 모듈 구조
- **DisplayManager** - 모든 시각적 요소 관리
- **MenuSystem** - 메뉴 네비게이션 처리
- **GameplayInterface** - 턴 기반 게임 로직
- **CLIInterface** - 메인 통합 및 상태 관리

### 오류 처리
- 호러 테마의 오류 메시지
- 긴급 저장 시스템
- Ctrl+C 우아한 처리
- 복구 메커니즘

## 📝 확장 가능성

### AI 통합
- 현재는 Mock 데이터 사용
- `_get_current_story_text()` - AI 스토리 생성 연결점
- `_get_current_choices()` - AI 선택지 생성 연결점
- `_get_choice_consequences()` - AI 결과 처리 연결점

### 게임 엔진 통합
- `set_game_engine()` 메서드로 게임 엔진 연결
- 캐릭터 데이터 실시간 반영
- 저장/불러오기 시스템 연결
- 시나리오 데이터 로드

### 추가 기능
- 사운드 효과 (가능하다면)
- 더 많은 호러 효과
- 커스터마이징 가능한 테마
- 멀티플레이 지원 인터페이스

## 🎨 예시 화면

```
╔═══════════════ CALL OF CTHULHU: SOLO ═══════════════╗
║                                                     ║
║  당신은 어두운 도서관에 홀로 서 있습니다...         ║
║  벽에 걸린 시계가 자정을 알리며 울려 퍼집니다.       ║
║                                                     ║
║  [1] 금지된 서적 코너로 향한다                      ║
║  [2] 사서에게 말을 건다                             ║
║  [3] 조용히 도서관을 떠난다                         ║
║                                                     ║
╠═════════════════ 상태 ═════════════════════════════╣
║ HP: ██████████ 15/15    MP: ████████░░ 12/15      ║
║ SAN: ██████░░░░ 60/100  LUCK: █████████░ 45/50    ║
╚═════════════════════════════════════════════════════╝
```

## 👤 개발자 노트

이 CLI 인터페이스는 크툴루 신화의 우주적 공포를 텍스트 기반으로 표현하는 것을 목표로 합니다. Rich 라이브러리의 강력한 기능을 활용하여 터미널에서도 몰입감 있는 호러 경험을 제공합니다.

*"The oldest and strongest emotion of mankind is fear, and the oldest and strongest kind of fear is fear of the unknown."* - H.P. Lovecraft

---

**Ph'nglui mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn**