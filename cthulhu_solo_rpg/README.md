# Cthulhu Solo TRPG

A Cthulhu horror TRPG game designed for solo play with an AI Game Master powered by Ollama.

## Features

- **Multi-Agent AI System**: Specialized agents for story, NPCs, environment, rules, and memory management
- **AI Game Master**: Powered by Ollama (GPT-oss-120b) for dynamic storytelling
- **Ultra-Think System**: Advanced multi-layered reasoning for complex game situations with coordinated agent analysis
- **Multiple Interfaces**: Both CLI and desktop GUI options
- **Session Management**: Save and load game sessions
- **Turn-Based Gameplay**: Classic TRPG mechanics with modern AI enhancement

## Architecture

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
└── tests/            # Test suite
```

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install and setup Ollama:**
   - Install Ollama from https://ollama.ai
   - Pull the required model:
     ```bash
     ollama pull gpt-oss-120b
     ```

3. **Run the game:**
   ```bash
   python main.py --interface cli
   ```

## Usage

### CLI Interface
```bash
python main.py --interface cli
```

### Desktop Interface
```bash
python main.py --interface desktop
```

### Debug Mode
```bash
python main.py --debug
```

## AI Agents

- **Story Agent**: Manages narrative progression and plot development
- **NPC Agent**: Handles non-player character behavior and dialogue
- **Environment Agent**: Manages locations, atmosphere, and world state
- **Rule Agent**: Interprets game rules and mechanics
- **Memory Agent**: Maintains continuity and game history

## Configuration

The game uses a JSON configuration file for settings:
- AI model parameters
- Game difficulty settings
- Interface preferences
- Logging configuration

## Ultra-Think System

The Ultra-Think system provides deep, multi-layered analysis for complex gaming situations, enhancing the AI's ability to handle intricate horror scenarios with nuanced understanding.

### Key Features

- **Multi-Mode Analysis**: Different thinking modes for various scenario types:
  - `HORROR_ATMOSPHERE`: Atmospheric and environmental horror enhancement
  - `CHARACTER_PSYCHOLOGY`: Deep character motivation and psychological analysis  
  - `MYTHOS_INTEGRATION`: Cosmic horror elements and forbidden knowledge
  - `CONSEQUENCE_ANALYSIS`: Long-term impact assessment of actions and decisions
  - `NARRATIVE_FLOW`: Story pacing and dramatic structure optimization
  - `TENSION_BUILDING`: Dramatic tension and suspense management

- **Coordinated Agent Analysis**: Multiple AI agents collaborate through the Ultra-Think Coordinator to provide comprehensive scenario analysis

- **Adaptive Complexity**: Automatically triggers for complex situations requiring deeper reasoning

- **Cthulhu-Specific Patterns**: Specialized analysis patterns for cosmic horror themes

### Usage Example

```bash
# Test the Ultra-think integration
python test_ultra_think_integration.py

# Run an example scenario demonstration  
python example_ultra_think_scenario.py
```

### Integration

Each AI agent automatically uses Ultra-think when encountering complex situations:

- **Story Agent**: Multi-scenario plot analysis, climax optimization, long-term narrative impact
- **NPC Agent**: Complex social interactions, psychological profiling, group dynamics  
- **Environment Agent**: Atmospheric optimization, multi-sensory horror experiences
- **Rule Agent**: Ambiguous rule interpretation, balanced challenge design
- **Memory Agent**: Continuity analysis, pattern recognition, story arc optimization

The GM Brain coordinates these analyses to provide enhanced, coherent responses that maintain narrative flow while maximizing horror impact.

## Development Status

This is the initial project structure. Core functionality is being developed in phases:

1. ✅ Project structure and basic components
2. 🔄 Core game mechanics implementation
3. 🔄 AI agent system development
4. 🔄 Ollama integration
5. ✅ Ultra-think system with coordinated agent analysis
6. 🔄 User interface completion
7. 🔄 Content and scenario system

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]