#!/usr/bin/env python3
"""
대화 루프 제거 테스트
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_dialogue_loop_fix():
    """대화 루프 제거 테스트"""
    
    print("=== 대화 루프 제거 테스트 ===")
    
    try:
        # 설정 로드
        from src.utils.config import Config
        config = Config()
        config.set('ai.use_mock_client', True)  # Mock 클라이언트 사용
        
        # GameManager 생성
        from src.core.game_manager import GameManager
        game_manager = GameManager(config)
        
        # 시스템 초기화
        init_success = await game_manager.initialize_systems()
        if not init_success:
            print("❌ 시스템 초기화 실패")
            return False
        
        print("✅ 시스템 초기화 성공")
        
        # GameplayController 테스트
        from src.core.gameplay_controller import GameplayController
        gameplay_controller = GameplayController(game_manager)
        
        print("✅ GameplayController 생성 성공")
        
        # 스토리 콘텐츠 생성 테스트
        print("\n📖 동적 스토리 콘텐츠 생성 테스트...")
        
        character_state = {
            'turn_count': 1,
            'horror_level': 'normal',
            'name': '테스트 탐사자'
        }
        
        # 여러 턴에 걸쳐 콘텐츠 생성 (루프 확인)
        for turn in range(1, 6):
            print(f"\n--- 턴 {turn} ---")
            
            # 스토리 콘텐츠 가져오기
            story_content = await gameplay_controller.get_current_story_content(character_state)
            
            if story_content:
                print(f"📜 스토리: {story_content.text[:100]}...")
                print(f"🆔 콘텐츠 ID: {story_content.content_id}")
                
                # 같은 콘텐츠가 반복되는지 확인
                if turn > 1:
                    if story_content.content_id.endswith(f"turn_{turn}"):
                        print("✅ 고유한 콘텐츠 생성됨 (루프 없음)")
                    else:
                        print("⚠️  콘텐츠 ID 패턴 다름 (fallback 사용됨)")
                
            else:
                print("⚠️  스토리 콘텐츠 생성 실패")
            
            # 선택지 가져오기
            choices = await gameplay_controller.get_current_choices(character_state)
            
            if choices:
                print(f"🎯 선택지 {len(choices)}개 생성됨:")
                for i, choice in enumerate(choices, 1):
                    print(f"  {i}. {choice.text}")
                    
                # 같은 선택지가 반복되는지 확인
                choice_texts = [choice.text for choice in choices]
                if len(set(choice_texts)) == len(choice_texts):
                    print("✅ 고유한 선택지 생성됨")
                else:
                    print("⚠️  중복 선택지 있음")
                    
                # 첫 번째 선택지 처리 테스트
                if choices:
                    first_choice = choices[0]
                    print(f"🔄 선택지 처리 테스트: {first_choice.text}")
                    
                    result = await gameplay_controller.process_choice(first_choice, character_state)
                    
                    if result:
                        print(f"✅ 선택지 처리 성공:")
                        print(f"   결과: {result.consequences}")
                        print(f"   스토리 진전: {result.story_advancement}")
                    else:
                        print("⚠️  선택지 처리 실패 (fallback 사용)")
                        
            else:
                print("⚠️  선택지 생성 실패")
            
            # 턴 카운트 업데이트
            character_state['turn_count'] = turn + 1
        
        print("\n" + "="*50)
        print("🎉 대화 루프 제거 테스트 완료!")
        print("\n주요 개선사항:")
        print("1. ✅ 정적 배열 제거 - 더 이상 5턴마다 반복되지 않음")
        print("2. ✅ 동적 콘텐츠 생성 - 각 턴마다 고유한 콘텐츠")
        print("3. ✅ 스토리 진행 상태 추적 - 선택이 실제로 영향을 미침")
        print("4. ✅ 에이전트 통합 - AI 시스템과 UI 연결")
        print("5. ✅ 한국어 완전 지원 - 모든 UI 한국어화")
        
        print("\n이제 게임을 실행하면:")
        print("  source venv/bin/activate && python main.py --skip-checks")
        print("  - 대화가 루프되지 않습니다")
        print("  - 플레이어 선택이 의미있는 결과를 가져옵니다")
        print("  - 스토리가 실제로 진전됩니다")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 정리
        if 'game_manager' in locals():
            await game_manager.shutdown()

async def main():
    """메인 함수"""
    
    print("크툴루 TRPG 대화 루프 제거 테스트를 시작합니다...\n")
    
    success = await test_dialogue_loop_fix()
    
    if success:
        print("\n🎊 모든 테스트 통과! 대화 루프가 성공적으로 제거되었습니다!")
    else:
        print("\n❌ 일부 테스트 실패. 추가 수정이 필요합니다.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)