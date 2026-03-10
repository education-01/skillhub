"""Skill Exporters - Export skills to different formats.

Supports exporting to:
- Codex (~/.codex/skills/)
- Claude Code (format compatible)
"""
from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class TargetFormat(Enum):
    """Supported export targets."""
    CODEX = "codex"
    CLAUDE_CODE = "claude_code"


@dataclass
class SkillExport:
    """A skill ready for export."""
    name: str
    version: str
    description: str
    author: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Content
    skill_md_content: str = ""
    scripts: Dict[str, str] = field(default_factory=dict)
    references: Dict[str, str] = field(default_factory=dict)
    assets: Dict[str, bytes] = field(default_factory=dict)
    
    # Metadata
    short_description: str = ""
    default_prompt: str = ""


class SkillHubToCodexExporter:
    """Export SkillHub skills to Codex format."""
    
    # Codex skills directory
    CODEX_SKILLS_DIR = Path.home() / ".codex" / "skills"
    
    @staticmethod
    def export(skill_dir: Path, target_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Export a SkillHub skill to Codex format.
        
        Args:
            skill_dir: Source SkillHub skill directory
            target_dir: Target directory (default: ~/.codex/skills/<name>)
        
        Returns:
            Path to exported skill, or None if failed
        """
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None
        
        # Parse SkillHub skill
        export_data = SkillHubToCodexExporter._parse_skillhub(skill_dir)
        if not export_data:
            return None
        
        # Determine target directory
        target = target_dir or SkillHubToCodexExporter.CODEX_SKILLS_DIR / export_data.name
        
        # Create directory structure
        target.mkdir(parents=True, exist_ok=True)
        
        # Write SKILL.md in Codex format
        codex_skill_md = SkillHubToCodexExporter._to_codex_format(export_data)
        (target / "SKILL.md").write_text(codex_skill_md)
        
        # Create agents/openai.yaml
        agents_dir = target / "agents"
        agents_dir.mkdir(exist_ok=True)
        openai_yaml = SkillHubToCodexExporter._generate_openai_yaml(export_data)
        (agents_dir / "openai.yaml").write_text(openai_yaml)
        
        # Copy scripts
        if export_data.scripts:
            scripts_dir = target / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            for name, content in export_data.scripts.items():
                (scripts_dir / name).write_text(content)
        
        # Copy references
        if export_data.references:
            refs_dir = target / "references"
            refs_dir.mkdir(exist_ok=True)
            for name, content in export_data.references.items():
                (refs_dir / name).write_text(content)
        
        # Copy assets (binary files)
        if export_data.assets:
            assets_dir = target / "assets"
            assets_dir.mkdir(exist_ok=True)
            for name, content in export_data.assets.items():
                (assets_dir / name).write_bytes(content)
        
        return target
    
    @staticmethod
    def _parse_skillhub(skill_dir: Path) -> Optional[SkillExport]:
        """Parse a SkillHub skill directory."""
        skill_md = skill_dir / "SKILL.md"
        content = skill_md.read_text()
        
        # Parse frontmatter
        meta = {}
        readme = content
        
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                readme = parts[2].strip()
                
                current_list_key = None
                current_list = []
                
                for line in frontmatter.split('\n'):
                    stripped = line.strip()
                    
                    if stripped.startswith('- '):
                        if current_list_key:
                            current_list.append(stripped[2:].strip())
                        continue
                    
                    if ':' in line and not line.startswith(' '):
                        if current_list_key and current_list:
                            meta[current_list_key] = current_list
                            current_list = []
                        
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if value == '' or value == '[]':
                            current_list_key = key
                            current_list = []
                            continue
                        
                        if value.startswith('[') and value.endswith(']'):
                            value = [v.strip() for v in value[1:-1].split(',') if v.strip()]
                        
                        meta[key] = value
                        current_list_key = None
                
                if current_list_key and current_list:
                    meta[current_list_key] = current_list
        
        # Collect scripts
        scripts = {}
        for py_file in skill_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                scripts[py_file.name] = py_file.read_text()
        
        # Collect references
        references = {}
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            for ref_file in refs_dir.glob("*.md"):
                references[ref_file.name] = ref_file.read_text()
        
        # Collect assets
        assets = {}
        assets_dir = skill_dir / "assets"
        if assets_dir.exists():
            for asset_file in assets_dir.rglob("*"):
                if asset_file.is_file():
                    rel_path = str(asset_file.relative_to(assets_dir))
                    assets[rel_path] = asset_file.read_bytes()
        
        # Generate short description
        description = meta.get('description', '')
        short_desc = description[:60] + "..." if len(description) > 60 else description
        
        return SkillExport(
            name=meta.get('name', skill_dir.name),
            version=meta.get('version', '1.0.0'),
            description=description,
            author=meta.get('author', ''),
            tags=meta.get('tags', []) if isinstance(meta.get('tags'), list) else [],
            skill_md_content=readme,
            scripts=scripts,
            references=references,
            assets=assets,
            short_description=short_desc,
            default_prompt=f"Use the {meta.get('name', skill_dir.name)} skill",
        )
    
    @staticmethod
    def _to_codex_format(export: SkillExport) -> str:
        """Convert to Codex SKILL.md format."""
        tags_str = ", ".join(export.tags) if export.tags else "utility"
        
        return f"""---
name: {export.name}
description: {export.description}
metadata:
  short-description: {export.short_description}
  tags: [{tags_str}]
---

{export.skill_md_content}
"""
    
    @staticmethod
    def _generate_openai_yaml(export: SkillExport) -> str:
        """Generate agents/openai.yaml for Codex UI."""
        return f"""# OpenAI UI metadata for {export.name}
display_name: "{export.name.replace('-', ' ').title()}"
short_description: "{export.short_description}"
default_prompt: "{export.default_prompt}"
"""


class SkillHubToClaudeCodeExporter:
    """Export SkillHub skills to Claude Code format."""
    
    # Claude Code might use similar format to Codex
    CLAUDE_SKILLS_DIR = Path.home() / ".claude" / "skills"
    
    @staticmethod
    def export(skill_dir: Path, target_dir: Optional[Path] = None) -> Optional[Path]:
        """Export to Claude Code format (similar to Codex)."""
        target = target_dir or SkillHubToClaudeCodeExporter.CLAUDE_SKILLS_DIR
        return SkillHubToCodexExporter.export(skill_dir, target)


class SkillExporter:
    """Main skill exporter that handles all formats."""
    
    EXPORTERS = {
        TargetFormat.CODEX: SkillHubToCodexExporter,
        TargetFormat.CLAUDE_CODE: SkillHubToClaudeCodeExporter,
    }
    
    @staticmethod
    def export(
        skill_dir: Path,
        target: str = "codex",
        output_dir: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Export a skill to target format.
        
        Args:
            skill_dir: Source skill directory
            target: Target format (codex, claude_code)
            output_dir: Custom output directory
        
        Returns:
            Path to exported skill, or None if failed
        """
        target_format = TargetFormat(target.lower())
        exporter = SkillExporter.EXPORTERS.get(target_format)
        
        if exporter:
            return exporter.export(skill_dir, output_dir)
        
        return None
    
    @staticmethod
    def export_all(
        skills_dir: Path,
        target: str = "codex",
        output_dir: Optional[Path] = None,
        select: Optional[List[str]] = None,
    ) -> Dict[str, Optional[Path]]:
        """
        Export multiple skills.
        
        Args:
            skills_dir: Directory containing skills
            target: Target format
            output_dir: Custom output directory
            select: List of skill names to export (None = all)
        
        Returns:
            Dict mapping skill names to export paths
        """
        results = {}
        
        for skill_path in skills_dir.iterdir():
            if not skill_path.is_dir():
                continue
            
            if skill_path.name.startswith('.'):
                continue
            
            if select and skill_path.name not in select:
                continue
            
            skill_md = skill_path / "SKILL.md"
            if not skill_md.exists():
                continue
            
            results[skill_path.name] = SkillExporter.export(
                skill_path, target, output_dir
            )
        
        return results


# Convenience functions
def export_to_codex(
    skill_dir: Path,
    output_dir: Optional[Path] = None,
) -> Optional[Path]:
    """Export a skill to Codex format."""
    return SkillExporter.export(skill_dir, "codex", output_dir)


def export_to_claude_code(
    skill_dir: Path,
    output_dir: Optional[Path] = None,
) -> Optional[Path]:
    """Export a skill to Claude Code format."""
    return SkillExporter.export(skill_dir, "claude_code", output_dir)


def export_all_skills(
    skills_dir: Path,
    target: str = "codex",
    select: Optional[List[str]] = None,
) -> Dict[str, Optional[Path]]:
    """Export all (or selected) skills to target format."""
    return SkillExporter.export_all(skills_dir, target, select=select)
