#!/usr/bin/env python3
"""
session_info 수정사항 최종 확인
"""

import sys
import os
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def verify_fix():
    """수정사항 최종 확인"""
    
    print("=== session_info 수정사항 최종 확인 ===")
    
    # 로그 캡처 설정
    import io
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.WARNING)
    
    # BaseAgent 로거 설정
    logger = logging.getLogger('src.agents.base_agent')
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    
    try:
        print("\n1. BaseAgent와 AgentContext 확인...")
        
        from src.agents.base_agent import BaseAgent, AgentContext
        
        # AgentContext에 session_info 필드 존재 확인
        context = AgentContext()
        assert hasattr(context, 'session_info'), "session_info 필드가 없습니다"
        print("✓ AgentContext에 session_info 필드 존재")
        
        print("\n2. Story Agent로 update_context 테스트...")
        
        from src.agents.story_agent import StoryAgent
        from src.ai.mock_ollama_client import MockOllamaClient
        
        mock_client = MockOllamaClient()
        story_agent = StoryAgent(ollama_client=mock_client)
        
        # session_info 포함하여 컨텍스트 업데이트
        story_agent.update_context(
            session_info={
                "session_id": "test-session",
                "scenario": "The Haunted Library", 
                "total_turns": 5
            },
            game_state={"phase": "investigation"},
            player_state={"sanity": 75, "hp": 12}
        )
        
        print("✓ update_context 호출 완료")
        
        # 로그 확인
        log_output = log_stream.getvalue()
        
        if "Unknown context field: session_info" in log_output:
            print("❌ session_info 경고가 여전히 발생합니다!")
            print("로그 내용:", log_output)
            return False
        elif "Unknown context field" in log_output:
            print("⚠️ 다른 unknown context field 경고:")
            print(log_output)
        else:
            print("✅ session_info 경고 없음!")
        
        # 컨텍스트 확인
        agent_context = story_agent.context.session_info
        expected_session_info = {
            "session_id": "test-session",
            "scenario": "The Haunted Library",
            "total_turns": 5
        }
        
        if agent_context == expected_session_info:
            print("✓ session_info가 올바르게 저장됨")
        else:
            print(f"❌ session_info 저장 실패: {agent_context}")
            return False
        
        print("\n3. 컨텍스트 문자열 생성 테스트...")
        
        test_input = {"action": "investigate", "target": "ancient tome"}
        context_string = story_agent._prepare_context_string(test_input)
        
        if "Session Info" in context_string:
            print("✓ 컨텍스트 문자열에 session_info 포함됨")
        else:
            print("⚠️ 컨텍스트 문자열에 session_info가 포함되지 않음")
        
        print("\n✅ 모든 확인 완료!")
        print("session_info context field 오류가 성공적으로 수정되었습니다.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 확인 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_fix()
    
    print("\n" + "="*60)
    if success:
        print("🎉 session_info 오류 수정 완료!")
        print("이제 게임 실행 시 'Unknown context field: session_info' 경고가 나타나지 않습니다.")
    else:
        print("❌ 수정 확인 실패")
    
    sys.exit(0 if success else 1)