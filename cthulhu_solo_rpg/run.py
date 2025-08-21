#!/usr/bin/env python3
"""
Convenience script to run Cthulhu Solo TRPG

This script provides easy shortcuts for common operations.
"""

import sys
import os
import subprocess

def run_game(interface='cli', debug=False):
    """Run the game with specified options."""
    cmd = [sys.executable, 'main.py', '--interface', interface]
    if debug:
        cmd.append('--debug')
    
    subprocess.run(cmd)

def run_tests():
    """Run the test suite."""
    subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'])

def install_requirements():
    """Install required packages."""
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def main():
    """Main entry point for convenience script."""
    if len(sys.argv) < 2:
        print("Usage: python run.py [command]")
        print("Commands:")
        print("  game [cli|desktop] [--debug] - Run the game")
        print("  test                         - Run tests")
        print("  install                      - Install requirements")
        print("  setup                        - Setup for first run")
        return
    
    command = sys.argv[1]
    
    if command == 'game':
        interface = sys.argv[2] if len(sys.argv) > 2 else 'cli'
        debug = '--debug' in sys.argv
        run_game(interface, debug)
    
    elif command == 'test':
        run_tests()
    
    elif command == 'install':
        install_requirements()
    
    elif command == 'setup':
        print("Setting up Cthulhu Solo TRPG...")
        install_requirements()
        
        # Create config file if it doesn't exist
        if not os.path.exists('config.json'):
            import shutil
            shutil.copy('config.example.json', 'config.json')
            print("Created config.json from example")
        
        print("Setup complete! Run 'python run.py game' to start playing.")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()