"""Skill Registry - Central storage for skills.

Manages skill discovery, installation, and version control.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .skill import Skill, SkillMeta, SkillValidator


@dataclass
class SearchResult:
    """Skill search result."""
    skill_id: str
    name: str
    description: str
    version: str
    author: str
    tags: List[str]
    source: str  # "local", "official", "community", "github"


class SkillRegistry:
    """
    Central registry for skills.
    
    Manages:
    - Local skills (installed)
    - Official skills (bundled)
    - Community skills (from registry)
    - GitHub skills (from repo)
    
    Example:
        >>> registry = SkillRegistry()
        >>> 
        >>> # Search for skills
        >>> results = registry.search("weather")
        >>> 
        >>> # Install a skill
        >>> registry.install("weather")
        >>> 
        >>> # List installed skills
        >>> installed = registry.list_installed()
    """
    
    def __init__(
        self,
        local_dir: Optional[Path] = None,
        official_dir: Optional[Path] = None,
        community_dir: Optional[Path] = None,
    ):
        self.local_dir = local_dir or Path.home() / ".skillhub" / "skills"
        self.official_dir = official_dir
        self.community_dir = community_dir
        self.validator = SkillValidator()
        
        # Ensure local dir exists
        self.local_dir.mkdir(parents=True, exist_ok=True)
    
    def discover(self, path: Path) -> Optional[Skill]:
        """Discover a skill from a directory."""
        if not path.is_dir():
            return None
        
        # Look for SKILL.md
        skill_md = path / "SKILL.md"
        if skill_md.exists():
            return Skill.from_dir(path)
        
        return None
    
    def list_local(self) -> List[SkillMeta]:
        """List all locally installed skills."""
        skills = []
        
        for skill_dir in self.local_dir.iterdir():
            if skill_dir.is_dir():
                skill = self.discover(skill_dir)
                if skill:
                    skills.append(skill.meta)
        
        return sorted(skills, key=lambda m: m.name)
    
    def list_official(self) -> List[SkillMeta]:
        """List official skills."""
        if not self.official_dir or not self.official_dir.exists():
            return []
        
        skills = []
        for skill_dir in self.official_dir.iterdir():
            if skill_dir.is_dir():
                skill = self.discover(skill_dir)
                if skill:
                    skills.append(skill.meta)
        
        return sorted(skills, key=lambda m: m.name)
    
    def search(self, query: str) -> List[SearchResult]:
        """
        Search for skills matching query.
        
        Searches in local, official, and community directories.
        """
        results = []
        query_lower = query.lower()
        
        # Search local
        for meta in self.list_local():
            if self._matches(meta, query_lower):
                results.append(SearchResult(
                    skill_id=meta.name,
                    name=meta.name,
                    description=meta.description,
                    version=meta.version,
                    author=meta.author,
                    tags=meta.tags,
                    source="local",
                ))
        
        # Search official
        for meta in self.list_official():
            if self._matches(meta, query_lower):
                results.append(SearchResult(
                    skill_id=meta.name,
                    name=meta.name,
                    description=meta.description,
                    version=meta.version,
                    author=meta.author,
                    tags=meta.tags,
                    source="official",
                ))
        
        return results
    
    def _matches(self, meta: SkillMeta, query: str) -> bool:
        """Check if skill matches query."""
        if query in meta.name.lower():
            return True
        if query in meta.description.lower():
            return True
        if any(query in tag.lower() for tag in meta.tags):
            return True
        return False
    
    def install(
        self,
        skill_id: str,
        source: Optional[str] = None,
        version: Optional[str] = None,
    ) -> Skill:
        """
        Install a skill.
        
        Args:
            skill_id: Skill name or GitHub repo (owner/repo)
            source: Optional source hint
            version: Optional version constraint
        
        Returns:
            Installed Skill
        """
        # Check if already installed
        installed_dir = self.local_dir / skill_id
        if installed_dir.exists():
            raise ValueError(f"Skill already installed: {skill_id}")
        
        # Try to find source
        if "/" in skill_id:
            # GitHub repo
            return self._install_from_github(skill_id, version)
        elif source == "official" or self._is_official(skill_id):
            return self._install_from_official(skill_id)
        else:
            raise ValueError(f"Skill not found: {skill_id}")
    
    def _is_official(self, skill_id: str) -> bool:
        """Check if skill is in official directory."""
        if not self.official_dir:
            return False
        return (self.official_dir / skill_id).exists()
    
    def _install_from_official(self, skill_id: str) -> Skill:
        """Install skill from official directory."""
        src = self.official_dir / skill_id
        dst = self.local_dir / skill_id
        
        if not src.exists():
            raise ValueError(f"Official skill not found: {skill_id}")
        
        shutil.copytree(src, dst)
        
        skill = self.discover(dst)
        if not skill:
            shutil.rmtree(dst)
            raise ValueError(f"Invalid skill: {skill_id}")
        
        # Validate
        errors = self.validator.validate(skill)
        if errors:
            shutil.rmtree(dst)
            raise ValueError(f"Invalid skill: {errors}")
        
        return skill
    
    def _install_from_github(self, repo: str, version: Optional[str]) -> Skill:
        """Install skill from GitHub."""
        dst = self.local_dir / repo.split("/")[-1]
        
        # Clone repo
        url = f"https://github.com/{repo}.git"
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, str(dst)],
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            raise ValueError(f"Failed to clone: {result.stderr}")
        
        # Remove .git directory
        git_dir = dst / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)
        
        # Validate
        skill = self.discover(dst)
        if not skill:
            shutil.rmtree(dst)
            raise ValueError(f"Invalid skill: {repo}")
        
        errors = self.validator.validate(skill)
        if errors:
            shutil.rmtree(dst)
            raise ValueError(f"Invalid skill: {errors}")
        
        return skill
    
    def uninstall(self, skill_id: str) -> bool:
        """Uninstall a skill."""
        skill_dir = self.local_dir / skill_id
        
        if not skill_dir.exists():
            raise ValueError(f"Skill not installed: {skill_id}")
        
        shutil.rmtree(skill_dir)
        return True
    
    def get(self, skill_id: str) -> Optional[Skill]:
        """Get a skill by ID."""
        # Check local first
        skill = self.discover(self.local_dir / skill_id)
        if skill:
            return skill
        
        # Check official
        if self.official_dir:
            skill = self.discover(self.official_dir / skill_id)
            if skill:
                return skill
        
        return None
    
    def update(self, skill_id: str) -> Optional[Skill]:
        """Update a skill to latest version."""
        # For GitHub skills, re-install
        # For official skills, copy latest
        skill = self.get(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")
        
        # Re-install
        self.uninstall(skill_id)
        return self.install(skill_id)


class SkillPack:
    """
    A pack of related skills.
    
    Example:
        >>> pack = SkillPack(name="dev-tools", skills=["git", "docker", "pytest"])
        >>> pack.install_all()
    """
    
    def __init__(self, name: str, skills: List[str], description: str = ""):
        self.name = name
        self.skill_ids = skills
        self.description = description
    
    def install(self, registry: SkillRegistry) -> Dict[str, bool]:
        """Install all skills in pack."""
        results = {}
        for skill_id in self.skill_ids:
            try:
                registry.install(skill_id)
                results[skill_id] = True
            except Exception as e:
                results[skill_id] = False
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "skills": self.skill_ids,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillPack":
        return cls(
            name=data.get("name", ""),
            skills=data.get("skills", []),
            description=data.get("description", ""),
        )


# Predefined skill packs
OFFICIAL_PACKS = [
    SkillPack(
        name="dev-basics",
        skills=["git", "bash", "python"],
        description="Basic development tools",
    ),
    SkillPack(
        name="ai-assistant",
        skills=["web-search", "file-manager", "code-runner"],
        description="AI assistant capabilities",
    ),
]
