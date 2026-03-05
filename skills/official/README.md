# Official Skills

This directory contains 5 official skills created for the SkillHub project.

## Skills Overview

### 1. calculator/
**Calculator with variable storage**
- Basic arithmetic operations (+, -, *, /, **, %)
- Advanced math functions (sqrt, sin, cos, tan, log, etc.)
- Variable storage and retrieval
- Mathematical constants (pi, e)

**Actions:**
- `calculate` - Evaluate mathematical expression
- `store_variable` - Store a variable
- `get_variable` - Retrieve a variable
- `list_variables` - List all variables
- `clear_variables` - Clear user variables

### 2. weather/
**Weather query using wttr.in API**
- Current weather conditions
- Multi-day forecasts (up to 3 days)
- Multiple city queries
- Detailed weather reports

**Actions:**
- `get_weather` - Get current weather for cities
- `get_forecast` - Get multi-day forecast
- `get_detailed_weather` - Get detailed weather report

### 3. web-search/
**Web search using DuckDuckGo**
- Privacy-focused search
- Result summarization
- Multiple result limit options
- No API key required

**Actions:**
- `search` - Perform web search
- `search_and_summarize` - Search with summary

### 4. file-ops/
**File operations**
- Read/write/append files
- List directory contents
- Create directories
- File existence checks
- File metadata

**Actions:**
- `read_file` - Read file contents
- `write_file` - Write to file
- `append_file` - Append to file
- `list_directory` - List directory
- `create_directory` - Create directory
- `file_exists` - Check existence
- `get_file_info` - Get file metadata

### 5. code-exec/
**Python code execution in sandbox**
- Secure execution environment
- Restricted builtins
- Timeout protection (5 seconds)
- Variable capture
- Function execution

**Actions:**
- `execute_code` - Execute Python code
- `execute_function` - Execute specific function
- `test_code` - Syntax check
- `get_variables` - Get defined variables

## Testing

Each skill includes a test suite in the `if __name__ == '__main__'` block of skill.py.

To test a skill:
```bash
cd /path/to/skill
python3 skill.py
```

## Usage Example

```python
from skill import execute

# Calculator
result = execute('calculate', expression='2 + 3 * 4')
print(result['result'])  # 14

# Weather
result = execute('get_weather', locations='Beijing')
print(result['weather'])

# Web Search
result = execute('search', query='Python tutorial', max_results=5)
print(result['results'])

# File Operations
result = execute('write_file', file_path='/tmp/test.txt', content='Hello')
result = execute('read_file', file_path='/tmp/test.txt')

# Code Execution
result = execute('execute_code', code='x = 10\nprint(x * 2)')
print(result['output'])  # 20
```

## Structure

Each skill follows this structure:
```
skill-name/
├── SKILL.md      # Skill documentation and metadata
└── skill.py      # Skill implementation
```

## Created

Date: 2026-03-06
Agent: Agent 3
Project: SkillHub Official Skills
