"""SkillHub - Skill Management Platform.

A platform for creating, sharing, and managing AI agent skills.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import re


@dataclass
class SkillMeta:
    """Skill metadata."""
    name: str
    version: str
    description: str
    author: str
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    min_python: str = "3.10"
    license: str = "MIT"
    homepage: Optional[str] = None
    repository: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "min_python": self.min_python,
            "license": self.license,
            "homepage": self.homepage,
            "repository": self.repository,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillMeta":
        return cls(
            name=data.get("name", ""),
            version=data.get("version", "0.0.1"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            min_python=data.get("min_python", "3.10"),
            license=data.get("license", "MIT"),
            homepage=data.get("homepage"),
            repository=data.get("repository"),
        )


@dataclass
class SkillFile:
    """A file in a skill."""
    path: str
    content: str
    file_type: str  # "skill", "script", "config", "doc"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "content": self.content,
            "file_type": self.file_type,
        }


@dataclass
class Skill:
    """A complete skill package."""
    meta: SkillMeta
    files: List[SkillFile] = field(default_factory=list)
    readme: str = ""
    skilL_id: Optional[str] = None
    installed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.skill_id:
            # Generate ID from name
            self.skill_id = re.sub(r'[^a-z0-9-]', '-', self.meta.name.lower())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "meta": self.meta.to_dict(),
            "files": [f.to_dict() for f in self.files],
            "readme": self.readme,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skill":
        meta = SkillMeta.from_dict(data.get("meta", {}))
        files = [
            SkillFile(
                path=f.get("path", ""),
                content=f.get("content", ""),
                file_type=f.get("file_type", "skill"),
            )
            for f in data.get("files", [])
        ]
        skill = cls(
            meta=meta,
            files=files,
            readme=data.get("readme", ""),
            skill_id=data.get("skill_id"),
        )
        return skill


class SkillLoader:
    """Load skills from directories."""
    
    SKILL_FILE = "SKILL.md"
    CONFIG_FILE = "skill.json"
    
    def __init__(self, skills_dir: Path):
        self.skills_dir = Path(skills_dir)
    
    def discover(self) -> List[str]:
        """Discover all skills in the directory."""
        skills = []
        for path in self.skills_dir.rglob(self.SKILL_FILE):
            skill_dir = path.parent
            skills.append(str(skill_dir.relative_to(self.skills_dir)))
        return skills
    
    def load(self, skill_path: str) -> Optional[Skill]:
        """Load a skill from path."""
        skill_dir = self.skills_dir / skill_path
        
        if not skill_dir.exists():
            return None
        
        # Load SKILL.md
        skill_file = skill_dir / self.SKILL_FILE
        if not skill_file.exists():
            return None
        
        content = skill_file.read_text()
        
        # Parse frontmatter
        meta, readme = self._parse_skill_md(content)
        
        # Load skill.json if exists
        config_file = skill_dir / self.CONFIG_FILE
        if config_file.exists():
            config = json.loads(config_file.read_text())
            meta = SkillMeta.from_dict(config)
        
        # Collect all files
        files = []
        for f in skill_dir.rglob("*"):
            if f.is_file() and f.name not in [self.SKILL_FILE, self.CONFIG_FILE]:
                rel_path = str(f.relative_to(skill_dir))
                file_type = self._get_file_type(f.name)
                files.append(SkillFile(
                    path=rel_path,
                    content=f.read_text(),
                    file_type=file_type,
                ))
        
        return Skill(meta=meta, files=files, readme=readme)
    
    def _parse_skill_md(self, content: str) -> tuple[SkillMeta, str]:
        """Parse SKILL.md with frontmatter."""
        meta = SkillMeta(name="", version="0.0.1", description="", author="")
        readme = content
        
        # Check for YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                readme = parts[2].strip()
                
                # Parse frontmatter (simple key: value)
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if key == "name":
                            meta.name = value
                        elif key == "version":
                            meta.version = value
                        elif key == "description":
                            meta.description = value
                        elif key == "author":
                            meta.author = value
                        elif key == "tags":
                            meta.tags = [t.strip() for t in value.split(',')]
        
        return meta, readme
    
    def _get_file_type(self, filename: str) -> str:
        """Determine file type from name."""
        if filename.endswith('.py'):
            return "script"
        elif filename.endswith('.sh'):
            return "script"
        elif filename.endswith('.json'):
            return "config"
        elif filename.endswith('.md'):
            return "doc"
        else:
            return "skill"


class SkillValidator:
    """Validate skills."""
    
    REQUIRED_FIELDS = ["name", "version", "description"]
    
    def validate(self, skill: Skill) -> List[str]:
        """Validate a skill, return list of errors."""
        errors = []
        
        # Check required fields
        if not skill.meta.name:
            errors.append("Missing required field: name")
        if not skill.meta.version:
            errors.append("Missing required field: version")
        if not skill.meta.description:
            errors.append("Missing required field: description")
        
        # Validate version format
        if skill.meta.version:
            if not re.match(r'^\d+\.\d+\.\d+', skill.meta.version):
                errors.append(f"Invalid version format: {skill.meta.version}")
        
        # Check for SKILL.md
        has_skill_md = any(f.path == "SKILL.md" for f in skill.files)
        if not has_skill_md and not skill.readme:
            errors.append("Missing SKILL.md")
        
        return errors
    
    def is_valid(self, skill: Skill) -> bool:
        """Check if skill is valid."""
        return len(self.validate(skill)) == 0
