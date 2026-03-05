#!/usr/bin/env python3
"""
Code Execution Skill - Python code execution in a secure sandbox
"""

import sys
import traceback
from io import StringIO
from typing import Dict, Any, List, Optional, Any
import signal
import threading


class TimeoutException(Exception):
    """Timeout exception for code execution"""
    pass


def timeout_handler(signum, frame):
    """Handle timeout"""
    raise TimeoutException("Code execution timed out")


class CodeExecSkill:
    """Secure Python code execution"""
    
    def __init__(self, timeout_seconds: int = 5, max_output_size: int = 10000):
        """
        Initialize code execution skill
        
        Args:
            timeout_seconds: Maximum execution time
            max_output_size: Maximum output size in characters
        """
        self.timeout = timeout_seconds
        self.max_output_size = max_output_size
        
        # Safe builtins - restricted set
        self.safe_builtins = {
            # Basic functions
            'print': print,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sorted': sorted,
            'reversed': reversed,
            'any': any,
            'all': all,
            'min': min,
            'max': max,
            'abs': abs,
            'sum': sum,
            'round': round,
            'pow': pow,
            'divmod': divmod,
            
            # Types
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'frozenset': frozenset,
            'bytes': bytes,
            'bytearray': bytearray,
            
            # Type checking
            'type': type,
            'isinstance': isinstance,
            'issubclass': issubclass,
            'hasattr': hasattr,
            'getattr': getattr,
            'setattr': setattr,
            'callable': callable,
            
            # Other safe functions
            'chr': chr,
            'ord': ord,
            'hex': hex,
            'oct': oct,
            'bin': bin,
            'id': id,
            'hash': hash,
            'repr': repr,
            'format': format,
            
            # Constants
            'True': True,
            'False': False,
            'None': None,
            
            # Exceptions (for try/except)
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'KeyError': KeyError,
            'IndexError': IndexError,
            'AttributeError': AttributeError,
            'RuntimeError': RuntimeError,
            'StopIteration': StopIteration,
        }
    
    def execute_code(
        self, 
        code: str, 
        variables: Optional[Dict[str, Any]] = None,
        return_variables: bool = False
    ) -> Dict[str, Any]:
        """
        Execute Python code
        
        Args:
            code: Python code to execute
            variables: Initial variables to inject
            return_variables: Return all defined variables
            
        Returns:
            Dictionary with execution result
        """
        # Validate code
        if not code or not isinstance(code, str):
            return {
                'success': False,
                'error': 'Invalid code: must be a non-empty string'
            }
        
        # Check code size
        if len(code) > 50000:  # 50KB limit
            return {
                'success': False,
                'error': 'Code too large (max 50KB)'
            }
        
        # Syntax check first
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return {
                'success': False,
                'error': f'Syntax error: {e.msg} at line {e.lineno}',
                'line': e.lineno
            }
        
        # Prepare execution environment
        exec_globals = {'__builtins__': self.safe_builtins}
        exec_locals = dict(variables) if variables else {}
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            # Execute with timeout (using threading for cross-platform)
            result_container = {'done': False, 'error': None}
            
            def run_code():
                try:
                    exec(code, exec_globals, exec_locals)
                    result_container['done'] = True
                except Exception as e:
                    result_container['error'] = e
            
            thread = threading.Thread(target=run_code)
            thread.daemon = True
            thread.start()
            thread.join(timeout=self.timeout)
            
            if thread.is_alive():
                return {
                    'success': False,
                    'error': f'Execution timed out (max {self.timeout}s)'
                }
            
            if result_container['error']:
                raise result_container['error']
            
            # Get captured output
            output = sys.stdout.getvalue()
            if len(output) > self.max_output_size:
                output = output[:self.max_output_size] + '\n... (output truncated)'
            
            result = {
                'success': True,
                'output': output,
            }
            
            # Return variables if requested
            if return_variables:
                # Filter out internal variables
                safe_vars = {
                    k: self._serialize_value(v) 
                    for k, v in exec_locals.items()
                    if not k.startswith('_')
                }
                result['variables'] = safe_vars
            
            # Check for a 'result' variable
            if 'result' in exec_locals:
                result['result'] = self._serialize_value(exec_locals['result'])
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            # Get traceback
            tb_lines = traceback.format_exception(type(e), e, e.__traceback__)
            tb_text = ''.join(tb_lines[-3:])  # Last 3 lines
            
            return {
                'success': False,
                'error': f'{error_type}: {error_msg}',
                'traceback': tb_text
            }
        finally:
            sys.stdout = old_stdout
    
    def execute_function(
        self,
        code: str,
        function_name: str,
        args: Optional[List] = None,
        kwargs: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute a specific function from code
        
        Args:
            code: Python code containing the function
            function_name: Name of function to call
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Dictionary with function result
        """
        args = args or []
        kwargs = kwargs or {}
        
        # First execute the code to define the function
        exec_result = self.execute_code(code, return_variables=True)
        
        if not exec_result['success']:
            return exec_result
        
        # Check if function exists
        if function_name not in exec_result.get('variables', {}):
            return {
                'success': False,
                'error': f'Function {function_name} not found in code'
            }
        
        # Get the function
        exec_globals = {'__builtins__': self.safe_builtins}
        exec_locals = {}
        exec(code, exec_globals, exec_locals)
        func = exec_locals[function_name]
        
        if not callable(func):
            return {
                'success': False,
                'error': f'{function_name} is not callable'
            }
        
        # Call the function
        try:
            result = func(*args, **kwargs)
            return {
                'success': True,
                'result': self._serialize_value(result)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'{type(e).__name__}: {str(e)}'
            }
    
    def test_code(self, code: str) -> Dict[str, Any]:
        """
        Test code syntax without executing
        
        Args:
            code: Python code to test
            
        Returns:
            Dictionary with syntax check result
        """
        try:
            compile(code, '<string>', 'exec')
            return {
                'success': True,
                'message': 'Syntax OK'
            }
        except SyntaxError as e:
            return {
                'success': False,
                'error': f'Syntax error: {e.msg}',
                'line': e.lineno,
                'offset': e.offset
            }
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize a value for safe return"""
        try:
            # Try to serialize basic types
            if isinstance(value, (str, int, float, bool, type(None))):
                return value
            elif isinstance(value, (list, tuple)):
                return [self._serialize_value(v) for v in value]
            elif isinstance(value, dict):
                return {str(k): self._serialize_value(v) for k, v in value.items()}
            elif isinstance(value, set):
                return [self._serialize_value(v) for v in value]
            else:
                # For other types, return string representation
                return str(value)
        except Exception:
            return f'<{type(value).__name__}>'


# Skill interface
_skill_instance = None

def get_skill():
    """Get or create skill instance"""
    global _skill_instance
    if _skill_instance is None:
        _skill_instance = CodeExecSkill()
    return _skill_instance


def execute(action: str, **kwargs) -> Dict[str, Any]:
    """
    Execute skill action
    
    Args:
        action: Action to perform
        **kwargs: Action-specific parameters
        
    Returns:
        Result dictionary
    """
    skill = get_skill()
    
    if action == 'execute_code':
        code = kwargs.get('code')
        variables = kwargs.get('variables')
        return_variables = kwargs.get('return_variables', False)
        
        if not code:
            return {'success': False, 'error': 'Missing code parameter'}
        
        return skill.execute_code(code, variables, return_variables)
    
    elif action == 'execute_function':
        code = kwargs.get('code')
        function_name = kwargs.get('function_name')
        args = kwargs.get('args', [])
        kwargs_dict = kwargs.get('kwargs', {})
        
        if not code or not function_name:
            return {'success': False, 'error': 'Missing code or function_name parameter'}
        
        return skill.execute_function(code, function_name, args, kwargs_dict)
    
    elif action == 'test_code':
        code = kwargs.get('code')
        if not code:
            return {'success': False, 'error': 'Missing code parameter'}
        return skill.test_code(code)
    
    elif action == 'get_variables':
        code = kwargs.get('code')
        if not code:
            return {'success': False, 'error': 'Missing code parameter'}
        return skill.execute_code(code, return_variables=True)
    
    else:
        return {
            'success': False,
            'error': f'Unknown action: {action}. Available actions: execute_code, execute_function, test_code, get_variables'
        }


if __name__ == '__main__':
    # Test the skill
    print("Testing Code Execution Skill...")
    
    # Test basic execution
    code1 = """
x = 10
y = 20
result = x + y
print(f"Sum: {result}")
"""
    result = execute('execute_code', code=code1, return_variables=True)
    print(f"Basic execution: {result}")
    
    # Test with variables
    code2 = "result = a * b + c"
    result = execute('execute_code', code=code2, variables={'a': 5, 'b': 3, 'c': 2})
    print(f"With variables: {result}")
    
    # Test function execution
    code3 = """
def calculate(x, y):
    return x ** y + 100
"""
    result = execute('execute_function', code=code3, function_name='calculate', args=[2, 10])
    print(f"Function execution: {result}")
    
    # Test syntax check
    code4 = "x = [1, 2, 3"
    result = execute('test_code', code=code4)
    print(f"Syntax test: {result}")
    
    # Test timeout
    code5 = "while True: pass"
    result = execute('execute_code', code=code5)
    print(f"Timeout test: {result}")
