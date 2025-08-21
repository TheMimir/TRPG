#!/usr/bin/env python3
"""
간소화된 크툴루 호러 TRPG 데모
AI 에이전트 없이 기본 게임 메카닉만 시연
"""

import sys
sys.path.append('src')

import random
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

# 기본 캐릭터 클래스
class SimpleCharacter:
    def __init__(self, name="무명의 조사자", age=25):
        self.name = name
        self.age = age
        
        # 크툴루 TRPG 기본 능력치 (3d6 x 5)
        self.strength = self.roll_stat()
        self.constitution = self.roll_stat()
        self.power = self.roll_stat()
        self.dexterity = self.roll_stat()
        self.appearance = self.roll_stat()
        self.size = self.roll_stat()
        self.intelligence = self.roll_stat()
        self.education = self.roll_stat()
        
        # 파생 능력치
        self.hit_points = (self.constitution + self.size) // 10
        self.magic_points = self.power // 5
        self.sanity = self.power
        self.max_sanity = self.sanity
        
        # 기본 기술
        self.skills = {
            "조사": 25 + random.randint(0, 40),
            "도서관 이용": 20 + random.randint(0, 30),
            "은밀행동": 20 + random.randint(0, 30),
            "설득": 15 + random.randint(0, 35),
            "심리학": 10 + random.randint(0, 20)
        }
    
    def roll_stat(self):
        """3d6 × 5로 능력치 생성"""
        return (random.randint(1,6) + random.randint(1,6) + random.randint(1,6)) * 5

# 주사위 시스템
class SimpleDice:
    @staticmethod
    def roll_d100():
        return random.randint(1, 100)
    
    @staticmethod
    def skill_check(skill_value, roll=None):
        if roll is None:
            roll = SimpleDice.roll_d100()
        
        if roll <= skill_value // 5:
            return "극성공", roll
        elif roll <= skill_value // 2:
            return "어려운 성공", roll
        elif roll <= skill_value:
            return "성공", roll
        elif roll >= 96:
            return "펌블", roll
        else:
            return "실패", roll

def display_title():
    """게임 타이틀 표시"""
    title = Text()
    title.append("🦑 크툴루의 부름 🦑\n", style="bold red")
    title.append("Call of Cthulhu: Solo Adventure\n", style="bold purple")
    title.append("━━━━━━━━━━━━━━━━━━━━━━", style="dim")
    
    console.print(Panel(
        title,
        title="Horror TRPG",
        border_style="red",
        padding=(1, 2)
    ))

def display_character(character):
    """캐릭터 시트 표시"""
    table = Table(title=f"📋 {character.name}의 조사자 기록")
    table.add_column("능력치", style="cyan")
    table.add_column("수치", justify="right", style="yellow")
    table.add_column("기술", style="cyan") 
    table.add_column("수치", justify="right", style="yellow")
    
    abilities = [
        ("근력 (STR)", character.strength),
        ("체력 (CON)", character.constitution),
        ("의지력 (POW)", character.power),
        ("민첩성 (DEX)", character.dexterity),
        ("매력 (APP)", character.appearance),
        ("크기 (SIZ)", character.size),
        ("지능 (INT)", character.intelligence),
        ("교육 (EDU)", character.education)
    ]
    
    skills = list(character.skills.items())
    
    for i, (ability, value) in enumerate(abilities):
        skill_name, skill_value = skills[i] if i < len(skills) else ("", "")
        table.add_row(ability, str(value), skill_name, str(skill_value))
    
    console.print(table)
    console.print(f"[green]💗 체력: {character.hit_points}  🧠 정신력: {character.sanity}/{character.max_sanity}  ✨ 마력: {character.magic_points}[/green]")

def create_character():
    """캐릭터 생성"""
    console.print("\n[bold blue]🎭 새로운 조사자를 만들어보세요[/bold blue]")
    
    name = Prompt.ask("조사자의 이름을 입력하세요", default="무명의 조사자")
    age = int(Prompt.ask("나이를 입력하세요", default="25"))
    
    character = SimpleCharacter(name, age)
    
    console.print(f"\n[green]✅ {name} 조사자가 생성되었습니다![/green]")
    return character

