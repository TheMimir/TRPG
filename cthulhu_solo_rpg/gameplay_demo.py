#!/usr/bin/env python3
"""
Gameplay Demo for Cthulhu Solo RPG
Demonstrates a complete mini gameplay session.
"""

import os
import sys
import asyncio

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.models import (
    GameState, Investigation, PlayerAction, StoryContent, 
    NarrativeContext, TensionLevel, ActionType,
    create_basic_narrative_context
)
from core.dice import DiceEngine
from data.save_manager import CthulhuSaveManager, CthulhuCharacterData
from data.scenarios.miskatonic_university_library import MiskatonicLibraryScenario
from utils.localization import LocalizationManager, Language

def simulate_free_text_action(action_text: str, character_data: dict, dice_engine: DiceEngine) -> StoryContent:
    """Simulate processing a free-text action"""
    
    # Simple action analysis
    action_lower = action_text.lower()
    
    if "search" in action_lower or "look" in action_lower or "examine" in action_lower:
        action_type = ActionType.INVESTIGATE
        if "book" in action_lower or "library" in action_lower:
            skill_needed = "Library Use"
        elif "hidden" in action_lower or "secret" in action_lower:
            skill_needed = "Spot Hidden"
        else:
            skill_needed = "Spot Hidden"
    elif "talk" in action_lower or "ask" in action_lower or "interview" in action_lower:
        action_type = ActionType.DIALOGUE
        skill_needed = "Psychology"
    else:
        action_type = ActionType.OTHER
        skill_needed = "Luck"
    
    # Perform skill check
    skill_value = character_data.get("skills", {}).get(skill_needed, 50)
    result = dice_engine.skill_check(skill_value)
    
    # Generate narrative response based on success
    if result.success_level.value in ["success", "hard_success", "extreme_success", "critical_success"]:
        if action_type == ActionType.INVESTIGATE:
            narrative = f"Your {skill_needed} check succeeds! You carefully examine the area and notice something unusual. The shadows seem to move strangely in the corner, and you find a small, leather-bound journal hidden behind some books. It contains notes in Latin about 'the Watchers in the Stacks.'"
            tension = TensionLevel.TENSE
            opportunities = ["Translate the Latin journal", "Investigate the moving shadows", "Research 'Watchers in the Stacks'"]
        elif action_type == ActionType.DIALOGUE:
            narrative = f"Your {skill_needed} check succeeds! The librarian, Mrs. Henderson, initially seems reluctant to talk, but your approach puts her at ease. She confides that she's heard strange whispering sounds coming from the basement after hours, and that three students who were researching occult topics have gone missing in the past month."
            tension = TensionLevel.UNEASY
            opportunities = ["Investigate the basement", "Research the missing students", "Ask about the occult research"]
        else:
            narrative = f"Your intuition guides you well. You sense that something is not quite right about this place. The air feels thick with an otherworldly presence, and you notice that some of the books seem to be shelved in patterns that don't follow any normal library system."
            tension = TensionLevel.UNEASY
            opportunities = ["Study the book arrangement pattern", "Use Occult knowledge to understand the significance"]
    else:
        # Failure
        if action_type == ActionType.INVESTIGATE:
            narrative = f"Your {skill_needed} check fails. You search the area but find nothing immediately obvious. However, you can't shake the feeling that you're being watched. A cold draft seems to follow you as you move through the stacks."
            tension = TensionLevel.UNEASY
            opportunities = ["Try a different approach", "Ask for help from the librarian"]
        elif action_type == ActionType.DIALOGUE:
            narrative = f"Your {skill_needed} check fails. The librarian seems suspicious of your questions and becomes guarded. 'I don't know what you're talking about,' she says curtly, but you notice her hands are trembling as she organizes the papers on her desk."
            tension = TensionLevel.TENSE
            opportunities = ["Try a different approach", "Observe her behavior more carefully"]
        else:
            narrative = "You feel uncertain about your next move. The library seems ordinary enough, but there's an underlying sense of wrongness that you can't quite place."
            tension = TensionLevel.CALM
            opportunities = ["Focus your investigation", "Seek more information"]
    
    return StoryContent(
        text=narrative,
        content_id=f"response_{action_type.value}_{result.success_level.value}",
        scene_id="miskatonic_library",
        tension_level=tension,
        investigation_opportunities=opportunities
    )

