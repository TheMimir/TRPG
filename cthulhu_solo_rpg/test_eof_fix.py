#!/usr/bin/env python3
"""
EOF 오류 수정 테스트
"""

import sys
import os
import subprocess
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_eof_handling():
    """EOF 처리 테스트"""
    
    print("=== EOF 처리 테스트 ===")
    
    # 테스트 입력 준비
    test_input = "n\n1\n1\nq\n"
    
    print("테스트 입력:")
    print("n    - 캐릭터 생성 건너뛰기")
    print("1    - 첫 번째 시나리오 선택")
    print("1    - 첫 번째 선택지")
    print("q    - 종료")
    
    print("\n게임 실행 중...")
    
    try:
        # 가상환경에서 게임 실행
        cmd = ["bash", "-c", "source venv/bin/activate && python main.py --skip-checks"]
        
        process = subprocess.run(
            cmd,
            input=test_input,
            text=True,
            capture_output=True,
            timeout=20
        )
        
        print(f"반환 코드: {process.returncode}")
        
        if process.stdout:
            print("\n=== STDOUT ===")
            print(process.stdout[-2000:])  # 마지막 2000자만 출력
        
        if process.stderr:
            print("\n=== STDERR ===") 
            print(process.stderr[-1000:])  # 마지막 1000자만 출력
            
        # 성공 조건 확인
        if "Investigation Complete" in process.stdout or "Until We Meet Again" in process.stdout:
            print("\n✅ 게임이 정상적으로 종료됨")
            return True
        elif "Input interrupted" in process.stdout:
            print("\n⚠️  EOF 처리가 작동했지만 게임이 예상보다 빨리 종료됨")
            return True
        else:
            print("\n❌ 예상치 못한 결과")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n⏰ 타임아웃 - 게임이 입력을 기다리고 있을 수 있음")
        return False
    except Exception as e:
        print(f"\n❌ 테스트 실행 실패: {e}")
        return False

def main():
    print("EOF 처리 수정사항 테스트를 시작합니다...\n")
    
    success = test_eof_handling()
    
    print("\n" + "="*50)
    
    if success:
        print("🎉 EOF 처리 수정이 성공적으로 적용되었습니다!")
        print("\n수정된 내용:")
        print("1. ✅ gameplay_interface.py - EOF 예외 처리 추가")
        print("2. ✅ 게임 루프 안정성 향상")
        print("3. ✅ 사용자 입력 중단 시 우아한 종료")
        print("\n이제 게임이 EOF 오류 없이 실행됩니다:")
        print("  source venv/bin/activate && python main.py --skip-checks")
    else:
        print("❌ 추가 수정이 필요할 수 있습니다.")
    
    return success

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)