"""Remote Registry - Fetches skills from remote sources.

Provides:
- GitHub repository fetching
- Remote API integration
- Skill index synchronization
- Version management
"""
from __future__ import annotations

import json
import subprocess
import shutil
import tempfile
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import urllib.request
import urllib.error
import threading

# Import from core module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.skill import Skill, SkillMeta, SkillValidator


@dataclass
class RemoteSkill:
    """A skill available from a remote source."""
    skill_id: str
    name: str
    version: str
    description: str
    author: str
    source: str  # "github", "official-api", "community-api"
    source_url: str
    tags: List[str] = field(default_factory=list)
    download_url: Optional[str] = None
    homepage: Optional[str] = None
    stars: int = 0
    downloads: int = 0
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "tags": self.tags,
            "source": self.source,
            "source_url": self.source_url,
            "download_url": self.download_url,
            "homepage": self.homepage,
            "stars": self.stars,
            "downloads": self.downloads,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RemoteSkill":
        return cls(
            skill_id=data["skill_id"],
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data["author"],
            source=data["source"],
            source_url=data["source_url"],
            tags=data.get("tags", []),
            download_url=data.get("download_url"),
            homepage=data.get("homepage"),
            stars=data.get("stars", 0),
            downloads=data.get("downloads", 0),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )


@dataclass
class VersionInfo:
    """Version information for a skill."""
    version: str
    released_at: Optional[datetime] = None
    changelog: Optional[str] = None
    download_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "released_at": self.released_at.isoformat() if self.released_at else None,
            "changelog": self.changelog,
            "download_url": self.download_url,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VersionInfo":
        return cls(
            version=data["version"],
            released_at=datetime.fromisoformat(data["released_at"]) if data.get("released_at") else None,
            changelog=data.get("changelog"),
            download_url=data.get("download_url"),
        )


