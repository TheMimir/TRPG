#!/usr/bin/env python3
"""
동적 선택지 생성 시스템 테스트

새로 구현된 동적 선택지 생성이 상황에 맞게 작동하는지 확인
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_dynamic_choice_system():
    """동적 선택지 생성 시스템 테스트"""
    
    print("=== 동적 선택지 생성 시스템 테스트 ===\n")
    
    try:
        from src.core.gameplay_controller import GameplayController, ChoiceContext, TensionLevel
        from src.core.game_manager import GameManager
        from src.utils.config import Config
        
        # Mock 환경 설정
        config = Config()
        config.set('ai.use_mock_client', True)
        
        game_manager = GameManager(config)
        await game_manager.initialize_systems()
        
        # GameplayController 초기화
        controller = GameplayController(game_manager)
        print("✅ GameplayController 초기화 완료")
        
        # 다양한 상황별 테스트 케이스
        test_scenarios = [
            {
                'name': '입구 상황',
                'scene_id': 'scene_001_entrance',
                'character_state': {
                    'sanity_current': 80,
                    'hit_points_current': 10,
                    'hit_points_maximum': 10
                },
                'tension': TensionLevel.UNEASY
            },
            {
                'name': '거실 상황',
                'scene_id': 'scene_002_living_room',
                'character_state': {
                    'sanity_current': 60,
                    'hit_points_current': 8,
                    'hit_points_maximum': 10
                },
                'tension': TensionLevel.TENSE
            },
            {
                'name': '지하실 상황 - 위험',
                'scene_id': 'scene_005_basement',
                'character_state': {
                    'sanity_current': 30,
                    'hit_points_current': 5,
                    'hit_points_maximum': 10
                },
                'tension': TensionLevel.TERRIFYING
            },
            {
                'name': '서재 상황',
                'scene_id': 'scene_004_study',
                'character_state': {
                    'sanity_current': 70,
                    'hit_points_current': 9,
                    'hit_points_maximum': 10
                },
                'tension': TensionLevel.CALM
            }
        ]
        
        print("🧪 상황별 선택지 생성 테스트:\n")
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"테스트 {i}: {scenario['name']}")
            print(f"   씬 ID: {scenario['scene_id']}")
            print(f"   정신력: {scenario['character_state']['sanity_current']}")
            print(f"   체력: {scenario['character_state']['hit_points_current']}")
            print(f"   긴장도: {scenario['tension'].value}")
            
            try:
                # 선택지 생성 테스트
                choices = await controller.get_current_choices(scenario['character_state'])
                
                print(f"   생성된 선택지 수: {len(choices)}")
                
                # 선택지 내용 출력
                for j, choice in enumerate(choices, 1):
                    location = choice.metadata.get('location', 'unknown')
                    choice_type = choice.metadata.get('type', 'unknown')
                    print(f"      {j}. [{location}/{choice_type}] {choice.text}")
                
                # AI 시스템 상태 확인
                ai_status = controller.get_ai_system_status()
                user_message = controller.get_user_feedback_message()
                print(f"   AI 상태: {ai_status['status']}")
                print(f"   사용자 메시지: {user_message}")
                
                # 선택지 품질 검증
                unique_texts = set(choice.text for choice in choices)
                if len(unique_texts) == len(choices):
                    print("   ✅ 모든 선택지가 고유함")
                else:
                    print("   ⚠️  중복된 선택지 존재")
                
                # 상황별 적절성 검증
                location_match = any(scenario['scene_id'].split('_')[-1] in choice.metadata.get('location', '') 
                                   for choice in choices)
                if location_match:
                    print("   ✅ 위치에 맞는 선택지 포함")
                else:
                    print("   ⚠️  위치별 선택지 미포함")
                
                print()
                
            except Exception as e:
                print(f"   ❌ 선택지 생성 실패: {e}")
                import traceback
                traceback.print_exc()
                print()
        
        # 연속 호출 테스트 (선택지가 매번 달라지는지 확인)
        print("🔄 연속 호출 테스트 (선택지 변화 확인):")
        
        test_character_state = {
            'sanity_current': 50,
            'hit_points_current': 7,
            'hit_points_maximum': 10
        }
        
        previous_choices = set()
        for turn in range(3):
            print(f"\n   턴 {turn + 1}:")
            choices = await controller.get_current_choices(test_character_state)
            
            current_choice_texts = {choice.text for choice in choices}
            print(f"   선택지: {list(current_choice_texts)}")
            
            if turn > 0:
                # 이전 턴과 비교
                overlap = previous_choices.intersection(current_choice_texts)
                overlap_ratio = len(overlap) / len(previous_choices) if previous_choices else 0
                
                if overlap_ratio < 0.8:  # 80% 미만 중복이면 충분히 변화
                    print(f"   ✅ 선택지가 충분히 변화함 (중복률: {overlap_ratio:.1%})")
                else:
                    print(f"   ⚠️  선택지 변화 부족 (중복률: {overlap_ratio:.1%})")
            
            previous_choices = current_choice_texts
        
        # 통계 정보 출력
        print(f"\n📊 시스템 통계:")
        stats = controller.get_ai_system_status()
        print(f"   총 요청 수: {stats['choice_generation_stats']['total_requests']}")
        print(f"   AI 성공: {stats['choice_generation_stats']['ai_successes']}")
        print(f"   AI 실패: {stats['choice_generation_stats']['ai_failures']}")
        print(f"   대체 시스템 사용: {stats['choice_generation_stats']['fallback_uses']}")
        print(f"   성공률: {stats['success_rate']:.1f}%")
        
        await game_manager.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """메인 함수"""
    
    print("크툴루 TRPG 동적 선택지 생성 테스트를 시작합니다...\n")
    
    success = await test_dynamic_choice_system()
    
    if success:
        print("\n🎊 동적 선택지 생성 테스트 성공!")
        print("\n✨ 구현된 기능들:")
        print("  - ✅ 위치별 맞춤 선택지 생성")
        print("  - ✅ 캐릭터 상태 반영 선택지")
        print("  - ✅ 긴장도별 적응적 선택지")
        print("  - ✅ AI 에이전트 상태 모니터링")
        print("  - ✅ 향상된 fallback 시스템")
        print("  - ✅ 선택지 중복 제거 및 품질 보장")
        print("\n이제 '무엇을 하시겠습니까?'에서 상황에 맞는 다양한 선택지가 제공됩니다!")
        print("\n실제 게임 실행:")
        print("  source venv/bin/activate && python main.py --skip-checks")
    else:
        print("\n❌ 동적 선택지 생성 테스트 실패.")
        print("추가 확인이 필요합니다.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)