"""Local Registry - Manages locally installed skills.

Provides:
- Skill registration and unregistration
- Local skill discovery and listing
- Version tracking
- Fast in-memory indexing
"""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import threading
import re

# Import from core module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.skill import Skill, SkillMeta, SkillValidator


@dataclass
class InstalledSkill:
    """Record of an installed skill."""
    skill_id: str
    name: str
    version: str
    install_path: Path
    installed_at: datetime
    source: str  # "official", "github", "local", "community"
    source_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "version": self.version,
            "install_path": str(self.install_path),
            "installed_at": self.installed_at.isoformat(),
            "source": self.source,
            "source_url": self.source_url,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstalledSkill":
        return cls(
            skill_id=data["skill_id"],
            name=data["name"],
            version=data["version"],
            install_path=Path(data["install_path"]),
            installed_at=datetime.fromisoformat(data["installed_at"]),
            source=data["source"],
            source_url=data.get("source_url"),
        )


class SkillIndex:
    """
    In-memory index for fast skill search.
    
    Uses inverted index for quick text search across:
    - Skill names
    - Descriptions
    - Tags
    - Authors
    """
    
    def __init__(self):
        self._skills: Dict[str, SkillMeta] = {}
        self._name_index: Dict[str, Set[str]] = {}  # lowercase name -> skill_ids
        self._tag_index: Dict[str, Set[str]] = {}   # tag -> skill_ids
        self._word_index: Dict[str, Set[str]] = {}  # word -> skill_ids (for full-text search)
        self._lock = threading.RLock()
    
    def add(self, skill_id: str, meta: SkillMeta) -> None:
        """Add skill to index."""
        with self._lock:
            self._skills[skill_id] = meta
            
            # Index name
            name_lower = meta.name.lower()
            for word in self._tokenize(name_lower):
                self._name_index.setdefault(word, set()).add(skill_id)
            
            # Index tags
            for tag in meta.tags:
                tag_lower = tag.lower()
                self._tag_index.setdefault(tag_lower, set()).add(skill_id)
            
            # Index full-text (description + name)
            full_text = f"{meta.name} {meta.description}"
            for word in self._tokenize(full_text):
                self._word_index.setdefault(word, set()).add(skill_id)
    
    def remove(self, skill_id: str) -> None:
        """Remove skill from index."""
        with self._lock:
            if skill_id not in self._skills:
                return
            
            meta = self._skills.pop(skill_id)
            
            # Remove from name index
            for word in self._tokenize(meta.name.lower()):
                if word in self._name_index:
                    self._name_index[word].discard(skill_id)
            
            # Remove from tag index
            for tag in meta.tags:
                tag_lower = tag.lower()
                if tag_lower in self._tag_index:
                    self._tag_index[tag_lower].discard(skill_id)
            
            # Remove from word index
            full_text = f"{meta.name} {meta.description}"
            for word in self._tokenize(full_text):
                if word in self._word_index:
                    self._word_index[word].discard(skill_id)
    
    def search(self, query: str, limit: int = 50) -> List[str]:
        """
        Search for skills matching query.
        
        Returns skill IDs sorted by relevance.
        """
        with self._lock:
            query_lower = query.lower()
            tokens = self._tokenize(query_lower)
            
            # Score each skill
            scores: Dict[str, float] = {}
            
            for token in tokens:
                # Exact name match (highest score)
                if token in self._name_index:
                    for skill_id in self._name_index[token]:
                        scores[skill_id] = scores.get(skill_id, 0) + 10.0
                
                # Tag match
                if token in self._tag_index:
                    for skill_id in self._tag_index[token]:
                        scores[skill_id] = scores.get(skill_id, 0) + 5.0
                
                # Full-text match
                if token in self._word_index:
                    for skill_id in self._word_index[token]:
                        scores[skill_id] = scores.get(skill_id, 0) + 1.0
            
            # Sort by score
            sorted_skills = sorted(
                scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return [skill_id for skill_id, _ in sorted_skills[:limit]]
    
    def get(self, skill_id: str) -> Optional[SkillMeta]:
        """Get skill metadata by ID."""
        return self._skills.get(skill_id)
    
    def list_all(self) -> List[str]:
        """List all skill IDs."""
        return list(self._skills.keys())
    
    def clear(self) -> None:
        """Clear all index data."""
        with self._lock:
            self._skills.clear()
            self._name_index.clear()
            self._tag_index.clear()
            self._word_index.clear()
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for indexing."""
        # Simple tokenization: split on non-alphanumeric
        tokens = re.findall(r'[a-z0-9]+', text.lower())
        # Filter short tokens
        return [t for t in tokens if len(t) >= 2]


class LocalRegistry:
    """
    Local skill registry.
    
    Manages skills installed on the local machine.
    Provides registration, discovery, and fast search.
    
    Example:
        >>> registry = LocalRegistry()
        >>> 
        >>> # Register a skill
        >>> registry.register(skill, source="github")
        >>> 
        >>> # Search skills
        >>> results = registry.search("weather")
        >>> 
        >>> # Get a specific skill
        >>> skill = registry.get("weather")
        >>> 
        >>> # List all installed
        >>> all_skills = registry.list_all()
    """
    
    REGISTRY_FILE = "registry.json"
    SKILLS_DIR = "skills"
    
    def __init__(
        self,
        base_dir: Optional[Path] = None,
        auto_discover: bool = True,
    ):
        """
        Initialize local registry.
        
        Args:
            base_dir: Base directory for skill storage
            auto_discover: Auto-discover skills on init
        """
        self.base_dir = base_dir or Path.home() / ".skillhub"
        self.skills_dir = self.base_dir / self.SKILLS_DIR
        self.registry_file = self.base_dir / self.REGISTRY_FILE
        
        self._installed: Dict[str, InstalledSkill] = {}
        self._index = SkillIndex()
        self._validator = SkillValidator()
        self._lock = threading.RLock()
        
        # Ensure directories exist
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        
        # Load registry
        self._load_registry()
        
        # Auto-discover if enabled
        if auto_discover:
            self._discover_skills()
    
    def register(
        self,
        skill: Skill,
        source: str = "local",
        source_url: Optional[str] = None,
        overwrite: bool = False,
    ) -> InstalledSkill:
        """
        Register a skill in the local registry.
        
        Args:
            skill: Skill to register
            source: Source of the skill ("local", "github", "official", "community")
            source_url: URL where skill was fetched from
            overwrite: Overwrite if already exists
        
        Returns:
            InstalledSkill record
        
        Raises:
            ValueError: If skill already exists and overwrite=False
        """
        with self._lock:
            skill_id = skill.skill_id or self._generate_skill_id(skill.meta.name)
            
            # Check if exists
            if skill_id in self._installed and not overwrite:
                raise ValueError(f"Skill already registered: {skill_id}")
            
            # Validate skill
            errors = self._validator.validate(skill)
            if errors:
                raise ValueError(f"Invalid skill: {errors}")
            
            # Install to disk
            install_path = self._install_skill_to_disk(skill, skill_id)
            
            # Create record
            installed = InstalledSkill(
                skill_id=skill_id,
                name=skill.meta.name,
                version=skill.meta.version,
                install_path=install_path,
                installed_at=datetime.now(),
                source=source,
                source_url=source_url,
            )
            
            # Update registry
            self._installed[skill_id] = installed
            self._index.add(skill_id, skill.meta)
            
            # Save registry
            self._save_registry()
            
            return installed
    
    def unregister(self, skill_id: str, delete_files: bool = True) -> bool:
        """
        Unregister a skill from the local registry.
        
        Args:
            skill_id: Skill to unregister
            delete_files: Also delete skill files from disk
        
        Returns:
            True if unregistered successfully
        
        Raises:
            ValueError: If skill not found
        """
        with self._lock:
            if skill_id not in self._installed:
                raise ValueError(f"Skill not registered: {skill_id}")
            
            installed = self._installed[skill_id]
            
            # Delete files
            if delete_files and installed.install_path.exists():
                shutil.rmtree(installed.install_path)
            
            # Remove from registry
            del self._installed[skill_id]
            self._index.remove(skill_id)
            
            # Save registry
            self._save_registry()
            
            return True
    
    def uninstall(self, name: str) -> bool:
        """Alias for unregister()."""
        return self.unregister(name, delete_files=True)
    
    def get(self, name: str) -> Optional[Skill]:
        """
        Get a skill by name or ID.
        
        Args:
            name: Skill name or ID
        
        Returns:
            Skill if found, None otherwise
        """
        with self._lock:
            # Try exact ID match
            if name in self._installed:
                return self._load_skill(name)
            
            # Try name match
            for skill_id, installed in self._installed.items():
                if installed.name.lower() == name.lower():
                    return self._load_skill(skill_id)
            
            return None
    
    def get_meta(self, name: str) -> Optional[SkillMeta]:
        """Get skill metadata by name or ID."""
        with self._lock:
            return self._index.get(name)
    
    def search(self, query: str, limit: int = 50) -> List[SkillMeta]:
        """
        Search for skills matching query.
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of matching skill metadata
        """
        with self._lock:
            skill_ids = self._index.search(query, limit)
            results = []
            for skill_id in skill_ids:
                meta = self._index.get(skill_id)
                if meta:
                    results.append(meta)
            return results
    
    def list_all(self) -> List[InstalledSkill]:
        """
        List all installed skills.
        
        Returns:
            List of InstalledSkill records
        """
        with self._lock:
            return list(self._installed.values())
    
    def list_names(self) -> List[str]:
        """List all skill names."""
        with self._lock:
            return [installed.name for installed in self._installed.values()]
    
    def exists(self, name: str) -> bool:
        """Check if a skill is installed."""
        with self._lock:
            if name in self._installed:
                return True
            return any(
                installed.name.lower() == name.lower()
                for installed in self._installed.values()
            )
    
    def get_version(self, name: str) -> Optional[str]:
        """Get installed version of a skill."""
        with self._lock:
            if name in self._installed:
                return self._installed[name].version
            for installed in self._installed.values():
                if installed.name.lower() == name.lower():
                    return installed.version
            return None
    
    def update_version(
        self,
        name: str,
        new_version: str,
        new_skill: Optional[Skill] = None,
    ) -> bool:
        """
        Update a skill to a new version.
        
        Args:
            name: Skill name or ID
            new_version: New version string
            new_skill: Optional new Skill object (updates files)
        
        Returns:
            True if updated successfully
        """
        with self._lock:
            skill_id = name
            if skill_id not in self._installed:
                # Try name match
                for sid, installed in self._installed.items():
                    if installed.name.lower() == name.lower():
                        skill_id = sid
                        break
                else:
                    raise ValueError(f"Skill not found: {name}")
            
            installed = self._installed[skill_id]
            
            # Update files if new skill provided
            if new_skill:
                # Delete old files
                if installed.install_path.exists():
                    shutil.rmtree(installed.install_path)
                # Install new files
                new_path = self._install_skill_to_disk(new_skill, skill_id)
                installed.install_path = new_path
            
            # Update version
            installed.version = new_version
            
            # Update index
            if new_skill:
                self._index.remove(skill_id)
                self._index.add(skill_id, new_skill.meta)
            
            # Save registry
            self._save_registry()
            
            return True
    
    def _load_registry(self) -> None:
        """Load registry from disk."""
        if not self.registry_file.exists():
            return
        
        try:
            data = json.loads(self.registry_file.read_text())
            for item in data.get("skills", []):
                installed = InstalledSkill.from_dict(item)
                self._installed[installed.skill_id] = installed
        except Exception as e:
            # Log error but don't fail
            print(f"Warning: Failed to load registry: {e}")
    
    def _save_registry(self) -> None:
        """Save registry to disk."""
        data = {
            "version": "1.0",
            "skills": [installed.to_dict() for installed in self._installed.values()],
        }
        self.registry_file.write_text(json.dumps(data, indent=2))
    
    def _discover_skills(self) -> None:
        """Discover skills in the skills directory."""
        if not self.skills_dir.exists():
            return
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_id = skill_dir.name
            
            # Skip if already in registry
            if skill_id in self._installed:
                # Load to index
                skill = self._load_skill_from_disk(skill_dir)
                if skill:
                    self._index.add(skill_id, skill.meta)
                continue
            
            # Try to load skill
            skill = self._load_skill_from_disk(skill_dir)
            if skill:
                # Add to registry
                installed = InstalledSkill(
                    skill_id=skill_id,
                    name=skill.meta.name,
                    version=skill.meta.version,
                    install_path=skill_dir,
                    installed_at=datetime.fromtimestamp(skill_dir.stat().st_mtime),
                    source="local",
                )
                self._installed[skill_id] = installed
                self._index.add(skill_id, skill.meta)
        
        # Save discovered skills
        self._save_registry()
    
    def _load_skill_from_disk(self, skill_dir: Path) -> Optional[Skill]:
        """Load a skill from disk."""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None
        
        try:
            # Import loader from core
            from ..core.skill import SkillLoader
            loader = SkillLoader(self.skills_dir)
            return loader.load(skill_dir.name)
        except Exception:
            # Fallback: basic parsing
            content = skill_md.read_text()
            meta, readme = self._parse_skill_md(content)
            
            return Skill(
                meta=meta,
                readme=readme,
                skill_id=skill_dir.name,
            )
    
    def _install_skill_to_disk(self, skill: Skill, skill_id: str) -> Path:
        """Install skill files to disk."""
        install_path = self.skills_dir / skill_id
        
        # Create directory
        install_path.mkdir(parents=True, exist_ok=True)
        
        # Write SKILL.md
        skill_md = install_path / "SKILL.md"
        skill_md.write_text(self._generate_skill_md(skill))
        
        # Write skill.json
        skill_json = install_path / "skill.json"
        skill_json.write_text(json.dumps(skill.meta.to_dict(), indent=2))
        
        # Write other files
        for file in skill.files:
            file_path = install_path / file.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file.content)
        
        return install_path
    
    def _generate_skill_md(self, skill: Skill) -> str:
        """Generate SKILL.md content."""
        lines = [
            "---",
            f"name: {skill.meta.name}",
            f"version: {skill.meta.version}",
            f"description: {skill.meta.description}",
            f"author: {skill.meta.author}",
        ]
        
        if skill.meta.tags:
            lines.append(f"tags: {', '.join(skill.meta.tags)}")
        
        lines.extend([
            "---",
            "",
        ])
        
        if skill.readme:
            lines.append(skill.readme)
        
        return "\n".join(lines)
    
    def _parse_skill_md(self, content: str) -> tuple:
        """Parse SKILL.md with frontmatter."""
        meta = SkillMeta(name="", version="0.0.1", description="", author="")
        readme = content
        
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                readme = parts[2].strip()
                
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
    
    def _generate_skill_id(self, name: str) -> str:
        """Generate a skill ID from name."""
        return re.sub(r'[^a-z0-9-]', '-', name.lower())
    
    def __len__(self) -> int:
        return len(self._installed)
    
    def __contains__(self, name: str) -> bool:
        return self.exists(name)
    
    def __iter__(self):
        return iter(self._installed.values())
