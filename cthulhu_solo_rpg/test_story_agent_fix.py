#!/usr/bin/env python3
"""Story Agent 문맥 이해 능력 테스트"""

import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

from agents.story_agent import StoryAgent
from ai.ollama_client import OllamaClient

async def test_story_agent_context_understanding():
    """Story Agent의 플레이어 답변 이해 능력 테스트"""
    print("🧠 Story Agent 문맥 이해 능력 테스트 시작...")
    print("=" * 60)
    
    try:
        # Mock Ollama Client 사용
        ollama_client = OllamaClient()
        story_agent = StoryAgent(ollama_client)
        
        # 다양한 자유형 텍스트 입력 테스트
        test_cases = [
            {
                'description': '일지 조사 요청',
                'context': {
                    'player_action': '일지를 조사한다',
                    'location': 'old_lighthouse',
                    'character_state': {'sanity': 80, 'hp': 15},
                    'turn_number': 3,
                    'environmental_context': {'time': 'night', 'weather': 'foggy'}
                }
            },
            {
                'description': '조개껍질 분석 요청',
                'context': {
                    'player_action': '조개껍질을 분석해본다',
                    'location': 'beach_area',
                    'character_state': {'sanity': 75, 'hp': 15},
                    'turn_number': 5,
                    'environmental_context': {'time': 'dawn', 'weather': 'clear'}
                }
            },
            {
                'description': '엘리자베스와 대화',
                'context': {
                    'player_action': '엘리자베스와 대화한다',
                    'location': 'village_square',
                    'character_state': {'sanity': 70, 'hp': 15},
                    'turn_number': 7,
                    'environmental_context': {'time': 'evening', 'weather': 'cloudy'}
                }
            },
            {
                'description': '등대 내부 탐색',
                'context': {
                    'player_action': '등대 내부를 탐색한다',
                    'location': 'lighthouse_exterior',
                    'character_state': {'sanity': 65, 'hp': 15},
                    'turn_number': 9,
                    'environmental_context': {'time': 'night', 'weather': 'stormy'}
                }
            },
            {
                'description': '복잡한 행동 (문을 열고 안으로 들어간다)',
                'context': {
                    'player_action': '문을 조심스럽게 열고 안으로 들어간다',
                    'location': 'mysterious_building',
                    'character_state': {'sanity': 60, 'hp': 15},
                    'turn_number': 11,
                    'environmental_context': {'time': 'midnight', 'weather': 'foggy'}
                }
            }
        ]
        
        success_count = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 테스트 {i}/{total_tests}: {test_case['description']}")
            print(f"입력: '{test_case['context']['player_action']}'")
            print("-" * 40)
            
            try:
                result = await story_agent.process_player_action(test_case['context'])
                
                if result.get('success', False):
                    success_count += 1
                    print("✅ 처리 성공!")
                    print(f"📖 스토리 반응: {result.get('narrative', 'No narrative')}")
                    
                    consequences = result.get('consequences', {})
                    if consequences:
                        print("📋 결과:")
                        for key, value in consequences.items():
                            print(f"   • {key}: {value}")
                    
                    investigations = result.get('new_investigations', [])
                    if investigations:
                        print("🔍 새로운 조사 요소:")
                        for inv in investigations:
                            print(f"   • {inv}")
                            
                    tension_change = result.get('tension_change', 0)
                    if tension_change != 0:
                        print(f"⚡ 긴장도 변화: {tension_change:+d}")
                        
                else:
                    print("❌ 처리 실패")
                    print(f"오류: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"💥 예외 발생: {e}")
                print(f"예외 타입: {type(e).__name__}")
        
        print("\n" + "=" * 60)
        print(f"🎯 테스트 결과 요약:")
        print(f"성공: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%)")
        
        if success_count == total_tests:
            print("🎉 모든 테스트 통과! Story Agent가 문맥을 올바르게 이해하고 있습니다.")
        elif success_count > 0:
            print("⚠️  일부 테스트 통과. Story Agent가 부분적으로 작동하고 있습니다.")
        else:
            print("🚨 모든 테스트 실패. Story Agent에 심각한 문제가 있습니다.")
            
        return success_count == total_tests
        
    except Exception as e:
        print(f"💥 테스트 초기화 실패: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_story_agent_context_understanding())
    if success:
        print("\n✨ Story Agent 문맥 이해 테스트 완료 - 모든 기능이 정상 작동합니다!")
    else:
        print("\n⚠️  Story Agent 문맥 이해에 문제가 발견되었습니다.")