#!/usr/bin/env python3
"""
한국어 크툴루 TRPG 데모
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.localization import get_localization_manager, t
from src.ui.menu_system import MenuSystem
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

class KoreanGameDemo:
    """한국어 게임 데모 클래스"""
    
    def __init__(self):
        self.console = Console()
        self.localization = get_localization_manager()
        
        # 한국어로 설정
        self.localization.set_language('ko')
        
    def show_welcome(self):
        """환영 메시지 표시"""
        self.console.clear()
        
        # 게임 제목
        title_text = Text()
        title_text.append("🦑 ", style="bold red")
        title_text.append(t("app.title"), style="bold cyan")
        title_text.append(" 🦑", style="bold red")
        
        title_panel = Panel(
            Align.center(title_text),
            title="호러 RPG 시스템",
            border_style="red"
        )
        
        self.console.print(title_panel)
        self.console.print()
        
        # 환영 메시지
        welcome_text = Text()
        welcome_text.append(t("messages.welcome"), style="bold yellow")
        welcome_text.append("\n\n")
        welcome_text.append(t("app.subtitle"), style="dim")
        
        welcome_panel = Panel(
            Align.center(welcome_text),
            border_style="yellow"
        )
        
        self.console.print(welcome_panel)
        self.console.print()
        
        # 러브크래프트 명언
        quote_text = Text()
        quote_text.append(f'"{t("quotes.lovecraft1")}"', style="italic cyan")
        quote_text.append("\n                                        - H.P. Lovecraft", style="dim")
        
        quote_panel = Panel(
            Align.center(quote_text),
            border_style="cyan"
        )
        
        self.console.print(quote_panel)
        
    def show_character_info(self):
        """캐릭터 정보 표시"""
        self.console.print("\n" + "="*60)
        self.console.print(f"[bold cyan]{t('character.creation.title')}[/bold cyan]")
        self.console.print("="*60)
        
        # 캐릭터 속성들
        attributes = [
            ("character.attributes.strength", "근력"),
            ("character.attributes.constitution", "체질"), 
            ("character.attributes.intelligence", "지능"),
            ("character.attributes.dexterity", "민첩성")
        ]
        
        for key, desc in attributes:
            self.console.print(f"• {t(key)}: {desc}")
        
        # 직업들
        self.console.print(f"\n[bold yellow]{t('character.creation.step2')}[/bold yellow]")
        occupations = [
            ("character.occupations.detective", "수사관"),
            ("character.occupations.professor", "교수"),
            ("character.occupations.doctor", "의사"),
            ("character.occupations.journalist", "기자")
        ]
        
        for key, desc in occupations:
            self.console.print(f"• {t(key)}: {desc}")
    
    def show_scenarios(self):
        """시나리오 목록 표시"""
        self.console.print("\n" + "="*60)
        self.console.print(f"[bold green]{t('game.scenario_selection')}[/bold green]")
        self.console.print("="*60)
        
        scenarios = [
            ("scenarios.haunted_house", "유령이 나오는 저택의 미스터리"),
            ("scenarios.missing_professor", "사라진 교수의 행방을 찾아서"),
            ("scenarios.ancient_artifact", "고대 유물에 얽힌 공포"),
            ("scenarios.strange_sounds", "밤에 들리는 기이한 소리의 정체")
        ]
        
        for i, (key, desc) in enumerate(scenarios, 1):
            self.console.print(f"{i}. [bold]{t(key)}[/bold]: {desc}")
    
    def show_ai_responses(self):
        """AI 응답 샘플 표시"""
        self.console.print("\n" + "="*60)
        self.console.print("[bold magenta]AI 에이전트 응답 샘플[/bold magenta]")
        self.console.print("="*60)
        
        from src.ai.mock_ollama_client import MockOllamaClient
        
        mock_client = MockOllamaClient()
        
        # 스토리 에이전트 응답
        story_response = mock_client.generate(
            prompt="고서관에서 무언가를 발견했습니다",
            system_prompt="스토리 에이전트로서 장면을 묘사하세요"
        )
        
        self.console.print("[bold blue]📖 스토리 에이전트:[/bold blue]")
        self.console.print(f"[cyan]{story_response.content}[/cyan]")
        
        # NPC 에이전트 응답  
        npc_response = mock_client.generate(
            prompt="수상한 도서관 사서를 만났습니다",
            system_prompt="NPC 에이전트로서 캐릭터를 묘사하세요"
        )
        
        self.console.print(f"\n[bold yellow]👤 NPC 에이전트:[/bold yellow]")
        self.console.print(f"[yellow]{npc_response.content}[/yellow]")
    
    def show_interface_elements(self):
        """인터페이스 요소들 표시"""
        self.console.print("\n" + "="*60)
        self.console.print("[bold white]게임 인터페이스 요소들[/bold white]")
        self.console.print("="*60)
        
        interface_elements = [
            ("interface.yes", "예"),
            ("interface.no", "아니오"),
            ("interface.continue", "계속"),
            ("interface.back", "뒤로"),
            ("interface.save", "저장"),
            ("interface.load", "불러오기"),
            ("interface.enter_choice", "선택지를 입력하세요"),
            ("interface.press_enter", "계속하려면 엔터를 누르세요")
        ]
        
        for key, desc in interface_elements:
            self.console.print(f"• {t(key)}: {desc}")
    
    def run_demo(self):
        """데모 실행"""
        try:
            self.show_welcome()
            
            self.console.print(f"\n[bold green]✅ {t('messages.success')}![/bold green]")
            self.console.print("한국어 언어 설정이 완벽하게 작동합니다!")
            
            input("\n계속하려면 엔터를 누르세요...")
            
            self.show_character_info()
            input("\n계속하려면 엔터를 누르세요...")
            
            self.show_scenarios()
            input("\n계속하려면 엔터를 누르세요...")
            
            self.show_ai_responses()
            input("\n계속하려면 엔터를 누르세요...")
            
            self.show_interface_elements()
            
            self.console.print(f"\n[bold green]🎉 한국어 데모 완료![/bold green]")
            self.console.print(f"{t('messages.goodbye')}")
            
        except KeyboardInterrupt:
            self.console.print(f"\n\n[yellow]⏹️ 사용자가 중단했습니다[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]❌ 오류: {e}[/red]")

def main():
    """메인 함수"""
    demo = KoreanGameDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()