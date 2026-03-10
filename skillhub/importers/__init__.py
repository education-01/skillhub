"""Skill Importers - Import skills from different formats.

Supports importing from:
- OpenClaw SKILL.md format
- Claude Code SKILL.md format  
- Codex skill format
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class SkillFormat(Enum):
    """Supported skill formats."""
    SKILLHUB = "skillhub"
    OPENCLAW = "openclaw"
    CLAUDE_CODE = "claude_code"
    CODEX = "codex"
    UNKNOWN = "unknown"


@dataclass
class ImportedSkill:
    """A skill imported from another format."""
    name: str
    version: str
    description: str
    author: str = "Imported"
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # Original format info
    source_format: SkillFormat = SkillFormat.UNKNOWN
    original_path: Optional[Path] = None
    
    # Content
    skill_md: str = ""
    readme: str = ""
    scripts: Dict[str, str] = field(default_factory=dict)
    
    def to_skillhub_format(self) -> str:
        """Convert to SkillHub SKILL.md format."""
        tags_str = "\n".join(f"  - {t}" for t in self.tags) if self.tags else "  - imported"
        deps_str = "\n".join(f"  - {d}" for d in self.dependencies) if self.dependencies else "  []"
        
        return f"""---
name: {self.name}
version: {self.version}
description: {self.description}
author: {self.author}
tags:
{tags_str}
dependencies:
{deps_str}
license: MIT
---

# {self.name}

{self.description}

## Usage

{self._generate_usage()}

## Imported from {self.source_format.value}

This skill was imported from {self.source_format.value} format.
Original path: {self.original_path or 'N/A'}
"""

    def _generate_usage(self) -> str:
        """Generate usage documentation."""
        if self.scripts:
            module_name = self.name.replace('-', '_')
            return f"""```python
from {module_name} import execute

result = execute({{'param': 'value'}})
print(result)
```"""
        return "See skill documentation for usage."


class FormatDetector:
    """Detect skill format from SKILL.md content."""
    
    @staticmethod
    def detect(content: str, path: Optional[Path] = None) -> SkillFormat:
        """Detect the format of a SKILL.md file."""
        
        # Check for OpenClaw format (has 'activate when' or specific OpenClaw markers)
        if FormatDetector._is_openclaw(content, path):
            return SkillFormat.OPENCLAW
        
        # Check for Claude Code format
        if FormatDetector._is_claude_code(content, path):
            return SkillFormat.CLAUDE_CODE
        
        # Check for Codex format
        if FormatDetector._is_codex(content, path):
            return SkillFormat.CODEX
        
        # Check for SkillHub format (standard frontmatter)
        if FormatDetector._is_skillhub(content):
            return SkillFormat.SKILLHUB
        
        return SkillFormat.UNKNOWN
    
    @staticmethod
    def _is_openclaw(content: str, path: Optional[Path]) -> bool:
        """Check if OpenClaw format."""
        # OpenClaw skills typically have these markers
        markers = ['activate when', 'location:', 'SKILL.md']
        
        # Check if path contains .openclaw
        if path and '.openclaw' in str(path):
            return True
        
        # Check content markers
        content_lower = content.lower()
        if 'activate when' in content_lower:
            return True
        if 'location:' in content_lower and 'name:' in content_lower:
            return True
        
        return False
    
    @staticmethod
    def _is_claude_code(content: str, path: Optional[Path]) -> bool:
        """Check if Claude Code format."""
        content_lower = content.lower()
        
        # Claude Code has similar format but with instructions
        if 'claude' in content_lower and 'instructions' in content_lower:
            return True
        
        return False
    
    @staticmethod
    def _is_codex(content: str, path: Optional[Path]) -> bool:
        """Check if Codex format."""
        content_lower = content.lower()
        
        # Codex might have specific markers
        if 'codex' in content_lower:
            return True
        
        return False
    
    @staticmethod
    def _is_skillhub(content: str) -> bool:
        """Check if SkillHub format."""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                required = ['name:', 'version:', 'description:']
                return all(r in frontmatter for r in required)
        return False


class BaseImporter:
    """Base class for skill importers."""
    
    @staticmethod
    def parse_frontmatter(content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter."""
        meta = {}
        
        if not content.startswith('---'):
            return meta
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return meta
        
        frontmatter = parts[1].strip()
        
        current_list_key = None
        current_list = []
        
        for line in frontmatter.split('\n'):
            stripped = line.strip()
            
            # List item
            if stripped.startswith('- '):
                if current_list_key:
                    current_list.append(stripped[2:].strip())
                continue
            
            # Key-value pair
            if ':' in line and not line.startswith(' '):
                # Save previous list
                if current_list_key and current_list:
                    meta[current_list_key] = current_list
                    current_list = []
                
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                # Start new list
                if value == '' or value == '[]':
                    current_list_key = key
                    current_list = []
                    continue
                
                # Handle inline list
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip() for v in value[1:-1].split(',') if v.strip()]
                
                meta[key] = value
                current_list_key = None
        
        # Save final list
        if current_list_key and current_list:
            meta[current_list_key] = current_list
        
        return meta
    
    @staticmethod
    def extract_readme(content: str) -> str:
        """Extract README content after frontmatter."""
        if not content.startswith('---'):
            return content
        
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[2].strip()
        
        return ""


