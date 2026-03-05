---
name: file-ops
version: 1.0.0
description: File operations - read, write, and directory listing
author: SkillHub
tags: file, io, directory, operations
---

# File Operations Skill

Perform file system operations including reading, writing, and directory listing.

## Features

- Read file contents
- Write to files (create/overwrite)
- Append to files
- List directory contents
- Create directories
- Check file/directory existence
- Get file information

## Usage

### Read File
```python
content = read_file("/path/to/file.txt")
```

### Write File
```python
result = write_file("/path/to/file.txt", "Hello, World!")
```

### List Directory
```python
files = list_directory("/path/to/directory")
```

### Create Directory
```python
result = create_directory("/path/to/new/directory")
```

## Actions

- `read_file`: Read file contents
- `write_file`: Write content to file (creates or overwrites)
- `append_file`: Append content to file
- `list_directory`: List directory contents
- `create_directory`: Create a new directory
- `file_exists`: Check if file exists
- `get_file_info`: Get file metadata

## Safety

- Validates paths to prevent directory traversal
- Respects file permissions
- Safe character encoding handling
