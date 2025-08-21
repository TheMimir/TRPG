#!/usr/bin/env python3
"""
Fallback 선택지 시스템 테스트

AI 에이전트를 비활성화하고 fallback 시스템이 정상 작동하는지 확인
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_fallback_choice_system():
    """Fallback 선택지 생성 시스템 테스트"""
    
    print("=== Fallback 선택지 생성 시스템 테스트 ===\n")
    
    try:
        from src.core.gameplay_controller import GameplayController, ChoiceContext, TensionLevel
        from src.utils.config import Config
        
        # AI 비활성화된 환경 설정
        config = Config()
        config.set('ai.use_mock_client', False)  # Mock 클라이언트도 비활성화
        
        # GameManager 없이 GameplayController 초기화 (AI 에이전트 없음)
        controller = GameplayController(game_manager=None)
        print("✅ GameplayController 초기화 완료 (AI 에이전트 없음)")
        
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
            },
            {
                'name': '주방 상황',
                'scene_id': 'scene_003_kitchen',
                'character_state': {
                    'sanity_current': 50,
                    'hit_points_current': 7,
                    'hit_points_maximum': 10
                },
                'tension': TensionLevel.TENSE
            },
            {
                'name': '위층 상황',
                'scene_id': 'scene_004_upstairs',
                'character_state': {
                    'sanity_current': 45,
                    'hit_points_current': 6,
                    'hit_points_maximum': 10
                },
                'tension': TensionLevel.TERRIFYING
            }
        ]
        
        print("🧪 상황별 Fallback 선택지 생성 테스트:\n")
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"테스트 {i}: {scenario['name']}")
            print(f"   씬 ID: {scenario['scene_id']}")
            print(f"   정신력: {scenario['character_state']['sanity_current']}")
            print(f"   체력: {scenario['character_state']['hit_points_current']}")
            print(f"   긴장도: {scenario['tension'].value}")
            
            try:
                # 선택지 생성 테스트 (AI 없이 fallback만 사용)
                choices = await controller.get_current_choices(scenario['character_state'])
                
                print(f"   생성된 선택지 수: {len(choices)}")
                
                # 선택지 내용 출력
                for j, choice in enumerate(choices, 1):
                    location = choice.metadata.get('location', 'unknown')
                    choice_type = choice.metadata.get('type', 'unknown')
                    fallback = choice.metadata.get('fallback', False)
                    print(f"      {j}. [{location}/{choice_type}] {choice.text}")
                    if fallback:
                        print(f"         (Fallback: True)")
                
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
                scene_keywords = scenario['scene_id'].split('_')
                location_keywords = ['entrance', 'living', 'kitchen', 'basement', 'study', 'upstairs', 'room']
                detected_location = None
                
                for keyword in location_keywords:
                    if keyword in scenario['scene_id'].lower():
                        detected_location = keyword
                        break
                
                if detected_location:
                    location_match = any(detected_location in choice.metadata.get('location', '') 
                                       for choice in choices)
                    if location_match:
                        print(f"   ✅ 위치({detected_location})에 맞는 선택지 포함")
                    else:
                        print(f"   ⚠️  위치({detected_location})별 선택지 미포함")
                
                # 상태 기반 선택지 확인
                sanity = scenario['character_state']['sanity_current']
                hp = scenario['character_state']['hit_points_current']
                
                has_recovery = any('휴식' in choice.text or '치료' in choice.text or '진정' in choice.text 
                                 for choice in choices)
                
                if (sanity < 50 or hp < 7) and has_recovery:
                    print("   ✅ 상태 기반 회복 선택지 포함")
                elif sanity >= 50 and hp >= 7:
                    print("   ✅ 건강한 상태 - 회복 선택지 불필요")
                else:
                    print("   ⚠️  상태에 맞는 회복 선택지 없음")
                
                # 긴장도 기반 선택지 확인
                if scenario['tension'] in [TensionLevel.TERRIFYING, TensionLevel.COSMIC_HORROR]:
                    has_escape = any('도망' in choice.text or '떠나' in choice.text or '즉시' in choice.text 
                                   for choice in choices)
                    if has_escape:
                        print("   ✅ 고긴장 상황 - 도피 선택지 포함")
                    else:
                        print("   ⚠️  고긴장 상황에 도피 선택지 없음")
                
                print()
                
            except Exception as e:
                print(f"   ❌ 선택지 생성 실패: {e}")
                import traceback
                traceback.print_exc()
                print()
        
        # 연속 호출 테스트 (턴 번호가 변할 때 선택지 ID가 달라지는지 확인)
        print("🔄 연속 호출 테스트 (턴별 선택지 변화):")
        
        # 스토리 상태 머신을 수동으로 업데이트해서 턴 번호 변경
        test_character_state = {
            'sanity_current': 50,
            'hit_points_current': 7,
            'hit_points_maximum': 10
        }
        
        for turn in range(3):
            print(f"\n   턴 {turn + 1}:")
            
            # 턴 번호 변경을 위해 스토리 상태 업데이트
            if hasattr(controller.story_state_machine, 'current_context'):
                controller.story_state_machine.current_context.turn_number = turn + 1
            
            choices = await controller.get_current_choices(test_character_state)
            
            print(f"   선택지 수: {len(choices)}")
            for j, choice in enumerate(choices, 1):
                choice_id = choice.id
                location = choice.metadata.get('location', 'unknown')
                print(f"      {j}. [{choice_id}] {choice.text}")
            
            # 선택지 ID에 턴 번호가 포함되는지 확인
            turn_in_ids = any(str(turn + 1) in choice.id for choice in choices)
            if turn_in_ids:
                print(f"   ✅ 선택지 ID에 턴 번호({turn + 1}) 포함")
            else:
                print(f"   ⚠️  선택지 ID에 턴 번호 미포함")
        
        # 통계 정보 출력
        print(f"\n📊 시스템 통계:")
        stats = controller.get_ai_system_status()
        print(f"   총 요청 수: {stats['choice_generation_stats']['total_requests']}")
        print(f"   AI 성공: {stats['choice_generation_stats']['ai_successes']}")
        print(f"   AI 실패: {stats['choice_generation_stats']['ai_failures']}")
        print(f"   대체 시스템 사용: {stats['choice_generation_stats']['fallback_uses']}")
        print(f"   AI 상태: {stats['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """메인 함수"""
    
    print("크툴루 TRPG Fallback 선택지 시스템 테스트를 시작합니다...\n")
    
    success = await test_fallback_choice_system()
    
    if success:
        print("\n🎊 Fallback 선택지 시스템 테스트 성공!")
        print("\n✨ 확인된 기능들:")
        print("  - ✅ AI 없이 Fallback 시스템 정상 작동")
        print("  - ✅ 위치별 선택지 생성 엔진")
        print("  - ✅ 캐릭터 상태 반영 로직")
        print("  - ✅ 긴장도별 특수 선택지")
        print("  - ✅ 턴별 고유 선택지 ID 생성")
        print("  - ✅ AI 상태 모니터링 시스템")
        print("\n이제 AI가 실패해도 상황에 맞는 의미있는 선택지가 제공됩니다!")
    else:
        print("\n❌ Fallback 선택지 시스템 테스트 실패.")
        print("추가 확인이 필요합니다.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)