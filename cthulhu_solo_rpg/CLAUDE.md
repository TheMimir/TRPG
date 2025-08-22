# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cthulhu Solo TRPG is a Lovecraftian horror tabletop RPG system designed for solo play with an AI Game Master powered by Ollama. The game features a sophisticated multi-agent AI system that manages different aspects of the horror gaming experience, from narrative generation to character interactions.

## AI Provider Configuration

The system now supports multiple AI providers:

### Automatic Detection (Recommended)
```bash
python main.py --ai-provider auto  # Default behavior
```
- Checks for OpenAI API key first
- Falls back to Ollama if available
- Provides best user experience

### Ollama (Local AI)
```bash
# Standard local setup
python main.py --ai-provider ollama

# Custom Ollama server
python main.py --ai-provider ollama --ollama-url http://localhost:11434

# Specific model
python main.py --ai-provider ollama --ai-model llama2:70b
```

**Requirements:**
- Ollama installed and running
- Model downloaded (e.g., `ollama pull gpt-oss:120b`)

### OpenAI API (Cloud AI)
```bash
# Using environment variable (recommended)
export OPENAI_API_KEY="your-api-key-here"
python main.py --ai-provider openai

# Using command line argument
python main.py --ai-provider openai --openai-api-key your-key-here

# Specific model
python main.py --ai-provider openai --ai-model gpt-4
```

**Requirements:**
- OpenAI API key
- Internet connection
- `pip install openai`

**Supported Models:**
- `gpt-4o-mini` - 기본값, 최고의 가성비 (권장)
- `gpt-4o` - 최신 최적화 모델
- `gpt-4` - 가장 강력한 모델, 높은 비용
- `gpt-4-turbo` - 빠른 GPT-4 변형
- `gpt-3.5-turbo` - 가장 경제적인 선택

### Environment Variables
```bash
# OpenAI Configuration
export OPENAI_API_KEY="your-api-key-here"        # Required for OpenAI
export AI_MODEL="gpt-4"                           # Override default model
export AI_TEMPERATURE="0.7"                      # Creativity level (0.0-1.0)
export AI_MAX_TOKENS="4000"                      # Maximum response length

# Ollama Configuration  
export OLLAMA_BASE_URL="http://localhost:11434"  # Ollama server URL
```

## Common Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install and configure Ollama (for local AI)
ollama pull gpt-oss-120b

# For OpenAI API support, install additional dependencies
pip install openai

# Set up OpenAI API key (choose one method):
# Method 1: Environment variable
export OPENAI_API_KEY="your-api-key-here"  # Unix/MacOS
set OPENAI_API_KEY=your-api-key-here       # Windows CMD
$env:OPENAI_API_KEY="your-api-key-here"    # Windows PowerShell

# Method 2: Pass as command line argument
# python main.py --openai-api-key your-api-key-here

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Unix/MacOS)
source venv/bin/activate
```

### Running the Game
```bash
# Standard CLI game (auto-detects available AI provider)
python main.py

# Specify AI provider explicitly
python main.py --ai-provider ollama    # Use local Ollama
python main.py --ai-provider openai    # Use OpenAI API
python main.py --ai-provider auto      # Auto-detect (default)

# Specify custom AI model
python main.py --ai-model gpt-4o-mini   # 기본값 (OpenAI) - 권장
python main.py --ai-model gpt-4         # Use GPT-4 (OpenAI)
python main.py --ai-model gpt-3.5-turbo # Use GPT-3.5 (OpenAI)
python main.py --ai-model llama2:70b    # Use Llama2 70B (Ollama)

# Configure Ollama connection
python main.py --ollama-url http://192.168.1.100:11434  # Remote Ollama

# OpenAI API key (if not set as environment variable)
python main.py --ai-provider openai --openai-api-key your-key-here

# Combined examples
python main.py --ai-provider openai --ai-model gpt-4 --debug
python main.py --ai-provider ollama --ai-model mixtral:8x7b --scenario library

# Debug mode with verbose logging
python main.py --debug

# Load specific saved game
python main.py --load-game saves/my_save.json

# Run integration tests
python main.py --test
```

### Testing
```bash
# Run specific test modules
python test_free_text_system.py
python test_final_system.py
python test_korean_language.py
python test_ultra_think_integration.py

# Run comprehensive tests
python comprehensive_system_test.py
python enhanced_system_test.py

