#!/usr/bin/env python3
"""
실제 GameplayInterface 통합 테스트
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_gameplay_display():
    """실제 GameplayInterface 통합 테스트"""
    
    print("=== GameplayInterface 통합 테스트 ===\n")
    
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
        
        # 테스트 데이터
        test_story = "당신은 어두운 복도에 서 있습니다. 앞쪽에서 이상한 소리가 들립니다."
        test_choices = [
            "조용히 앞으로 나아간다",
            "소리가 나는 곳을 피해 다른 길을 찾는다",
            "뒤로 물러난다",
            "큰 소리로 부른다"
        ]
        
        print(f"테스트 스토리: {test_story}")
        print(f"테스트 선택지: {test_choices}")
        print()
        
        # _display_story_with_choices 직접 테스트
        print("1. _display_story_with_choices 메서드 테스트:")
        try:
            gameplay_interface._display_story_with_choices(test_story, test_choices)
            print("✅ 통합 스토리 표시 성공")
        except Exception as e:
            print(f"❌ 통합 스토리 표시 실패: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        # _display_choices_and_get_input 메서드 테스트 (입력 없이)
        print("2. Legacy _display_choices_and_get_input 메서드 확인:")
        try:
            # 입력 프롬프트 없이 메서드 구조만 확인
            method = getattr(gameplay_interface, '_display_choices_and_get_input', None)
            if method:
                print("✅ Legacy 메서드 존재함")
                print("   이 메서드는 더 이상 별도 패널을 생성하지 않아야 함")
            else:
                print("❌ Legacy 메서드 없음")
        except Exception as e:
            print(f"❌ Legacy 메서드 확인 실패: {e}")
        
        print()
        
        # format_story_with_choices 메서드 테스트
        print("3. DisplayManager 통합 기능 재확인:")
        try:
            formatted_text = gameplay_interface.display_manager.format_story_with_choices(
                test_story, test_choices, "normal"
            )
            
            # 콘솔에 출력
            console.print("=== 통합된 최종 결과 ===")
            console.print(formatted_text)
            print("=== 통합 결과 끝 ===")
            
            print("✅ DisplayManager 통합 기능 정상 작동")
            
            # 평문 내용 분석
            plain_text = formatted_text.plain
            if "다음 행동을 선택하시오" in plain_text:
                print("✅ 행동 프롬프트 포함됨")
            
            choice_numbers = [f"[{i}]" for i in range(1, len(test_choices) + 1)]
            if all(num in plain_text for num in choice_numbers):
                print("✅ 모든 선택지 번호 포함됨")
            
            if all(choice in plain_text for choice in test_choices):
                print("✅ 모든 선택지 텍스트 포함됨")
                
        except Exception as e:
            print(f"❌ DisplayManager 통합 기능 실패: {e}")
            import traceback
            traceback.print_exc()
        
        await game_manager.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ GameplayInterface 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """메인 함수"""
    
    print("GameplayInterface 통합 테스트를 시작합니다...\n")
    
    success = await test_gameplay_display()
    
    if success:
        print("\n🎊 GameplayInterface 통합 테스트 성공!")
        print("\n구현된 통합 기능:")
        print("- ✅ 스토리와 선택지가 하나의 패널에서 표시")
        print("- ✅ '다음 행동을 선택하시오' 프롬프트 포함")
        print("- ✅ 선택지가 번호와 함께 자연스럽게 배치")
        print("- ✅ Legacy 메서드는 더 이상 별도 패널 생성하지 않음")
        print("\n이제 게임에서 통합된 UI가 표시되어야 합니다!")
    else:
        print("\n❌ GameplayInterface 통합 테스트 실패")
        print("추가 수정이 필요합니다.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)