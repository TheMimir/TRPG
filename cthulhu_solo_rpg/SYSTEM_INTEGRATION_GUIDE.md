# Cthulhu Solo TRPG - System Integration Guide

🎲 **Complete Horror Gaming Experience with Integrated AI System**

## Overview

The Cthulhu Solo TRPG system has been fully integrated into a cohesive gaming experience that combines:

- **Complete Game Loop**: Seamless turn-based gameplay with AI-driven narrative
- **AI Agent Coordination**: Multiple specialized AI agents working together
- **Ultra-think Integration**: Advanced AI reasoning for complex scenarios
- **Comprehensive Testing**: Full system validation and error handling
- **Professional Launcher**: Easy setup, diagnostics, and game management

## Quick Start

### 1. System Check
Before first use, run a comprehensive system check:

```bash
python main.py --system-check
```

This will verify:
- Python environment and dependencies
- Ollama AI service connection
- File permissions and disk space
- Game data integrity

### 2. Basic Launch
Start the game with default settings:

```bash
python main.py
```

### 3. Advanced Launch Options

```bash
# Use desktop interface
python main.py --desktop

# Load specific configuration
python main.py --config my_config.json

# Skip system checks for faster startup
python main.py --skip-checks

# Enable debug mode
python main.py --debug

# Load saved game
python main.py --load-game saves/my_game.json.gz

# Start with specific character and scenario
python main.py --character characters/investigator.json --scenario "The Haunted House"
```

## System Architecture

### Core Components

1. **Game Manager** (`src/core/game_manager.py`)
   - Central orchestrator for all game systems
   - Manages AI agent coordination
   - Handles save/load operations
   - Monitors system performance

2. **AI Agent System**
   - **Story Agent**: Main narrative generation and plot management
   - **NPC Agent**: Character interactions and social dynamics
   - **Environment Agent**: Atmospheric descriptions and sensory details
   - **Rule Agent**: Game mechanics and rule interpretation
   - **Memory Agent**: Continuity tracking and information synthesis

3. **Ultra-think Coordinator**
   - Advanced AI reasoning for complex scenarios
   - Multi-agent coordination for nuanced responses
   - Context-aware decision making
   - Priority-based analysis allocation

4. **Game Engine** (`src/core/game_engine.py`)
   - Core game mechanics and rules
   - Turn processing and state management
   - Character and action handling

### Game Loop Flow

```
Game Start
├── System Initialization
│   ├── Load Configuration
│   ├── Verify Dependencies
│   ├── Connect to Ollama AI
│   ├── Initialize AI Agents
│   └── Setup Ultra-think
├── Character Creation/Loading
├── Scenario Selection
└── Main Game Loop
    ├── Player Action Input
    ├── AI Agent Coordination
    │   ├── Story Agent: Narrative response
    │   ├── Memory Agent: Continuity check
    │   ├── Rule Agent: Mechanics handling
    │   ├── Environment Agent: Atmosphere
    │   └── NPC Agent: Character reactions
    ├── Ultra-think Analysis (if complex)
    ├── State Updates
    ├── Auto-save (if enabled)
    └── Next Turn
```

## Configuration

### Basic Configuration (`config.json`)

```json
{
  "ai": {
    "ollama_url": "http://localhost:11434",
    "model": "gpt-oss-120b",
    "temperature": 0.7,
    "ultra_think_enabled": true,
    "ultra_think_depth": 3
  },
  "game": {
    "auto_save": true,
    "auto_save_interval": 300,
    "difficulty": "normal",
    "sanity_multiplier": 1.0
  },
  "ui": {
    "interface": "cli",
    "colors_enabled": true
  },
  "logging": {
    "level": "INFO",
    "log_ai_interactions": true,
    "log_game_events": true
  }
}
```

### AI Model Requirements

- **Recommended**: `gpt-oss-120b` or similar large language model
- **Minimum**: Any Ollama-compatible model with good reasoning capabilities
- **Memory**: At least 4GB VRAM for optimal performance
- **Processing**: Response times typically 2-10 seconds depending on model

## Features

### 🤖 AI Agent Coordination

The system coordinates multiple AI agents to provide rich, immersive gameplay:

- **Narrative Consistency**: Story agent maintains plot coherence
- **Character Development**: NPC agent manages character relationships
- **Atmospheric Immersion**: Environment agent provides sensory details
- **Rule Enforcement**: Rule agent ensures fair and consistent mechanics
- **Memory Continuity**: Memory agent tracks storylines and clues

### 🧠 Ultra-think Integration

For complex scenarios, the system uses advanced AI reasoning:

- **Multi-perspective Analysis**: Considers multiple viewpoints
- **Consequence Prediction**: Anticipates action outcomes
- **Narrative Integration**: Weaves complex elements together
- **Dynamic Difficulty**: Adjusts based on situation complexity

