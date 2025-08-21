# Suggested Commands for Cthulhu Solo TRPG Development

## Running the Application
```bash
# Run the game with CLI interface
python main.py

# Run with debug logging
python main.py --debug

# Run system tests
python main.py --test

# Run specific test files
python test_story_agent_final.py
python comprehensive_system_test.py
```

## Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
pytest --cov=src tests/

# Code formatting
black src/ tests/
black --check src/ tests/

# Linting
flake8 src/ tests/
mypy src/ tests/

# Create logs directory
mkdir -p logs

# Check Ollama connection
ollama list
ollama pull gpt-oss-120b
```

## Debugging Commands
```bash
# Check system status
python basic_system_test.py
python enhanced_system_test.py

# Test specific components
python test_game_manager.py
python test_agent_init.py
python test_story_agent_fix.py

# Debug game engine
python test_actual_gameplay.py
python test_investigation_opportunities.py
```

## System Utilities (macOS)
```bash
# File operations
ls -la
find . -name "*.py" -type f
grep -r "pattern" src/

# Process management
ps aux | grep python
kill -9 <pid>

# Git operations
git status
git log --oneline
git diff
```