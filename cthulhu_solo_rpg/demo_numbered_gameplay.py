#!/usr/bin/env python3
"""
Demo: Numbered Investigation Gameplay
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def demo_numbered_gameplay():
    """Demonstrate numbered investigation gameplay"""
    print("🎮 크툴루 솔로 TRPG - 번호 선택 시스템 데모")
    print("=" * 60)
    
    try:
        from core.game_manager import GameManager
        from core.gameplay_controller import GameplayController
        from ui.gameplay_interface import GameplayInterface
        
        # Initialize systems
        print("🔧 게임 시스템 초기화 중...")
        game_manager = GameManager()
        await game_manager.initialize()
        
        # Start game
        default_character = {
            "name": "박민수 박사",
            "occupation": "investigator", 
            "age": 35,
            "stats": {"STR": 10, "CON": 12, "POW": 14, "DEX": 11, "APP": 10, "SIZ": 13, "INT": 16, "EDU": 18},
            "skills": {"도서관 이용": 80, "탐지": 70, "교육": 85}
        }
        
        await game_manager.start_new_game(default_character, "miskatonic_university_library")
        
        # Create interface
        current_scenario = getattr(game_manager, 'current_scenario', None)
        if hasattr(GameplayController.__init__, '__code__') and 'current_scenario' in GameplayController.__init__.__code__.co_varnames:
            gameplay_controller = GameplayController(game_manager.game_engine, game_manager.agent_manager, current_scenario)
        else:
            gameplay_controller = GameplayController(game_manager.game_engine, game_manager.agent_manager)
        
        interface = GameplayInterface(gameplay_controller)
        
        # Get initial story
        interface.current_story_content = await gameplay_controller.get_current_story_content()
        
        print("✅ 게임 시작 완료!")
        print("\n" + "="*80)
        print(f"🏛️ 장면: {interface.current_story_content.scene_id}")
        print(f"😰 긴장도: {interface.current_story_content.tension_level.value}")
        print("-" * 60)
        print(interface.current_story_content.text)
        print("-" * 60)
        
        print("\n🔍 조사 기회:")
        for i, opp in enumerate(interface.current_story_content.investigation_opportunities, 1):
            print(f"  {i}. {opp}")
        
        print(f"\n💡 조사하려는 항목의 번호를 입력하세요 (1-{len(interface.current_story_content.investigation_opportunities)})")
        
        # Simulate choosing option 1
        print("\n" + "="*60)
        print("📝 플레이어가 '1'을 입력한다고 가정...")
        
        # Test the conversion
        converted_action = interface._convert_investigation_number("1")
        print(f"🔄 '{converted_action}'으로 변환됨")
        
        # Process the action
        print("\n⚙️  액션 처리 중...")
        result = await gameplay_controller.process_player_action(converted_action)
        
        print("\n📖 AI가 생성한 스토리:")
        print("-" * 40)
        print(result.story_content.text)
        print("-" * 40)
        
        print(f"\n🏷️  컨텐츠 정보:")
        print(f"   소스: {result.story_content.metadata.get('source', '알 수 없음')}")
        print(f"   에이전트: {result.story_content.metadata.get('agent', '없음')}")
        
        print(f"\n🔬 새로운 조사 기회:")
        for i, inv in enumerate(result.story_content.investigation_opportunities, 1):
            print(f"  {i}. {inv}")
        
        print("\n" + "="*60)
        print("🎉 번호 선택 시스템이 성공적으로 작동합니다!")
        print("   - 번호 입력 시 해당 조사 기회로 자동 변환")
        print("   - AI가 풍부한 스토리 내용 생성")
        print("   - 새로운 조사 기회들도 동적으로 생성")
        
        await game_manager.shutdown()
        return True
        
    except Exception as e:
        print(f"💥 데모 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(demo_numbered_gameplay())
    if success:
        print("\n✨ 번호 선택 시스템 데모 완료!")
    else:
        print("\n💥 데모 실패!")