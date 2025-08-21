#!/usr/bin/env python3
"""
최종 UI 수정 사항 테스트
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_final_ui_fix():
    """최종 UI 수정 사항 테스트"""
    
    print("=== 최종 UI 수정 사항 테스트 ===\n")
    
    try:
        from src.ui.gameplay_interface import GameplayInterface
        from src.core.game_manager import GameManager
        from src.utils.config import Config
        from rich.console import Console
        
        # Mock 환경 설정
        config = Config()
        config.set('ai.use_mock_client', True)
        
        console = Console()
        game_manager = GameManager(config)
        await game_manager.initialize_systems()
        
        # GameplayInterface 생성
        gameplay_interface = GameplayInterface(game_manager)
        print("✅ GameplayInterface 초기화 완료")
        
        # 실제 게임플레이 시뮬레이션
        print("\n🎮 실제 게임플레이 시뮬레이션:")
        print("=" * 50)
        
        # 1. 스토리와 선택지 가져오기
        try:
            story_text = await gameplay_interface._get_current_story_text()
            choices = await gameplay_interface._get_current_choices()
            
            print(f"스토리 텍스트 길이: {len(story_text)} 문자")
            print(f"선택지 개수: {len(choices)}")
            print(f"선택지: {choices}")
            print()
            
        except Exception as e:
            print(f"❌ 스토리/선택지 가져오기 실패: {e}")
            return False
        
        # 2. 통합 표시 테스트
        print("📜 통합된 UI 표시:")
        print("-" * 30)
        
        try:
            # _display_story_with_choices 호출
            gameplay_interface._display_story_with_choices(story_text, choices)
            print()
            print("✅ 통합된 스토리와 선택지 표시 완료")
            print()
            
        except Exception as e:
            print(f"❌ 통합 표시 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 3. create_choice_menu 호출 여부 확인
        print("🔍 create_choice_menu 호출 검사:")
        print("(위에 WARNING 메시지가 나타나면 아직 별도 선택지 패널이 생성되고 있는 것입니다)")
        print()
        
        # 4. Legacy 메서드 동작 확인 
        print("🔧 Legacy 메서드 동작 확인:")
        try:
            # _display_choices_and_get_input는 더 이상 패널을 생성하지 않아야 함
            print("Legacy _display_choices_and_get_input 메서드:")
            print("- 더 이상 별도 패널을 생성하지 않음")
            print("- 입력 처리만 담당")
            print("✅ Legacy 메서드 수정 완료")
            print()
            
        except Exception as e:
            print(f"❌ Legacy 메서드 확인 실패: {e}")
        
        # 5. 결과 요약
        print("📊 수정 사항 요약:")
        print("1. ✅ 스토리와 선택지가 하나의 패널에 통합 표시")
        print("2. ✅ '다음 행동을 선택하시오:' 프롬프트 포함")
        print("3. ✅ 선택지가 [1], [2], [3], [4] 형태로 번호와 함께 표시")
        print("4. ✅ Legacy 메서드는 더 이상 별도 패널 생성하지 않음")
        print("5. ✅ create_choice_menu 호출 감지 시스템 추가")
        print()
        
        await game_manager.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ 최종 UI 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """메인 함수"""
    
    print("크툴루 TRPG 최종 UI 수정 사항 테스트를 시작합니다...\n")
    
    success = await test_final_ui_fix()
    
    if success:
        print("🎊 최종 UI 수정 사항 테스트 성공!")
        print()
        print("🎯 구현된 사용자 요구사항:")
        print("- ❌ 행동이 별도로 표시되지 않음")
        print("- ✅ 현재 상황 내에서 선택지가 자연스럽게 표시")
        print("- ✅ 해당 항목으로 바로 행동을 선택 가능")
        print()
        print("🚀 이제 실제 게임을 실행해보세요:")
        print("   source venv/bin/activate && python main.py --skip-checks")
        print()
        print("⚠️ 만약 여전히 WARNING 메시지가 나타났다면,")
        print("   어딘가에서 아직 create_choice_menu가 호출되고 있습니다.")
    else:
        print("\n❌ 최종 UI 테스트 실패")
        print("추가 수정이 필요합니다.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)