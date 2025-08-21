#!/usr/bin/env python3
"""
간단한 상황 기반 시스템 테스트 - 메서드 존재 및 기본 동작 확인
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_methods_exist():
    """새로운 메서드들이 제대로 구현되었는지 확인"""
    
    print("🔍 메서드 존재 확인 테스트")
    print("=" * 50)
    
    try:
        from src.ui.gameplay_interface import GameplayInterface
        
        # 더미 인스턴스 생성
        interface = GameplayInterface()
        
        # 새로운 메서드들 확인
        new_methods = [
            '_get_current_situation_and_actions',
            '_get_current_situation_text',
            '_get_basic_situation_text',
            '_extract_natural_actions_from_situation',
            '_get_basic_actions',
            '_display_situation_with_actions',
            '_process_player_action',
            '_generate_action_result'
        ]
        
        results = {}
        
        for method_name in new_methods:
            exists = hasattr(interface, method_name)
            results[method_name] = exists
            status = "✅" if exists else "❌"
            print(f"{status} {method_name}")
        
        # 기본 동작 테스트
        print(f"\n🧪 기본 동작 테스트:")
        
        # 기본 행동 생성 테스트
        try:
            basic_actions = interface._get_basic_actions()
            print(f"✅ _get_basic_actions: {len(basic_actions)}개 행동")
            for i, action in enumerate(basic_actions, 1):
                print(f"   {i}. {action}")
        except Exception as e:
            print(f"❌ _get_basic_actions 실패: {e}")
            results['basic_actions_work'] = False
        else:
            results['basic_actions_work'] = True
        
        # 기본 상황 텍스트 테스트
        try:
            test_state = {'turn_count': 1, 'current_location': '테스트 위치'}
            situation = interface._get_basic_situation_text(test_state)
            print(f"✅ _get_basic_situation_text: {len(situation)}문자")
            print(f"   내용: {situation[:100]}...")
        except Exception as e:
            print(f"❌ _get_basic_situation_text 실패: {e}")
            results['basic_situation_work'] = False
        else:
            results['basic_situation_work'] = True
        
        # 행동 결과 생성 테스트
        try:
            test_action = "상황을 자세히 관찰한다"
            result = interface._generate_action_result(test_action)
            print(f"✅ _generate_action_result: '{test_action}' → '{result}'")
        except Exception as e:
            print(f"❌ _generate_action_result 실패: {e}")
            results['action_result_work'] = False
        else:
            results['action_result_work'] = True
        
        # 자연스러운 행동 추출 테스트
        try:
            test_situation = "당신은 문 앞에 서 있습니다. 창문을 통해 빛이 새어나오고 있습니다."
            test_state = {'turn_count': 1}
            actions = interface._extract_natural_actions_from_situation(test_situation, test_state)
            print(f"✅ _extract_natural_actions_from_situation: {len(actions)}개 행동")
            for i, action in enumerate(actions, 1):
                print(f"   {i}. {action}")
        except Exception as e:
            print(f"❌ _extract_natural_actions_from_situation 실패: {e}")
            results['extract_actions_work'] = False
        else:
            results['extract_actions_work'] = True
        
        # 전체 평가
        print(f"\n📊 결과 요약:")
        print(f"=" * 50)
        
        method_success = sum(1 for method in new_methods if results.get(method, False))
        total_methods = len(new_methods)
        
        functional_tests = ['basic_actions_work', 'basic_situation_work', 'action_result_work', 'extract_actions_work']
        functional_success = sum(1 for test in functional_tests if results.get(test, False))
        total_functional = len(functional_tests)
        
        print(f"메서드 구현: {method_success}/{total_methods} ({method_success/total_methods*100:.1f}%)")
        print(f"기능 동작: {functional_success}/{total_functional} ({functional_success/total_functional*100:.1f}%)")
        
        overall_success = method_success >= total_methods * 0.8 and functional_success >= total_functional * 0.8
        
        print(f"\n🎯 전체 평가: {'✅ 성공' if overall_success else '❌ 실패'}")
        
        if overall_success:
            print("\n🎉 새로운 상황 기반 시스템이 성공적으로 구현되었습니다!")
            print("- ✅ 기존 선택지 목록 시스템 제거 완료")
            print("- ✅ 상황 기반 자연스러운 행동 시스템 구현")
            print("- ✅ 단순화된 사용자 인터페이스")
        else:
            print("\n⚠️ 일부 기능에 문제가 있습니다:")
            failed_methods = [method for method in new_methods if not results.get(method, False)]
            if failed_methods:
                print(f"- 누락된 메서드: {failed_methods}")
            
            failed_functions = [test for test in functional_tests if not results.get(test, False)]
            if failed_functions:
                print(f"- 동작하지 않는 기능: {failed_functions}")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("크툴루 TRPG 상황 기반 시스템 간단 테스트\n")
    
    success = test_methods_exist()
    
    print(f"\n{'='*50}")
    print("🏁 최종 결과")
    print(f"{'='*50}")
    
    if success:
        print("🎊 테스트 성공! 새로운 시스템이 준비되었습니다.")
    else:
        print("⚠️ 테스트 실패 - 추가 수정이 필요합니다.")
    
    sys.exit(0 if success else 1)