class OpenClawImporter(BaseImporter):
    """Import skills from OpenClaw format."""
    
    @staticmethod
    def import_skill(skill_dir: Path) -> Optional[ImportedSkill]:
        """Import a skill from OpenClaw format."""
        skill_md_path = skill_dir / "SKILL.md"
        
        if not skill_md_path.exists():
            return None
        
        content = skill_md_path.read_text()
        
        # Parse frontmatter
        meta = OpenClawImporter.parse_frontmatter(content)
        readme = OpenClawImporter.extract_readme(content)
        
        # Find scripts
        scripts = {}
        for py_file in skill_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                scripts[py_file.name] = py_file.read_text()
        
        # Create imported skill
        skill = ImportedSkill(
            name=meta.get('name', skill_dir.name),
            version=meta.get('version', '1.0.0'),
            description=meta.get('description', ''),
            author=meta.get('author', 'Unknown'),
            tags=meta.get('tags', []) if isinstance(meta.get('tags'), list) else [],
            dependencies=meta.get('dependencies', []) if isinstance(meta.get('dependencies'), list) else [],
            source_format=SkillFormat.OPENCLAW,
            original_path=skill_dir,
            skill_md=content,
            readme=readme,
            scripts=scripts,
        )
        
        return skill


class ClaudeCodeImporter(BaseImporter):
    """Import skills from Claude Code format."""
    
    @staticmethod
    def import_skill(skill_dir: Path) -> Optional[ImportedSkill]:
        """Import a skill from Claude Code format."""
        skill_md_path = skill_dir / "SKILL.md"
        
        if not skill_md_path.exists():
            return None
        
        content = skill_md_path.read_text()
        
        meta = ClaudeCodeImporter.parse_frontmatter(content)
        readme = ClaudeCodeImporter.extract_readme(content)
        
        scripts = {}
        for py_file in skill_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                scripts[py_file.name] = py_file.read_text()
        
        skill = ImportedSkill(
            name=meta.get('name', skill_dir.name),
            version=meta.get('version', '1.0.0'),
            description=meta.get('description', ''),
            author=meta.get('author', 'Unknown'),
            tags=meta.get('tags', []) if isinstance(meta.get('tags'), list) else [],
            dependencies=meta.get('dependencies', []) if isinstance(meta.get('dependencies'), list) else [],
            source_format=SkillFormat.CLAUDE_CODE,
            original_path=skill_dir,
            skill_md=content,
            readme=readme,
            scripts=scripts,
        )
        
        return skill


