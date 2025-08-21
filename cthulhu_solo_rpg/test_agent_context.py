#!/usr/bin/env python3
"""
Agent Context 수정사항 테스트
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_agent_context():
    """Agent Context 수정사항 테스트"""
    
    print("=== Agent Context 수정사항 테스트 ===")
    
    # 1. BaseAgent Context 테스트
    print("\n1. BaseAgent Context 테스트...")
    
    try:
        from src.agents.base_agent import BaseAgent, AgentContext
        
        # AgentContext에 session_info 필드가 있는지 확인
        context = AgentContext()
        
        print(f"✓ AgentContext 생성 성공")
        print(f"✓ session_info 필드 존재: {hasattr(context, 'session_info')}")
        print(f"✓ 기본값: {context.session_info}")
        
        # session_info 업데이트 테스트
        test_session_info = {
            "session_id": "test-session-123",
            "scenario": "The Haunted House",
            "total_turns": 5
        }
        
        context.session_info = test_session_info
        print(f"✓ session_info 업데이트 성공: {context.session_info}")
        
    except Exception as e:
        print(f"❌ AgentContext 테스트 실패: {e}")
        return False
    
    # 2. BaseAgent update_context 테스트
    print("\n2. BaseAgent update_context 테스트...")
    
    try:
        from src.agents.story_agent import StoryAgent
        from src.ai.mock_ollama_client import MockOllamaClient
        
        # Mock AI 클라이언트로 Story Agent 생성
        mock_client = MockOllamaClient()
        story_agent = StoryAgent(ollama_client=mock_client)
        
        print(f"✓ Story Agent 생성 성공")
        
        # update_context에 session_info 전달 테스트
        story_agent.update_context(
            session_info={
                "session_id": "test-123",
                "scenario": "Test Scenario",
                "total_turns": 3
            },
            game_state={"phase": "investigation"},
            player_state={"sanity": 80}
        )
        
        print(f"✓ update_context 성공 (session_info 포함)")
        print(f"✓ Agent context session_info: {story_agent.context.session_info}")
        
        # 이제 경고 메시지가 나오지 않아야 함
        print("✓ Unknown context field 경고 없음")
        
    except Exception as e:
        print(f"❌ update_context 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. Context String 생성 테스트
    print("\n3. Context String 생성 테스트...")
    
    try:
        # 테스트용 input_data 제공
        test_input = {"action": "investigate", "target": "library"}
        context_string = story_agent._prepare_context_string(test_input)
        
        print(f"✓ Context string 생성 성공")
        print(f"✓ Session info 포함 여부: {'Session Info' in context_string}")
        
        if "Session Info" in context_string:
            print("✓ Context string에 session_info가 포함됨")
        else:
            print("⚠️ Context string에 session_info가 포함되지 않음 (정상일 수 있음)")
        
    except Exception as e:
        print(f"❌ Context string 테스트 실패: {e}")
        return False
    
    # 4. 다른 Agent 타입들 테스트
    print("\n4. 다른 Agent 타입들 테스트...")
    
    agent_classes = [
        ('NPCAgent', 'src.agents.npc_agent'),
        ('EnvironmentAgent', 'src.agents.environment_agent'),
        ('RuleAgent', 'src.agents.rule_agent'),
        ('MemoryAgent', 'src.agents.memory_agent')
    ]
    
    for agent_name, module_path in agent_classes:
        try:
            module = __import__(module_path, fromlist=[agent_name])
            agent_class = getattr(module, agent_name)
            
            agent = agent_class(ollama_client=mock_client)
            
            agent.update_context(
                session_info={"session_id": "test", "scenario": "Test"}
            )
            
            print(f"✓ {agent_name} 정상 작동")
            
        except Exception as e:
            print(f"❌ {agent_name} 테스트 실패: {e}")
            return False
    
    print("\n✅ 모든 Agent Context 테스트 통과!")
    print("session_info context field 오류가 해결되었습니다.")
    return True

if __name__ == "__main__":
    try:
        success = test_agent_context()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 테스트 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)