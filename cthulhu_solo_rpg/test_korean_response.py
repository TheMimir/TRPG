#!/usr/bin/env python3
"""
Korean Response Test Script for Cthulhu Solo TRPG

Tests that all AI agents respond consistently in Korean after modifications.
"""

import asyncio
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from src.ai.ollama_client import OllamaClient
    from src.agents.story_agent import StoryAgent
    from src.agents.environment_agent import EnvironmentAgent
    from src.agents.rule_agent import RuleAgent
    print("모듈 임포트 성공!")
except ImportError as e:
    print(f"모듈 임포트 실패: {e}")
    print("Ollama 서비스가 실행 중인지 확인하고, 필요한 의존성이 설치되어 있는지 확인하세요.")
    sys.exit(1)

def test_korean_character_detection(text: str) -> dict:
    """Test Korean character detection logic."""
    if not text:
        return {"is_korean": False, "korean_ratio": 0.0, "english_ratio": 0.0}
    
    # Count Korean characters (Hangul)
    korean_chars = sum(1 for char in text if 0xAC00 <= ord(char) <= 0xD7A3)
    # Count English alphabetic characters 
    english_chars = sum(1 for char in text if char.isalpha() and ord(char) < 128)
    total_chars = len(text.replace(' ', '').replace('\n', ''))
    
    if total_chars == 0:
        return {"is_korean": False, "korean_ratio": 0.0, "english_ratio": 0.0}
    
    korean_ratio = korean_chars / total_chars
    english_ratio = english_chars / total_chars
    
    # Response should be primarily Korean (at least 30% Korean chars and less than 50% English)
    is_korean = korean_ratio >= 0.3 and english_ratio < 0.5
    
    return {
        "is_korean": is_korean,
        "korean_ratio": korean_ratio,
        "english_ratio": english_ratio,
        "korean_chars": korean_chars,
        "english_chars": english_chars,
        "total_chars": total_chars
    }

async def test_story_agent():
    """Test StoryAgent Korean responses."""
    print("\n=== 스토리 에이전트 한국어 테스트 ===")
    
    try:
        ollama_client = OllamaClient()
        story_agent = StoryAgent(ollama_client)
        
        # Test scene generation
        test_input = {
            "action_type": "scene_generation",
            "player_action": "조사자가 오래된 도서관에 들어간다",
            "location": "미스카토닉 대학 도서관",
            "user_input": "도서관의 분위기를 묘사해주세요"
        }
        
        print("테스트 입력:", test_input["user_input"])
        response = await story_agent.process_input(test_input)
        
        if "scene" in response and "description" in response["scene"]:
            description = response["scene"]["description"]
            print("응답:", description[:200] + "..." if len(description) > 200 else description)
            
            korean_test = test_korean_character_detection(description)
            print(f"한국어 테스트 결과: {korean_test}")
            
            if korean_test["is_korean"]:
                print("✅ 한국어 응답 성공!")
            else:
                print("❌ 한국어 응답 실패!")
                
        else:
            print("❌ 응답 구조 오류:", response)
            
    except Exception as e:
        print(f"❌ 스토리 에이전트 테스트 실패: {e}")

async def test_environment_agent():
    """Test EnvironmentAgent Korean responses."""
    print("\n=== 환경 에이전트 한국어 테스트 ===")
    
    try:
        ollama_client = OllamaClient()
        env_agent = EnvironmentAgent(ollama_client)
        
        # Test location description
        test_input = {
            "action_type": "describe_location",
            "location_id": "test_library",
            "name": "어둠의 도서관",
            "user_input": "이 장소를 자세히 묘사해주세요"
        }
        
        print("테스트 입력:", test_input["user_input"])
        response = await env_agent.process_input(test_input)
        
        if "description" in response:
            description = response["description"]
            print("응답:", description[:200] + "..." if len(description) > 200 else description)
            
            korean_test = test_korean_character_detection(description)
            print(f"한국어 테스트 결과: {korean_test}")
            
            if korean_test["is_korean"]:
                print("✅ 한국어 응답 성공!")
            else:
                print("❌ 한국어 응답 실패!")
                
        else:
            print("❌ 응답 구조 오류:", response)
            
    except Exception as e:
        print(f"❌ 환경 에이전트 테스트 실패: {e}")

