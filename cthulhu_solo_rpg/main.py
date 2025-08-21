#!/usr/bin/env python3
"""
Cthulhu Solo TRPG - Main Entry Point

A horror tabletop RPG experience powered by AI.
"""

import asyncio
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

async def main():
    """Main entry point for the Cthulhu Solo TRPG system."""
    
    parser = argparse.ArgumentParser(description="Cthulhu Solo TRPG - AI-Powered Horror Gaming")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--test", action="store_true", help="Run system tests")
    parser.add_argument("--scenario", default="miskatonic_university_library", 
                       help="Scenario to load (default: miskatonic_university_library)")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/game.log'),
            logging.StreamHandler()
        ]
    )
    
    if args.test:
        # Run system tests
        print("🧪 Running system tests...")
        import subprocess
        result = subprocess.run([sys.executable, "comprehensive_system_test.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return
    
    try:
        # Import game components
        from core.game_manager import GameManager
        from core.gameplay_controller import GameplayController
        from ui.gameplay_interface import GameplayInterface
        from utils.localization import LocalizationManager
        
        print("🎮 크툴루 솔로 TRPG 시작!")
        print("=" * 50)
        
        # Initialize systems
        game_manager = GameManager()
        await game_manager.initialize()
        
        # Create default character for demo
        default_character = {
            "name": "조사관",
            "age": 30,
            "occupation": "investigator",
            "residence": "Arkham, Massachusetts",
            "characteristics": {
                "strength": 60,
                "constitution": 70,
                "power": 65,
                "dexterity": 55,
                "appearance": 50,
                "size": 60,
                "intelligence": 75,
                "education": 80
            }
        }
        
        # Start new game with Miskatonic Library scenario
        game_started = await game_manager.start_new_game(default_character, args.scenario)
        if not game_started:
            print("❌ 게임 시작에 실패했습니다.")
            return
        
        # Create gameplay controller with scenario
        gameplay_controller = GameplayController(game_manager.game_engine, game_manager.agent_manager, game_manager.current_scenario)
        
        # Start UI
        interface = GameplayInterface(gameplay_controller)
        await interface.start_game_loop()
        
    except KeyboardInterrupt:
        print("\n\n👋 게임을 종료합니다. 안녕히 계세요!")
    except Exception as e:
        print(f"💥 오류가 발생했습니다: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
    finally:
        try:
            await game_manager.shutdown()
        except:
            pass

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 안녕히 계세요!")