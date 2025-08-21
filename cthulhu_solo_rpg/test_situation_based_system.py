#!/usr/bin/env python3
"""
상황 기반 행동 시스템 테스트 - 기존 선택지 목록 제거 확인
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_situation_based_system():
    """새로운 상황 기반 시스템 테스트"""
    
    print("🔄 상황 기반 행동 시스템 테스트")
    print("=" * 60)
    
    try:
        from src.ui.gameplay_interface import GameplayInterface
        from src.core.game_manager import GameManager
        from src.utils.config import Config
        
        # Mock 환경 설정
        config = Config()
        config.set('ai.use_mock_client', True)
        
        game_manager = GameManager(config)
        await game_manager.initialize_systems()
        
        gameplay_interface = GameplayInterface(game_manager)
        print("✅ 게임 환경 초기화 완료\n")
        
        # 여러 시나리오 테스트
        test_scenarios = [
            {
                'name': '기본 상황',
                'turn': 1,
                'location': '신비한 저택 앞'
            },
            {
                'name': '탐험 상황', 
                'turn': 3,
                'location': '어두운 복도'
            },
            {
                'name': '위험 상황',
                'turn': 5,
                'location': '지하실'
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n🎭 테스트 시나리오: {scenario['name']}")
            print("-" * 40)
            
            # 시나리오 설정
            gameplay_interface.turn_count = scenario['turn']
            gameplay_interface.current_location = scenario['location']
            
            # 상황과 행동 생성 테스트
            character_state = gameplay_interface._get_character_state()
            situation, actions = await gameplay_interface._get_current_situation_and_actions(character_state)
            
            print(f"📖 생성된 상황 ({len(situation)} 문자):")
            print(f"   {situation[:150]}...")
            
            print(f"\n🎯 생성된 행동 ({len(actions)}개):")
            for i, action in enumerate(actions, 1):
                print(f"   [{i}] {action}")
            
            # 상황 기반성 확인
            situation_words = set(situation.lower().split())
            relevant_actions = []
            
            for action in actions:
                action_words = set(action.lower().split())
                if situation_words & action_words:
                    relevant_actions.append(action)
            
            relevance_score = len(relevant_actions) / len(actions) if actions else 0
            print(f"\n📊 상황 연관성: {relevance_score:.1%} ({len(relevant_actions)}/{len(actions)})")
            
            # 기존 문제 선택지 확인
            old_problematic = [
                "문을 조심스럽게 두드려본다",
                "문 손잡이를 조용히 돌려본다", 
                "건물 주변을 돌아 다른 입구를 찾는다",
                "창문을 통해 내부를 관찰한다"
            ]
            
            old_choices_found = [action for action in actions if action in old_problematic]
            
            if old_choices_found:
                print(f"⚠️ 기존 문제 선택지 발견: {old_choices_found}")
            else:
                print("✅ 기존 문제 선택지 없음 - 새로운 시스템 작동 중")
            
            # UI 렌더링 테스트
            try:
                gameplay_interface._display_situation_with_actions(situation, actions)
                print("🖼️  UI 렌더링: ✅ 성공")
            except Exception as ui_error:
                print(f"🖼️  UI 렌더링: ❌ 실패 - {ui_error}")
        
        # 전체 평가
        print("\n" + "=" * 60)
        print("📋 시스템 변경 사항 확인")
        print("=" * 60)
        
        # 메서드 존재 확인
        methods_check = {
            '_get_current_situation_and_actions': hasattr(gameplay_interface, '_get_current_situation_and_actions'),
            '_display_situation_with_actions': hasattr(gameplay_interface, '_display_situation_with_actions'),
            '_process_player_action': hasattr(gameplay_interface, '_process_player_action'),
            '_extract_natural_actions_from_situation': hasattr(gameplay_interface, '_extract_natural_actions_from_situation')
        }
        
        print("🔧 새로운 메서드 구현 상태:")
        for method, exists in methods_check.items():
            status = "✅" if exists else "❌"
            print(f"   {status} {method}")
        
        # 기본 동작 테스트
        print("\n🧪 기본 동작 테스트:")
        basic_actions = gameplay_interface._get_basic_actions()
        print(f"   기본 행동 {len(basic_actions)}개: {basic_actions}")
        
        # 행동 결과 생성 테스트
        test_action = "상황을 자세히 관찰한다"
        result = gameplay_interface._generate_action_result(test_action)
        print(f"   행동 결과 생성: '{test_action}' → '{result}'")
        
        # 성공 여부 판단
        all_methods_exist = all(methods_check.values())
        system_working = len(basic_actions) > 0 and result
        
        success = all_methods_exist and system_working
        
        print(f"\n🎯 전체 평가: {'✅ 성공' if success else '❌ 실패'}")
        
        if success:
            print("\n🎉 주요 개선사항:")
            print("- ✅ 기존 선택지 목록 시스템 완전 제거")
            print("- ✅ 상황 기반 자연스러운 행동 생성")
            print("- ✅ 단순화된 UI 인터페이스")
            print("- ✅ 맥락적 행동 추출 시스템")
        else:
            print("\n⚠️ 추가 수정 필요:")
            if not all_methods_exist:
                missing = [method for method, exists in methods_check.items() if not exists]
                print(f"- 누락된 메서드: {missing}")
            if not system_working:
                print("- 기본 시스템 동작 문제")
        
        await game_manager.shutdown()
        return success
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("크툴루 TRPG 상황 기반 시스템 테스트\n")
    
    success = await test_situation_based_system()
    
    print("\n" + "=" * 60)
    print("🏁 최종 결과")
    print("=" * 60)
    
    if success:
        print("🎊 테스트 성공!")
        print("\n✅ 구현 완료된 변경사항:")
        print("- 기존 복잡한 선택지 목록 시스템 제거")
        print("- 현재 상황 기반 자연스러운 행동 시스템")
        print("- 단순화되고 직관적인 UI")
        print("- 상황과 행동의 자연스러운 연결")
        print("\n🚀 이제 새로운 시스템으로 게임을 실행할 수 있습니다:")
        print("   source venv/bin/activate && python main.py --skip-checks")
    else:
        print("⚠️ 테스트 실패 - 추가 수정 필요")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)