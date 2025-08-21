# Test Driven Document (TDD)
# Cthulhu Solo TRPG System

## 1. Testing Philosophy

### 1.1 Core Principles
- **Test-First Development**: Write tests before implementation
- **Comprehensive Coverage**: Unit, integration, and system tests
- **Continuous Validation**: Automated testing in development workflow
- **Behavioral Testing**: Focus on user-facing functionality

### 1.2 Testing Pyramid
```
         /\
        /E2E\        ← End-to-End Tests (10%)
       /─────\
      /System \      ← System Integration Tests (20%)
     /─────────\
    /Integration\    ← Component Integration Tests (30%)
   /─────────────\
  /   Unit Tests  \  ← Unit Tests (40%)
 /─────────────────\
```

## 2. Test Categories

### 2.1 Unit Tests
**Purpose**: Test individual components in isolation

**Coverage Areas**:
- Individual agent methods
- Utility functions
- Data structures
- Game mechanics calculations

### 2.2 Integration Tests
**Purpose**: Test component interactions

**Coverage Areas**:
- Agent-to-agent communication
- AI system integration
- Save/load functionality
- UI-to-controller interactions

### 2.3 System Tests
**Purpose**: Test complete workflows

**Coverage Areas**:
- Full gameplay loops
- Multi-turn scenarios
- Error recovery paths
- Performance under load

### 2.4 End-to-End Tests
**Purpose**: Test from user perspective

**Coverage Areas**:
- Complete game sessions
- User input processing
- Display rendering
- Save game continuity

## 3. Test Implementation

### 3.1 Test Structure
```python
# Standard test structure
class TestComponentName:
    """Test suite for ComponentName"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.component = ComponentName()
        self.test_data = load_test_data()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.component.cleanup()
    
    def test_specific_behavior(self):
        """Test specific behavior description"""
        # Arrange
        input_data = self.prepare_input()
        
        # Act
        result = self.component.process(input_data)
        
        # Assert
        assert result.status == "success"
        assert len(result.data) > 0
```

## 4. Critical Test Scenarios

### 4.1 Free-Text Input Processing

#### Test: Player Action Interpretation
```python
@pytest.mark.asyncio
async def test_player_action_interpretation():
    """Test that free-text input is correctly interpreted"""
    
    test_cases = [
        {
            "input": "문을 조사한다",
            "expected_type": "investigate",
            "expected_target": "door"
        },
        {
            "input": "NPC와 대화한다", 
            "expected_type": "interact",
            "expected_target": "npc"
        },
        {
            "input": "2층으로 올라간다",
            "expected_type": "movement",
            "expected_target": "upstairs"
        }
    ]
    
    story_agent = StoryAgent()
    
    for case in test_cases:
        context = {"player_action": case["input"]}
        result = await story_agent.process_player_action(context)
        
        assert result["action_type"] == case["expected_type"]
        assert case["expected_target"] in result["parsed_action"].lower()
```

#### Test: Edge Case Handling
```python
def test_edge_case_inputs():
    """Test handling of edge case inputs"""
    
    edge_cases = [
        "",  # Empty input
        " " * 100,  # Whitespace only
        "a" * 1000,  # Very long input
        "!@#$%^&*()",  # Special characters
        "DROP TABLE users;",  # SQL injection attempt
    ]
    
    interface = GameplayInterface()
    
    for input_text in edge_cases:
        result = interface.validate_input(input_text)
        assert result["is_valid"] in [True, False]
        assert "error" not in result or result["error"] is not None
```

### 4.2 Investigation Opportunities Display

#### Test: Investigation Generation
```python
@pytest.mark.asyncio
async def test_investigation_opportunities_generation():
    """Test that investigation opportunities are properly generated"""
    
    controller = GameplayController()
    context = NarrativeContext(
        scene_id="scene_001_entrance",
        tension_level=TensionLevel.UNEASY,
        turn_number=1
    )
    
    story_content = await controller.get_current_story_content(context)
    
    # Verify structure
    assert hasattr(story_content, 'investigation_opportunities')
    assert isinstance(story_content.investigation_opportunities, list)
    
    # Verify content
    assert len(story_content.investigation_opportunities) > 0
    assert all(isinstance(opp, str) for opp in story_content.investigation_opportunities)
    assert all(len(opp) > 0 for opp in story_content.investigation_opportunities)
```

#### Test: UI Display Integration
```python
def test_investigation_ui_display():
    """Test that investigations are displayed in UI"""
    
    # Create test story content
    story_content = StoryContent(
        text="Test narrative",
        content_id="test_001",
        scene_id="scene_001",
        tension_level=TensionLevel.CALM,
        metadata={},
        investigation_opportunities=[
            "조사 기회 1",
            "조사 기회 2",
            "조사 기회 3"
        ]
    )
    
    # Test display formatting
    display_manager = DisplayManager()
    panel = display_manager.format_investigations(story_content)
    
    assert panel is not None
    assert "조사 기회" in str(panel)
    assert all(opp in str(panel) for opp in story_content.investigation_opportunities)
```

### 4.3 Memory Management

