"""
Gameplay Interface for Cthulhu Solo TRPG System

Core gameplay interface supporting:
- Free-text input processing (no numbered menus)
- Rich terminal display with panels
- Real-time status updates
- Investigation opportunities display
- Korean language support
- Session management and commands
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import re
import json

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.columns import Columns
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.prompt import Prompt
    from rich.markup import escape
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = object
    Panel = object
    Text = object
    Columns = object
    Table = object
    Layout = object
    Live = object
    Prompt = object

from core.models import StoryContent, TensionLevel
from core.gameplay_controller import GameplayController, TurnResult


logger = logging.getLogger(__name__)


class InterfaceMode(Enum):
    """Interface display modes"""
    STORY = "story"          # Main story display
    CHARACTER = "character"  # Character sheet focus
    INVESTIGATION = "investigation"  # Investigation focus
    HELP = "help"           # Help and commands
    SETTINGS = "settings"   # Settings and configuration


@dataclass
class InterfaceConfig:
    """Configuration for the gameplay interface"""
    use_rich: bool = RICH_AVAILABLE
    max_story_lines: int = 50
    max_history_lines: int = 20
    auto_scroll: bool = True
    show_dice_rolls: bool = True
    show_typing_animation: bool = True
    input_timeout: float = 300.0  # 5 minutes
    enable_shortcuts: bool = True
    
    # Display styling
    story_width: int = 70
    sidebar_width: int = 30
    panel_padding: int = 1
    
    # Language settings
    language: str = "ko"  # "ko" for Korean, "en" for English


class GameplayInterface:
    """
    Main gameplay interface for the Cthulhu Solo TRPG system.
    
    Provides a rich, interactive interface with free-text input,
    real-time updates, and comprehensive game information display.
    """
    
    def __init__(self, gameplay_controller: GameplayController, 
                 config: Optional[InterfaceConfig] = None):
        """
        Initialize the gameplay interface.
        
        Args:
            gameplay_controller: Controller for game logic
            config: Interface configuration
        """
        self.controller = gameplay_controller
        self.config = config or InterfaceConfig()
        
        # Interface state
        self.current_mode = InterfaceMode.STORY
        self.is_running = False
        self.current_story_content: Optional[StoryContent] = None
        self.input_history: List[str] = []
        self.display_history: List[str] = []
        
        # Rich console setup
        if self.config.use_rich and RICH_AVAILABLE:
            self.console = Console(width=120, force_terminal=True)
            self.live = None
        else:
            self.console = None
            logger.warning("Rich library not available - using basic text interface")
        
        # Command system
        self.commands = self._initialize_commands()
        
        # Interface text (for localization)
        self.text = self._initialize_interface_text()
        
        logger.info("GameplayInterface initialized")
    
    def _initialize_commands(self) -> Dict[str, Callable]:
        """Initialize command system for special inputs"""
        return {
            "/help": self._command_help,
            "/character": self._command_character,
            "/inventory": self._command_inventory,
            "/save": self._command_save,
            "/load": self._command_load,
            "/quit": self._command_quit,
            "/settings": self._command_settings,
            "/history": self._command_history,
            "/clear": self._command_clear,
            "/stats": self._command_stats,
            # Korean aliases
            "/도움말": self._command_help,
            "/캐릭터": self._command_character,
            "/저장": self._command_save,
            "/불러오기": self._command_load,
            "/종료": self._command_quit,
        }
    
    def _initialize_interface_text(self) -> Dict[str, str]:
        """Initialize interface text for localization"""
        if self.config.language == "ko":
            return {
                "welcome": "크툴루 솔로 TRPG에 오신 것을 환영합니다!",
                "input_prompt": "조사 번호나 행동을 입력하세요",
                "processing": "처리 중...",
                "error": "오류가 발생했습니다",
                "turn_completed": "턴 완료",
                "character_sheet": "캐릭터 시트",
                "investigation_opportunities": "조사 기회",
                "story_threads": "스토리 진행 상황",
                "game_status": "게임 상태",
                "commands_available": "사용 가능한 명령어",
                "type_action": "조사 기회 번호(1, 2, 3...)를 입력하거나 자유롭게 행동을 입력하세요",
                "dice_roll": "주사위 굴림",
                "investigation_result": "조사 결과",
                "tension_level": "긴장도",
                "turn_number": "턴 번호",
            }
        else:  # English
            return {
                "welcome": "Welcome to Cthulhu Solo TRPG!",
                "input_prompt": "Enter your action",
                "processing": "Processing...",
                "error": "An error occurred",
                "turn_completed": "Turn completed",
                "character_sheet": "Character Sheet",
                "investigation_opportunities": "Investigation Opportunities",
                "story_threads": "Story Progress",
                "game_status": "Game Status",
                "commands_available": "Available Commands",
                "type_action": "Enter your action freely (e.g., 'examine the door', 'go upstairs')",
                "dice_roll": "Dice Roll",
                "investigation_result": "Investigation Result",
                "tension_level": "Tension Level",
                "turn_number": "Turn Number",
            }
    
    async def start_game_loop(self):
        """Start the main game loop"""
        self.is_running = True
        
        # Display welcome message
        self._display_welcome()
        
        # Get initial story content
        self.current_story_content = await self.controller.get_current_story_content()
        
        if self.config.use_rich and RICH_AVAILABLE:
            await self._start_rich_game_loop()
        else:
            await self._start_basic_game_loop()
    
    async def _start_rich_game_loop(self):
        """Start game loop with Rich interface"""
        try:
            while self.is_running:
                # Create layout
                layout = self._create_rich_layout()
                
                # Display current state
                self.console.clear()
                self.console.print(layout)
                
                # Get user input
                user_input = await self._get_user_input()
                
                if user_input is None:  # Timeout or quit
                    break
                
                # Process input
                await self._process_user_input(user_input)
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]게임이 중단되었습니다.[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]인터페이스 오류: {e}[/red]")
            logger.error(f"Interface error: {e}")
        finally:
            self.is_running = False
    
    async def _start_basic_game_loop(self):
        """Start game loop with basic text interface"""
        try:
            while self.is_running:
                # Display current state
                self._display_basic_interface()
                
                # Get user input
                user_input = await self._get_user_input_basic()
                
                if user_input is None:
                    break
                
                # Process input
                await self._process_user_input(user_input)
                
        except KeyboardInterrupt:
            print("\n게임이 중단되었습니다.")
        except Exception as e:
            print(f"\n인터페이스 오류: {e}")
            logger.error(f"Interface error: {e}")
        finally:
            self.is_running = False
    
    def _create_rich_layout(self) -> Layout:
        """Create Rich layout for the interface"""
        # Create main layout
        layout = Layout()
        
        # Split into header, body, footer
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Split body into main content and sidebar
        layout["body"].split_row(
            Layout(name="main", ratio=7),
            Layout(name="sidebar", ratio=3)
        )
        
        # Header
        layout["header"].update(self._create_header_panel())
        
        # Main content
        layout["main"].update(self._create_story_panel())
        
        # Sidebar
        layout["sidebar"].split_column(
            Layout(name="character", ratio=4),
            Layout(name="investigations", ratio=3),
            Layout(name="status", ratio=3)
        )
        
        layout["sidebar"]["character"].update(self._create_character_panel())
        layout["sidebar"]["investigations"].update(self._create_investigations_panel())
        layout["sidebar"]["status"].update(self._create_status_panel())
        
        # Footer
        layout["footer"].update(self._create_input_panel())
        
        return layout
    
    def _create_header_panel(self) -> Panel:
        """Create header panel"""
        title = f"🐙 {self.text['welcome']} 🐙"
        
        if self.current_story_content:
            scene_info = f"장면: {self.current_story_content.scene_id} | 턴: {self.controller.game_engine.turn_number}"
            tension_info = f"긴장도: {self.current_story_content.tension_level.value}"
            header_text = f"{title}\n{scene_info} | {tension_info}"
        else:
            header_text = title
        
        return Panel(
            Text(header_text, justify="center"),
            style="bold green",
            title="Cthulhu Solo TRPG"
        )
    
    def _create_story_panel(self) -> Panel:
        """Create main story content panel"""
        if not self.current_story_content:
            content = Text("게임을 시작합니다...", style="italic")
        else:
            content = Text()
            content.append(self.current_story_content.text, style="white")
            
            # Add recent history
            if self.display_history:
                content.append("\n\n--- 최근 행동 ---\n", style="dim")
                for action in self.display_history[-3:]:
                    content.append(f"• {action}\n", style="dim")
        
        return Panel(
            content,
            title=f"📖 {self.text['story_threads']}",
            border_style="blue",
            padding=(1, 2)
        )
    
    def _create_character_panel(self) -> Panel:
        """Create character information panel"""
        if not self.controller.game_engine.character:
            content = Text("캐릭터가 로드되지 않았습니다.", style="red")
        else:
            char = self.controller.game_engine.character
            
            content = Text()
            content.append(f"이름: {char.name}\n", style="bold")
            content.append(f"직업: {char.occupation}\n")
            content.append(f"HP: {char.current_hp}/{char.hit_points}\n", 
                         style="green" if char.current_hp > char.hit_points * 0.7 else "yellow" if char.current_hp > char.hit_points * 0.3 else "red")
            content.append(f"정신력: {char.current_sanity}/{char.sanity_points}\n",
                         style="green" if char.current_sanity > char.sanity_points * 0.7 else "yellow" if char.current_sanity > char.sanity_points * 0.3 else "red")
            content.append(f"행운: {char.current_luck}/{char.luck_points}\n")
            
            if char.conditions:
                content.append("\n상태이상:\n", style="yellow")
                for condition in char.conditions:
                    content.append(f"• {condition.value}\n", style="red")
        
        return Panel(
            content,
            title=f"👤 {self.text['character_sheet']}",
            border_style="green"
        )
    
    def _create_investigations_panel(self) -> Panel:
        """Create investigation opportunities panel"""
        if not self.current_story_content or not self.current_story_content.investigation_opportunities:
            content = Text("현재 조사 가능한 항목이 없습니다.", style="dim")
        else:
            content = Text()
            for i, opportunity in enumerate(self.current_story_content.investigation_opportunities, 1):
                content.append(f"{i}. {opportunity}\n", style="cyan")
        
        return Panel(
            content,
            title=f"🔍 {self.text['investigation_opportunities']}",
            border_style="cyan"
        )
    
    def _create_status_panel(self) -> Panel:
        """Create game status panel"""
        content = Text()
        
        # Game information
        content.append(f"턴: {self.controller.game_engine.turn_number}\n")
        content.append(f"장면: {self.controller.game_engine.current_scene}\n")
        
        if self.current_story_content:
            content.append(f"긴장도: {self.current_story_content.tension_level.value}\n")
        
        # Performance info
        stats = self.controller.get_controller_statistics()
        content.append(f"\n처리된 턴: {stats['total_turns_processed']}\n", style="dim")
        content.append(f"평균 처리 시간: {stats['average_turn_time']:.2f}s\n", style="dim")
        
        return Panel(
            content,
            title=f"📊 {self.text['game_status']}",
            border_style="yellow"
        )
    
    def _create_input_panel(self) -> Panel:
        """Create input instruction panel"""
        content = Text()
        content.append(self.text['type_action'], style="italic")
        content.append("\n명령어: /help (도움말), /character (캐릭터), /save (저장), /quit (종료)", style="dim")
        
        return Panel(
            content,
            title="💭 입력 가이드",
            border_style="magenta"
        )
    
    def _display_basic_interface(self):
        """Display basic text interface without Rich"""
        print("\n" + "="*80)
        print(f"크툴루 솔로 TRPG | 턴: {self.controller.game_engine.turn_number}")
        print("="*80)
        
        if self.current_story_content:
            print(f"\n장면: {self.current_story_content.scene_id}")
            print(f"긴장도: {self.current_story_content.tension_level.value}")
            print("\n" + "-"*60)
            print(self.current_story_content.text)
            print("-"*60)
            
            if self.current_story_content.investigation_opportunities:
                print("\n조사 기회:")
                for i, opp in enumerate(self.current_story_content.investigation_opportunities, 1):
                    print(f"  {i}. {opp}")
                print(f"\n💡 조사하려는 항목의 번호를 입력하세요 (1-{len(self.current_story_content.investigation_opportunities)})")
        
        if self.controller.game_engine.character:
            char = self.controller.game_engine.character
            print(f"\n캐릭터: {char.name} ({char.occupation})")
            print(f"HP: {char.current_hp}/{char.hit_points} | 정신력: {char.current_sanity}/{char.sanity_points}")
    
    async def _get_user_input(self) -> Optional[str]:
        """Get user input with Rich interface"""
        if not RICH_AVAILABLE:
            return await self._get_user_input_basic()
        
        try:
            # Use Rich prompt
            user_input = Prompt.ask(
                f"\n[bold green]{self.text['input_prompt']}[/bold green]",
                console=self.console,
                default=""
            )
            
            # Store in history
            if user_input.strip():
                self.input_history.append(user_input)
                if len(self.input_history) > 50:
                    self.input_history = self.input_history[-50:]
            
            return user_input.strip()
            
        except (EOFError, KeyboardInterrupt):
            return None
    
    async def _get_user_input_basic(self) -> Optional[str]:
        """Get user input with basic text interface"""
        try:
            user_input = input(f"\n{self.text['input_prompt']}: ").strip()
            
            if user_input:
                self.input_history.append(user_input)
                if len(self.input_history) > 50:
                    self.input_history = self.input_history[-50:]
            
            return user_input
            
        except (EOFError, KeyboardInterrupt):
            return None
    
    async def _process_user_input(self, user_input: str):
        """Process user input and update game state"""
        if not user_input:
            return
        
        # Check for commands
        if user_input.startswith('/'):
            await self._handle_command(user_input)
            return
        
        # Convert investigation number to action text
        processed_input = self._convert_investigation_number(user_input)
        
        # Validate input
        if not self._validate_input(processed_input):
            self._display_error("입력이 올바르지 않습니다. 다시 시도해주세요.")
            return
        
        # Show processing indicator
        if self.config.use_rich and RICH_AVAILABLE:
            with self.console.status(f"[bold green]{self.text['processing']}[/bold green]"):
                turn_result = await self.controller.process_player_action(processed_input)
        else:
            print(f"\n{self.text['processing']}")
            turn_result = await self.controller.process_player_action(processed_input)
        
        # Update interface with results
        await self._update_interface_with_turn_result(turn_result)
    
    def _convert_investigation_number(self, user_input: str) -> str:
        """Convert investigation number to full action text"""
        if not user_input.strip():
            return user_input
        
        # Check if input is just a number
        try:
            choice_num = int(user_input.strip())
            
            # Check if we have current investigation opportunities
            if (self.current_story_content and 
                self.current_story_content.investigation_opportunities and
                1 <= choice_num <= len(self.current_story_content.investigation_opportunities)):
                
                # Convert number to the full investigation text
                selected_investigation = self.current_story_content.investigation_opportunities[choice_num - 1]
                print(f"🔍 선택한 조사: {selected_investigation}")
                return selected_investigation
            else:
                # Invalid number, inform user
                max_num = len(self.current_story_content.investigation_opportunities) if (
                    self.current_story_content and self.current_story_content.investigation_opportunities
                ) else 0
                if max_num > 0:
                    print(f"❌ 올바른 번호를 입력하세요 (1-{max_num})")
                else:
                    print("❌ 현재 조사 기회가 없습니다.")
                return ""
        except ValueError:
            # Not a number, treat as regular text action
            return user_input
    
    def _validate_input(self, user_input: str) -> bool:
        """Validate user input"""
        # Basic validation
        if len(user_input.strip()) == 0:
            return False
        
        if len(user_input) > 500:  # Too long
            return False
        
        # Check for potentially harmful input
        dangerous_patterns = [
            r'__.*__',  # Python magic methods
            r'eval\s*\(',  # eval function
            r'exec\s*\(',  # exec function
            r'import\s+',  # import statements
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return False
        
        return True
    
    async def _update_interface_with_turn_result(self, turn_result: TurnResult):
        """Update interface with turn processing results"""
        if not turn_result.success:
            self._display_error(f"턴 처리 실패: {turn_result.error_message}")
            return
        
        # Update current story content
        self.current_story_content = turn_result.story_content
        
        # Add to display history
        action_summary = f"{turn_result.player_action} → {turn_result.story_content.text[:100]}..."
        self.display_history.append(action_summary)
        if len(self.display_history) > self.config.max_history_lines:
            self.display_history = self.display_history[-self.config.max_history_lines:]
        
        # Display dice rolls if any
        if turn_result.dice_rolls and self.config.show_dice_rolls:
            await self._display_dice_rolls(turn_result.dice_rolls)
        
        # Display investigation results
        if turn_result.investigation_results:
            await self._display_investigation_results(turn_result.investigation_results)
        
        # Show completion message
        if self.config.use_rich and RICH_AVAILABLE:
            self.console.print(f"\n[green]✓ {self.text['turn_completed']} (처리 시간: {turn_result.processing_time:.2f}초)[/green]")
        else:
            print(f"\n✓ {self.text['turn_completed']} (처리 시간: {turn_result.processing_time:.2f}초)")
    
    async def _display_dice_rolls(self, dice_rolls: List[Dict[str, Any]]):
        """Display dice roll results"""
        if not dice_rolls:
            return
        
        if self.config.use_rich and RICH_AVAILABLE:
            table = Table(title=f"🎲 {self.text['dice_roll']}")
            table.add_column("기능", style="cyan")
            table.add_column("굴림", style="white")
            table.add_column("목표", style="yellow")
            table.add_column("결과", style="green")
            
            for roll in dice_rolls:
                skill = roll.get("skill", "알 수 없음")
                roll_value = str(roll.get("roll", "?"))
                target = str(roll.get("target", "?"))
                success = "성공" if roll.get("success", False) else "실패"
                success_style = "green" if roll.get("success", False) else "red"
                
                table.add_row(skill, roll_value, target, f"[{success_style}]{success}[/{success_style}]")
            
            self.console.print(table)
        else:
            print(f"\n🎲 {self.text['dice_roll']}:")
            for roll in dice_rolls:
                skill = roll.get("skill", "알 수 없음")
                roll_value = roll.get("roll", "?")
                target = roll.get("target", "?")
                success = "성공" if roll.get("success", False) else "실패"
                print(f"  {skill}: {roll_value} vs {target} - {success}")
    
    async def _display_investigation_results(self, investigation_results: List[Dict[str, Any]]):
        """Display investigation results"""
        if not investigation_results:
            return
        
        if self.config.use_rich and RICH_AVAILABLE:
            for result in investigation_results:
                if result.get("success", False):
                    discoveries = result.get("discoveries", [])
                    if discoveries:
                        panel_content = Text()
                        for discovery in discoveries:
                            panel_content.append(f"• {discovery}\n", style="green")
                        
                        panel = Panel(
                            panel_content,
                            title=f"🔍 {self.text['investigation_result']}",
                            border_style="green"
                        )
                        self.console.print(panel)
        else:
            print(f"\n🔍 {self.text['investigation_result']}:")
            for result in investigation_results:
                if result.get("success", False):
                    discoveries = result.get("discoveries", [])
                    for discovery in discoveries:
                        print(f"  • {discovery}")
    
    def _display_error(self, error_message: str):
        """Display error message"""
        if self.config.use_rich and RICH_AVAILABLE:
            self.console.print(f"[red]❌ {error_message}[/red]")
        else:
            print(f"❌ {error_message}")
    
    def _display_welcome(self):
        """Display welcome message"""
        if self.config.use_rich and RICH_AVAILABLE:
            welcome_panel = Panel(
                Text(self.text['welcome'], justify="center", style="bold green"),
                title="🐙 Cthulhu Solo TRPG 🐙",
                border_style="green"
            )
            self.console.print(welcome_panel)
        else:
            print(f"\n🐙 {self.text['welcome']} 🐙")
            print("="*60)
    
    # Command handlers
    async def _handle_command(self, command: str):
        """Handle special commands"""
        parts = command.split()
        base_command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if base_command in self.commands:
            await self.commands[base_command](args)
        else:
            self._display_error(f"알 수 없는 명령어: {command}")
    
    async def _command_help(self, args: List[str]):
        """Show help information"""
        help_text = """
