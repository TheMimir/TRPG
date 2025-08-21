#!/bin/bash
# 크툴루 호러 TRPG 게임 실행 스크립트

echo "🦑 크툴루 호러 TRPG 시작합니다..."
echo "======================================"

# 가상환경 활성화
source venv/bin/activate

echo "어떤 버전을 실행하시겠습니까?"
echo "1. 완전한 AI 에이전트 게임 (main.py)"
echo "2. 간단한 데모 버전 (simple_game.py)"
echo "3. 시스템 테스트 (simple_test.py)"
echo "4. 한국어 언어 데모 (korean_game_demo.py)"
echo ""

read -p "선택하세요 (1-4): " choice

case $choice in
    1)
        echo "🤖 AI 에이전트 게임을 시작합니다..."
        python main.py
        ;;
    2)
        echo "🎲 간단한 데모 게임을 시작합니다..."
        python simple_game.py
        ;;
    3)
        echo "🔧 시스템 테스트를 실행합니다..."
        python simple_test.py
        ;;
    4)
        echo "🌐 한국어 언어 데모를 실행합니다..."
        python korean_game_demo.py
        ;;
    *)
        echo "잘못된 선택입니다. 데모 게임을 실행합니다..."
        python simple_game.py
        ;;
esac

echo ""
echo "🦑 게임이 종료되었습니다. 플레이해주셔서 감사합니다!"