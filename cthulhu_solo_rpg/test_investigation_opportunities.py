#!/usr/bin/env python3
"""조사기회 표시 기능 테스트"""

import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, '.')

async def test_investigation_opportunities():
    """조사기회 표시 기능 테스트"""
    print("🔍 조사기회 표시 기능 테스트 시작...")
    print("=" * 60)
    
    try:
        from src.core.gameplay_controller import GameplayController, StoryContent, NarrativeContext, TensionLevel
        from src.core.game_manager import GameManager
        
        # Game Manager 초기화
        print("🔧 게임 시스템 초기화 중...")
        game_manager = GameManager()
        
        # Gameplay Controller 초기화
        gameplay_controller = GameplayController(game_manager)
        
        # 테스트용 narrative context 생성
        context = NarrativeContext(
            scene_id="scene_001_entrance",
            turn_number=3,
            story_threads={"main_investigation": {"progress": 2}},
            choice_history=[],
            narrative_flags={"lighthouse_visited": True},
            character_state={"sanity": 80, "hp": 15},
            tension_level=TensionLevel.UNEASY
        )
        
        print(f"📝 테스트 컨텍스트: {context.scene_id}, 턴 {context.turn_number}")
        
        # Story Content 생성 테스트
        print("\n1️⃣ Story Content 생성 테스트...")
        story_content = await gameplay_controller.get_current_story_content(context.character_state)
        
        print(f"✅ Story Content 생성 완료:")
        print(f"   📖 내용: {story_content.text[:100]}...")
        print(f"   🔬 조사기회 개수: {len(story_content.investigation_opportunities)}")
        
        if story_content.investigation_opportunities:
            print("   📋 조사기회 목록:")
            for i, inv in enumerate(story_content.investigation_opportunities, 1):
                print(f"      {i}. {inv}")
        else:
            print("   ❌ 조사기회가 없습니다!")
        
        if story_content.story_threads:
            print(f"   📈 스토리 스레드 개수: {len(story_content.story_threads)}")
            print("   📋 스토리 스레드:")
            for i, thread in enumerate(story_content.story_threads, 1):
                print(f"      {i}. {thread}")
        
        # AI Agent 직접 테스트 (가능한 경우)
        print("\n2️⃣ Story Agent 직접 테스트...")
        if hasattr(game_manager, 'agents') and 'story_agent' in game_manager.agents:
            story_agent = game_manager.agents['story_agent']
            
            agent_input = {
                'action_type': 'scene_generation',
                'scene_id': context.scene_id,
                'turn_number': context.turn_number,
                'tension_level': context.tension_level.value,
                'character_state': context.character_state
            }
            
            try:
                agent_response = await story_agent.process_input(agent_input)
                print(f"✅ Story Agent 응답 받음")
                
                if 'investigations' in agent_response:
                    investigations = agent_response['investigations']
                    print(f"   🔬 Agent 조사기회: {len(investigations)}개")
                    for i, inv in enumerate(investigations, 1):
                        print(f"      {i}. {inv}")
                else:
                    print("   ⚠️ Agent 응답에 조사기회 없음")
                
            except Exception as e:
                print(f"   ❌ Story Agent 테스트 실패: {e}")
        else:
            print("   ⚠️ Story Agent를 사용할 수 없습니다 (fallback 시스템 사용)")
        
        # Fallback 시스템 테스트
        print("\n3️⃣ Fallback 시스템 테스트...")
        fallback_content = gameplay_controller._get_contextual_fallback_content(context)
        
        print(f"✅ Fallback Content 생성 완료:")
        print(f"   📖 내용: {fallback_content.text[:100]}...")
        print(f"   🔬 조사기회 개수: {len(fallback_content.investigation_opportunities)}")
        
        if fallback_content.investigation_opportunities:
            print("   📋 Fallback 조사기회:")
            for i, inv in enumerate(fallback_content.investigation_opportunities, 1):
                print(f"      {i}. {inv}")
        
        if fallback_content.story_threads:
            print(f"   📈 Fallback 스토리 스레드: {len(fallback_content.story_threads)}개")
            for i, thread in enumerate(fallback_content.story_threads, 1):
                print(f"      {i}. {thread}")
        
        # 다른 씬에서도 테스트
        print("\n4️⃣ 다른 씬 테스트...")
        test_scenes = ["scene_002_inside_house", "scene_003_upper_floor"]
        
        for scene_id in test_scenes:
            print(f"\n   🏠 씬 테스트: {scene_id}")
            test_context = NarrativeContext(
                scene_id=scene_id,
                turn_number=5,
                story_threads={},
                choice_history=[],
                narrative_flags={},
                character_state={"sanity": 75, "hp": 15},
                tension_level=TensionLevel.TENSE
            )
            
            test_content = gameplay_controller._get_contextual_fallback_content(test_context)
            print(f"      🔬 조사기회: {len(test_content.investigation_opportunities)}개")
            if test_content.investigation_opportunities:
                for j, inv in enumerate(test_content.investigation_opportunities[:2], 1):
                    print(f"         {j}. {inv}")
        
        print("\n" + "=" * 60)
        print("🎯 테스트 결과 분석:")
        
        # 성공 기준 확인
        success_criteria = []
        
        # 기본 조사기회 생성 확인
        if len(story_content.investigation_opportunities) > 0:
            success_criteria.append("✅ 기본 조사기회 생성")
        else:
            success_criteria.append("❌ 기본 조사기회 생성 실패")
        
        # Fallback 조사기회 생성 확인
        if len(fallback_content.investigation_opportunities) > 0:
            success_criteria.append("✅ Fallback 조사기회 생성")
        else:
            success_criteria.append("❌ Fallback 조사기회 생성 실패")
        
        # 스토리 스레드 생성 확인
        if len(story_content.story_threads) > 0 or len(fallback_content.story_threads) > 0:
            success_criteria.append("✅ 스토리 스레드 생성")
        else:
            success_criteria.append("❌ 스토리 스레드 생성 실패")
        
        # StoryContent 필드 확인
        if hasattr(story_content, 'investigation_opportunities') and hasattr(story_content, 'story_threads'):
            success_criteria.append("✅ StoryContent 구조 올바름")
        else:
            success_criteria.append("❌ StoryContent 구조 문제")
        
        for criterion in success_criteria:
            print(f"   {criterion}")
        
        success_count = sum(1 for c in success_criteria if c.startswith("✅"))
        total_count = len(success_criteria)
        
        if success_count == total_count:
            print(f"\n🎉 모든 테스트 통과! ({success_count}/{total_count})")
            print("   '#조사기회' 항목이 정상적으로 표시될 것입니다!")
            return True
        else:
            print(f"\n⚠️ 일부 테스트 실패 ({success_count}/{total_count})")
            print("   추가 수정이 필요할 수 있습니다.")
            return False
        
    except Exception as e:
        print(f"💥 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_investigation_opportunities())
    if success:
        print("\n✨ 조사기회 표시 기능이 정상적으로 작동합니다!")
    else:
        print("\n🔧 추가 수정이 필요한 부분이 있습니다.")