#!/usr/bin/env python3
"""
실제 게임플레이 테스트 - 문제 해결 확인
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_actual_gameplay():
    """실제 게임플레이 환경에서 테스트"""
    
    print("🎮 실제 게임플레이 테스트")
    print("=" * 60)
    
    try:
        from src.ui.gameplay_interface import GameplayInterface
        from src.core.game_manager import GameManager
        from src.utils.config import Config
        
        # 실제 게임과 동일한 설정
        config = Config()
        config.set('ai.use_mock_client', True)
        
        game_manager = GameManager(config)
        await game_manager.initialize_systems()
        
        gameplay_interface = GameplayInterface(game_manager)
        print("✅ 게임 환경 초기화 완료\n")
        
        # 실제 게임과 동일한 시나리오 시작
        print("🏁 시나리오 시작 시뮬레이션")
        print("-" * 40)
        
        # 시나리오 설정
        gameplay_interface.current_scenario = "등대의 비밀"
        gameplay_interface.turn_count = 0
        
        # 3턴 동안 실제 게임플레이 시뮬레이션
        results = []
        
        for turn in range(1, 4):
            print(f"\n🔄 턴 {turn}")
            gameplay_interface.turn_count = turn
            
            # 실제 게임과 동일한 방식으로 스토리-선택지 생성
            story_text, choices = await gameplay_interface._get_synchronized_story_and_choices()
            
            print(f"   📖 스토리 ({len(story_text)} 문자):")
            print(f"      {story_text[:150]}...")
            
            print(f"\n   🎯 생성된 선택지 ({len(choices)}개):")
            for i, choice in enumerate(choices, 1):
                print(f"      [{i}] {choice}")
            
            # 스토리-선택지 일관성 분석
            story_words = set(story_text.lower().split())
            choice_words = set()
            for choice in choices:
                choice_words.update(choice.lower().split())
            
            common_words = story_words & choice_words
            meaningful_common = [word for word in common_words if len(word) > 3]
            
            consistency_score = len(meaningful_common) / max(len(choices), 1)
            
            # 결과 저장
            turn_result = {
                'turn': turn,
                'story_length': len(story_text),
                'choice_count': len(choices),
                'choices': choices,
                'consistency_score': consistency_score,
                'story_threads': getattr(gameplay_interface, '_current_story_threads', []),
                'investigations': getattr(gameplay_interface, '_current_investigations', [])
            }
            results.append(turn_result)
            
            print(f"   📊 일관성 점수: {consistency_score:.2f}")
            
            # 스토리 스레드와 조사 기회 확인
            if turn_result['story_threads']:
                print(f"   🧵 스토리 스레드: {len(turn_result['story_threads'])}개")
            if turn_result['investigations']:
                print(f"   🔍 조사 기회: {len(turn_result['investigations'])}개")
            
            # UI 렌더링 테스트
            try:
                gameplay_interface._display_story_with_choices(story_text, choices)
                print(f"   🖼️  UI 렌더링: ✅ 성공")
            except Exception as ui_error:
                print(f"   🖼️  UI 렌더링: ❌ 실패 - {ui_error}")
        
        # 전체 결과 분석
        print("\n" + "=" * 60)
        print("📊 전체 게임플레이 분석")
        print("=" * 60)
        
        avg_consistency = sum(r['consistency_score'] for r in results) / len(results)
        total_story_threads = sum(len(r['story_threads']) for r in results)
        total_investigations = sum(len(r['investigations']) for r in results)
        
        print(f"평균 일관성 점수: {avg_consistency:.2f}")
        print(f"총 스토리 스레드: {total_story_threads}개")
        print(f"총 조사 기회: {total_investigations}개")
        
        # 선택지 다양성 확인
        all_choices = []
        for result in results:
            all_choices.extend(result['choices'])
        
        unique_choices = len(set(all_choices))
        total_choices = len(all_choices)
        diversity_rate = (unique_choices / total_choices) * 100
        
        print(f"선택지 다양성: {unique_choices}/{total_choices} ({diversity_rate:.1f}%)")
        
        # 문제 있었던 기존 선택지 확인
        problematic_choices = [
            "문을 조심스럽게 두드려본다",
            "문 손잡이를 조용히 돌려본다", 
            "건물 주변을 돌아 다른 입구를 찾는다",
            "창문을 통해 내부를 관찰한다"
        ]
        
        problematic_count = sum(1 for choice in all_choices if choice in problematic_choices)
        
        print(f"기존 문제 선택지 출현: {problematic_count}/{total_choices} ({(problematic_count/total_choices)*100:.1f}%)")
        
        # 전체 평가
        success_criteria = [
            avg_consistency >= 0.3,  # 일관성 점수 0.3 이상
            diversity_rate >= 70,    # 다양성 70% 이상
            problematic_count < total_choices * 0.8  # 기존 문제 선택지 80% 미만
        ]
        
        success = all(success_criteria)
        
        print(f"\n🎯 전체 평가: {'✅ 성공' if success else '⚠️ 개선 필요'}")
        
        if success:
            print("\n🎉 주요 개선사항:")
            print("- ✅ 스토리-선택지 동기화 구현")
            print("- ✅ 맥락적 선택지 생성")
            print("- ✅ 선택지 다양성 확보")
            print("- ✅ UI 통합 표시")
        else:
            print("\n⚠️ 추가 개선 필요:")
            if avg_consistency < 0.3:
                print("- 스토리-선택지 일관성 개선")
            if diversity_rate < 70:
                print("- 선택지 다양성 확보")
            if problematic_count >= total_choices * 0.8:
                print("- 반복적 선택지 문제 해결")
        
        await game_manager.shutdown()
        return success
        
    except Exception as e:
        print(f"❌ 게임플레이 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("크툴루 TRPG 실제 게임플레이 테스트\n")
    
    success = await test_actual_gameplay()
    
    print("\n" + "=" * 60)
    print("🏁 최종 결과")
    print("=" * 60)
    
    if success:
        print("🎊 테스트 성공!")
        print("\n✅ 구현 완료된 기능:")
        print("- 스토리와 선택지의 동기화된 생성")
        print("- 스토리 내용 기반 맥락적 선택지")
        print("- 스토리 스레드 및 조사 기회 UI 표시")
        print("- 향상된 게임 일관성")
        print("\n🚀 이제 실제 게임을 즐길 수 있습니다:")
        print("   source venv/bin/activate && python main.py --skip-checks")
    else:
        print("⚠️ 테스트 실패 - 추가 개선 필요")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)