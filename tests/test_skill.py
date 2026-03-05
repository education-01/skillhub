"""Tests for Skill module.

Tests cover:
- Skill loading
- Skill validation
- Skill execution
"""
from __future__ import annotations

import tempfile
from pathlib import Path
import pytest

from skillhub.core.skill import (
    Skill,
    SkillMeta,
    SkillFile,
    SkillLoader,
    SkillValidator,
)


class TestSkillMeta:
    """Tests for SkillMeta."""
    
    def test_create_meta(self):
        """Test creating skill metadata."""
        meta = SkillMeta(
            name="test-skill",
            version="1.0.0",
            description="Test skill",
            author="Test Author",
        )
        
        assert meta.name == "test-skill"
        assert meta.version == "1.0.0"
        assert meta.description == "Test skill"
        assert meta.author == "Test Author"
        assert meta.tags == []
        assert meta.dependencies == []
    
    def test_meta_to_dict(self):
        """Test converting metadata to dict."""
        meta = SkillMeta(
            name="test",
            version="1.0.0",
            description="Test",
            author="Author",
            tags=["tag1", "tag2"],
        )
        
        data = meta.to_dict()
        
        assert data["name"] == "test"
        assert data["version"] == "1.0.0"
        assert data["tags"] == ["tag1", "tag2"]
    
    def test_meta_from_dict(self):
        """Test creating metadata from dict."""
        data = {
            "name": "test",
            "version": "2.0.0",
            "description": "Test skill",
            "author": "Author",
            "tags": ["utility"],
        }
        
        meta = SkillMeta.from_dict(data)
        
        assert meta.name == "test"
        assert meta.version == "2.0.0"
        assert meta.tags == ["utility"]


class TestSkill:
    """Tests for Skill class."""
    
    def test_create_skill(self):
        """Test creating a skill."""
        meta = SkillMeta(
            name="test-skill",
            version="1.0.0",
            description="Test",
            author="Author",
        )
        
        skill = Skill(meta=meta)
        
        assert skill.meta == meta
        assert skill.skill_id == "test-skill"
        assert skill.files == []
        assert skill.readme == ""
    
    def test_skill_id_generation(self):
        """Test skill ID is generated from name."""
        meta = SkillMeta(
            name="My Cool Skill!",
            version="1.0.0",
            description="Test",
            author="Author",
        )
        
        skill = Skill(meta=meta)
        
        # ID should be lowercase and special chars replaced
        assert "my" in skill.skill_id
        assert "!" not in skill.skill_id
    
    def test_skill_to_dict(self):
        """Test converting skill to dict."""
        meta = SkillMeta(
            name="test",
            version="1.0.0",
            description="Test",
            author="Author",
        )
        
        files = [
            SkillFile(path="skill.py", content="# code", file_type="script"),
        ]
        
        skill = Skill(
            meta=meta,
            files=files,
            readme="# Test",
        )
        
        data = skill.to_dict()
        
        assert data["meta"]["name"] == "test"
        assert len(data["files"]) == 1
        assert data["readme"] == "# Test"
    
    def test_skill_from_dict(self):
        """Test creating skill from dict."""
        data = {
            "skill_id": "my-skill",
            "meta": {
                "name": "My Skill",
                "version": "1.0.0",
                "description": "Test",
                "author": "Author",
            },
            "files": [
                {
                    "path": "skill.py",
                    "content": "# code",
                    "file_type": "script",
                }
            ],
            "readme": "# README",
        }
        
        skill = Skill.from_dict(data)
        
        assert skill.skill_id == "my-skill"
        assert skill.meta.name == "My Skill"
        assert len(skill.files) == 1
        assert skill.readme == "# README"


class TestSkillLoader:
    """Tests for SkillLoader."""
    
    def test_discover_skills(self):
        """Test discovering skills in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir)
            
            # Create skill directories
            skill1 = skills_dir / "skill1"
            skill1.mkdir()
            (skill1 / "SKILL.md").write_text("---\nname: skill1\n---\n# Skill 1")
            
            skill2 = skills_dir / "skill2"
            skill2.mkdir()
            (skill2 / "SKILL.md").write_text("---\nname: skill2\n---\n# Skill 2")
            
            loader = SkillLoader(skills_dir)
            discovered = loader.discover()
            
            assert len(discovered) == 2
            assert "skill1" in discovered
            assert "skill2" in discovered
    
    def test_load_skill(self):
        """Test loading a skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir)
            
            skill_dir = skills_dir / "test-skill"
            skill_dir.mkdir()
            
            # Create SKILL.md with frontmatter
            skill_md = """---
name: test-skill
version: 1.0.0
description: Test skill
author: Test Author
tags: test, demo
---

# Test Skill

This is a test skill.
"""
            (skill_dir / "SKILL.md").write_text(skill_md)
            
            # Create skill.py
            (skill_dir / "skill.py").write_text("""
def execute(params):
    return {"success": True}
""")
            
            loader = SkillLoader(skills_dir)
            skill = loader.load("test-skill")
            
            assert skill is not None
            assert skill.meta.name == "test-skill"
            assert skill.meta.version == "1.0.0"
            assert skill.meta.author == "Test Author"
            assert "test" in skill.meta.tags
            assert len(skill.files) == 1
            assert skill.files[0].path == "skill.py"
    
    def test_load_skill_with_config(self):
        """Test loading skill with skill.json config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir)
            
            skill_dir = skills_dir / "config-skill"
            skill_dir.mkdir()
            
            (skill_dir / "SKILL.md").write_text("# Skill")
            (skill_dir / "skill.json").write_text("""{
                "name": "config-skill",
                "version": "2.0.0",
                "description": "From config",
                "author": "Config Author"
            }""")
            
            loader = SkillLoader(skills_dir)
            skill = loader.load("config-skill")
            
            assert skill is not None
            # Config should override frontmatter
            assert skill.meta.version == "2.0.0"
            assert skill.meta.description == "From config"
    
    def test_load_nonexistent_skill(self):
        """Test loading non-existent skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = SkillLoader(Path(tmpdir))
            skill = loader.load("nonexistent")
            
            assert skill is None