async def test_rule_agent():
    """Test RuleAgent Korean responses."""
    print("\n=== 규칙 에이전트 한국어 테스트 ===")
    
    try:
        ollama_client = OllamaClient()
        rule_agent = RuleAgent(ollama_client)
        
        # Test rule interpretation
        test_input = {
            "action_type": "rule_interpretation",
            "player_action": "조사자가 숨겨진 문을 찾기 위해 탐지 판정을 한다",
            "skill": "Spot Hidden",
            "user_input": "이 상황에 대한 규칙을 설명해주세요"
        }
        
        print("테스트 입력:", test_input["user_input"])
        response = await rule_agent.process_input(test_input)
        
        # Rule agent might have different response structure
        response_text = ""
        if isinstance(response, dict):
            if "interpretation" in response:
                response_text = response["interpretation"]
            elif "description" in response:
                response_text = response["description"]
            else:
                response_text = str(response)
        else:
            response_text = str(response)
            
        print("응답:", response_text[:200] + "..." if len(response_text) > 200 else response_text)
        
        korean_test = test_korean_character_detection(response_text)
        print(f"한국어 테스트 결과: {korean_test}")
        
        if korean_test["is_korean"]:
            print("✅ 한국어 응답 성공!")
        else:
            print("❌ 한국어 응답 실패!")
            
    except Exception as e:
        print(f"❌ 규칙 에이전트 테스트 실패: {e}")

async def test_ollama_client():
    """Test OllamaClient Korean enforcement."""
    print("\n=== Ollama 클라이언트 한국어 강제 테스트 ===")
    
    try:
        ollama_client = OllamaClient()
        
        # Check if Ollama is available
        if not ollama_client.is_available():
            print("⚠️  Ollama 서비스를 사용할 수 없습니다. 로컬에서 Ollama를 실행하세요.")
            return
            
        # Test basic Korean response
        response = ollama_client.generate(
            prompt="크툴루 호러 RPG에서 무서운 도서관을 묘사해주세요.",
            system_prompt="당신은 한국어로만 응답하는 AI입니다.",
            temperature=0.7
        )
        
        print("테스트 프롬프트: 크툴루 호러 RPG에서 무서운 도서관을 묘사해주세요.")
        print("응답:", response.content[:200] + "..." if len(response.content) > 200 else response.content)
        
        korean_test = test_korean_character_detection(response.content)
        print(f"한국어 테스트 결과: {korean_test}")
        
        if korean_test["is_korean"]:
            print("✅ Ollama 클라이언트 한국어 강제 성공!")
        else:
            print("❌ Ollama 클라이언트 한국어 강제 실패!")
            
    except Exception as e:
        print(f"❌ Ollama 클라이언트 테스트 실패: {e}")

async def main():
    """Run all Korean response tests."""
    print("🎲 크툴루 솔로 TRPG 한국어 응답 테스트 시작 🎲")
    print("=" * 50)
    
    # Test character detection first
    print("\n=== 한국어 감지 로직 테스트 ===")
    test_cases = [
        "안녕하세요. 이것은 한국어 문장입니다.",
        "Hello, this is an English sentence.",
        "안녕하세요. Hello, mixed language sentence.",
        "한국어 90% English 10%",
        "Korean 10% 한국어가 대부분인 문장입니다만 영어도 조금 섞여있어요.",
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        result = test_korean_character_detection(test_case)
        print(f"테스트 {i}: '{test_case}' -> {result['is_korean']} (한국어: {result['korean_ratio']:.2f}, 영어: {result['english_ratio']:.2f})")
    
    # Test Ollama client
    await test_ollama_client()
    
    # Test agents
    await test_story_agent()
    await test_environment_agent()
    await test_rule_agent()
    
    print("\n" + "=" * 50)
    print("🎲 한국어 응답 테스트 완료 🎲")

if __name__ == "__main__":
    asyncio.run(main())