class GitHubClient:
    """
    Client for fetching skills from GitHub.
    
    Supports:
    - Repository cloning
    - Release fetching
    - Version listing
    """
    
    GITHUB_API = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token (optional, increases rate limit)
        """
        self.token = token
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = timedelta(minutes=30)
        self._lock = threading.RLock()
    
    def fetch_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository information."""
        cache_key = f"repo:{owner}/{repo}"
        
        with self._lock:
            if cache_key in self._cache:
                cached, timestamp = self._cache[cache_key]
                if datetime.now() - timestamp < self._cache_ttl:
                    return cached
        
        url = f"{self.GITHUB_API}/repos/{owner}/{repo}"
        data = self._fetch_json(url)
        
        with self._lock:
            self._cache[cache_key] = (data, datetime.now())
        
        return data
    
    def fetch_releases(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch all releases for a repository."""
        url = f"{self.GITHUB_API}/repos/{owner}/{repo}/releases"
        return self._fetch_json(url)
    
    def fetch_readme(self, owner: str, repo: str) -> str:
        """Fetch repository README content."""
        url = f"{self.GITHUB_API}/repos/{owner}/{repo}/readme"
        try:
            data = self._fetch_json(url)
            # Decode base64 content
            import base64
            return base64.b64decode(data["content"]).decode("utf-8")
        except Exception:
            return ""
    
    def list_versions(self, owner: str, repo: str) -> List[VersionInfo]:
        """List all available versions (from releases and tags)."""
        versions = []
        
        # Try releases first
        try:
            releases = self.fetch_releases(owner, repo)
            for release in releases:
                if release.get("draft") or release.get("prerelease"):
                    continue
                versions.append(VersionInfo(
                    version=release["tag_name"].lstrip("v"),
                    released_at=datetime.fromisoformat(
                        release["published_at"].replace("Z", "+00:00")
                    ) if release.get("published_at") else None,
                    changelog=release.get("body"),
                    download_url=release.get("zipball_url"),
                ))
        except Exception:
            pass
        
        # Fallback to tags if no releases
        if not versions:
            try:
                url = f"{self.GITHUB_API}/repos/{owner}/{repo}/tags"
                tags = self._fetch_json(url)
                for tag in tags[:20]:  # Limit to 20 most recent tags
                    versions.append(VersionInfo(
                        version=tag["name"].lstrip("v"),
                        download_url=tag.get("zipball_url"),
                    ))
            except Exception:
                pass
        
        return versions
    
    def clone_repo(
        self,
        owner: str,
        repo: str,
        target_dir: Path,
        version: Optional[str] = None,
        depth: int = 1,
    ) -> bool:
        """
        Clone a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            target_dir: Target directory
            version: Specific version/tag to clone
            depth: Clone depth (1 for shallow)
        
        Returns:
            True if successful
        """
        url = f"https://github.com/{owner}/{repo}.git"
        
        cmd = ["git", "clone", "--depth", str(depth)]
        
        if version:
            cmd.extend(["--branch", version])
        
        cmd.extend([url, str(target_dir)])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        
        return result.returncode == 0
    
    def search_skills(self, query: str, limit: int = 20) -> List[RemoteSkill]:
        """
        Search for skills on GitHub.
        
        Searches repositories with 'skillhub-skill' topic or matching name.
        """
        results = []
        
        # Search for skillhub-skill topic
        url = f"{self.GITHUB_API}/search/repositories"
        search_query = f"{query} topic:skillhub-skill"
        
        try:
            data = self._fetch_json(f"{url}?q={urllib.parse.quote(search_query)}&per_page={limit}")
            
            for item in data.get("items", []):
                results.append(self._repo_to_remote_skill(item, "github"))
        except Exception:
            # Fallback: simple name search
            search_query = f"{query} skill"
            try:
                data = self._fetch_json(f"{url}?q={urllib.parse.quote(search_query)}&per_page={limit}")
                for item in data.get("items", []):
                    results.append(self._repo_to_remote_skill(item, "github"))
            except Exception:
                pass
        
        return results
    
    def _repo_to_remote_skill(self, repo: Dict[str, Any], source: str) -> RemoteSkill:
        """Convert GitHub repo data to RemoteSkill."""
        return RemoteSkill(
            skill_id=repo["name"].lower(),
            name=repo["name"],
            version="latest",  # Will be resolved on fetch
            description=repo.get("description", ""),
            author=repo["owner"]["login"],
            tags=[],  # Would need additional API call
            source=source,
            source_url=repo["html_url"],
            download_url=repo.get("clone_url"),
            homepage=repo.get("homepage"),
            stars=repo.get("stargazers_count", 0),
            updated_at=datetime.fromisoformat(
                repo["updated_at"].replace("Z", "+00:00")
            ) if repo.get("updated_at") else None,
        )
    
    def _fetch_json(self, url: str) -> Any:
        """Fetch JSON from URL."""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))


class RegistryAPIClient:
    """
    Client for official SkillHub registry API.
    
    Provides:
    - Skill search
    - Skill metadata
    - Version listing
    - Download URLs
    """
    
    DEFAULT_API_URL = "https://api.skillhub.dev"
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        cache_dir: Optional[Path] = None,
    ):
        self.api_url = api_url or self.DEFAULT_API_URL
        self.cache_dir = cache_dir or Path.home() / ".skillhub" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._index_cache: Optional[List[RemoteSkill]] = None
        self._index_cache_time: Optional[datetime] = None
        self._cache_ttl = timedelta(hours=1)
        self._lock = threading.RLock()
    
    def fetch_index(self, force: bool = False) -> List[RemoteSkill]:
        """
        Fetch the complete skill index.
        
        Args:
            force: Force refresh even if cached
        
        Returns:
            List of all available skills
        """
        with self._lock:
            if not force and self._index_cache and self._index_cache_time:
                if datetime.now() - self._index_cache_time < self._cache_ttl:
                    return self._index_cache
        
        # Try API first
        try:
            url = f"{self.api_url}/v1/skills"
            data = self._fetch_json(url)
            skills = [RemoteSkill.from_dict(item) for item in data.get("skills", [])]
            
            with self._lock:
                self._index_cache = skills
                self._index_cache_time = datetime.now()
            
            return skills
        except Exception:
            pass
        
        # Fallback to local cache file
        cache_file = self.cache_dir / "index.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                skills = [RemoteSkill.from_dict(item) for item in data.get("skills", [])]
                
                with self._lock:
                    self._index_cache = skills
                    self._index_cache_time = datetime.now()
                
                return skills
            except Exception:
                pass
        
        return []
    
    def search(self, query: str, limit: int = 20) -> List[RemoteSkill]:
        """Search for skills in the registry."""
        # Try API search
        try:
            url = f"{self.api_url}/v1/skills/search?q={urllib.parse.quote(query)}&limit={limit}"
            data = self._fetch_json(url)
            return [RemoteSkill.from_dict(item) for item in data.get("skills", [])]
        except Exception:
            pass
        
        # Fallback to local index search
        index = self.fetch_index()
        query_lower = query.lower()
        
        results = []
        for skill in index:
            score = 0
            
            # Name match
            if query_lower in skill.name.lower():
                score += 10
            
            # Description match
            if query_lower in skill.description.lower():
                score += 5
            
            # Tag match
            for tag in skill.tags:
                if query_lower in tag.lower():
                    score += 3
            
            if score > 0:
                results.append((skill, score))
        
        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        return [skill for skill, _ in results[:limit]]
    
    def get_skill(self, skill_id: str) -> Optional[RemoteSkill]:
        """Get a specific skill by ID."""
        try:
            url = f"{self.api_url}/v1/skills/{skill_id}"
            data = self._fetch_json(url)
            return RemoteSkill.from_dict(data)
        except Exception:
            # Fallback to index search
            index = self.fetch_index()
            for skill in index:
                if skill.skill_id == skill_id:
                    return skill
            return None
    
    def get_versions(self, skill_id: str) -> List[VersionInfo]:
        """Get all available versions for a skill."""
        try:
            url = f"{self.api_url}/v1/skills/{skill_id}/versions"
            data = self._fetch_json(url)
            return [VersionInfo.from_dict(item) for item in data.get("versions", [])]
        except Exception:
            return []
    
    def download_skill(
        self,
        skill_id: str,
        version: Optional[str] = None,
        target_dir: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Download a skill to a directory.
        
        Args:
            skill_id: Skill to download
            version: Specific version (default: latest)
            target_dir: Target directory (default: temp)
        
        Returns:
            Path to downloaded skill directory
        """
        skill = self.get_skill(skill_id)
        if not skill:
            return None
        
        target_dir = target_dir or Path(tempfile.mkdtemp())
        
        # Try download URL
        if skill.download_url:
            try:
                # Download and extract
                return self._download_and_extract(skill.download_url, target_dir)
            except Exception:
                pass
        
        # If source is GitHub, clone it
        if skill.source == "github" and skill.source_url:
            match = re.match(r'https://github\.com/([^/]+)/([^/]+)', skill.source_url)
            if match:
                owner, repo = match.groups()
                github = GitHubClient()
                if github.clone_repo(owner, repo, target_dir, version):
                    return target_dir
        
        return None
    
    def _download_and_extract(self, url: str, target_dir: Path) -> Path:
        """Download and extract a zip/tar file."""
        import zipfile
        import tarfile
        
        # Download to temp file
        with tempfile.NamedTemporaryFile(suffix=".download", delete=False) as f:
            temp_path = Path(f.name)
            urllib.request.urlretrieve(url, temp_path)
        
        try:
            # Try zip
            if url.endswith(".zip") or zipfile.is_zipfile(temp_path):
                with zipfile.ZipFile(temp_path) as zf:
                    # Find root directory in archive
                    names = zf.namelist()
                    if names:
                        root = names[0].split("/")[0]
                        zf.extractall(tempfile.gettempdir())
                        extracted = Path(tempfile.gettempdir()) / root
                        if extracted != target_dir:
                            shutil.move(str(extracted), str(target_dir))
                        return target_dir
            
            # Try tar
            if tarfile.is_tarfile(temp_path):
                with tarfile.open(temp_path) as tf:
                    tf.extractall(target_dir)
                    return target_dir
        finally:
            temp_path.unlink(missing_ok=True)
        
        raise ValueError("Unsupported archive format")
    
    def _fetch_json(self, url: str) -> Any:
        """Fetch JSON from URL."""
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))


