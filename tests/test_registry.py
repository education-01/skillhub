"""Tests for Skill Registry.

Tests cover:
- Registration
- Search
- Install/Uninstall
"""
from __future__ import annotations

import tempfile
import shutil
from pathlib import Path
import pytest

from skillhub.core.registry import (
    SkillRegistry,
    SearchResult,
    SkillPack,
    OFFICIAL_PACKS,
)
from skillhub.core.skill import Skill, SkillMeta


class TestSkillRegistry:
    """Tests for SkillRegistry."""
    
    def test_create_registry(self):
        """Test creating a registry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(local_dir=Path(tmpdir) / "skills")
            
            assert registry.local_dir.exists()
            assert registry.list_local() == []
    
    def test_list_local_empty(self):
        """Test listing when no skills installed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(local_dir=Path(tmpdir) / "skills")
            
            skills = registry.list_local()
            
            assert skills == []
    
    def test_list_local_with_skills(self):
        """Test listing installed skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            local_dir = Path(tmpdir) / "skills"
            local_dir.mkdir()
            
            # Create a skill
            skill_dir = local_dir / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: test-skill
version: 1.0.0
description: Test skill
author: Author
---
# Test
""")
            
            registry = SkillRegistry(local_dir=local_dir)
            skills = registry.list_local()
            
            assert len(skills) == 1
            assert skills[0].name == "test-skill"
    
    def test_list_official_empty(self):
        """Test listing official skills when none available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(
                local_dir=Path(tmpdir) / "skills",
                official_dir=None,
            )
            
            skills = registry.list_official()
            
            assert skills == []
    
    def test_list_official_with_skills(self):
        """Test listing official skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            
            # Create official skill
            official_dir = tmp / "official"
            official_dir.mkdir()
            skill_dir = official_dir / "official-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: official-skill
version: 1.0.0
description: Official skill
author: SkillHub Team
---
# Official Skill
""")
            
            registry = SkillRegistry(
                local_dir=tmp / "local",
                official_dir=official_dir,
            )
            
            skills = registry.list_official()
            
            assert len(skills) == 1
            assert skills[0].name == "official-skill"


class TestSkillSearch:
    """Tests for skill search functionality."""
    
    def test_search_by_name(self):
        """Test searching by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            
            # Create skill
            local_dir = tmp / "skills"
            local_dir.mkdir()
            skill_dir = local_dir / "weather-forecast"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: weather-forecast
version: 1.0.0
description: Weather forecast skill
author: Test
---
# Weather
""")
            
            registry = SkillRegistry(local_dir=local_dir)
            results = registry.search("weather")
            
            assert len(results) == 1
            assert results[0].name == "weather-forecast"
            assert results[0].source == "local"
    
    def test_search_by_description(self):
        """Test searching by description."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            
            local_dir = tmp / "skills"
            local_dir.mkdir()
            skill_dir = local_dir / "calc"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: calc
version: 1.0.0
description: Mathematical calculations and conversions
author: Test
---
# Calculator
""")
            
            registry = SkillRegistry(local_dir=local_dir)
            results = registry.search("math")
            
            assert len(results) == 1
            assert results[0].name == "calc"
    
    def test_search_by_tag(self):
        """Test searching by tag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            
            local_dir = tmp / "skills"
            local_dir.mkdir()
            skill_dir = local_dir / "docker-helper"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: docker-helper
version: 1.0.0
description: Docker utilities
author: Test
tags: [devops, docker, containers]
---
# Docker
""")
            
            registry = SkillRegistry(local_dir=local_dir)
            results = registry.search("devops")
            
            assert len(results) == 1
            assert results[0].name == "docker-helper"
    
    def test_search_no_results(self):
        """Test search with no results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(local_dir=Path(tmpdir) / "skills")
            
            results = registry.search("nonexistent")
            
            assert results == []
    
    def test_search_multiple_sources(self):
        """Test search returns results from multiple sources."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            
            # Create local skill
            local_dir = tmp / "local"
            local_dir.mkdir()
            local_skill = local_dir / "test-util"
            local_skill.mkdir()
            (local_skill / "SKILL.md").write_text("""---
name: test-util
version: 1.0.0
description: Test utility
author: Local
---
# Local
""")
            
            # Create official skill
            official_dir = tmp / "official"
            official_dir.mkdir()
            official_skill = official_dir / "test-official"
            official_skill.mkdir()
            (official_skill / "SKILL.md").write_text("""---