def investigation_scene(character):
    """간단한 조사 시나리오"""
    console.print("\n" + "="*50)
    console.print(Panel(
        "[italic]당신은 어둠에 싸인 낡은 도서관에 홀로 서 있습니다.\n"
        "먼지 냄새와 함께 묘한 썩은 냄새가 코끝을 찌릅니다.\n"
        "벽에 걸린 시계가 자정을 알리며 천천히 울려 퍼집니다...[/italic]",
        title="🌙 미드나잇 도서관",
        border_style="red"
    ))
    
    choices = [
        "1. 금지된 서적 코너로 향한다",
        "2. 사서에게 말을 건다", 
        "3. 조용히 주변을 조사한다",
        "4. 이상한 냄새의 근원을 찾는다"
    ]
    
    for choice in choices:
        console.print(f"   {choice}")
    
    action = Prompt.ask("\n어떻게 하시겠습니까?", choices=["1", "2", "3", "4"])
    
    if action == "1":
        forbidden_books_scene(character)
    elif action == "2":
        librarian_scene(character)
    elif action == "3":
        investigation_check(character, "조사")
    elif action == "4":
        investigation_check(character, "조사")

def forbidden_books_scene(character):
    """금지된 서적 시나리오"""
    console.print("\n[red]📚 금지된 서적 코너[/red]")
    console.print("[italic]어둠 속에서 가죽으로 장정된 고서들이 당신을 바라보는 것 같습니다...[/italic]")
    
    # 정신력 체크
    sanity_loss = random.randint(1, 4)
    character.sanity = max(0, character.sanity - sanity_loss)
    
    console.print(f"[red]😱 정신력 {sanity_loss} 손실! (현재: {character.sanity}/{character.max_sanity})[/red]")
    
    if character.sanity < character.max_sanity // 2:
        console.print("[red]당신은 공포에 떨기 시작합니다...[/red]")

def librarian_scene(character):
    """사서와의 만남"""
    console.print("\n[blue]👤 야간 사서[/blue]")
    console.print("[italic]창백한 얼굴의 사서가 당신을 째려봅니다...[/italic]")
    
    result, roll = SimpleDice.skill_check(character.skills["설득"])
    console.print(f"[yellow]🎲 설득 판정: {roll} ({result})[/yellow]")
    
    if "성공" in result:
        console.print("[green]사서가 수상한 미소를 지으며 비밀 정보를 알려줍니다.[/green]")
    else:
        console.print("[red]사서가 당신을 의심스럽게 바라보며 입을 다뭅니다.[/red]")

def investigation_check(character, skill_name):
    """조사 판정"""
    skill_value = character.skills.get(skill_name, 25)
    result, roll = SimpleDice.skill_check(skill_value)
    
    console.print(f"\n[yellow]🎲 {skill_name} 판정 (목표값: {skill_value})[/yellow]")
    console.print(f"[yellow]주사위 결과: {roll} → {result}[/yellow]")
    
    if "성공" in result:
        clues = [
            "바닥에 이상한 기호가 새겨져 있습니다.",
            "책장 뒤에서 희미한 속삭임이 들립니다.",
            "낡은 일기장을 발견했습니다.",
            "벽에 숨겨진 문을 찾았습니다."
        ]
        clue = random.choice(clues)
        console.print(f"[green]🔍 발견: {clue}[/green]")
    else:
        console.print("[red]특별한 것을 발견하지 못했습니다.[/red]")

def main_game():
    """메인 게임 루프"""
    display_title()
    
    console.print("\n[bold]📖 크툴루 호러 TRPG에 오신 것을 환영합니다![/bold]")
    console.print("[dim]이 게임은 H.P. 러브크래프트의 우주적 공포 세계를 배경으로 합니다.[/dim]")
    
    character = create_character()
    console.print("\n")
    display_character(character)
    
    if Confirm.ask("\n🎮 조사를 시작하시겠습니까?"):
        investigation_scene(character)
        
        while character.sanity > 0 and Confirm.ask("\n계속 조사하시겠습니까?"):
            investigation_scene(character)
    
    # 게임 종료
    console.print("\n" + "="*50)
    if character.sanity <= 0:
        console.print(Panel(
            "[red bold]🌀 당신은 광기에 빠졌습니다...\n"
            "우주의 진실은 인간이 감당하기에는 너무 끔찍했습니다.[/red bold]",
            title="💀 GAME OVER",
            border_style="red"
        ))
    else:
        console.print(Panel(
            f"[green]🎉 조사를 마쳤습니다!\n"
            f"정신력: {character.sanity}/{character.max_sanity}\n"
            f"당신은 무사히 살아남았습니다... 지금까지는.[/green]",
            title="✅ 조사 완료",
            border_style="green"
        ))
    
    console.print("\n[dim]Ph'nglui mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn...[/dim]")
    console.print("🦑 [bold red]크툴루의 부름[/bold red]에서 플레이해주셔서 감사합니다!")

if __name__ == "__main__":
    try:
        main_game()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]게임이 중단되었습니다. 안녕히 가세요...[/yellow]")
    except Exception as e:
        console.print(f"\n[red]오류가 발생했습니다: {e}[/red]")