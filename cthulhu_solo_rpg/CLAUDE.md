# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cthulhu Solo TRPG is a Lovecraftian horror tabletop RPG system designed for solo play with an AI Game Master powered by Ollama. The game features a sophisticated multi-agent AI system that manages different aspects of the horror gaming experience, from narrative generation to character interactions.

## Architecture

The system follows a modular, agent-based architecture:

### Core Systems
- **GameManager** (`src/core/game_manager.py`): Central orchestrator that coordinates all systems and manages game state
- **GameEngine** (`src/core/game_engine.py`): Handles core game mechanics, dice rolling, and rule processing 
- **GameplayController** (`src/core/gameplay_controller.py`): Manages turn-based gameplay flow and player interactions

### AI Agent System
Located in `src/agents/`, each agent specializes in different aspects:
- **StoryAgent**: Narrative progression and plot development
- **NPCAgent**: Non-player character behavior and dialogue  
- **EnvironmentAgent**: Location descriptions, atmosphere, and world state
- **RuleAgent**: Game rule interpretation and mechanics
- **MemoryAgent**: Continuity tracking and game history

### AI Infrastructure
- **OllamaClient** (`src/ai/ollama_client.py`): Interface to Ollama LLM (gpt-oss-120b model)
- **UltraThink** (`src/ai/ultra_think.py`): Advanced multi-layered reasoning system for complex scenarios
- **UltraThinkCoordinator** (`src/ai/ultra_think_coordinator.py`): Coordinates multiple agents for complex analysis

### UI Systems
- **GameplayInterface** (`src/ui/gameplay_interface.py`): Core gameplay interface supporting free-text input (no numbered action lists)
- **CLIInterface** (`src/ui/cli_interface.py`): Command-line interface
- **DesktopInterface** (`src/ui/desktop_interface.py`): GUI interface using tkinter

## Common Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install and configure Ollama
ollama pull gpt-oss-120b

# Activate virtual environment (if using)
source venv/bin/activate
```

### Running the Game
```bash
# Standard CLI game
python main.py

# With desktop GUI
python main.py --desktop

# Skip system checks for faster startup
python main.py --skip-checks

# Debug mode with verbose logging
python main.py --debug

# Load specific saved game
python main.py --load-game saves/my_save.json
```

### Testing and Diagnostics
```bash
# Run comprehensive system check
python main.py --system-check

# Run integration tests (full suite)
python main.py --test

# Run fast integration tests
python main.py --test-fast

# Run specific test files
python test_free_text_system.py
python test_final_system.py
```

### Game Shell Script
```bash
# Interactive game launcher
./run_game.sh
```

## Key Implementation Details

### Free-Text Action System
The game uses a revolutionary free-text input system instead of numbered choice lists:
- Players input natural language actions like "문을 열어본다" (open the door)
- AI agents parse and interpret the actions contextually
- No restriction to predefined action lists

### Agent Coordination
- Multiple AI agents work together through the UltraThinkCoordinator
- Each agent provides specialized analysis for complex scenarios
- Results are synthesized into coherent narrative responses

### Save System
- Comprehensive save/load system in `src/data/save_manager.py`
- Auto-save functionality with configurable intervals
- Multiple save slots and campaign management

### Configuration
- JSON-based configuration system (`config.json`)
- Example configuration in `config.example.json`
- Runtime configuration through Config class

### Localization
- Multi-language support (Korean/English) in `localization/`
- Localization manager handles text rendering

## Testing Architecture

### Integration Tests
- Comprehensive test suite in `tests/integration_test.py`
- System validation tests for AI agents, save/load, and gameplay loop
- Performance and stress testing capabilities

### Specialized Tests
- Individual system tests (e.g., `test_free_text_system.py`)
- Agent-specific validation tests
- UI integration tests

## Development Notes

### Recent Major Changes
The system recently underwent a significant architectural change:
- Removed numbered action lists ([1], [2], [3] style menus)
- Implemented free-text natural language input system
- Enhanced AI agent integration for action interpretation

### Error Handling
- Comprehensive error handling throughout the system
- Graceful degradation when AI services are unavailable
- Fallback systems for critical gameplay functions

### Performance Considerations
- Async/await patterns throughout for non-blocking operations
- Agent response caching for performance
- Configurable timeouts and retry logic

### Configuration Management
Critical configuration paths:
- AI model settings in `ai` section
- Game mechanics in `game` section  
- UI preferences in `ui` section
- Logging configuration in `logging` section

## File Structure Highlights

```
src/
├── core/           # Game engine and mechanics
├── agents/         # Specialized AI agents
├── ai/            # AI infrastructure and Ultra-think system
├── ui/            # User interfaces (CLI, desktop, gameplay)
├── data/          # Content, saves, and data management
└── utils/         # Configuration, logging, and utilities

saves/             # Game save files and campaigns
logs/              # Application and error logs
tests/             # Test suite and validation
localization/      # Multi-language support
```

The system is designed for extensibility and modular development, with clear separation between game logic, AI systems, and user interfaces.