class RemoteRegistry:
    """
    Remote skill registry.
    
    Combines multiple sources:
    - Official SkillHub API
    - GitHub repositories
    - Community registries
    
    Example:
        >>> registry = RemoteRegistry()
        >>> 
        >>> # Search for skills
        >>> results = registry.search("weather")
        >>> 
        >>> # Get skill info
        >>> skill = registry.get("weather-forecast")
        >>> 
        >>> # List available versions
        >>> versions = registry.list_versions("weather-forecast")
        >>> 
        >>> # Fetch a skill
        >>> skill_path = registry.fetch("weather-forecast", version="1.2.0")
    """
    
    def __init__(
        self,
        github_token: Optional[str] = None,
        api_url: Optional[str] = None,
        cache_dir: Optional[Path] = None,
    ):
        """
        Initialize remote registry.
        
        Args:
            github_token: GitHub personal access token
            api_url: SkillHub API URL
            cache_dir: Cache directory
        """
        self.github = GitHubClient(token=github_token)
        self.api = RegistryAPIClient(api_url=api_url, cache_dir=cache_dir)
        self.cache_dir = cache_dir or Path.home() / ".skillhub" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._lock = threading.RLock()
    
    def search(self, query: str, limit: int = 20) -> List[RemoteSkill]:
        """
        Search for skills across all sources.
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of matching skills
        """
        results = []
        seen_ids = set()
        
        # Search API
        api_results = self.api.search(query, limit)
        for skill in api_results:
            if skill.skill_id not in seen_ids:
                results.append(skill)
                seen_ids.add(skill.skill_id)
        
        # Search GitHub if we need more results
        if len(results) < limit:
            github_results = self.github.search_skills(query, limit - len(results))
            for skill in github_results:
                if skill.skill_id not in seen_ids:
                    results.append(skill)
                    seen_ids.add(skill.skill_id)
        
        return results[:limit]
    
    def get(self, skill_id: str) -> Optional[RemoteSkill]:
        """
        Get a skill by ID.
        
        Tries API first, then GitHub.
        """
        # Try API
        skill = self.api.get_skill(skill_id)
        if skill:
            return skill
        
        # Try GitHub (owner/repo format)
        if "/" in skill_id:
            try:
                owner, repo = skill_id.split("/", 1)
                repo_info = self.github.fetch_repo_info(owner, repo)
                return self.github._repo_to_remote_skill(repo_info, "github")
            except Exception:
                pass
        
        return None
    
    def list_versions(self, skill_id: str) -> List[VersionInfo]:
        """
        List all available versions for a skill.
        
        Args:
            skill_id: Skill ID or GitHub repo (owner/repo)
        
        Returns:
            List of VersionInfo
        """
        # Try API first
        versions = self.api.get_versions(skill_id)
        if versions:
            return versions
        
        # Try GitHub
        if "/" in skill_id:
            owner, repo = skill_id.split("/", 1)
            return self.github.list_versions(owner, repo)
        
        return []
    
    def fetch(
        self,
        skill_id: str,
        version: Optional[str] = None,
        target_dir: Optional[Path] = None,
    ) -> Optional[Skill]:
        """
        Fetch a skill from remote.
        
        Args:
            skill_id: Skill ID or GitHub repo (owner/repo)
            version: Specific version to fetch
            target_dir: Target directory
        
        Returns:
            Loaded Skill object
        """
        target_dir = target_dir or Path(tempfile.mkdtemp())
        
        # Try API download
        if "/" not in skill_id:
            downloaded = self.api.download_skill(skill_id, version, target_dir)
            if downloaded:
                return self._load_skill(downloaded)
        
        # Try GitHub clone
        if "/" in skill_id:
            owner, repo = skill_id.split("/", 1)
        else:
            # Get source URL from API
            skill = self.api.get_skill(skill_id)
            if skill and skill.source_url:
                match = re.match(r'https://github\.com/([^/]+)/([^/]+)', skill.source_url)
                if match:
                    owner, repo = match.groups()
                else:
                    return None
            else:
                return None
        
        if self.github.clone_repo(owner, repo, target_dir, version):
            # Remove .git directory
            git_dir = target_dir / ".git"
            if git_dir.exists():
                shutil.rmtree(git_dir)
            return self._load_skill(target_dir)
        
        return None
    
    def fetch_index(self, force: bool = False) -> List[RemoteSkill]:
        """
        Fetch the complete skill index.
        
        Args:
            force: Force refresh
        
        Returns:
            List of all available skills
        """
        return self.api.fetch_index(force=force)
    
    def is_update_available(
        self,
        skill_id: str,
        current_version: str,
    ) -> Optional[str]:
        """
        Check if an update is available.
        
        Args:
            skill_id: Skill ID
            current_version: Currently installed version
        
        Returns:
            Latest version if update available, None otherwise
        """
        versions = self.list_versions(skill_id)
        if not versions:
            return None
        
        latest = versions[0].version
        
        # Simple version comparison (assumes semver)
        if latest != current_version:
            try:
                from packaging import version
                if version.parse(latest) > version.parse(current_version):
                    return latest
            except ImportError:
                # Fallback: string comparison
                if latest > current_version:
                    return latest
        
        return None
    
    def _load_skill(self, skill_dir: Path) -> Optional[Skill]:
        """Load a skill from directory."""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None
        
        try:
            from ..core.skill import SkillLoader
            loader = SkillLoader(skill_dir.parent)
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


# Import urllib.parse for URL encoding
import urllib.parse
