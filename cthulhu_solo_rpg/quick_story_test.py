#!/usr/bin/env python3
"""Story Agent 빠른 기능 테스트"""

import sys
import os

# 프로젝트 루트 추가
sys.path.insert(0, 'src')

def test_story_agent_methods():
    """Story Agent 메서드 존재 여부 확인"""
    print("🔍 Story Agent 메서드 존재 여부 확인...")
    
    try:
        from agents.story_agent import StoryAgent
        
        # 클래스 메서드 목록 확인
        methods = [method for method in dir(StoryAgent) if not method.startswith('_')]
        print(f"✅ Story Agent 클래스 로드 성공")
        print(f"📝 공개 메서드 ({len(methods)}개):")
        for method in sorted(methods):
            print(f"   • {method}")
        
        # 핵심 메서드 확인
        essential_methods = ['process_input', 'process_player_action']
        print(f"\n🎯 핵심 메서드 확인:")
        for method in essential_methods:
            exists = hasattr(StoryAgent, method)
            status = "✅" if exists else "❌"
            print(f"   {status} {method}")
        
        # process_player_action 메서드 시그니처 확인
        if hasattr(StoryAgent, 'process_player_action'):
            import inspect
            signature = inspect.signature(StoryAgent.process_player_action)
            print(f"\n📋 process_player_action 시그니처:")
            print(f"   {signature}")
            
        return True
        
    except ImportError as e:
        print(f"❌ Story Agent 임포트 실패: {e}")
        return False
    except Exception as e:
        print(f"💥 예외 발생: {e}")
        return False

def test_action_type_analysis():
    """액션 타입 분석 기능 테스트"""
    print(f"\n🧠 액션 타입 분석 테스트...")
    
    try:
        from agents.story_agent import StoryAgent
        from ai.ollama_client import OllamaClient
        
        ollama_client = OllamaClient()
        story_agent = StoryAgent(ollama_client)
        
        # 다양한 행동 텍스트 테스트
        test_actions = [
            ('일지를 조사한다', 'investigation'),
            ('조개껍질을 분석해본다', 'investigation'),
            ('엘리자베스와 대화한다', 'social_interaction'),
            ('등대로 이동한다', 'movement'),
            ('문을 열어본다', 'examination'),
            ('주변을 둘러본다', 'investigation')
        ]
        
        success_count = 0
        for action_text, expected_type in test_actions:
            try:
                detected_type = story_agent._analyze_action_type(action_text)
                status = "✅" if detected_type == expected_type else "⚠️"
                print(f"   {status} '{action_text}' → {detected_type} (예상: {expected_type})")
                if detected_type == expected_type:
                    success_count += 1
            except Exception as e:
                print(f"   ❌ '{action_text}' → 오류: {e}")
        
        accuracy = success_count / len(test_actions) * 100
        print(f"\n📊 정확도: {success_count}/{len(test_actions)} ({accuracy:.1f}%)")
        
        return accuracy >= 80  # 80% 이상이면 성공
        
    except Exception as e:
        print(f"❌ 액션 분석 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Story Agent 빠른 기능 테스트")
    print("=" * 50)
    
    # 메서드 존재 여부 확인
    methods_ok = test_story_agent_methods()
    
    # 액션 분석 기능 테스트
    analysis_ok = test_action_type_analysis()
    
    print("\n" + "=" * 50)
    print("📋 테스트 결과 요약:")
    print(f"   메서드 존재: {'✅' if methods_ok else '❌'}")
    print(f"   액션 분석: {'✅' if analysis_ok else '❌'}")
    
    if methods_ok and analysis_ok:
        print("\n🎉 Story Agent가 정상적으로 구현되었습니다!")
        print("   이제 플레이어 입력을 제대로 이해할 수 있습니다.")
    else:
        print("\n⚠️  Story Agent에 일부 문제가 있습니다.")
        print("   추가 수정이 필요할 수 있습니다.")