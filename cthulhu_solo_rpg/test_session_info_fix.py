#!/usr/bin/env python3
"""
session_info 오류 수정 확인 테스트
"""

import sys
import os
import asyncio
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 로깅 설정 - WARNING 레벨 이상만 캡처
logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(name)s - %(message)s')

async def test_session_info_fix():
    """session_info 오류 수정 확인"""
    
    print("=== session_info 오류 수정 확인 테스트 ===")
    
    try:
        from src.core.game_manager import GameManager
        from src.core.character import Character
        from src.utils.config import Config
        
        print("\n1. GameManager 초기화...")
        
        # 설정 생성
        config = Config()
        config.data = {
            'ai': {
                'use_mock_client': True,
                'model': 'mock-model',
                'ultra_think_enabled': False
            },
            'game': {
                'auto_save': False
            },
            'saves_directory': './saves'
        }
        
        game_manager = GameManager(config)
        print("✓ GameManager 생성됨")
        
        # 시스템 초기화
        success = await game_manager.initialize_systems()
        if success:
            print("✓ 시스템 초기화 성공")
        else:
            print("❌ 시스템 초기화 실패")
            return False
        
        print("\n2. 캐릭터 생성 및 게임 시작...")
        
        # 테스트 캐릭터 생성
        character = Character("테스트 조사자", age=30, gender="male")
        character.generate_attributes("rolled")
        character.set_occupation("Detective", 300)
        character.background = "베테랑 수사관"
        
        print("✓ 캐릭터 생성됨")
        
        # 게임 시작 (여기서 session_info가 에이전트들에게 전달됨)
        game_success = await game_manager.start_new_game(
            character=character,
            scenario_name="테스트 시나리오"
        )
        
        if game_success:
            print("✓ 게임 시작 성공")
        else:
            print("❌ 게임 시작 실패")
            return False
        
        print("\n3. 플레이어 액션 시뮬레이션...")
        
        # 플레이어 액션 실행 (에이전트들이 session_info 컨텍스트를 사용함)
        from src.core.game_engine import PlayerAction
        
        action = PlayerAction(
            action_type="investigation",
            parameters={"target": "도서관", "skill": "Library Use"},
            time_cost=30
        )
        
        result = await game_manager.process_player_action(action)
        
        if result.get("success"):
            print("✓ 플레이어 액션 처리 성공")
            print(f"  턴 번호: {result.get('turn_number', 'N/A')}")
        else:
            print(f"❌ 플레이어 액션 실패: {result.get('error', 'Unknown error')}")
            return False
        
        print("\n✅ session_info 오류 수정 테스트 완료!")
        print("경고 메시지 없이 모든 에이전트가 정상 작동했습니다.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 정리
        if 'game_manager' in locals():
            try:
                await game_manager.shutdown()
                print("✓ 정리 완료")
            except:
                pass

async def main():
    """메인 함수"""
    
    # 로그 캡처를 위한 핸들러 설정
    import io
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.WARNING)
    
    # 특정 로거에 핸들러 추가
    base_agent_logger = logging.getLogger('src.agents.base_agent')
    base_agent_logger.addHandler(handler)
    base_agent_logger.setLevel(logging.WARNING)
    
    # 테스트 실행
    success = await test_session_info_fix()
    
    # 로그 확인
    log_output = log_stream.getvalue()
    
    print("\n" + "="*60)
    if "Unknown context field: session_info" in log_output:
        print("❌ session_info 경고 메시지가 여전히 발생합니다:")
        print(log_output)
        success = False
    elif log_output.strip():
        print("⚠️ 다른 경고 메시지들:")
        print(log_output)
    else:
        print("✅ session_info 관련 경고 메시지 없음 - 수정 완료!")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)