name: test-official
version: 1.0.0
description: Official test utility
author: Official
---
# Official
""")
            
            registry = SkillRegistry(
                local_dir=local_dir,
                official_dir=official_dir,
            )
            
            results = registry.search("test")
            
            # Should find both local and official
            sources = {r.source for r in results}
            assert "local" in sources
            assert "official" in sources


class TestSkillInstall:
    """Tests for skill installation."""
    
    def test_install_from_official(self):
        """Test installing from official directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            
            # Create official skill
            official_dir = tmp / "official"
            official_dir.mkdir()
            skill_dir = official_dir / "installable-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: installable-skill
version: 1.0.0
description: Installable skill
author: Test
---
# Installable
""")
            (skill_dir / "skill.py").write_text("def execute(p): return {}")
            
            # Create registry
            local_dir = tmp / "local"
            registry = SkillRegistry(
                local_dir=local_dir,
                official_dir=official_dir,
            )
            
            # Install
            skill = registry.install("installable-skill")
            
            assert skill is not None
            assert skill.meta.name == "installable-skill"
            assert (local_dir / "installable-skill").exists()
    
    def test_install_already_installed(self):
        """Test installing already installed skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            
            # Create skill in local dir
            local_dir = tmp / "local"
            local_dir.mkdir()
            skill_dir = local_dir / "existing-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: existing-skill
version: 1.0.0
description: Existing
author: Test
---
# Existing
""")
            
            registry = SkillRegistry(local_dir=local_dir)
            
            # Should raise error
            with pytest.raises(ValueError, match="already installed"):
                registry.install("existing-skill")
    
    def test_install_nonexistent(self):
        """Test installing non-existent skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(local_dir=Path(tmpdir) / "local")
            
            with pytest.raises(ValueError, match="not found"):
                registry.install("nonexistent-skill")
    
    def test_install_copies_all_files(self):
        """Test that install copies all skill files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            
            # Create official skill with multiple files
            official_dir = tmp / "official"
            official_dir.mkdir()
            skill_dir = official_dir / "multi-file-skill"
            skill_dir.mkdir()
            
            (skill_dir / "SKILL.md").write_text("""
---
name: multi-file-skill
version: 1.0.0
description: Multi file
author: Test
---
# Multi
""")
            (skill_dir / "skill.py").write_text("# skill")
            (skill_dir / "config.json").write_text("{}")
            
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "helper.py").write_text("# helper")
            
            # Install
            local_dir = tmp / "local"
            registry = SkillRegistry(
                local_dir=local_dir,
                official_dir=official_dir,
            )
            
            skill = registry.install("multi-file-skill")
            
            # Check all files copied
            installed_dir = local_dir / "multi-file-skill"
            assert (installed_dir / "SKILL.md").exists()
            assert (installed_dir / "skill.py").exists()
            assert (installed_dir / "config.json").exists()
            assert (installed_dir / "scripts" / "helper.py").exists()


class TestSkillUninstall:
    """Tests for skill uninstallation."""
    
    def test_uninstall_skill(self):
        """Test uninstalling a skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            local_dir = Path(tmpdir) / "skills"
            local_dir.mkdir()
            
            # Create skill
            skill_dir = local_dir / "removable-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""
---
name: removable-skill
version: 1.0.0
description: Removable
author: Test
---
# Removable
""")
            
            registry = SkillRegistry(local_dir=local_dir)
            
            # Verify installed
            assert len(registry.list_local()) == 1
            
            # Uninstall
            result = registry.uninstall("removable-skill")
            
            assert result is True
            assert len(registry.list_local()) == 0
            assert not skill_dir.exists()
    
    def test_uninstall_nonexistent(self):
        """Test uninstalling non-existent skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(local_dir=Path(tmpdir) / "skills")
            
            with pytest.raises(ValueError, match="not installed"):
                registry.uninstall("nonexistent")


