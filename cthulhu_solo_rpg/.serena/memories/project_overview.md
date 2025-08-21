# Cthulhu Solo TRPG Project Overview

## Project Purpose
A Cthulhu horror TRPG game designed for solo play with an AI Game Master powered by Ollama. The system provides a complete tabletop RPG experience with multi-agent AI handling story, NPCs, environment, rules, and memory management.

## Tech Stack
- **Python 3.11+**: Core language
- **Ollama**: AI model integration (gpt-oss-120b)
- **Pydantic**: Data validation and settings management
- **Click**: CLI framework
- **Rich/Colorama**: Terminal UI enhancements
- **Tkinter**: Desktop GUI (standard library)
- **PyYAML**: Configuration management
- **Pytest**: Testing framework
- **Black/Flake8/MyPy**: Code quality tools

## Current Project Structure
```
cthulhu_solo_rpg/
├── src/
│   ├── core/          # Game engine, character system, dice mechanics
│   ├── agents/        # AI agents (Story, NPC, Environment, Rule, Memory)
│   ├── ai/           # Ollama integration and Ultra-think system
│   ├── ui/           # CLI and desktop interfaces
│   ├── data/         # Content management and save system
│   └── utils/        # Logging, configuration, helpers
├── saves/            # Game save files
├── logs/             # Application logs
├── tests/            # Test suite
├── main.py           # Main entry point
└── requirements.txt  # Dependencies
```

## Development Status
- ✅ Project structure and basic components set up
- 🔄 Core game mechanics need full implementation
- 🔄 AI agent system needs development
- 🔄 Ollama integration partially implemented
- 🔄 User interfaces need completion

## Entry Points
- `python main.py` - Default CLI interface
- `python main.py --debug` - Debug mode
- `python main.py --test` - Run system tests