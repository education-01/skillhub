"""Calculator skill.

Perform mathematical calculations.
"""
from __future__ import annotations

import math
import re
from typing import Union


SKILL_INFO = {
    "name": "calculator",
    "version": "1.0.0",
    "description": "Perform mathematical calculations",
}

# Allowed names in eval
SAFE_NAMES = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "pi": math.pi,
    "e": math.e,
    "ceil": math.ceil,
    "floor": math.floor,
    "factorial": math.factorial,
}


def calculate(expression: str) -> Union[float, int, str]:
    """
    Calculate a mathematical expression.
    
    Args:
        expression: Math expression (e.g., "2 + 2", "sqrt(16)")
    
    Returns:
        Result of calculation
    """
    # Clean expression
    expr = expression.strip()
    
    # Basic validation
    if not expr:
        return "Error: Empty expression"
    
    # Check for dangerous patterns
    dangerous = ["import", "exec", "eval", "__", "open", "file"]
    for word in dangerous:
        if word in expr.lower():
            return f"Error: Forbidden word: {word}"
    
    try:
        # Use eval with restricted globals
        result = eval(expr, {"__builtins__": {}}, SAFE_NAMES)
        
        # Round to reasonable precision
        if isinstance(result, float):
            if result.is_integer():
                return int(result)
            return round(result, 10)
        
        return result
    except ZeroDivisionError:
        return "Error: Division by zero"
    except SyntaxError as e:
        return f"Error: Invalid syntax - {e}"
    except Exception as e:
        return f"Error: {e}"


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert between units.
    
    Args:
        value: Value to convert
        from_unit: Source unit
        to_unit: Target unit
    
    Returns:
        Converted value
    """
    # Conversion factors (to base unit)
    length = {
        "m": 1, "meter": 1, "meters": 1,
        "km": 1000, "kilometer": 1000, "kilometers": 1000,
        "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01,
        "mm": 0.001, "millimeter": 0.001, "millimeters": 0.001,
        "in": 0.0254, "inch": 0.0254, "inches": 0.0254,
        "ft": 0.3048, "foot": 0.3048, "feet": 0.3048,
        "yd": 0.9144, "yard": 0.9144, "yards": 0.9144,
        "mi": 1609.344, "mile": 1609.344, "miles": 1609.344,
    }
    
    weight = {
        "g": 1, "gram": 1, "grams": 1,
        "kg": 1000, "kilogram": 1000, "kilograms": 1000,
        "mg": 0.001, "milligram": 0.001, "milligrams": 0.001,
        "lb": 453.592, "pound": 453.592, "pounds": 453.592,
        "oz": 28.3495, "ounce": 28.3495, "ounces": 28.3495,
    }
    
    temperature = {
        "c": "celsius", "celsius": "celsius",
        "f": "fahrenheit", "fahrenheit": "fahrenheit",
        "k": "kelvin", "kelvin": "kelvin",
    }
    
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    # Length conversion
    if from_unit in length and to_unit in length:
        base = value * length[from_unit]
        return base / length[to_unit]
    
    # Weight conversion
    if from_unit in weight and to_unit in weight:
        base = value * weight[from_unit]
        return base / weight[to_unit]
    
    # Temperature conversion (special case)
    if from_unit in temperature and to_unit in temperature:
        from_t = temperature[from_unit]
        to_t = temperature[to_unit]
        
        # Convert to Celsius first
        if from_t == "fahrenheit":
            celsius = (value - 32) * 5/9
        elif from_t == "kelvin":
            celsius = value - 273.15
        else:
            celsius = value
        
        # Convert from Celsius to target
        if to_t == "fahrenheit":
            return celsius * 9/5 + 32
        elif to_t == "kelvin":
            return celsius + 273.15
        else:
            return celsius
    
    raise ValueError(f"Cannot convert from {from_unit} to {to_unit}")


def execute(params: dict) -> dict:
    """
    Execute calculator skill.
    
    Args:
        params: Dict with 'expression' or 'value', 'from', 'to' for conversion
    
    Returns:
        Result dict
    """
    # Check for conversion
    if "value" in params and "from" in params and "to" in params:
        try:
            result = convert(
                float(params["value"]),
                params["from"],
                params["to"],
            )
            return {
                "success": True,
                "result": result,
                "from": params["from"],
                "to": params["to"],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    # Regular calculation
    expression = params.get("expression") or params.get("expr")
    if not expression:
        return {
            "success": False,
            "error": "Expression is required",
        }
    
    result = calculate(expression)
    
    if isinstance(result, str) and result.startswith("Error"):
        return {
            "success": False,
            "error": result,
        }
    
    return {
        "success": True,
        "expression": expression,
        "result": result,
    }


if __name__ == "__main__":
    # Demo
    print("Calculator Demo")
    print("=" * 40)
    
    tests = [
        "2 + 2",
        "10 * 5",
        "sqrt(16)",
        "sin(pi/2)",
        "2 ** 10",
        "sum([1, 2, 3, 4, 5])",
    ]
    
    for expr in tests:
        result = calculate(expr)
        print(f"  {expr} = {result}")
    
    print("\nConversions:")
    print(f"  100 km to miles = {convert(100, 'km', 'mi'):.2f}")
    print(f"  100°F to °C = {convert(100, 'f', 'c'):.1f}")
