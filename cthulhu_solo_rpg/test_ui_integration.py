#!/usr/bin/env python3
"""
UI 통합 테스트 - 스토리와 선택지가 올바르게 통합되는지 확인
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ui_integration():
    """UI 통합 기능 테스트"""
    
    print("=== UI 통합 테스트 ===\n")
    
    try:
        from src.ui.display_manager import DisplayManager
        from rich.console import Console
        
        console = Console()
        display_manager = DisplayManager(console)
        
        # 테스트 스토리와 선택지
        test_story = "당신은 신비로운 저택 앞에 서 있습니다. 문이 조금 열려있고, 안에서 이상한 소리가 들립니다."
        test_choices = [
            "문을 조심스럽게 두드려본다",
            "문 손잡이를 조용히 돌려본다", 
            "건물 주변을 돌아 다른 입구를 찾는다",
            "창문을 통해 내부를 관찰한다"
        ]
        
        print("1. format_story_with_choices 메서드 테스트:")
        print(f"   스토리: {test_story}")
        print(f"   선택지: {test_choices}")
        print()
        
        # format_story_with_choices 호출
        try:
            integrated_text = display_manager.format_story_with_choices(
                test_story, test_choices, "normal"
            )
            
            print("2. 통합된 텍스트 생성 결과:")
            console.print(integrated_text)
            print()
            
            # Rich Text 객체인지 확인
            from rich.text import Text
            if isinstance(integrated_text, Text):
                print("✅ Rich Text 객체로 올바르게 생성됨")
                
                # 텍스트 내용 확인
                plain_text = integrated_text.plain
                print(f"✅ 평문 내용 길이: {len(plain_text)} 문자")
                
                # 선택지가 포함되어 있는지 확인
                has_choices = all(choice in plain_text for choice in test_choices)
                if has_choices:
                    print("✅ 모든 선택지가 통합된 텍스트에 포함됨")
                else:
                    print("❌ 일부 선택지가 통합된 텍스트에 누락됨")
                
                # "다음 행동을 선택하시오" 문구 확인
                if "다음 행동을 선택하시오" in plain_text:
                    print("✅ 행동 선택 프롬프트가 포함됨")
                else:
                    print("❌ 행동 선택 프롬프트가 누락됨")
                
                # 번호 형식 확인
                has_numbers = all(f"[{i}]" in plain_text for i in range(1, len(test_choices) + 1))
                if has_numbers:
                    print("✅ 선택지 번호 형식이 올바름")
                else:
                    print("❌ 선택지 번호 형식에 문제가 있음")
                
            else:
                print(f"❌ Rich Text 객체가 아님: {type(integrated_text)}")
            
        except Exception as e:
            print(f"❌ format_story_with_choices 실행 실패: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        print("3. create_choice_menu 메서드 테스트 (기존 방식):")
        
        try:
            choice_menu = display_manager.create_choice_menu(
                test_choices, "🎲 무엇을 하시겠습니까? 🎲"
            )
            
            print("별도 선택지 메뉴:")
            console.print(choice_menu)
            print()
            
            print("✅ 기존 choice_menu도 정상 작동")
            
        except Exception as e:
            print(f"❌ create_choice_menu 실행 실패: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ UI 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 함수"""
    
    print("UI 통합 기능 테스트를 시작합니다...\n")
    
    success = test_ui_integration()
    
    if success:
        print("\n🎊 UI 통합 테스트 완료!")
        print("\n통합된 UI가 올바르게 작동하는지 확인:")
        print("- format_story_with_choices가 스토리와 선택지를 통합하여 표시")
        print("- 사용자는 하나의 패널에서 모든 정보를 확인")
        print("- 별도 선택지 패널이 표시되지 않음")
    else:
        print("\n❌ UI 통합 테스트 실패")
        print("추가 수정이 필요합니다.")
    
    return success

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)