class CodexImporter(BaseImporter):
    """Import skills from Codex format."""
    
    @staticmethod
    def import_skill(skill_dir: Path) -> Optional[ImportedSkill]:
        """Import a skill from Codex format."""
        skill_md_path = skill_dir / "SKILL.md"
        
        if not skill_md_path.exists():
            return None
        
        content = skill_md_path.read_text()
        
        meta = CodexImporter.parse_frontmatter(content)
        readme = CodexImporter.extract_readme(content)
        
        scripts = {}
        for py_file in skill_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                scripts[py_file.name] = py_file.read_text()
        
        skill = ImportedSkill(
            name=meta.get('name', skill_dir.name),
            version=meta.get('version', '1.0.0'),
            description=meta.get('description', ''),
            author=meta.get('author', 'Unknown'),
            tags=meta.get('tags', []) if isinstance(meta.get('tags'), list) else [],
            dependencies=meta.get('dependencies', []) if isinstance(meta.get('dependencies'), list) else [],
            source_format=SkillFormat.CODEX,
            original_path=skill_dir,
            skill_md=content,
            readme=readme,
            scripts=scripts,
        )
        
        return skill


class SkillImporter:
    """Main skill importer that handles all formats."""
    
    IMPORTERS = {
        SkillFormat.OPENCLAW: OpenClawImporter,
        SkillFormat.CLAUDE_CODE: ClaudeCodeImporter,
        SkillFormat.CODEX: CodexImporter,
    }
    
    @staticmethod
    def detect_and_import(skill_dir: Path) -> Optional[ImportedSkill]:
        """Detect format and import skill."""
        skill_md_path = skill_dir / "SKILL.md"
        
        if not skill_md_path.exists():
            return None
        
        content = skill_md_path.read_text()
        detected_format = FormatDetector.detect(content, skill_dir)
        
        if detected_format == SkillFormat.SKILLHUB:
            # Already in correct format
            return None
        
        importer = SkillImporter.IMPORTERS.get(detected_format)
        if importer:
            return importer.import_skill(skill_dir)
        
        # Try all importers
        for fmt, importer in SkillImporter.IMPORTERS.items():
            result = importer.import_skill(skill_dir)
            if result:
                result.source_format = fmt
                return result
        
        return None
    
    @staticmethod
    def convert_to_skillhub(
        imported: ImportedSkill,
        output_dir: Path,
        include_scripts: bool = True,
    ) -> Path:
        """Convert imported skill to SkillHub format."""
        skill_dir = output_dir / imported.name.replace(' ', '-').lower()
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Write SKILL.md
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(imported.to_skillhub_format())
        
        # Write scripts if available
        if include_scripts and imported.scripts:
            for script_name, script_content in imported.scripts.items():
                script_path = skill_dir / script_name
                script_path.write_text(script_content)
        
        # Write README
        if imported.readme:
            readme_path = skill_dir / "README.md"
            readme_path.write_text(imported.readme)
        
        return skill_dir


# Convenience function
def import_skill(
    source_path: Path,
    output_dir: Optional[Path] = None,
    format: Optional[str] = None,
) -> Optional[Path]:
    """
    Import a skill from another format.
    
    Args:
        source_path: Path to source skill directory
        output_dir: Output directory (default: current)
        format: Force format (openclaw, claude_code, codex)
    
    Returns:
        Path to converted skill, or None if failed
    """
    output_dir = output_dir or Path.cwd()
    
    if format:
        format_enum = SkillFormat(format.lower())
        importer = SkillImporter.IMPORTERS.get(format_enum)
        if importer:
            imported = importer.import_skill(source_path)
        else:
            return None
    else:
        imported = SkillImporter.detect_and_import(source_path)
    
    if imported:
        return SkillImporter.convert_to_skillhub(imported, output_dir)
    
    return None
