---
name: calculator
version: 1.0.0
description: Calculator with basic math operations and variable storage
author: SkillHub
tags: math, calculator, variables
---

# Calculator Skill

A powerful calculator that supports basic mathematical operations and variable storage for complex calculations.

## Features

- Basic arithmetic operations (+, -, *, /, **, %)
- Advanced math functions (sqrt, sin, cos, tan, log, etc.)
- Variable storage and retrieval
- Expression evaluation
- Support for parentheses and operator precedence

## Usage

### Basic Calculation
```python
result = calculate("2 + 3 * 4")  # Returns 14
```

### Using Variables
```python
# Store a variable
store_variable("x", 10)

# Use in calculation
result = calculate("x * 2 + 5")  # Returns 25
```

### Advanced Functions
```python
result = calculate("sqrt(16) + pow(2, 3)")  # Returns 8
result = calculate("sin(pi/2)")  # Returns 1.0
```

## Available Functions

- `sqrt(x)` - Square root
- `pow(x, y)` - Power
- `abs(x)` - Absolute value
- `sin(x)`, `cos(x)`, `tan(x)` - Trigonometric functions
- `log(x)`, `log10(x)`, `exp(x)` - Logarithmic and exponential
- `floor(x)`, `ceil(x)`, `round(x)` - Rounding functions
- `pi`, `e` - Mathematical constants

## Actions

- `calculate`: Evaluate a mathematical expression
- `store_variable`: Store a value in a variable
- `get_variable`: Retrieve a stored variable
- `list_variables`: List all stored variables
- `clear_variables`: Clear all stored variables
