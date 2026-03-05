#!/usr/bin/env python3
"""
File Operations Skill - Read, write, and manage files
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class FileOpsSkill:
    """File system operations"""
    
    def __init__(self, allowed_base_path: Optional[str] = None):
        """
        Initialize file operations skill
        
        Args:
            allowed_base_path: Optional base path to restrict operations
        """
        self.allowed_base_path = allowed_base_path
    
    def _validate_path(self, path: str) -> bool:
        """Validate path to prevent directory traversal"""
        try:
            # Resolve absolute path
            abs_path = os.path.abspath(path)
            
            # Check for directory traversal attempts
            if '..' in path:
                return False
            
            # If base path is set, ensure path is within it
            if self.allowed_base_path:
                abs_base = os.path.abspath(self.allowed_base_path)
                if not abs_path.startswith(abs_base):
                    return False
            
            return True
        except Exception:
            return False
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Read file contents
        
        Args:
            file_path: Path to file
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary with file contents or error
        """
        try:
            if not self._validate_path(file_path):
                return {
                    'success': False,
                    'error': 'Invalid path or access denied'
                }
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }
            
            if not os.path.isfile(file_path):
                return {
                    'success': False,
                    'error': f'Not a file: {file_path}'
                }
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                'success': True,
                'file_path': file_path,
                'content': content,
                'size': len(content)
            }
        except UnicodeDecodeError:
            # Try to read as binary if text fails
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                return {
                    'success': True,
                    'file_path': file_path,
                    'content': f'[Binary file, {len(content)} bytes]',
                    'is_binary': True,
                    'size': len(content)
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Write content to file
        
        Args:
            file_path: Path to file
            content: Content to write
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary with operation result
        """
        try:
            if not self._validate_path(file_path):
                return {
                    'success': False,
                    'error': 'Invalid path or access denied'
                }
            
            # Create parent directories if needed
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return {
                'success': True,
                'file_path': file_path,
                'message': f'File written successfully',
                'size': len(content)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def append_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Append content to file
        
        Args:
            file_path: Path to file
            content: Content to append
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary with operation result
        """
        try:
            if not self._validate_path(file_path):
                return {
                    'success': False,
                    'error': 'Invalid path or access denied'
                }
            
            # Create parent directories if needed
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            
            with open(file_path, 'a', encoding=encoding) as f:
                f.write(content)
            
            return {
                'success': True,
                'file_path': file_path,
                'message': f'Content appended successfully',
                'appended_size': len(content)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_directory(self, dir_path: str, pattern: str = '*') -> Dict[str, Any]:
        """
        List directory contents
        
        Args:
            dir_path: Path to directory
            pattern: Glob pattern to filter files (default: *)
            
        Returns:
            Dictionary with directory listing
        """
        try:
            if not self._validate_path(dir_path):
                return {
                    'success': False,
                    'error': 'Invalid path or access denied'
                }
            
            if not os.path.exists(dir_path):
                return {
                    'success': False,
                    'error': f'Directory not found: {dir_path}'
                }
            
            if not os.path.isdir(dir_path):
                return {
                    'success': False,
                    'error': f'Not a directory: {dir_path}'
                }
            
            # List files with pattern
            path_obj = Path(dir_path)
            items = []
            
            for item in path_obj.glob(pattern):
                try:
                    stat = item.stat()
                    items.append({
                        'name': item.name,
                        'path': str(item),
                        'is_file': item.is_file(),
                        'is_dir': item.is_dir(),
                        'size': stat.st_size if item.is_file() else None,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except Exception:
                    items.append({
                        'name': item.name,
                        'path': str(item),
                        'is_file': item.is_file(),
                        'is_dir': item.is_dir(),
                        'error': 'Could not get file info'
                    })
            
            return {
                'success': True,
                'directory': dir_path,
                'items': items,
                'count': len(items)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_directory(self, dir_path: str) -> Dict[str, Any]:
        """
        Create a new directory
        
        Args:
            dir_path: Path to new directory
            
        Returns:
            Dictionary with operation result
        """
        try:
            if not self._validate_path(dir_path):
                return {
                    'success': False,
                    'error': 'Invalid path or access denied'
                }
            
            if os.path.exists(dir_path):
                return {
                    'success': False,
                    'error': f'Directory already exists: {dir_path}'
                }
            
            os.makedirs(dir_path, exist_ok=False)
            
            return {
                'success': True,
                'directory': dir_path,
                'message': f'Directory created successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def file_exists(self, path: str) -> Dict[str, Any]:
        """
        Check if file or directory exists
        
        Args:
            path: Path to check
            
        Returns:
            Dictionary with existence check result
        """
        try:
            if not self._validate_path(path):
                return {
                    'success': False,
                    'error': 'Invalid path or access denied'
                }
            
            exists = os.path.exists(path)
            is_file = os.path.isfile(path) if exists else False
            is_dir = os.path.isdir(path) if exists else False
            
            return {
                'success': True,
                'path': path,
                'exists': exists,
                'is_file': is_file,
                'is_dir': is_dir
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file metadata
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        try:
            if not self._validate_path(file_path):
                return {
                    'success': False,
                    'error': 'Invalid path or access denied'
                }
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'Path not found: {file_path}'
                }
            
            stat = os.stat(file_path)
            
            return {
                'success': True,
                'path': file_path,
                'is_file': os.path.isfile(file_path),
                'is_dir': os.path.isdir(file_path),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'permissions': oct(stat.st_mode)[-3:]
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Skill interface
_skill_instance = None

def get_skill():
    """Get or create skill instance"""
    global _skill_instance
    if _skill_instance is None:
        _skill_instance = FileOpsSkill()
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
    
    if action == 'read_file':
        file_path = kwargs.get('file_path') or kwargs.get('path')
        encoding = kwargs.get('encoding', 'utf-8')
        if not file_path:
            return {'success': False, 'error': 'Missing file_path parameter'}
        return skill.read_file(file_path, encoding)
    
    elif action == 'write_file':
        file_path = kwargs.get('file_path') or kwargs.get('path')
        content = kwargs.get('content')
        encoding = kwargs.get('encoding', 'utf-8')
        if not file_path or content is None:
            return {'success': False, 'error': 'Missing file_path or content parameter'}
        return skill.write_file(file_path, content, encoding)
    
    elif action == 'append_file':
        file_path = kwargs.get('file_path') or kwargs.get('path')
        content = kwargs.get('content')
        encoding = kwargs.get('encoding', 'utf-8')
        if not file_path or content is None:
            return {'success': False, 'error': 'Missing file_path or content parameter'}
        return skill.append_file(file_path, content, encoding)
    
    elif action == 'list_directory':
        dir_path = kwargs.get('dir_path') or kwargs.get('path')
        pattern = kwargs.get('pattern', '*')
        if not dir_path:
            return {'success': False, 'error': 'Missing dir_path parameter'}
        return skill.list_directory(dir_path, pattern)
    
    elif action == 'create_directory':
        dir_path = kwargs.get('dir_path') or kwargs.get('path')
        if not dir_path:
            return {'success': False, 'error': 'Missing dir_path parameter'}
        return skill.create_directory(dir_path)
    
    elif action == 'file_exists':
        path = kwargs.get('path') or kwargs.get('file_path')
        if not path:
            return {'success': False, 'error': 'Missing path parameter'}
        return skill.file_exists(path)
    
    elif action == 'get_file_info':
        file_path = kwargs.get('file_path') or kwargs.get('path')
        if not file_path:
            return {'success': False, 'error': 'Missing file_path parameter'}
        return skill.get_file_info(file_path)
    
    else:
        return {
            'success': False,
            'error': f'Unknown action: {action}. Available actions: read_file, write_file, append_file, list_directory, create_directory, file_exists, get_file_info'
        }


if __name__ == '__main__':
    # Test the skill
    print("Testing File Operations Skill...")
    
    # Test write
    test_file = '/tmp/test_file_ops.txt'
    result = execute('write_file', file_path=test_file, content='Hello, World!\n')
    print(f"Write result: {result}")
    
    # Test read
    result = execute('read_file', file_path=test_file)
    print(f"Read result: {result}")
    
    # Test append
    result = execute('append_file', file_path=test_file, content='Appended line\n')
    print(f"Append result: {result}")
    
    # Test file exists
    result = execute('file_exists', path=test_file)
    print(f"Exists: {result}")
    
    # Test list directory
    result = execute('list_directory', dir_path='/tmp', pattern='test_*')
    print(f"List result: {result.get('count')} items")
    
    # Test get file info
    result = execute('get_file_info', file_path=test_file)
    print(f"File info: {result}")
