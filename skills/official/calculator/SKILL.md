---
name: calculator
description: "Perform mathematical calculations and expressions. Use when: user needs to calculate numbers, percentages, or evaluate math expressions. Supports basic arithmetic, advanced functions, and variable storage."
metadata: { "openclaw": { "emoji": "🧮" } }
---

# Calculator Skill

Perform mathematical calculations with Python expressions.

## When to Use

✅ **USE this skill when:**

- "Calculate 15% of 200"
- "What's 2 + 3 * 4?"
- "Compute sqrt(144)"
- "Convert 100 USD to EUR"
- Any math expression evaluation

## When NOT to Use

❌ **DON'T use this skill when:**

- Complex data analysis → use pandas/numpy directly
- Graphing/plotting → use matplotlib
- Symbolic math → use Wolfram Alpha
- Statistical analysis → use scipy

## Commands

### Basic Calculation

```bash
python3 -c "print(2 + 3 * 4)"
# Output: 14
```

### Percentage

```bash
python3 -c "print(200 * 0.15)"
# Output: 30.0
```

### Advanced Functions

```bash
# Square root
python3 -c "import math; print(math.sqrt(144))"

# Power
python3 -c "print(2 ** 10)"

# Trigonometry
python3 -c "import math; print(math.sin(math.pi/2))"
```

### With Variables

```bash
python3 -c "
x = 10
y = 20
print(f'Sum: {x + y}')
print(f'Product: {x * y}')
"
```

## Available Functions

- `abs(x)` — Absolute value
- `round(x, n)` — Round to n decimals
- `pow(x, y)` — x to the power of y
- `min(a, b, ...)` — Minimum value
- `max(a, b, ...)` — Maximum value
- `sum([...])` — Sum of values

### Math Module

```bash
python3 -c "import math; print(dir(math))"
```

- `math.sqrt(x)` — Square root
- `math.sin/cos/tan(x)` — Trigonometry
- `math.log(x), math.log10(x)` — Logarithms
- `math.floor(x), math.ceil(x)` — Rounding
- `math.pi, math.e` — Constants

## Quick Responses

**"Calculate 15% of 200"**
```bash
python3 -c "print(f'15% of 200 = {200 * 0.15}')"
```

**"What's 2^10?"**
```bash
python3 -c "print(f'2^10 = {2 ** 10}')"
```

**"Square root of 144"**
```bash
python3 -c "import math; print(f'√144 = {math.sqrt(144)}')"
```