# Run integration test suite
python tests/integration_test.py
```

### Demo Scripts
```bash
# Various demo modes
python simple_game.py           # Simple demo version
python korean_game_demo.py      # Korean language demo
python demo_cli.py              # CLI interface demo
python demo_numbered_gameplay.py # Numbered gameplay demo
python example_ultra_think_scenario.py # Ultra-think demo
```

### Shell Script (Unix/Linux)
```bash
./run_game.sh  # Interactive launcher menu
```

## Architecture

### Core Systems
- **GameManager** (`src/core/game_manager.py`): Central orchestrator that coordinates all systems and manages game state
- **GameEngine** (`src/core/game_engine.py`): Handles core game mechanics, dice rolling, and rule processing 
- **GameplayController** (`src/core/gameplay_controller.py`): Manages turn-based gameplay flow and player interactions

### AI Agent System
Located in `src/agents/`:
- **StoryAgent**: Narrative progression and plot development
- **NPCAgent**: Non-player character behavior and dialogue  
- **EnvironmentAgent**: Location descriptions, atmosphere, and world state
- **RuleAgent**: Game rule interpretation and mechanics
- **MemoryAgent**: Continuity tracking and game history
- **BaseAgent** (`base_agent.py`): Abstract base class for all agents

### AI Infrastructure
Located in `src/ai/`:
- **OllamaClient** (`ollama_client.py`): Interface to Ollama LLM (gpt-oss-120b model)
- **UltraThink**: Advanced multi-layered reasoning system for complex scenarios
- **UltraThinkCoordinator**: Coordinates multiple agents for complex analysis

### UI Systems
Located in `src/ui/`:
- **GameplayInterface** (`gameplay_interface.py`): Core gameplay interface supporting free-text input
- **CLIInterface**: Command-line interface
- **DesktopInterface**: GUI interface using tkinter

### Data Management
Located in `src/data/`:
- **SaveManager** (`save_manager.py`): Comprehensive save/load system with auto-save
- **ContentLoader** (`content_loader.py`): Loads game content from JSON files
- **GameData** (`game_data.py`): Central data management

### Configuration
- Example configuration: `config.example.json`
- Copy to `config.json` for actual use
- Key sections: `ai`, `game`, `ui`, `logging`, `content`, `performance`

## Key Implementation Details

### Free-Text Action System
- Players input natural language actions (e.g., "문을 열어본다", "examine the book")
- AI agents parse and interpret actions contextually
- No numbered choice lists - complete freedom of action

### Save System Structure
```
saves/
├── autosaves/        # Automatic saves
├── campaigns/        # Compressed campaign saves (.gz)
├── characters/       # Character profiles
├── metadata/         # Save metadata
├── quicksaves/       # Quick save slots
└── user_saves/       # Manual saves
```

### Localization
- Multi-language support in `localization/` directory
- Currently supports Korean (`ko.json`) and English (`en.json`)
- Localization system in `src/utils/localization.py`

### Testing Architecture
- Unit tests: `tests/test_core.py`, `tests/test_agents.py`
- Integration tests: `tests/integration_test.py`
- Specialized test files in root directory (test_*.py)

## Development Notes

### Error Handling
- Comprehensive try-catch blocks throughout
- Graceful degradation when Ollama is unavailable
- Fallback mechanisms for critical functions

### Performance Considerations
- Async/await patterns for non-blocking operations
- Configurable AI response caching
- Configurable timeouts (default 90s for AI calls)

### Recent Architectural Changes
- Removed numbered action menus in favor of free-text input
- Enhanced AI agent coordination through UltraThinkCoordinator
- Improved save system with compression and metadata

## File Structure

```
cthulhu_solo_rpg/
├── src/
│   ├── core/          # Game engine and mechanics
│   ├── agents/        # Specialized AI agents
│   ├── ai/           # AI infrastructure
│   ├── ui/           # User interfaces
│   ├── data/         # Content and save management
│   └── utils/        # Configuration and utilities
├── saves/            # Game save files
├── logs/             # Application logs
├── tests/            # Test suite
├── localization/     # Language files
├── docs/             # Documentation
└── backup_rebuild_2025/  # Backup/rebuild system
```

## Data Content Structure
Game content JSON files in `src/data/`:
- `atmosphere/`: Horror descriptors
- `entities/`: Cultists, creatures, gods
- `events/`: Random encounters
- `items/`: Artifacts, tools, books, weapons
- `locations/`: Various game locations
- `scenarios/`: Game scenarios and templates

## Important Files
- `main.py`: Primary entry point
- `run.py`: Alternative launcher
- `requirements.txt`: Python dependencies
- `config.example.json`: Configuration template
- `run_game.sh`: Unix/Linux launcher script