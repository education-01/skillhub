---
name: code-exec
version: 1.0.0
description: Python code execution in a secure sandbox
author: SkillHub
tags: python, code, execution, sandbox
---

# Code Execution Skill

Execute Python code in a secure sandbox environment.

## Features

- Python code execution
- Restricted builtins for security
- Timeout protection
- Variable capture and inspection
- Support for functions and scripts
- Safe execution environment

## Usage

### Execute Code
```python
result = execute_code("x = 10\ny = 20\nprint(x + y)")
```

### Execute with Variables
```python
result = execute_code(
    code="result = a + b",
    variables={'a': 5, 'b': 3}
)
```

### Execute Function
```python
code = '''
def calculate(x, y):
    return x * y + 100
'''
result = execute_function(code, 'calculate', args=[5, 10])
```

## Safety Features

- Restricted builtins (no file operations, imports, etc.)
- Timeout protection (default 5 seconds)
- Memory limits
- Safe evaluation context
- No system access

## Actions

- `execute_code`: Execute Python code and return result
- `execute_function`: Execute a specific function from code
- `get_variables`: Get variables defined in execution
- `test_code`: Test code without executing (syntax check)

## Allowed Builtins

- Basic: print, len, range, enumerate, zip, map, filter
- Types: int, float, str, bool, list, dict, tuple, set
- Math: min, max, abs, sum, round
- Other: type, isinstance, hasattr