#### Test: Memory Comparison Fix
```python
def test_memory_sorting_without_comparison_error():
    """Test that memory sorting works without comparison errors"""
    
    agent = BaseAgent("test_agent")
    
    # Create memories with identical importance and timestamp
    memories = [
        AgentMemory(
            content=f"Memory {i}",
            timestamp=1234567890.0,
            importance=5,
            metadata={},
            memory_type="test"
        )
        for i in range(10)
    ]
    
    agent.memory.extend(memories)
    
    # This should not raise TypeError
    try:
        agent._cleanup_memory()
        assert True
    except TypeError as e:
        if "'<' not supported" in str(e):
            pytest.fail(f"Memory comparison error not fixed: {e}")
```

#### Test: Memory Relevance Scoring
```python
def test_memory_relevance_calculation():
    """Test memory relevance scoring algorithm"""
    
    agent = BaseAgent("test_agent")
    
    # Add test memories
    memories = [
        AgentMemory("Ancient book about Cthulhu", time.time() - 3600, 8, {}, "knowledge"),
        AgentMemory("Player examined door", time.time() - 60, 5, {}, "action"),
        AgentMemory("NPC mentioned strange sounds", time.time() - 1800, 6, {}, "dialogue")
    ]
    
    for memory in memories:
        agent.add_memory(memory)
    
    # Test relevance calculation
    context = {"keywords": ["door", "examine"]}
    relevant = agent.get_relevant_memories(context, limit=2)
    
    assert len(relevant) <= 2
    assert "door" in relevant[0].content.lower()
```

### 4.4 AI Agent Integration

#### Test: Ollama Connection Resilience
```python
@pytest.mark.asyncio
async def test_ollama_timeout_handling():
    """Test Ollama client timeout and retry behavior"""
    
    client = OllamaClient(
        timeout=300,
        max_retries=5,
        retry_delay=2.0
    )
    
    # Mock slow response
    with patch('requests.Session.post') as mock_post:
        mock_post.side_effect = [
            requests.Timeout("Connection timeout"),
            requests.Timeout("Connection timeout"),
            MockResponse({"response": "Success after retries"})
        ]
        
        response = client.generate("Test prompt")
        
        assert response.content == "Success after retries"
        assert mock_post.call_count == 3
```

#### Test: Agent Fallback System
```python
@pytest.mark.asyncio
async def test_agent_fallback_on_ai_failure():
    """Test fallback system when AI is unavailable"""
    
    controller = GameplayController()
    
    # Disable AI
    with patch('src.ai.ollama_client.OllamaClient.generate') as mock_generate:
        mock_generate.side_effect = Exception("AI unavailable")
        
        context = NarrativeContext(
            scene_id="scene_001_entrance",
            tension_level=TensionLevel.CALM,
            turn_number=1
        )
        
        # Should use fallback
        content = await controller.get_current_story_content(context)
        
        assert content is not None
        assert content.text != ""
        assert "fallback" in content.metadata.get("source", "")
```

### 4.5 Save System

#### Test: Save and Load Consistency
```python
@pytest.mark.asyncio
async def test_save_load_consistency():
    """Test that game state is preserved through save/load"""
    
    manager = GameManager()
    
    # Create game state
    await manager.start_new_game({
        "name": "Test Character",
        "occupation": "Investigator",
        "stats": {"STR": 10, "INT": 15}
    })
    
    # Play some turns
    for i in range(3):
        await manager.process_turn(f"Test action {i}")
    
    # Save state
    save_data = await manager.save_game("test_slot")
    
    # Create new manager and load
    new_manager = GameManager()
    await new_manager.load_game("test_slot")
    
    # Verify state
    assert new_manager.character.name == "Test Character"
    assert new_manager.turn_number == 3
    assert len(new_manager.history) == 3
```

### 4.6 Performance Tests

#### Test: Response Time Under Load
```python
@pytest.mark.performance
async def test_response_time_under_load():
    """Test system response time under concurrent requests"""
    
    controller = GameplayController()
    
    async def single_request():
        start = time.time()
        await controller.process_player_action("조사한다")
        return time.time() - start
    
    # Run concurrent requests
    tasks = [single_request() for _ in range(10)]
    times = await asyncio.gather(*tasks)
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    assert avg_time < 5.0  # Average under 5 seconds
    assert max_time < 10.0  # Max under 10 seconds
```

#### Test: Memory Usage
```python
def test_memory_usage_limits():
    """Test that memory usage stays within limits"""
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Run intensive operations
    manager = GameManager()
    for _ in range(100):
        manager.add_to_history("Large content " * 1000)
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    assert memory_increase < 500  # Less than 500MB increase
```

## 5. Test Data Management

### 5.1 Test Fixtures
```python
# conftest.py
import pytest
from src.core.game_manager import GameManager

@pytest.fixture
async def game_manager():
    """Provide initialized game manager"""
    manager = GameManager()
    await manager.initialize()
    yield manager
    await manager.shutdown()

@pytest.fixture
def test_character():
    """Provide test character data"""
    return {
        "name": "테스트 탐사자",
        "occupation": "고고학자",
        "age": 35,
        "stats": {
            "STR": 10, "CON": 12, "POW": 14,
            "DEX": 11, "APP": 10, "SIZ": 13,
            "INT": 16, "EDU": 18
        },
        "skills": {
            "도서관 이용": 70,
            "고고학": 80,
            "역사": 65
        }
    }
```

