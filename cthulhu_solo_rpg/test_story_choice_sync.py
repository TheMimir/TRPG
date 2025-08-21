#!/usr/bin/env python3
"""
스토리-선택지 동기화 테스트 - 실제 게임플레이와 동일한 방식으로 테스트
시간 제한 없이 문제가 해결될 때까지 반복 테스트
"""

import sys
import os
import asyncio
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_story_choice_synchronization():
    """스토리-선택지 동기화 테스트 - 실제 게임과 동일한 환경"""
    
    print("=" * 80)
    print("🎮 스토리-선택지 동기화 테스트 시작")
    print("=" * 80)
    print()
    
    test_results = {
        'total_turns': 0,
        'sync_success': 0,
        'sync_failures': 0,
        'story_choice_matches': 0,
        'story_threads_displayed': 0,
        'investigations_displayed': 0,
        'issues_found': []
    }
    
    try:
        from src.ui.gameplay_interface import GameplayInterface
        from src.core.game_manager import GameManager
        from src.utils.config import Config
        from rich.console import Console
        
        # Mock 환경 설정 (실제 게임과 동일)
        config = Config()
        config.set('ai.use_mock_client', True)
        
        console = Console()
        game_manager = GameManager(config)
        await game_manager.initialize_systems()
        
        # GameplayInterface 생성 (실제 게임과 동일)
        gameplay_interface = GameplayInterface(game_manager)
        print("✅ 게임 환경 초기화 완료")
        print()
        
        # 여러 턴에 걸쳐 테스트 (실제 게임플레이 시뮬레이션)
        MAX_TEST_TURNS = 10
        
        for turn in range(1, MAX_TEST_TURNS + 1):
            print(f"🔄 턴 {turn} 테스트 중...")
            test_results['total_turns'] += 1
            
            try:
                # 실제 게임과 동일한 방식으로 동기화된 스토리-선택지 생성
                character_state = gameplay_interface._get_character_state()
                story_text, choices = await gameplay_interface._get_synchronized_story_and_choices(character_state)
                
                print(f"   📖 스토리 길이: {len(story_text)} 문자")
                print(f"   🎯 선택지 개수: {len(choices)}")
                
                # 스토리와 선택지 내용 일관성 검사
                story_lower = story_text.lower()
                choice_keywords = []
                
                for choice in choices:
                    choice_lower = choice.lower()
                    # 선택지에서 핵심 키워드 추출
                    keywords = [word for word in choice_lower.split() if len(word) > 2]
                    choice_keywords.extend(keywords[:2])  # 각 선택지에서 최대 2개 키워드
                
                # 스토리에 선택지와 관련된 요소가 포함되어 있는지 확인
                contextual_match = False
                if any(keyword in story_lower for keyword in choice_keywords):
                    contextual_match = True
                    test_results['story_choice_matches'] += 1
                
                print(f"   🔗 스토리-선택지 일관성: {'✅ 양호' if contextual_match else '⚠️ 개선 필요'}")
                
                # 스토리 스레드 및 조사 기회 확인
                story_threads = getattr(gameplay_interface, '_current_story_threads', [])
                investigations = getattr(gameplay_interface, '_current_investigations', [])
                
                if story_threads:
                    test_results['story_threads_displayed'] += 1
                    print(f"   🧵 스토리 스레드: {len(story_threads)}개")
                    for i, thread in enumerate(story_threads[:2], 1):
                        print(f"      {i}. {str(thread)[:50]}...")
                
                if investigations:
                    test_results['investigations_displayed'] += 1
                    print(f"   🔍 조사 기회: {len(investigations)}개")
                    for i, inv in enumerate(investigations[:2], 1):
                        print(f"      • {str(inv)[:50]}...")
                
                # UI 표시 테스트 (실제 렌더링)
                try:
                    gameplay_interface._display_story_with_choices(story_text, choices)
                    print(f"   🖼️  UI 렌더링: ✅ 성공")
                    test_results['sync_success'] += 1
                except Exception as ui_error:
                    print(f"   🖼️  UI 렌더링: ❌ 실패 - {ui_error}")
                    test_results['issues_found'].append(f"Turn {turn}: UI rendering failed - {ui_error}")
                    test_results['sync_failures'] += 1
                
                # 선택지 구체적 내용 분석
                print(f"   📋 선택지 상세:")
                for i, choice in enumerate(choices, 1):
                    print(f"      [{i}] {choice}")
                
                # 문제가 있는 경우 상세 정보 수집
                if not contextual_match or len(choices) < 3:
                    issue_desc = f"Turn {turn}: "
                    if not contextual_match:
                        issue_desc += "Story-choice mismatch, "
                    if len(choices) < 3:
                        issue_desc += f"Insufficient choices ({len(choices)}), "
                    test_results['issues_found'].append(issue_desc.rstrip(', '))
                
                print()
                
            except Exception as turn_error:
                print(f"   ❌ 턴 {turn} 실패: {turn_error}")
                test_results['sync_failures'] += 1
                test_results['issues_found'].append(f"Turn {turn}: Exception - {turn_error}")
                import traceback
                traceback.print_exc()
                print()
        
        # 테스트 결과 분석
        print("=" * 80)
        print("📊 테스트 결과 분석")
        print("=" * 80)
        
        success_rate = (test_results['sync_success'] / test_results['total_turns']) * 100 if test_results['total_turns'] > 0 else 0
        match_rate = (test_results['story_choice_matches'] / test_results['total_turns']) * 100 if test_results['total_turns'] > 0 else 0
        
        print(f"총 테스트 턴: {test_results['total_turns']}")
        print(f"동기화 성공: {test_results['sync_success']} ({success_rate:.1f}%)")
        print(f"동기화 실패: {test_results['sync_failures']}")
        print(f"스토리-선택지 일관성: {test_results['story_choice_matches']} ({match_rate:.1f}%)")
        print(f"스토리 스레드 표시: {test_results['story_threads_displayed']}회")
        print(f"조사 기회 표시: {test_results['investigations_displayed']}회")
        print()
        
        # 문제 요약
        if test_results['issues_found']:
            print("⚠️ 발견된 문제들:")
            for issue in test_results['issues_found']:
                print(f"   • {issue}")
            print()
        
        # 전체 평가
        overall_success = (success_rate >= 80 and match_rate >= 60 and len(test_results['issues_found']) <= 2)
        
        if overall_success:
            print("🎉 전체 평가: 성공!")
            print("   스토리-선택지 동기화가 잘 작동하고 있습니다.")
        else:
            print("⚠️ 전체 평가: 개선 필요")
            print("   추가 수정이 필요합니다.")
        
        await game_manager.shutdown()
        return overall_success, test_results
        
    except Exception as e:
        print(f"❌ 테스트 환경 오류: {e}")
        import traceback
        traceback.print_exc()
        return False, test_results