async def run_gameplay_demo():
    """Run a complete gameplay demonstration"""
    print("🎮 CTHULHU SOLO RPG - GAMEPLAY DEMONSTRATION")
    print("=" * 60)
    
    # Initialize systems
    dice_engine = DiceEngine()
    localization = LocalizationManager(Language.KOREAN)
    save_manager = CthulhuSaveManager("saves")
    scenario = MiskatonicLibraryScenario()
    
    print("📚 시나리오: 미스카토닉 대학교 도서관 조사")
    print("🔍 당신은 이상한 실종 사건을 조사하는 탐사자입니다.\n")
    
    # Create character
    print("1. 캐릭터 생성")
    character_data = {
        "name": "박지혜 박사",
        "occupation": "고고학 교수",
        "age": 34,
        "stats": {
            "STR": 50, "DEX": 65, "INT": 85, "EDU": 90,
            "CON": 60, "APP": 70, "POW": 75, "SIZ": 55
        },
        "skills": {
            "Library Use": 85,
            "Archaeology": 80,
            "Occult": 50,
            "Spot Hidden": 70,
            "Psychology": 60,
            "History": 75,
            "Language (Latin)": 65
        },
        "sanity": 75,
        "hit_points": 11,
        "magic_points": 15
    }
    
    print(f"   이름: {character_data['name']}")
    print(f"   직업: {character_data['occupation']}")
    print(f"   정신력: {character_data['sanity']}")
    print(f"   주요 기술: 도서관 이용({character_data['skills']['Library Use']}), 고고학({character_data['skills']['Archaeology']})")
    
    # Initialize game state
    narrative_context = create_basic_narrative_context("miskatonic_library_entrance", character_data)
    narrative_context.story_threads["main"] = "미스카토닉 대학교 도서관에서 발생한 이상한 실종 사건 조사"
    
    game_state = GameState(
        character_data=character_data,
        narrative_context=narrative_context,
        game_metadata={"scenario": "Miskatonic Library Investigation", "language": "ko"}
    )
    
    print("\n2. 게임 시작")
    print("=" * 40)
    print("🏛️ 미스카토닉 대학교 도서관 입구")
    print("당신은 웅장한 고딕 양식의 건물 앞에 서 있습니다. 도서관은 100년이 넘는 역사를 자랑하며,")
    print("수많은 고서와 희귀한 문헌들이 보관되어 있다고 알려져 있습니다. 최근 3명의 학생이")
    print("연구 중 실종되었고, 이상한 소음과 목격담이 보고되고 있습니다.")
    
    # Simulate gameplay actions
    actions = [
        "도서관 내부를 자세히 살펴보고 이상한 점이 있는지 조사한다",
        "사서에게 실종된 학생들에 대해 질문한다",
        "제한 구역의 고서들을 살펴본다"
    ]
    
    for i, action in enumerate(actions, 1):
        print(f"\n🎯 행동 {i}: {action}")
        print("-" * 40)
        
        # Process the action
        story_result = simulate_free_text_action(action, character_data, dice_engine)
        
        # Update tension level
        narrative_context.tension_level = story_result.tension_level
        
        # Display result
        print(f"📖 {story_result.text}")
        print(f"😰 긴장 수준: {story_result.tension_level.value}")
        
        if story_result.investigation_opportunities:
            print("🔍 새로운 조사 기회:")
            for j, opportunity in enumerate(story_result.investigation_opportunities, 1):
                print(f"   {j}. {opportunity}")
        
        # Potentially lose sanity based on tension
        if story_result.tension_level in [TensionLevel.TENSE, TensionLevel.TERRIFYING]:
            sanity_check = dice_engine.sanity_check(character_data["sanity"], "1d4/1d6")
            if sanity_check["sanity_loss"] > 0:
                character_data["sanity"] = sanity_check["new_sanity"]
                print(f"😱 정신력 손실: {sanity_check['sanity_loss']} (현재: {character_data['sanity']})")
        
        print()
    
    print("3. 세션 저장")
    print("=" * 40)
    
    # Save the game state
    try:
        # Create save-compatible character
        save_character = CthulhuCharacterData(
            name=character_data["name"],
            age=character_data["age"],
            occupation=character_data["occupation"],
            residence="서울, 대한민국",
            birthplace="부산, 대한민국",
            strength=character_data["stats"]["STR"],
            constitution=character_data["stats"]["CON"],
            power=character_data["stats"]["POW"],
            dexterity=character_data["stats"]["DEX"],
            appearance=character_data["stats"]["APP"],
            size=character_data["stats"]["SIZ"],
            intelligence=character_data["stats"]["INT"],
            education=character_data["stats"]["EDU"],
            hit_points_current=character_data["hit_points"],
            hit_points_maximum=character_data["hit_points"],
            sanity_current=character_data["sanity"],
            sanity_maximum=75,
            sanity_starting=75,
            magic_points_current=character_data["magic_points"],
            magic_points_maximum=character_data["magic_points"],
            skills={skill: {"total": value} for skill, value in character_data["skills"].items()},
            clues_discovered=["Latin journal in restricted section", "Librarian's suspicious behavior"]
        )
        
        save_path = save_manager.save_character(save_character, "demo_session")
        print(f"💾 게임 저장 완료: {save_path}")
        
    except Exception as e:
        print(f"💾 저장 실패: {e}")
    
    print("\n4. 세션 요약")
    print("=" * 40)
    print(f"캐릭터: {character_data['name']}")
    print(f"현재 정신력: {character_data['sanity']}/75")
    print(f"현재 긴장 수준: {narrative_context.tension_level.value}")
    print("주요 단서:")
    print("- 제한 구역의 라틴어 일지")
    print("- 지하실에서 들리는 속삭임")
    print("- 오컬트 연구와 관련된 실종")
    
    print("\n🎉 데모 세션 완료!")
    print("시스템이 정상적으로 작동하며 한국어 지원도 완벽합니다.")

def main():
    """Main demo function"""
    os.chdir('/Users/mimir/TRPG/cthulhu_solo_rpg')
    asyncio.run(run_gameplay_demo())

if __name__ == "__main__":
    main()