### 5.2 Mock Data
```python
# test_data/mock_responses.py
MOCK_STORY_RESPONSES = {
    "scene_001": {
        "text": "음산한 저택의 현관문 앞에 서 있습니다.",
        "investigations": [
            "문고리를 조사한다",
            "창문을 들여다본다"
        ]
    }
}

MOCK_NPC_DIALOGUES = {
    "butler": [
        "어서오십시오, 주인님이 기다리고 계십니다.",
        "이 저택에는... 말하기 어려운 일들이 있었습니다."
    ]
}
```

## 6. Test Execution

### 6.1 Test Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific category
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with markers
pytest -m "not slow"
pytest -m "performance"

# Run specific test file
pytest tests/test_story_agent.py

# Run with verbose output
pytest -v

# Run with parallel execution
pytest -n 4
```

### 6.2 Continuous Integration
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 7. Test Metrics

### 7.1 Coverage Goals
- **Overall Coverage**: > 80%
- **Core Systems**: > 90%
- **AI Agents**: > 75%
- **UI Components**: > 70%
- **Utilities**: > 95%

### 7.2 Quality Metrics
- **Test Execution Time**: < 5 minutes for full suite
- **Flaky Test Rate**: < 2%
- **Test Maintenance**: Update within 24 hours of code change
- **Documentation**: All tests have descriptive docstrings

## 8. Test Debugging

### 8.1 Debugging Failed Tests
```python
# Add debugging information
@pytest.mark.debug
def test_complex_scenario():
    """Test with detailed debugging output"""
    
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Add breakpoint for interactive debugging
    import pdb; pdb.set_trace()
    
    # Or use pytest's built-in
    pytest.set_trace()
```

### 8.2 Test Isolation
```python
# Ensure test isolation
def test_isolated_operation(tmp_path):
    """Test using isolated temporary directory"""
    
    test_file = tmp_path / "test_save.json"
    
    # Operations on test_file
    # Automatically cleaned up after test
```

## 9. Test Patterns

### 9.1 Async Test Pattern
```python
@pytest.mark.asyncio
async def test_async_operation():
    """Standard async test pattern"""
    
    # Setup
    async with AsyncResource() as resource:
        # Execute
        result = await resource.async_operation()
        
        # Verify
        assert result.status == "success"
```

### 9.2 Parameterized Tests
```python
@pytest.mark.parametrize("input_text,expected_type", [
    ("조사한다", "investigate"),
    ("대화한다", "interact"),
    ("이동한다", "movement"),
])
def test_action_classification(input_text, expected_type):
    """Test multiple scenarios with parameters"""
    
    classifier = ActionClassifier()
    result = classifier.classify(input_text)
    assert result == expected_type
```

### 9.3 Property-Based Testing
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=1000))
def test_input_handling_properties(input_text):
    """Test properties that should hold for all inputs"""
    
    handler = InputHandler()
    result = handler.process(input_text)
    
    # Properties that should always be true
    assert result is not None
    assert isinstance(result, dict)
    assert "processed" in result
```

## 10. Test Maintenance

### 10.1 Test Review Checklist
- [ ] Test name clearly describes what is being tested
- [ ] Test has single responsibility
- [ ] Test is independent of other tests
- [ ] Test uses appropriate assertions
- [ ] Test handles both success and failure cases
- [ ] Test data is minimal but sufficient
- [ ] Test execution time is reasonable

### 10.2 Test Refactoring Guidelines
1. **Extract common setup** into fixtures
2. **Parameterize** similar tests
3. **Remove duplicate** test logic
4. **Update outdated** assertions
5. **Improve test** descriptions
6. **Optimize slow** tests

## 11. Known Test Issues

### 11.1 Current Limitations
- **Ollama Dependency**: Some tests require Ollama service running
- **Async Timing**: Occasional timing issues in async tests
- **UI Testing**: Limited automated UI testing capabilities
- **Performance Tests**: May vary based on hardware

### 11.2 Workarounds
```python
# Skip tests requiring external services
@pytest.mark.skipif(not ollama_available(), 
                    reason="Ollama service not available")
def test_requiring_ollama():
    pass

# Mark slow tests
@pytest.mark.slow
def test_performance_intensive():
    pass
```

## 12. Future Test Enhancements

### 12.1 Planned Improvements
- **Visual Regression Testing**: For UI components
- **Mutation Testing**: To verify test effectiveness
- **Contract Testing**: For AI agent interfaces
- **Load Testing**: For multiplayer scenarios
- **Security Testing**: For input validation

### 12.2 Tooling Upgrades
- Integrate pytest-xdist for parallel execution
- Add pytest-timeout for hanging test detection
- Implement pytest-benchmark for performance tracking
- Use pytest-mock for improved mocking

---

*Last Updated: 2025-01-21*
*Version: 1.0.0*
*Document Status: Active*