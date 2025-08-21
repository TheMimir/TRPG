#!/usr/bin/env python3
"""
Demo script for Cthulhu Solo TRPG CLI Interface

Run this script to test the Rich-based horror-themed CLI interface.
This demonstrates the immersive UI components without requiring
a full game engine integration.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ui.cli_interface import create_cli_interface
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    
    def main():
        """Main demo function."""
        console = Console()
        
        # Show demo info
        demo_text = Text()
        demo_text.append("🎭 CTHULHU SOLO TRPG CLI DEMO 🎭\n\n", style="bold cyan")
        demo_text.append("This is a demonstration of the Rich-based CLI interface\n", style="white")
        demo_text.append("for the Cthulhu Solo Horror TRPG system.\n\n", style="white")
        demo_text.append("Features demonstrated:\n", style="yellow")
        demo_text.append("• Immersive horror-themed UI with Rich library\n", style="dim")
        demo_text.append("• Character creation wizard\n", style="dim")
        demo_text.append("• Atmospheric story presentation\n", style="dim")
        demo_text.append("• Interactive choice menus\n", style="dim")
        demo_text.append("• Dice rolling animations\n", style="dim")
        demo_text.append("• Sanity loss effects\n", style="dim")
        demo_text.append("• Horror-themed visual styling\n\n", style="dim")
        demo_text.append("Note: This is a UI demo. Full AI integration and\n", style="dim")
        demo_text.append("game engine features require additional setup.\n", style="dim")
        
        demo_panel = Panel(
            demo_text,
            title="Demo Information",
            title_style="bold red",
            border_style="cyan"
        )
        
        console.print(demo_panel)
        
        # Ask if user wants to continue
        from rich.prompt import Confirm
        if not Confirm.ask("\nProceed with demo?", default=True):
            console.print("[dim]Demo cancelled.[/dim]")
            return
        
        # Create and run CLI interface
        console.print("\n[yellow]Starting CLI interface...[/yellow]\n")
        
        cli = create_cli_interface()
        cli.run()
        
        console.print("\n[green]Demo completed![/green]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except ImportError as e:
        print(f"\nImport Error: {e}")
        print("\nMake sure you have installed the required dependencies:")
        print("pip install rich")
        print("\nAlso ensure you're running from the correct directory.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("\nPlease check your installation and try again.")
        sys.exit(1)