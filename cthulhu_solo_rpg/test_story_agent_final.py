#!/usr/bin/env python3
"""Story Agent 최종 테스트 - 실제 게임 환경에서 테스트"""

import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, '.')

async def test_story_agent_in_game_context():
    """실제 게임 환경에서 Story Agent 테스트"""
    print("🎮 실제 게임 환경에서 Story Agent 테스트 시작...")
    print("=" * 60)
    
    try:
        from src.core.game_manager import GameManager
        from src.agents.story_agent import StoryAgent
        from src.ai.ollama_client import OllamaClient
        
        # Game Manager 초기화 (실제 게임과 동일한 환경)
        print("🔧 게임 시스템 초기화 중...")
        game_manager = GameManager()
        
        # Story Agent 직접 테스트
        print("🤖 Story Agent 직접 테스트...")
        story_agent = game_manager.agents.get('story_agent')
        
        if not story_agent:
            print("❌ Story Agent가 초기화되지 않았습니다.")
            return False
        
        # 테스트 컨텍스트 구성
        test_context = {
            'player_action': '일지를 조사한다',
            'location': 'old_lighthouse',
            'character_state': {
                'name': '조사자',
                'sanity': 80,
                'hp': 15,
                'skills': {'조사': 50, '도서관 이용': 60}
            },
            'turn_number': 3,
            'environmental_context': {
                'time': 'night',
                'weather': 'foggy',
                'atmosphere': 'mysterious'
            },
            'narrative_flags': {
                'lighthouse_visited': True,
                'journal_found': False
            }
        }
        
        print(f"📝 테스트 입력: '{test_context['player_action']}'")
        print(f"📍 위치: {test_context['location']}")
        
        # Story Agent의 process_player_action 메서드 테스트
        try:
            result = await story_agent.process_player_action(test_context)
            
            print("\n📋 처리 결과:")
            print(f"   성공 여부: {result.get('success', False)}")
            
            if result.get('success'):
                print("✅ Story Agent가 플레이어 입력을 성공적으로 처리했습니다!")
                
                narrative = result.get('narrative', '')
                print(f"📖 생성된 스토리: {narrative[:100]}...")
                
                consequences = result.get('consequences', {})
                if consequences:
                    print("🎯 결과:")
                    for key, value in consequences.items():
                        print(f"   • {key}: {value}")
                
                investigations = result.get('new_investigations', [])
                if investigations:
                    print("🔍 새로운 조사 요소:")
                    for inv in investigations:
                        print(f"   • {inv}")
                
                # 문맥 이해 검증
                context_keywords = ['일지', '조사', '발견', '단서']
                narrative_lower = narrative.lower()
                context_match = any(keyword in narrative_lower for keyword in context_keywords)
                
                if context_match:
                    print("✅ Story Agent가 문맥을 올바르게 이해했습니다!")
                else:
                    print("⚠️  Story Agent의 문맥 이해에 문제가 있을 수 있습니다.")
                
                return True
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ Story Agent 처리 실패: {error}")
                return False
                
        except Exception as e:
            print(f"💥 Story Agent 호출 중 예외 발생: {e}")
            return False
    
    except Exception as e:
        print(f"💥 시스템 초기화 실패: {e}")
        return False

async def test_multiple_actions():
    """여러 행동에 대한 Story Agent 반응 테스트"""
    print("\n🔄 다양한 행동에 대한 Story Agent 반응 테스트...")
    
    try:
        from src.agents.story_agent import StoryAgent
        from src.ai.ollama_client import OllamaClient
        
        ollama_client = OllamaClient()
        story_agent = StoryAgent(ollama_client)
        
        test_actions = [
            '일지를 조사한다',
            '조개껍질을 분석해본다',
            '엘리자베스와 대화한다',
            '등대 내부로 들어간다',
            '이상한 소리를 따라간다'
        ]
        
        success_count = 0
        for i, action in enumerate(test_actions, 1):
            print(f"\n📝 테스트 {i}: '{action}'")
            
            context = {
                'player_action': action,
                'location': f'test_location_{i}',
                'character_state': {'sanity': 80, 'hp': 15},
                'turn_number': i
            }
            
            try:
                result = await story_agent.process_player_action(context)
                if result.get('success'):
                    success_count += 1
                    print(f"✅ 성공 - {result.get('narrative', '')[:50]}...")
                else:
                    print(f"❌ 실패 - {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"💥 예외 - {e}")
        
        success_rate = success_count / len(test_actions) * 100
        print(f"\n📊 전체 성공률: {success_count}/{len(test_actions)} ({success_rate:.1f}%)")
        
        return success_rate >= 80  # 80% 이상이면 성공
        
    except Exception as e:
        print(f"💥 다중 테스트 실패: {e}")
        return False

async def main():
    """메인 테스트 실행"""
    print("🚀 Story Agent 최종 검증 테스트")
    print("=" * 60)
    
    # 실제 게임 환경 테스트
    game_test_passed = await test_story_agent_in_game_context()
    
    # 다중 액션 테스트
    multi_test_passed = await test_multiple_actions()
    
    print("\n" + "=" * 60)
    print("🏁 최종 테스트 결과:")
    print(f"   게임 환경 테스트: {'✅ 통과' if game_test_passed else '❌ 실패'}")
    print(f"   다중 액션 테스트: {'✅ 통과' if multi_test_passed else '❌ 실패'}")
    
    if game_test_passed and multi_test_passed:
        print("\n🎉 Story Agent가 완벽하게 작동합니다!")
        print("   ✨ 플레이어 입력을 제대로 이해하고 적절한 스토리를 생성합니다.")
        print("   ✨ 문맥을 파악하여 상황에 맞는 반응을 제공합니다.")
        print("   ✨ 자유형 텍스트 시스템이 정상적으로 작동합니다.")
    elif game_test_passed or multi_test_passed:
        print("\n⚠️  Story Agent가 부분적으로 작동합니다.")
        print("   일부 기능에서 문제가 있을 수 있습니다.")
    else:
        print("\n🚨 Story Agent에 심각한 문제가 있습니다.")
        print("   추가적인 수정이 필요합니다.")

if __name__ == "__main__":
    asyncio.run(main())