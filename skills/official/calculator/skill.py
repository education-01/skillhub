#!/usr/bin/env python3
"""
Calculator Skill - Basic math operations with variable storage
"""

import math
import re
from typing import Dict, Any, Optional

class CalculatorSkill:
    """Calculator with variable storage support"""
    
    def __init__(self):
        self.variables: Dict[str, float] = {
            'pi': math.pi,
            'e': math.e,
        }
        self.safe_functions = {
            'sqrt': math.sqrt,
            'pow': pow,
            'abs': abs,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'floor': math.floor,
            'ceil': math.ceil,
            'round': round,
        }
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Dictionary with result or error
        """
        try:
            # Sanitize expression - only allow safe characters
            if not self._is_safe_expression(expression):
                return {
                    'success': False,
                    'error': 'Invalid characters in expression'
                }
            
            # Replace variable names with their values
            safe_expr = expression
            for var_name, var_value in sorted(self.variables.items(), key=lambda x: -len(x[0])):
                # Use word boundary to avoid partial replacements
                safe_expr = re.sub(r'\b' + re.escape(var_name) + r'\b', str(var_value), safe_expr)
            
            # Evaluate in a restricted namespace
            namespace = {**self.safe_functions, '__builtins__': {}}
            result = eval(safe_expr, namespace)
            
            return {
                'success': True,
                'expression': expression,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'expression': expression,
                'error': str(e)
            }
    
    def _is_safe_expression(self, expression: str) -> bool:
        """Check if expression contains only safe characters"""
        # Allow numbers, operators, parentheses, function names, variables, spaces
        allowed_pattern = r'^[\d\s\+\-\*\/\%\(\)\.\,\w]+$'
        return bool(re.match(allowed_pattern, expression))
    
    def store_variable(self, name: str, value: float) -> Dict[str, Any]:
        """
        Store a variable value
        
        Args:
            name: Variable name
            value: Variable value
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Validate variable name
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
                return {
                    'success': False,
                    'error': 'Invalid variable name. Use letters, numbers, and underscores, starting with a letter or underscore.'
                }
            
            self.variables[name] = float(value)
            return {
                'success': True,
                'variable': name,
                'value': value,
                'message': f'Stored {name} = {value}'
            }
        except (ValueError, TypeError) as e:
            return {
                'success': False,
                'error': f'Invalid value: {str(e)}'
            }
    
    def get_variable(self, name: str) -> Dict[str, Any]:
        """
        Get a stored variable value
        
        Args:
            name: Variable name
            
        Returns:
            Dictionary with variable value or error
        """
        if name in self.variables:
            return {
                'success': True,
                'variable': name,
                'value': self.variables[name]
            }
        else:
            return {
                'success': False,
                'error': f'Variable {name} not found'
            }
    
    def list_variables(self) -> Dict[str, Any]:
        """
        List all stored variables
        
        Returns:
            Dictionary with all variables
        """
        return {
            'success': True,
            'variables': dict(self.variables),
            'count': len(self.variables)
        }
    
    def clear_variables(self) -> Dict[str, Any]:
        """
        Clear all user-defined variables (keep constants)
        
        Returns:
            Dictionary with operation result
        """
        # Keep constants
        self.variables = {
            'pi': math.pi,
            'e': math.e,
        }
        return {
            'success': True,
            'message': 'All user-defined variables cleared'
        }


# Skill interface
_skill_instance = None

def get_skill():
    """Get or create skill instance"""
    global _skill_instance
    if _skill_instance is None:
        _skill_instance = CalculatorSkill()
    return _skill_instance


def execute(action: str, **kwargs) -> Dict[str, Any]:
    """
    Execute skill action
    
    Args:
        action: Action to perform (calculate, store_variable, get_variable, list_variables, clear_variables)
        **kwargs: Action-specific parameters
        
    Returns:
        Result dictionary
    """
    skill = get_skill()
    
    if action == 'calculate':
        expression = kwargs.get('expression')
        if not expression:
            return {'success': False, 'error': 'Missing expression parameter'}
        return skill.calculate(expression)
    
    elif action == 'store_variable':
        name = kwargs.get('name')
        value = kwargs.get('value')
        if not name or value is None:
            return {'success': False, 'error': 'Missing name or value parameter'}
        return skill.store_variable(name, value)
    
    elif action == 'get_variable':
        name = kwargs.get('name')
        if not name:
            return {'success': False, 'error': 'Missing name parameter'}
        return skill.get_variable(name)
    
    elif action == 'list_variables':
        return skill.list_variables()
    
    elif action == 'clear_variables':
        return skill.clear_variables()
    
    else:
        return {
            'success': False,
            'error': f'Unknown action: {action}. Available actions: calculate, store_variable, get_variable, list_variables, clear_variables'
        }


if __name__ == '__main__':
    # Test the skill
    print("Testing Calculator Skill...")
    
    # Test basic calculation
    result = execute('calculate', expression='2 + 3 * 4')
    print(f"2 + 3 * 4 = {result}")
    
    # Test variable storage
    result = execute('store_variable', name='x', value=10)
    print(f"Store x = 10: {result}")
    
    # Test calculation with variable
    result = execute('calculate', expression='x * 2 + 5')
    print(f"x * 2 + 5 = {result}")
    
    # Test advanced functions
    result = execute('calculate', expression='sqrt(16) + pow(2, 3)')
    print(f"sqrt(16) + pow(2, 3) = {result}")
    
    # List variables
    result = execute('list_variables')
    print(f"Variables: {result}")