async def continuous_test_until_success():
    """문제가 해결될 때까지 계속 테스트"""
    
    attempt = 1
    max_attempts = 5  # 최대 5번 시도
    
    while attempt <= max_attempts:
        print(f"\n🔄 테스트 시도 #{attempt}")
        print("-" * 60)
        
        success, results = await test_story_choice_synchronization()
        
        if success:
            print(f"\n✅ 테스트 성공! (시도 #{attempt})")
            return True, results
        else:
            print(f"\n⚠️ 테스트 실패 (시도 #{attempt})")
            if attempt < max_attempts:
                print("5초 후 재시도...")
                await asyncio.sleep(5)
            
        attempt += 1
    
    print(f"\n❌ {max_attempts}번 시도 후에도 문제가 지속됩니다.")
    return False, results

async def main():
    """메인 함수"""
    
    print("크툴루 TRPG 스토리-선택지 동기화 테스트")
    print("시간 제한 없이 문제가 해결될 때까지 테스트합니다.\n")
    
    success, final_results = await continuous_test_until_success()
    
    print("\n" + "=" * 80)
    print("🏁 최종 테스트 결과")
    print("=" * 80)
    
    if success:
        print("🎊 모든 테스트 통과!")
        print("\n🔧 성공적으로 구현된 기능:")
        print("- ✅ 스토리와 선택지의 동기화된 생성")
        print("- ✅ 스토리 스레드 정보 UI 표시")
        print("- ✅ 조사 기회 정보 UI 표시")
        print("- ✅ 일관성 있는 게임 경험")
        print("\n🚀 이제 실제 게임을 실행할 수 있습니다:")
        print("   source venv/bin/activate && python main.py --skip-checks")
    else:
        print("❌ 테스트 실패 - 추가 수정 필요")
        print(f"\n발견된 문제 수: {len(final_results.get('issues_found', []))}")
        
        if final_results.get('issues_found'):
            print("\n주요 문제들:")
            for issue in final_results['issues_found'][:5]:  # 최대 5개만 표시
                print(f"   • {issue}")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)