class TestSkillGet:
    """Tests for getting skills."""
    
    def test_get_local_skill(self):
        """Test getting a local skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            local_dir = Path(tmpdir) / "skills"
            local_dir.mkdir()
            
            skill_dir = local_dir / "gettable-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""
---
name: gettable-skill
version: 1.0.0
description: Gettable
author: Test
---
# Gettable
""")
            
            registry = SkillRegistry(local_dir=local_dir)
            skill = registry.get("gettable-skill")
            
            assert skill is not None
            assert skill.meta.name == "gettable-skill"
    
    def test_get_official_skill(self):
        """Test getting an official skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            
            # Create official skill
            official_dir = tmp / "official"
            official_dir.mkdir()
            skill_dir = official_dir / "official-get"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""
---
name: official-get
version: 1.0.0
description: Official
author: Official
---
# Official
""")
            
            registry = SkillRegistry(
                local_dir=tmp / "local",
                official_dir=official_dir,
            )
            
            skill = registry.get("official-get")
            
            assert skill is not None
            assert skill.meta.name == "official-get"
    
    def test_get_nonexistent(self):
        """Test getting non-existent skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(local_dir=Path(tmpdir) / "skills")
            
            skill = registry.get("nonexistent")
            
            assert skill is None


class TestSearchResult:
    """Tests for SearchResult."""
    
    def test_create_search_result(self):
        """Test creating a search result."""
        result = SearchResult(
            skill_id="test-id",
            name="Test Skill",
            description="Test description",
            version="1.0.0",
            author="Author",
            tags=["test"],
            source="local",
        )
        
        assert result.skill_id == "test-id"
        assert result.name == "Test Skill"
        assert result.source == "local"


class TestSkillPack:
    """Tests for SkillPack."""
    
    def test_create_pack(self):
        """Test creating a skill pack."""
        pack = SkillPack(
            name="dev-tools",
            skills=["git", "docker", "pytest"],
            description="Development tools",
        )
        
        assert pack.name == "dev-tools"
        assert len(pack.skill_ids) == 3
        assert "git" in pack.skill_ids
    
    def test_pack_to_dict(self):
        """Test converting pack to dict."""
        pack = SkillPack(
            name="test-pack",
            skills=["skill1", "skill2"],
            description="Test",
        )
        
        data = pack.to_dict()
        
        assert data["name"] == "test-pack"
        assert data["skills"] == ["skill1", "skill2"]
    
    def test_pack_from_dict(self):
        """Test creating pack from dict."""
        data = {
            "name": "from-dict",
            "skills": ["a", "b"],
            "description": "From dict",
        }
        
        pack = SkillPack.from_dict(data)
        
        assert pack.name == "from-dict"
        assert pack.skill_ids == ["a", "b"]
    
    def test_official_packs_exist(self):
        """Test that official packs are defined."""
        assert len(OFFICIAL_PACKS) > 0
        
        pack_names = [p.name for p in OFFICIAL_PACKS]
        assert "dev-basics" in pack_names or "ai-assistant" in pack_names


# Integration tests
class TestRegistryIntegration:
    """Integration tests for SkillRegistry."""
    
    def test_full_install_uninstall_cycle(self):
        """Test complete install/uninstall cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            
            # Create official skill
            official_dir = tmp / "official"
            official_dir.mkdir()
            skill_dir = official_dir / "cycle-test"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""
---
name: cycle-test
version: 1.0.0
description: Cycle test
author: Test
---
# Cycle Test
""")
            (skill_dir / "skill.py").write_text("def execute(p): return {}")
            
            # Create registry
            local_dir = tmp / "local"
            registry = SkillRegistry(
                local_dir=local_dir,
                official_dir=official_dir,
            )
            
            # Search
            results = registry.search("cycle")
            assert len(results) == 1
            
            # Install
            skill = registry.install("cycle-test")
            assert skill is not None
            
            # List
            installed = registry.list_local()
            assert len(installed) == 1
            
            # Get
            fetched = registry.get("cycle-test")
            assert fetched is not None
            
            # Uninstall
            registry.uninstall("cycle-test")
            assert len(registry.list_local()) == 0
    
    def test_search_after_install(self):
        """Test that installed skills show as local in search."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            
            # Create official skill
            official_dir = tmp / "official"
            official_dir.mkdir()
            skill_dir = official_dir / "search-test"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""
---
name: search-test
version: 1.0.0
description: Search test skill
author: Test
---
# Search Test
""")
            (skill_dir / "skill.py").write_text("pass")
            
            local_dir = tmp / "local"
            registry = SkillRegistry(
                local_dir=local_dir,
                official_dir=official_dir,
            )
            
            # Before install - shows as official
            results_before = registry.search("search")
            sources_before = {r.source for r in results_before}
            assert "official" in sources_before
            
            # Install
            registry.install("search-test")
            
            # After install - shows as local
            results_after = registry.search("search")
            sources_after = {r.source for r in results_after}
            assert "local" in sources_after