사용 가능한 명령어:
• /help, /도움말 - 이 도움말 표시
• /character, /캐릭터 - 캐릭터 정보 상세 보기
• /inventory - 인벤토리 보기
• /save, /저장 [이름] - 게임 저장
• /load, /불러오기 [파일] - 게임 불러오기
• /stats - 게임 통계 보기
• /history - 행동 기록 보기
• /clear - 화면 지우기
• /quit, /종료 - 게임 종료

자유 입력 예시:
• "문을 조사한다"
• "2층으로 올라간다"
• "NPC와 대화한다"
• "상자를 열어본다"
"""
        
        if self.config.use_rich and RICH_AVAILABLE:
            panel = Panel(Text(help_text), title="📚 도움말", border_style="blue")
            self.console.print(panel)
        else:
            print(help_text)
    
    async def _command_character(self, args: List[str]):
        """Show detailed character information"""
        if not self.controller.game_engine.character:
            self._display_error("캐릭터가 로드되지 않았습니다.")
            return
        
        char = self.controller.game_engine.character
        
        if self.config.use_rich and RICH_AVAILABLE:
            table = Table(title=f"👤 {char.name} - 상세 정보")
            table.add_column("항목", style="cyan")
            table.add_column("값", style="white")
            
            table.add_row("이름", char.name)
            table.add_row("직업", char.occupation)
            table.add_row("나이", str(char.age))
            table.add_row("거주지", char.residence or "알 수 없음")
            
            table.add_row("", "")  # Separator
            
            table.add_row("체력", f"{char.current_hp}/{char.hit_points}")
            table.add_row("정신력", f"{char.current_sanity}/{char.sanity_points}")
            table.add_row("마법력", f"{char.current_mp}/{char.magic_points}")
            table.add_row("행운", f"{char.current_luck}/{char.luck_points}")
            
            self.console.print(table)
            
            # Show top skills
            if char.skills:
                skills_table = Table(title="주요 기능")
                skills_table.add_column("기능", style="cyan")
                skills_table.add_column("수치", style="white")
                
                # Sort skills by value and show top 10
                sorted_skills = sorted(char.skills.items(), key=lambda x: x[1], reverse=True)
                for skill, value in sorted_skills[:10]:
                    skills_table.add_row(skill, str(value))
                
                self.console.print(skills_table)
        else:
            print(f"\n👤 {char.name} - 상세 정보")
            print(f"직업: {char.occupation}, 나이: {char.age}")
            print(f"체력: {char.current_hp}/{char.hit_points}")
            print(f"정신력: {char.current_sanity}/{char.sanity_points}")
            print(f"행운: {char.current_luck}/{char.luck_points}")
    
    async def _command_inventory(self, args: List[str]):
        """Show character inventory"""
        if not self.controller.game_engine.character:
            self._display_error("캐릭터가 로드되지 않았습니다.")
            return
        
        char = self.controller.game_engine.character
        
        if not char.equipment:
            self._display_error("인벤토리가 비어있습니다.")
            return
        
        if self.config.use_rich and RICH_AVAILABLE:
            table = Table(title="🎒 인벤토리")
            table.add_column("아이템", style="cyan")
            
            for item in char.equipment:
                table.add_row(item)
            
            self.console.print(table)
        else:
            print("\n🎒 인벤토리:")
            for item in char.equipment:
                print(f"  • {item}")
    
    async def _command_save(self, args: List[str]):
        """Save the game"""
        save_name = args[0] if args else f"manual_save_{int(time.time())}"
        
        # This would integrate with the GameManager's save system
        self._display_error("저장 기능은 구현 중입니다.")
    
    async def _command_load(self, args: List[str]):
        """Load a saved game"""
        self._display_error("불러오기 기능은 구현 중입니다.")
    
    async def _command_stats(self, args: List[str]):
        """Show game statistics"""
        stats = self.controller.get_controller_statistics()
        
        if self.config.use_rich and RICH_AVAILABLE:
            table = Table(title="📊 게임 통계")
            table.add_column("항목", style="cyan")
            table.add_column("값", style="white")
            
            table.add_row("처리된 턴", str(stats['total_turns_processed']))
            table.add_row("평균 처리 시간", f"{stats['average_turn_time']:.2f}초")
            table.add_row("오류 발생 횟수", str(stats['error_count']))
            table.add_row("현재 장면", stats['current_scene'])
            table.add_row("활성 조사", str(stats['active_investigations']))
            
            self.console.print(table)
        else:
            print("\n📊 게임 통계:")
            print(f"  처리된 턴: {stats['total_turns_processed']}")
            print(f"  평균 처리 시간: {stats['average_turn_time']:.2f}초")
            print(f"  현재 장면: {stats['current_scene']}")
    
    async def _command_history(self, args: List[str]):
        """Show action history"""
        if not self.input_history:
            self._display_error("행동 기록이 없습니다.")
            return
        
        if self.config.use_rich and RICH_AVAILABLE:
            table = Table(title="📜 행동 기록")
            table.add_column("#", style="dim")
            table.add_column("행동", style="white")
            
            recent_history = self.input_history[-10:]  # Last 10 actions
            for i, action in enumerate(recent_history, 1):
                table.add_row(str(i), action)
            
            self.console.print(table)
        else:
            print("\n📜 최근 행동 기록:")
            for i, action in enumerate(self.input_history[-10:], 1):
                print(f"  {i}. {action}")
    
    async def _command_clear(self, args: List[str]):
        """Clear the screen"""
        if self.config.use_rich and RICH_AVAILABLE:
            self.console.clear()
        else:
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
    
    async def _command_settings(self, args: List[str]):
        """Show settings"""
        self._display_error("설정 기능은 구현 중입니다.")
    
    async def _command_quit(self, args: List[str]):
        """Quit the game"""
        if self.config.use_rich and RICH_AVAILABLE:
            self.console.print("[yellow]게임을 종료합니다...[/yellow]")
        else:
            print("게임을 종료합니다...")
        
        self.is_running = False
    
    def get_interface_statistics(self) -> Dict[str, Any]:
        """Get interface usage statistics"""
        return {
            "current_mode": self.current_mode.value,
            "is_running": self.is_running,
            "input_history_size": len(self.input_history),
            "display_history_size": len(self.display_history),
            "rich_available": RICH_AVAILABLE,
            "use_rich": self.config.use_rich,
            "language": self.config.language
        }