#!/usr/bin/env python3
"""
한국어 언어 설정 테스트
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_korean_language():
    """한국어 언어 설정 테스트"""
    
    print("=== 한국어 언어 설정 테스트 ===")
    
    # 1. 번역 시스템 테스트
    print("\n1. 번역 시스템 테스트...")
    from src.utils.localization import get_localization_manager, t
    
    loc = get_localization_manager()
    
    # 한국어로 설정
    loc.set_language('ko')
    print(f"✓ 현재 언어: {loc.current_language}")
    
    # 번역 테스트
    print(f"✓ 앱 제목: {t('app.title')}")
    print(f"✓ 메인 메뉴: {t('menu.main.title')}")
    print(f"✓ 새 게임: {t('menu.main.new_game')}")
    print(f"✓ 환영 메시지: {t('messages.welcome')}")
    
    # 2. AI 응답 테스트  
    print("\n2. AI 응답 테스트...")
    from src.ai.mock_ollama_client import MockOllamaClient
    
    mock_client = MockOllamaClient()
    
    # 한국어 응답 테스트
    response = mock_client.generate(
        prompt="도서관에서 무서운 장면을 묘사해주세요",
        system_prompt="당신은 크툴루 호러 게임의 스토리 에이전트입니다."
    )
    
    print(f"✓ AI 응답 (한국어): {response.content[:100]}...")
    
    # 3. 영어로 변경 테스트
    print("\n3. 영어로 변경 테스트...")
    loc.set_language('en')
    print(f"✓ 현재 언어: {loc.current_language}")
    print(f"✓ 앱 제목: {t('app.title')}")
    print(f"✓ 메인 메뉴: {t('menu.main.title')}")
    
    # 영어 AI 응답 테스트
    response_en = mock_client.generate(
        prompt="Describe a scary scene in the library",
        system_prompt="You are a story agent for a Cthulhu horror game."
    )
    
    print(f"✓ AI 응답 (영어): {response_en.content[:100]}...")
    
    # 4. 다시 한국어로 복원
    print("\n4. 한국어로 복원...")
    loc.set_language('ko')
    print(f"✓ 복원된 언어: {loc.current_language}")
    print(f"✓ 메시지: {t('messages.success')}")
    
    print("\n✅ 모든 언어 설정 테스트 통과!")
    return True

if __name__ == "__main__":
    try:
        test_korean_language()
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)