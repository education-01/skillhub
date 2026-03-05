---
name: file-ops
description: "File operations: read, write, list, delete files and directories. Use when: user needs to manage files, read content, or organize directories. Handle with care - file operations can be destructive."
metadata: { "openclaw": { "emoji": "📁" } }
---

# File Operations Skill

Read, write, list, and manage files and directories.

## When to Use

✅ **USE this skill when:**

- "Read the file..."
- "Create a file..."
- "List files in..."
- "Delete..."
- "Copy/move..."
- File management tasks

## When NOT to Use

❌ **DON'T use this skill when:**

- Editing code → use code editor
- Binary file operations → use specialized tools
- Large file processing → use streaming
- System files → be very careful!

## Commands

### Read File

```bash
# Read entire file
cat /path/to/file.txt

# Read with line numbers
cat -n /path/to/file.txt

# Read first/last lines
head -20 /path/to/file.txt
tail -20 /path/to/file.txt
```

### Write File

```bash
# Write content
echo "Hello World" > /path/to/file.txt

# Append content
echo "More text" >> /path/to/file.txt

# Write multiple lines
cat > /path/to/file.txt << 'EOF'
Line 1
Line 2
Line 3
EOF
```

### List Directory

```bash
# List files
ls -la /path/to/directory

# List recursively
find /path/to/directory -type f

# List by extension
ls *.py
```

### Copy/Move

```bash
# Copy file
cp /source/file.txt /dest/file.txt

# Copy directory
cp -r /source/dir /dest/dir

# Move/rename
mv /old/path /new/path
```

### Delete

```bash
# Delete file
rm /path/to/file.txt

# Delete directory
rm -rf /path/to/directory

# ⚠️ BE CAREFUL with rm -rf!
```

### Check File Info

```bash
# File exists?
test -f /path/to/file && echo "exists" || echo "not found"

# Directory exists?
test -d /path/to/dir && echo "exists" || echo "not found"

# File size
du -h /path/to/file

# File permissions
stat /path/to/file
```

## Quick Responses

**"Read the config file"**

```bash
cat ~/.config/app/config.yaml
```

**"List all Python files"**

```bash
find . -name "*.py" -type f
```

**"Create a new file with content"**

```bash
cat > /path/to/newfile.txt << 'EOF'
Your content here
EOF
```

## Safety Notes

⚠️ **Destructive Operations:**
- `rm` - Cannot be undone
- `mv` - Overwrites destination
- `>` - Overwrites file content

**Best Practices:**
- Use `trash` instead of `rm` when available
- Backup important files
- Double-check paths before deleting
