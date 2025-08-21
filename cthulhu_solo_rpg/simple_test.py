#!/usr/bin/env python3
"""
Simple test to verify the game components are working
"""

import sys
sys.path.append('src')

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def test_imports():
    """Test if all imports work"""
    try:
        console.print("[green]Testing imports...[/green]")
        
        # Test core imports
        from core.character import Character
        from core.dice import DiceRoller
        from core.game_engine import GameEngine
        console.print("✅ Core systems imported successfully")
        
        # Test utils
        from utils.config import Config
        from utils.logger import GameLogger
        console.print("✅ Utilities imported successfully")
        
        # Test UI
        from ui.display_manager import DisplayManager
        console.print("✅ UI components imported successfully")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Import failed: {e}[/red]")
        return False

def test_character_creation():
    """Test character creation"""
    try:
        console.print("[green]Testing character creation...[/green]")
        
        from core.character import Character
        
        # Create a simple character
        character = Character(
            name="테스트 탐정",
            gender="남성",
            age=30
        )
        
        console.print(f"✅ Character created: {character.name}")
        console.print(f"   나이: {character.age}")
        if hasattr(character, 'current_sanity'):
            console.print(f"   정신력: {character.current_sanity}/{character.max_sanity}")
        else:
            console.print("   (정신력 시스템 미완성)")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Character creation failed: {e}[/red]")
        return False

def test_dice_system():
    """Test dice rolling"""
    try:
        console.print("[green]Testing dice system...[/green]")
        
        from core.dice import DiceRoller
        
        dice = DiceRoller()
        
        # Test basic roll
        result = dice.roll_d100()
        console.print(f"✅ D100 roll: {result}")
        
        # Test 3d6 roll
        stat_roll = dice.roll_3d6()
        console.print(f"✅ 3D6 roll: {stat_roll}")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Dice system failed: {e}[/red]")
        return False

def test_basic_ui():
    """Test basic UI components"""
    try:
        console.print("[green]Testing UI display...[/green]")
        
        from ui.display_manager import DisplayManager
        
        display = DisplayManager()
        
        # Test character sheet formatting
        from core.character import Character
        test_char = Character(name="Test", age=25)
        formatted_sheet = display.format_character_sheet(test_char)
        console.print("✅ Character sheet formatted")
        
        console.print("✅ UI display working")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ UI test failed: {e}[/red]")
        return False

def main():
    """Run all tests"""
    console.print(Panel.fit(
        Text("🎲 크툴루 호러 TRPG - 간단 테스트", style="bold purple"),
        title="Call of Cthulhu Solo TRPG",
        border_style="purple"
    ))
    
    tests = [
        ("Import Test", test_imports),
        ("Character Creation", test_character_creation), 
        ("Dice System", test_dice_system),
        ("Basic UI", test_basic_ui)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        console.print(f"\n[bold blue]🔍 {test_name}[/bold blue]")
        if test_func():
            passed += 1
        console.print()
    
    # Summary
    if passed == total:
        console.print(Panel(
            f"[green]🎉 모든 테스트 통과! ({passed}/{total})[/green]\n"
            f"[dim]기본 시스템이 정상 작동합니다.[/dim]",
            title="테스트 결과",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[yellow]⚠️  일부 테스트 실패 ({passed}/{total})[/yellow]\n"
            f"[dim]일부 기능에 문제가 있을 수 있습니다.[/dim]",
            title="테스트 결과", 
            border_style="yellow"
        ))

if __name__ == "__main__":
    main()