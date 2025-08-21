# Code Style and Conventions for Cthulhu Solo TRPG

## Python Style Guidelines

### Naming Conventions
- **Classes**: PascalCase (e.g., `GameManager`, `StoryAgent`)
- **Functions/Methods**: snake_case (e.g., `initialize_agents`, `process_user_input`)
- **Variables**: snake_case (e.g., `game_state`, `current_scenario`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_OLLAMA_URL`)
- **Private methods**: Leading underscore (e.g., `_generate_response`)

### Type Hints
- Use comprehensive type hints for all functions and class methods
- Import types from `typing` module: `Dict`, `List`, `Optional`, `Union`, `Any`
- Use dataclasses with type annotations for configuration objects

### Documentation
- **Docstrings**: Use triple-quoted strings for all modules, classes, and functions
- **Format**: Follow Google-style docstrings
- **Example**:
```python
def process_input(self, user_input: str) -> Dict[str, Any]:
    """
    Process user input and generate appropriate response.
    
    Args:
        user_input: The raw input from the player
        
    Returns:
        Dictionary containing response data and metadata
        
    Raises:
        ValueError: If input is invalid or empty
    """
```

### Code Organization
- **Imports**: Grouped in order (standard library, third-party, local imports)
- **Class structure**: Public methods first, private methods at end
- **Error handling**: Use specific exception types, comprehensive logging
- **Async/await**: Used for AI calls and I/O operations

### Design Patterns
- **Dataclasses**: For configuration and data transfer objects
- **Enums**: For game states and status values
- **Agent pattern**: Specialized AI agents for different game aspects
- **Manager pattern**: Central coordinators for complex systems

### Logging
- Use structured logging with appropriate levels
- Include context information in log messages
- Use logger names matching module hierarchy

### Testing
- Test files prefixed with `test_`
- Use pytest framework
- Include both unit and integration tests
- Mock external dependencies (Ollama API calls)