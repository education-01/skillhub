"""SkillHub Registry - Unified skill registry.

Combines local and remote registries into a single interface.

Example:
    >>> from skillhub.registry import Registry
    >>> 
    >>> # Initialize registry
    >>> registry = Registry()
    >>> 
    >>> # Search for skills (local + remote)
    >>> results = registry.search("weather")
    >>> 
    >>> # Install a skill from remote
    >>> registry.install("weather-forecast")
    >>> 
    >>> # Get installed skill
    >>> skill = registry.get("weather-forecast")
    >>> 
    >>> # List all installed skills
    >>> installed = registry.list_all()
    >>> 
    >>> # Uninstall a skill
    >>> registry.uninstall("weather-forecast")
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import threading

from .local import LocalRegistry, InstalledSkill, SkillIndex
from .remote import RemoteRegistry, RemoteSkill, VersionInfo, GitHubClient, RegistryAPIClient

# Import from core
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.skill import Skill, SkillMeta


@dataclass
class SearchResult:
    """Unified search result from local and remote sources."""
    skill_id: str
    name: str
    version: str
    description: str
    author: str
    tags: List[str]
    source: str  # "local", "github", "official-api", "community-api"
    installed: bool = False
    update_available: Optional[str] = None  # Latest version if update available
    
    # Remote-only fields
    source_url: Optional[str] = None
    stars: int = 0
    downloads: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "tags": self.tags,
            "source": self.source,
            "installed": self.installed,
            "update_available": self.update_available,
            "source_url": self.source_url,
            "stars": self.stars,
            "downloads": self.downloads,
        }


class Registry:
    """
    Unified skill registry.
    
    Combines local and remote sources with a simple interface.
    
    Features:
    - Local skill management (install, uninstall, list)
    - Remote skill discovery (search, fetch)
    - Version management (list versions, update)
    - Fast in-memory indexing
    
    Example:
        >>> registry = Registry()
        >>> 
        >>> # Search
        >>> results = registry.search("weather")
        >>> for r in results:
        ...     print(f"{r.name} ({r.source}) - {r.description}")
        >>> 
        >>> # Install
        >>> skill = registry.install("weather-forecast", version="1.2.0")
        >>> 
        >>> # Update
        >>> if registry.is_update_available("weather-forecast"):
        ...     registry.update("weather-forecast")
        >>> 
        >>> # Uninstall
        >>> registry.uninstall("weather-forecast")
    """
    
    def __init__(
        self,
        local_dir: Optional[Path] = None,
        github_token: Optional[str] = None,
        api_url: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        auto_discover: bool = True,
    ):
        """
        Initialize unified registry.
        
        Args:
            local_dir: Directory for local skills
            github_token: GitHub personal access token
            api_url: SkillHub API URL
            cache_dir: Cache directory
            auto_discover: Auto-discover local skills on init
        """
        self.local = LocalRegistry(
            base_dir=local_dir,
            auto_discover=auto_discover,
        )
        self.remote = RemoteRegistry(
            github_token=github_token,
            api_url=api_url,
            cache_dir=cache_dir,
        )
        
        self._lock = threading.RLock()
    
    # ==================== Local Operations ====================
    
    def register(
        self,
        skill: Skill,
        source: str = "local",
        source_url: Optional[str] = None,
    ) -> InstalledSkill:
        """
        Register a skill in the local registry.
        
        Args:
            skill: Skill to register
            source: Source of the skill
            source_url: URL where skill was fetched from
        
        Returns:
            InstalledSkill record
        """
        return self.local.register(skill, source=source, source_url=source_url)
    
    def uninstall(self, name: str) -> bool:
        """
        Uninstall a skill from the local registry.
        
        Args:
            name: Skill name or ID
        
        Returns:
            True if uninstalled successfully
        """
        return self.local.uninstall(name)
    
    def get(self, name: str, include_remote: bool = False) -> Optional[Union[Skill, RemoteSkill]]:
        """
        Get a skill by name or ID.
        
        Args:
            name: Skill name or ID
            include_remote: Also search remote if not found locally
        
        Returns:
            Skill or RemoteSkill if found, None otherwise
        """
        # Check local first
        skill = self.local.get(name)
        if skill:
            return skill
        
        # Check remote if requested
        if include_remote:
            return self.remote.get(name)
        
        return None
    
    def get_meta(self, name: str) -> Optional[SkillMeta]:
        """Get skill metadata by name or ID."""
        return self.local.get_meta(name)
    
    def list_all(self) -> List[InstalledSkill]:
        """
        List all locally installed skills.
        
        Returns:
            List of InstalledSkill records
        """
        return self.local.list_all()
    
    def list_installed(self) -> List[InstalledSkill]:
        """Alias for list_all()."""
        return self.list_all()
    
    def exists(self, name: str) -> bool:
        """Check if a skill is installed locally."""
        return self.local.exists(name)
    
    def get_version(self, name: str) -> Optional[str]:
        """Get installed version of a skill."""
        return self.local.get_version(name)
    
    # ==================== Remote Operations ====================
    
    def search(
        self,
        query: str,
        limit: int = 20,
        include_installed: bool = True,
    ) -> List[SearchResult]:
        """
        Search for skills across all sources.
        
        Args:
            query: Search query
            limit: Maximum results
            include_installed: Include installed skills in results
        
        Returns:
            List of SearchResult
        """
        results = []
        seen_ids = set()
        
        # Search local first
        if include_installed:
            local_results = self.local.search(query, limit)
            for meta in local_results:
                skill_id = meta.name.lower().replace(" ", "-")
                if skill_id not in seen_ids:
                    installed = self.local.get(meta.name)
                    if installed:
                        results.append(SearchResult(
                            skill_id=skill_id,
                            name=meta.name,
                            version=meta.version,
                            description=meta.description,
                            author=meta.author,
                            tags=meta.tags,
                            source="local",
                            installed=True,
                        ))
                        seen_ids.add(skill_id)
        
        # Search remote
        remote_results = self.remote.search(query, limit * 2)  # Get more to account for duplicates
        for remote_skill in remote_results:
            if remote_skill.skill_id not in seen_ids:
                # Check if installed
                is_installed = self.local.exists(remote_skill.skill_id)
                current_version = self.local.get_version(remote_skill.skill_id) if is_installed else None
                
                # Check for updates
                update_available = None
                if is_installed and current_version:
                    update_available = self.remote.is_update_available(
                        remote_skill.skill_id,
                        current_version,
                    )
                
                results.append(SearchResult(
                    skill_id=remote_skill.skill_id,
                    name=remote_skill.name,
                    version=remote_skill.version,
                    description=remote_skill.description,
                    author=remote_skill.author,
                    tags=remote_skill.tags,
                    source=remote_skill.source,
                    installed=is_installed,
                    update_available=update_available,
                    source_url=remote_skill.source_url,
                    stars=remote_skill.stars,
                    downloads=remote_skill.downloads,
                ))
                seen_ids.add(remote_skill.skill_id)
        
        return results[:limit]
    
    def search_remote(self, query: str, limit: int = 20) -> List[RemoteSkill]:
        """Search only remote sources."""
        return self.remote.search(query, limit)
    
    def list_versions(self, skill_id: str) -> List[VersionInfo]:
        """
        List all available versions for a skill.
        
        Args:
            skill_id: Skill ID or GitHub repo (owner/repo)
        
        Returns:
            List of VersionInfo
        """
        return self.remote.list_versions(skill_id)
    
    def fetch(
        self,
        skill_id: str,
        version: Optional[str] = None,
    ) -> Optional[Skill]:
        """
        Fetch a skill from remote without installing.
        
        Args:
            skill_id: Skill ID or GitHub repo (owner/repo)
            version: Specific version to fetch
        
        Returns:
            Skill if found, None otherwise
        """
        return self.remote.fetch(skill_id, version)
    
    # ==================== Install/Update Operations ====================
    
    def install(
        self,
        skill_id: str,
        version: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Skill:
        """
        Install a skill from remote.
        
        Args:
            skill_id: Skill ID or GitHub repo (owner/repo)
            version: Specific version to install
            source: Source hint ("github", "official-api")
        
        Returns:
            Installed Skill
        
        Raises:
            ValueError: If skill not found or already installed
        """
        with self._lock:
            # Check if already installed
            if self.local.exists(skill_id):
                raise ValueError(f"Skill already installed: {skill_id}")
            
            # Fetch from remote
            skill = self.remote.fetch(skill_id, version)
            if not skill:
                raise ValueError(f"Skill not found: {skill_id}")
            
            # Determine source
            if "/" in skill_id:
                install_source = "github"
                source_url = f"https://github.com/{skill_id}"
            else:
                remote_info = self.remote.get(skill_id)
                install_source = remote_info.source if remote_info else "remote"
                source_url = remote_info.source_url if remote_info else None
            
            # Register locally
            self.local.register(
                skill,
                source=install_source,
                source_url=source_url,
            )
            
            return skill
    
    def update(
        self,
        name: str,
        version: Optional[str] = None,
    ) -> Optional[Skill]:
        """
        Update a skill to a newer version.
        
        Args:
            name: Skill name or ID
            version: Specific version to update to (default: latest)
        
        Returns:
            Updated Skill
        """
        with self._lock:
            # Get installed skill info
            installed = self.local.get(name)
            if not installed:
                raise ValueError(f"Skill not installed: {name}")
            
            # Find skill ID for remote lookup
            skill_id = name
            installed_info = None
            for info in self.local.list_all():
                if info.name.lower() == name.lower() or info.skill_id == name:
                    skill_id = info.skill_id
                    installed_info = info
                    break
            
            # Fetch new version
            new_skill = self.remote.fetch(skill_id, version)
            if not new_skill:
                raise ValueError(f"Could not fetch skill: {skill_id}")
            
            # Update local registry
            self.local.update_version(name, new_skill.meta.version, new_skill)
            
            return new_skill
    
    def is_update_available(self, name: str) -> Optional[str]:
        """
        Check if an update is available for a skill.
        
        Args:
            name: Skill name or ID
        
        Returns:
            Latest version if update available, None otherwise
        """
        # Get installed version
        current_version = self.local.get_version(name)
        if not current_version:
            return None
        
        # Get skill ID
        skill_id = name
        for info in self.local.list_all():
            if info.name.lower() == name.lower() or info.skill_id == name:
                skill_id = info.skill_id
                break
        
        return self.remote.is_update_available(skill_id, current_version)
    
    # ==================== Utility Methods ====================
    
    def refresh_index(self) -> None:
        """Refresh the remote skill index."""
        self.remote.fetch_index(force=True)
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.remote.api._index_cache = None
        self.remote.api._index_cache_time = None
    
    def stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        installed = self.local.list_all()
        
        return {
            "installed_count": len(installed),
            "installed_skills": [
                {
                    "name": s.name,
                    "version": s.version,
                    "source": s.source,
                }
                for s in installed
            ],
        }
    
    def __len__(self) -> int:
        return len(self.local)
    
    def __contains__(self, name: str) -> bool:
        return self.local.exists(name)
    
    def __iter__(self):
        return iter(self.local.list_all())


# Convenience function
def get_registry(**kwargs) -> Registry:
    """
    Get a configured registry instance.
    
    Args:
        **kwargs: Arguments passed to Registry constructor
    
    Returns:
        Configured Registry instance
    """
    return Registry(**kwargs)


# Exports
__all__ = [
    # Main class
    "Registry",
    "get_registry",
    
    # Local
    "LocalRegistry",
    "InstalledSkill",
    "SkillIndex",
    
    # Remote
    "RemoteRegistry",
    "RemoteSkill",
    "VersionInfo",
    "GitHubClient",
    "RegistryAPIClient",
    
    # Results
    "SearchResult",
]
