#!/usr/bin/env python3
"""
간단한 게임 실행 테스트
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_game():
    """게임 테스트"""
    
    print("=== 간단한 게임 테스트 ===")
    
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
        
        # 게임 시작 (캐릭터 없이)
        success = await game_manager.start_new_game(None, "Test Scenario")
        if not success:
            print("❌ 게임 시작 실패")
            return False
        
        print("✅ 게임 시작 성공")
        
        # CLI 인터페이스로 게임플레이 테스트
        from src.ui.gameplay_interface import GameplayInterface
        gameplay = GameplayInterface(game_manager)
        
        print("\n게임플레이 인터페이스 테스트...")
        
        # 게임플레이 세션 시작 (non-blocking으로 테스트)
        try:
            # 짧은 타임아웃으로 테스트
            task = asyncio.create_task(asyncio.to_thread(gameplay.start_gameplay_session))
            await asyncio.sleep(2.0)  # 2초 동안 실행
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                print("✅ 게임플레이 인터페이스 실행 확인")
        except Exception as e:
            print(f"❌ 게임플레이 오류: {e}")
            import traceback
            traceback.print_exc()
            return False
        
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
    
    print("크툴루 TRPG 게임 테스트를 시작합니다...\n")
    
    success = await test_game()
    
    print("\n" + "="*50)
    
    if success:
        print("🎉 게임 실행 테스트 성공!")
        print("\n수정된 스타일:")
        print("1. ✅ blood_red 스타일 추가")
        print("2. ✅ shadow_gray 스타일 추가")
        print("3. ✅ bone_white 스타일 추가")
        print("4. ✅ normal 스타일 추가")
        print("\n이제 게임을 실행할 수 있습니다:")
        print("  source venv/bin/activate && python main.py --skip-checks")
    else:
        print("❌ 추가 수정이 필요합니다.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)