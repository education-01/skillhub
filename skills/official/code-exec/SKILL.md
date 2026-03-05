---
name: code-exec
description: "Execute Python code safely. Use when: user needs to run Python code, test snippets, or compute complex operations. Runs in a sandboxed environment with timeout protection."
metadata: { "openclaw": { "emoji": "🐍" } }
---

# Code Execution Skill

Execute Python code for calculations, data processing, and testing.

## When to Use

✅ **USE this skill when:**

- "Run this Python code..."
- "Execute..."
- "Test this snippet..."
- "What does this code do?"
- Complex calculations
- Data transformations

## When NOT to Use

❌ **DON'T use this skill when:**

- Running production code → use proper environment
- Installing packages → use pip directly
- System administration → use shell commands
- Long-running processes → use background jobs

## Commands

### Basic Execution

```bash
# Single line
python3 -c "print('Hello, World!')"

# Multi-line
python3 << 'EOF'
x = 10
y = 20
print(f"Sum: {x + y}")
EOF
```

### With Imports

```bash
python3 << 'EOF'
import json
import math

data = {"name": "test", "value": math.sqrt(144)}
print(json.dumps(data, indent=2))
EOF
```

### Safe Execution with Timeout

```bash
# 5 second timeout
timeout 5 python3 -c "print('quick execution')"
```

### Read from File

```bash
# Execute a Python file
python3 /path/to/script.py

# With arguments
python3 /path/to/script.py arg1 arg2
```

## Available Modules

**Built-in (always available):**
- `json` — JSON parsing
- `math` — Mathematical functions
- `datetime` — Date/time operations
- `re` — Regular expressions
- `os`, `sys` — System operations
- `collections` — Data structures

**Check available:**

```bash
python3 -c "import sys; print(sys.builtin_module_names)"
```

## Quick Responses

**"Execute a simple calculation"**

```bash
python3 -c "print(2 ** 10)"
```

**"Parse JSON"**

```bash
python3 << 'EOF'
import json
text = '{"name": "Alice", "age": 30}'
data = json.loads(text)
print(f"Name: {data['name']}, Age: {data['age']}")
EOF
```

**"Generate a list"**

```bash
python3 -c "print([x**2 for x in range(10)])"
```

**"Format output"**

```bash
python3 << 'EOF'
for i in range(5):
    print(f"Item {i+1}: {'✓' if i % 2 == 0 else '✗'}")
EOF
```

## Safety Notes

⚠️ **Important:**
- Code runs with user permissions
- Timeout recommended for unknown code
- Don't execute untrusted code
- Avoid file system modifications in sandbox

**Best Practices:**
- Use `timeout` for long-running code
- Validate input before execution
- Use virtual environments for isolation
