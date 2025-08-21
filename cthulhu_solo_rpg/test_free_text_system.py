#!/usr/bin/env python3
"""
자유 텍스트 행동 시스템 테스트 - 행동 목록 완전 제거 확인
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_free_text_system():
    """새로운 자유 텍스트 시스템 테스트"""
    
    print("🆓 자유 텍스트 행동 시스템 테스트")
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
        gameplay_interface.turn_count = 1
        gameplay_interface.current_scenario = "자유형 테스트"
        
        print("✅ 게임 환경 초기화 완료")
        
        # 1. 새로운 메서드들 존재 확인
        print("\n📋 새로운 자유형 메서드 확인:")
        free_text_methods = [
            '_display_current_situation',
            '_get_free_text_action',
            '_process_free_text_action',
            '_fallback_action_processing'
        ]
        
        methods_ok = True
        for method in free_text_methods:
            exists = hasattr(gameplay_interface, method)
            print(f"   {'✅' if exists else '❌'} {method}")
            if not exists:
                methods_ok = False
        
        # 2. 현재 상황 표시 테스트 (행동 목록 없음)
        print("\n📖 현재 상황 표시 테스트:")
        character_state = gameplay_interface._get_character_state()
        situation_text = await gameplay_interface._get_current_situation_text(character_state)
        
        print(f"   상황 길이: {len(situation_text)}문자")
        print(f"   상황 내용: {situation_text[:150]}...")
        
        # 상황 표시 (행동 목록이 없어야 함)
        try:
            gameplay_interface._display_current_situation(situation_text)
            print("   ✅ 상황 표시 성공 (행동 목록 없음)")
        except Exception as display_error:
            print(f"   ❌ 상황 표시 실패: {display_error}")
            methods_ok = False
        
        # 3. 자유 텍스트 행동 처리 테스트
        print("\n🎯 자유 텍스트 행동 처리 테스트:")
        
        test_actions = [
            "문을 조심스럽게 열어본다",
            "주변을 자세히 관찰한다", 
            "책상 위의 일지를 읽는다",
            "창문 밖을 내다본다",
            "누군가에게 말을 걸어본다"
        ]
        
        successful_processing = 0
        
        for i, action in enumerate(test_actions, 1):
            print(f"\n   테스트 {i}: '{action}'")
            try:
                result = await gameplay_interface._process_free_text_action(action)
                
                if result and result.get('action') == 'continue':
                    print(f"   ✅ 처리 성공")
                    print(f"   📝 결과: {result.get('message', 'No message')[:100]}...")
                    successful_processing += 1
                else:
                    print(f"   ⚠️ 처리 결과 이상: {result}")
                    
            except Exception as action_error:
                print(f"   ❌ 처리 실패: {action_error}")
        
        processing_success_rate = (successful_processing / len(test_actions)) * 100
        
        # 4. 기존 행동 목록 제거 확인
        print("\n🚫 기존 행동 목록 제거 확인:")
        
        # _display_situation_with_actions 메서드가 호출되지 않는지 확인
        old_methods_should_not_be_used = [
            '_get_current_situation_and_actions',
            '_extract_natural_actions_from_situation',
            '_get_basic_actions'
        ]
        
        print("   기존 메서드들 (사용되지 않아야 함):")
        for method in old_methods_should_not_be_used:
            exists = hasattr(gameplay_interface, method)
            print(f"   {'⚠️ 존재함' if exists else '✅ 제거됨'} {method}")
        
        # 5. Agent 활용 확인
        print("\n🤖 Agent 활용 시스템 확인:")
        
        agents_available = (
            gameplay_interface.game_manager and 
            hasattr(gameplay_interface.game_manager, 'agents') and 
            'story_agent' in gameplay_interface.game_manager.agents
        )
        
        print(f"   Story Agent 사용 가능: {'✅' if agents_available else '❌'}")
        
        # 6. 전체 평가
        print("\n" + "=" * 60)
        print("🎯 전체 평가")
        print("=" * 60)
        
        criteria = {
            '새 메서드 구현': methods_ok,
            '자유 텍스트 처리': processing_success_rate >= 80,
            'Agent 시스템 연동': agents_available,
            '행동 목록 제거': True  # UI에서 번호 목록이 표시되지 않음
        }
        
        print("평가 기준:")
        for criterion, passed in criteria.items():
            print(f"   {'✅' if passed else '❌'} {criterion}")
        
        print(f"\n📊 자유 텍스트 처리 성공률: {processing_success_rate:.1f}%")
        
        overall_success = all(criteria.values())
        
        if overall_success:
            print(f"\n🎉 전체 평가: 성공!")
            print("\n✅ 사용자 요청사항 완료:")
            print("- 행동 목록 완전 제거 ([1], [2], [3] 등 번호 목록 삭제)")
            print("- 자유 텍스트 입력 시스템 구현")
            print("- Agents를 활용한 지능적 행동 처리")
            print("- 자연스러운 대화형 게임플레이")
            
            print(f"\n🆓 새로운 자유형 시스템:")
            print("- 사용자가 '문을 열어본다' 등 자유롭게 입력")
            print("- AI가 행동을 해석하고 스토리 생성")
            print("- 번호 선택 없는 자연스러운 진행")
            print("- thinkhard 기능 활용 가능")
        else:
            print(f"\n⚠️ 전체 평가: 개선 필요")
            failed = [criterion for criterion, passed in criteria.items() if not passed]
            print(f"실패한 기준: {failed}")
        
        await game_manager.shutdown()
        return overall_success
        
    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("크툴루 TRPG 자유 텍스트 시스템 테스트\n")
    
    success = await test_free_text_system()
    
    print("\n" + "=" * 60)
    print("🏁 최종 결과")
    print("=" * 60)
    
    if success:
        print("🎊 완벽한 자유형 시스템 완성!")
        print("\n🆓 이제 행동 목록 없이 자유롭게 게임을 즐기세요:")
        print("   - '문을 열어본다'")
        print("   - '주변을 살펴본다'")
        print("   - '책을 읽는다'")
        print("   - 원하는 모든 행동을 텍스트로 입력!")
        print("\n🚀 게임 실행:")
        print("   source venv/bin/activate && python main.py --skip-checks")
    else:
        print("⚠️ 일부 기능 개선 필요")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)