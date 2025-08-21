#!/usr/bin/env python3
"""
CLI Interface run_async 수정사항 테스트
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_cli_interface():
    """CLI Interface run_async 메서드 테스트"""
    
    print("=== CLI Interface run_async 테스트 ===")
    
    try:
        print("\n1. CLIInterface 클래스 확인...")
        
        from src.ui.cli_interface import CLIInterface
        from src.core.game_manager import GameManager
        from src.utils.config import Config
        
        # Mock 설정으로 GameManager 생성
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
        
        # CLIInterface 생성
        cli_interface = CLIInterface(game_manager)
        print("✓ CLIInterface 생성됨")
        
        print("\n2. 메서드 존재 확인...")
        
        # run_async 메서드 존재 확인
        if hasattr(cli_interface, 'run_async'):
            print("✓ run_async 메서드 존재")
        else:
            print("❌ run_async 메서드 없음")
            return False
        
        # run_async가 코루틴인지 확인
        import inspect
        if inspect.iscoroutinefunction(cli_interface.run_async):
            print("✓ run_async는 async 함수")
        else:
            print("❌ run_async가 async 함수가 아님")
            return False
        
        # 기존 run 메서드도 여전히 존재하는지 확인
        if hasattr(cli_interface, 'run'):
            print("✓ 기존 run 메서드도 존재 (호환성 유지)")
        else:
            print("⚠️ 기존 run 메서드 없음")
        
        print("\n3. 메서드 호출 테스트...")
        
        # run_async 메서드 호출이 가능한지 확인 (실제 실행하지는 않음)
        try:
            # 0.1초 후 취소하는 타이머 설정
            task = asyncio.create_task(cli_interface.run_async())
            
            # 아주 짧은 시간 실행 후 취소
            await asyncio.sleep(0.1)
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                print("✓ run_async 메서드 호출 가능 (정상 취소됨)")
            
        except Exception as e:
            print(f"❌ run_async 호출 실패: {e}")
            return False
        
        print("\n4. DesktopInterface 호환성 확인...")
        
        try:
            from src.ui.desktop_interface import DesktopInterface
            
            desktop_interface = DesktopInterface(game_manager)
            
            if hasattr(desktop_interface, 'run_async'):
                print("✓ DesktopInterface도 run_async 메서드 존재")
            else:
                print("⚠️ DesktopInterface에 run_async 메서드 없음")
        
        except Exception as e:
            print(f"⚠️ DesktopInterface 테스트 실패: {e}")
        
        print("\n✅ CLI Interface 수정사항 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_game_launcher_integration():
    """GameLauncher 통합 테스트"""
    
    print("\n=== GameLauncher 통합 테스트 ===")
    
    try:
        from main import GameLauncher
        
        launcher = GameLauncher()
        print("✓ GameLauncher 생성됨")
        
        # 설정으로 Mock 클라이언트 사용하도록 강제
        await launcher.initialize(skip_checks=True)
        
        print("✓ GameLauncher 초기화 완료")
        
        # CLI 인터페이스 론칭 시뮬레이션 (실제로는 실행하지 않음)
        from src.ui.cli_interface import CLIInterface
        
        if launcher.game_manager:
            interface = CLIInterface(launcher.game_manager)
            
            # run_async 메서드 존재 확인
            if hasattr(interface, 'run_async'):
                print("✓ 인터페이스에 run_async 메서드 존재")
                print("✓ GameLauncher와 CLI 인터페이스 호환성 확인됨")
                
                # 호출 가능성만 확인 (실제 실행하지 않음)
                import inspect
                if inspect.iscoroutinefunction(interface.run_async):
                    print("✓ await interface.run_async() 호출 가능")
                else:
                    print("❌ run_async가 코루틴이 아님")
                    return False
            else:
                print("❌ run_async 메서드 없음")
                return False
        else:
            print("❌ GameManager 초기화 실패")
            return False
        
        print("✅ GameLauncher 통합 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"\n❌ 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 정리
        if 'launcher' in locals() and launcher.game_manager:
            try:
                await launcher.shutdown()
            except:
                pass

async def main():
    """메인 테스트 함수"""
    
    print("CLI Interface run_async 수정사항 검증을 시작합니다...")
    
    test1 = await test_cli_interface()
    test2 = await test_game_launcher_integration()
    
    print("\n" + "="*60)
    
    if test1 and test2:
        print("🎉 CLI Interface 수정 완료!")
        print("이제 'run_async' 메서드 오류 없이 게임을 실행할 수 있습니다.")
        print("\n실행 방법:")
        print("  python main.py --skip-checks")
        return True
    else:
        print("❌ 수정 확인 실패")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)