class TestSkillValidator:
    """Tests for SkillValidator."""
    
    def test_validate_valid_skill(self):
        """Test validating a valid skill."""
        meta = SkillMeta(
            name="valid-skill",
            version="1.0.0",
            description="A valid skill",
            author="Author",
        )
        
        skill = Skill(
            meta=meta,
            readme="# Valid Skill",
        )
        
        validator = SkillValidator()
        errors = validator.validate(skill)
        
        assert errors == []
        assert validator.is_valid(skill)
    
    def test_validate_missing_name(self):
        """Test validation catches missing name."""
        meta = SkillMeta(
            name="",
            version="1.0.0",
            description="Test",
            author="Author",
        )
        
        skill = Skill(meta=meta, readme="# Test")
        
        validator = SkillValidator()
        errors = validator.validate(skill)
        
        assert len(errors) > 0
        assert any("name" in e.lower() for e in errors)
        assert not validator.is_valid(skill)
    
    def test_validate_missing_description(self):
        """Test validation catches missing description."""
        meta = SkillMeta(
            name="test",
            version="1.0.0",
            description="",
            author="Author",
        )
        
        skill = Skill(meta=meta, readme="# Test")
        
        validator = SkillValidator()
        errors = validator.validate(skill)
        
        assert any("description" in e.lower() for e in errors)
    
    def test_validate_invalid_version(self):
        """Test validation catches invalid version format."""
        meta = SkillMeta(
            name="test",
            version="invalid",
            description="Test",
            author="Author",
        )
        
        skill = Skill(meta=meta, readme="# Test")
        
        validator = SkillValidator()
        errors = validator.validate(skill)
        
        assert any("version" in e.lower() for e in errors)
    
    def test_validate_missing_skill_md(self):
        """Test validation catches missing SKILL.md."""
        meta = SkillMeta(
            name="test",
            version="1.0.0",
            description="Test",
            author="Author",
        )
        
        skill = Skill(meta=meta, readme="", files=[])
        
        validator = SkillValidator()
        errors = validator.validate(skill)
        
        assert any("skill.md" in e.lower() for e in errors)


class TestSkillFile:
    """Tests for SkillFile."""
    
    def test_create_skill_file(self):
        """Test creating a skill file."""
        file = SkillFile(
            path="scripts/main.py",
            content="print('hello')",
            file_type="script",
        )
        
        assert file.path == "scripts/main.py"
        assert file.content == "print('hello')"
        assert file.file_type == "script"
    
    def test_file_to_dict(self):
        """Test converting file to dict."""
        file = SkillFile(
            path="config.json",
            content='{"key": "value"}',
            file_type="config",
        )
        
        data = file.to_dict()
        
        assert data["path"] == "config.json"
        assert data["content"] == '{"key": "value"}'
        assert data["file_type"] == "config"


# Integration tests
class TestSkillIntegration:
    """Integration tests for Skill module."""
    
    def test_full_skill_lifecycle(self):
        """Test complete skill lifecycle: create, validate, serialize."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir)
            
            # Create skill directory
            skill_dir = skills_dir / "lifecycle-test"
            skill_dir.mkdir()
            
            # Create SKILL.md
            skill_md = """---
name: lifecycle-test
version: 1.0.0
description: Test lifecycle
author: Test
tags: [test]
---

# Lifecycle Test

A test skill for lifecycle testing.
"""
            (skill_dir / "SKILL.md").write_text(skill_md)
            
            # Create skill.py
            (skill_dir / "skill.py").write_text("""
SKILL_INFO = {
    "name": "lifecycle-test",
    "version": "1.0.0",
}

def execute(params):
    return {"success": True, "params": params}
""")
            
            # Load skill
            loader = SkillLoader(skills_dir)
            skill = loader.load("lifecycle-test")
            
            assert skill is not None
            
            # Validate
            validator = SkillValidator()
            assert validator.is_valid(skill)
            
            # Serialize
            data = skill.to_dict()
            assert data["meta"]["name"] == "lifecycle-test"
            
            # Deserialize
            skill2 = Skill.from_dict(data)
            assert skill2.meta.name == skill.meta.name
            assert skill2.meta.version == skill.meta.version