### 💾 Save System

Comprehensive save/load functionality:

```bash
# Auto-saves every 5 minutes (configurable)
# Manual saves available through interface
# Multiple save slots supported
# Compressed saves for space efficiency
```

### 🔧 Diagnostics and Testing

Built-in system validation:

```bash
# Run integration tests
python main.py --test

# Fast test mode (for CI/development)
python main.py --test-fast

# System diagnostics
python main.py --system-check
```

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Failed
```
❌ Cannot connect to Ollama service at http://localhost:11434
```

**Solutions:**
- Ensure Ollama is installed and running: `ollama serve`
- Check if the model is available: `ollama list`
- Pull the required model: `ollama pull gpt-oss-120b`
- Verify the URL in your config file

#### 2. AI Agents Not Responding
```
⚠️ Warning: Insufficient AI agents available
```

**Solutions:**
- Check Ollama service status
- Verify model compatibility
- Review system logs for specific agent errors
- Try running with `--debug` for detailed error information

#### 3. Save/Load Issues
```
❌ Failed to save game: Permission denied
```

**Solutions:**
- Check file permissions in saves directory
- Ensure sufficient disk space
- Verify the saves directory exists and is writable

#### 4. Performance Issues
```
⚠️ Model response timeout (>10s)
```

**Solutions:**
- Use a smaller, faster model for testing
- Increase timeout values in configuration
- Check system resources (CPU, memory, GPU)
- Disable Ultra-think for faster responses

### Debug Mode

Enable detailed logging:

```bash
python main.py --debug
```

This provides:
- Detailed error traces
- AI interaction logs
- Performance timing information
- System state dumps

## Performance Optimization

### For Development/Testing
```json
{
  "ai": {
    "model": "tinyllama",
    "temperature": 0.1,
    "ultra_think_enabled": false
  },
  "game": {
    "auto_save": false
  },
  "logging": {
    "level": "WARNING"
  }
}
```

### For Production Gaming
```json
{
  "ai": {
    "model": "gpt-oss-120b",
    "temperature": 0.7,
    "ultra_think_enabled": true,
    "ultra_think_depth": 3
  },
  "game": {
    "auto_save": true,
    "auto_save_interval": 300
  }
}
```

## Development and Extension

### Adding New AI Agents

1. Create agent class inheriting from `BaseAgent`
2. Implement required methods: `process_input()`, `get_specialized_prompts()`
3. Register agent in `GameManager._initialize_ai_agents()`
4. Add agent-specific context in `GameManager._build_agent_context()`

### Custom Scenarios

Scenarios are loaded from `src/data/scenarios/`. Add new JSON files following the existing format.

### Integration Testing

The system includes comprehensive integration tests:

```python
# Run specific test categories
pytest tests/integration_test.py::IntegrationTestSuite::_run_ai_system_tests
```

## System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 2GB disk space
- Ollama installed and running

### Recommended Requirements
- Python 3.10+
- 8GB RAM
- 4GB VRAM (for AI model)
- 5GB disk space
- SSD for faster loading

## Security Considerations

- AI model responses are processed locally (no external API calls)
- Save files are compressed but not encrypted
- Configuration files may contain sensitive URLs/tokens
- System checks validate file permissions before operations

## Support and Community

### Getting Help

1. Run system diagnostics: `python main.py --system-check`
2. Check the troubleshooting section above
3. Enable debug mode for detailed error information
4. Review log files in the `logs/` directory

### Reporting Issues

When reporting issues, include:
- System check report output
- Integration test results (if applicable)
- Configuration file (remove sensitive information)
- Error logs with timestamps
- Steps to reproduce the issue

### Contributing

The system is designed for extensibility:
- AI agents can be easily added or modified
- Game mechanics are modular and configurable
- UI interfaces can be swapped or enhanced
- Save system supports custom data formats

---

## Quick Reference

### Essential Commands

```bash
# System validation
python main.py --system-check

# Quick test
python main.py --test-fast

# Standard game launch
python main.py

# Debug mode
python main.py --debug

# Desktop interface
python main.py --desktop

# Load saved game
python main.py --load-game path/to/save.json.gz
```

### Directory Structure

```
cthulhu_solo_rpg/
├── main.py                    # Main launcher
├── config.json               # Configuration
├── src/
│   ├── core/
│   │   ├── game_manager.py   # Central coordinator
│   │   ├── game_engine.py    # Core mechanics
│   │   └── character.py      # Character system
│   ├── agents/               # AI agents
│   ├── ai/                   # AI systems
│   ├── ui/                   # User interfaces
│   ├── utils/                # Utilities
│   └── data/                 # Game content
├── tests/
│   └── integration_test.py   # System tests
├── saves/                    # Save files
└── logs/                     # Log files
```

🎲 **The system is now fully integrated and ready for immersive Cthulhu horror gaming!**