#!/usr/bin/env python3
"""Custom skill creation example for SkillHub.

Demonstrates:
- Creating a custom skill
- Writing SKILL.md
- Implementing execute function
- Testing the skill
"""
from pathlib import Path
from skillhub.core import Skill, SkillMeta, SkillFile, SkillValidator


def create_custom_skill():
    """Create a custom skill example."""
    print("=" * 60)
    print("Creating a Custom Skill")
    print("=" * 60)
    
    # 1. Define skill metadata
    print("\n1. Creating metadata...")
    meta = SkillMeta(
        name="greeting",
        version="1.0.0",
        description="Generate personalized greetings",
        author="Your Name",
        tags=["utility", "text"],
        dependencies=[],
        license="MIT",
    )
    print(f"   Name: {meta.name}")
    print(f"   Version: {meta.version}")
    print(f"   Tags: {meta.tags}")
    
    # 2. Create skill code
    print("\n2. Writing skill code...")
    skill_code = '''"""Greeting skill - Generate personalized greetings."""
from typing import Dict, Any


SKILL_INFO = {
    "name": "greeting",
    "version": "1.0.0",
    "description": "Generate personalized greetings",
}


def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a greeting.
    
    Args:
        params: Dict with optional 'name' and 'style' keys
            - name: Person to greet (default: "Friend")
            - style: Greeting style ("formal", "casual", "friendly")
    
    Returns:
        Dict with 'success' and 'greeting' keys
    """
    name = params.get("name", "Friend")
    style = params.get("style", "friendly")
    
    greetings = {
        "formal": f"Good day, {name}. It is a pleasure to meet you.",
        "casual": f"Hey {name}! What's up?",
        "friendly": f"Hi {name}! Great to see you! 👋",
    }
    
    greeting = greetings.get(style, greetings["friendly"])
    
    return {
        "success": True,
        "greeting": greeting,
        "name": name,
        "style": style,
    }


if __name__ == "__main__":
    # Test the skill
    print("Testing greeting skill:")
    print(execute({"name": "Alice", "style": "friendly"}))
    print(execute({"name": "Bob", "style": "formal"}))
'''
    print("   Skill code created")
    
    # 3. Create README
    print("\n3. Creating README...")
    readme = """# Greeting Skill

Generate personalized greetings in different styles.

## Installation

```bash
skillhub install greeting
```

## Usage

```python
from greeting import execute

# Friendly greeting
result = execute({"name": "Alice", "style": "friendly"})
print(result["greeting"])  # Hi Alice! Great to see you! 👋

# Formal greeting
result = execute({"name": "Bob", "style": "formal"})
print(result["greeting"])  # Good day, Bob...

# Casual greeting
result = execute({"name": "Charlie", "style": "casual"})
print(result["greeting"])  # Hey Charlie! What's up?
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| name | string | "Friend" | Name to greet |
| style | string | "friendly" | Greeting style (formal/casual/friendly) |

## License

MIT
"""
    print("   README created")
    
    # 4. Create SKILL.md
    print("\n4. Creating SKILL.md...")
    skill_md = f"""---
name: {meta.name}
version: {meta.version}
description: {meta.description}
author: {meta.author}
tags: {meta.tags}
license: {meta.license}
---

{readme}
"""
    print("   SKILL.md created")
    
    # 5. Assemble the skill
    print("\n5. Assembling skill package...")
    skill = Skill(
        meta=meta,
        files=[
            SkillFile(path="skill.py", content=skill_code, file_type="script"),
        ],
        readme=readme,
    )
    print(f"   Skill ID: {skill.skill_id}")
    print(f"   Files: {len(skill.files)}")
    
    # 6. Validate the skill
    print("\n6. Validating skill...")
    validator = SkillValidator()
    errors = validator.validate(skill)
    
    if errors:
        print("   ❌ Validation failed:")
        for error in errors:
            print(f"      - {error}")
    else:
        print("   ✅ Skill is valid!")
    
    return skill, skill_md, skill_code


def save_skill_to_directory(skill, skill_md, skill_code, output_dir):
    """Save skill to a directory."""
    print("\n" + "=" * 60)
    print("Saving Skill to Directory")
    print("=" * 60)
    
    skill_dir = Path(output_dir) / skill.meta.name
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    # Save files
    (skill_dir / "SKILL.md").write_text(skill_md)
    (skill_dir / "skill.py").write_text(skill_code)
    
    print(f"\n✅ Saved to: {skill_dir}")
    print("\nFiles:")
    for f in skill_dir.iterdir():
        print(f"   - {f.name}")


def test_custom_skill():
    """Test the custom skill."""
    print("\n" + "=" * 60)
    print("Testing Custom Skill")
    print("=" * 60)
    
    # Import and test
    # Note: In real usage, you'd import from the installed skill
    from typing import Dict, Any
    
    def execute(params: Dict[str, Any]) -> Dict[str, Any]:
        """Simplified execute for testing."""
        name = params.get("name", "Friend")
        style = params.get("style", "friendly")
        
        greetings = {
            "formal": f"Good day, {name}.",
            "casual": f"Hey {name}!",
            "friendly": f"Hi {name}! 👋",
        }
        
        return {
            "success": True,
            "greeting": greetings.get(style, greetings["friendly"]),
        }
    
    # Test cases
    test_cases = [
        {"name": "Alice", "style": "friendly"},
        {"name": "Bob", "style": "formal"},
        {"name": "Charlie", "style": "casual"},
        {"name": "Diana"},  # Default style
        {},  # All defaults
    ]
    
    print("\nTest cases:")
    for i, params in enumerate(test_cases, 1):
        result = execute(params)
        print(f"\n   Test {i}: {params}")
        print(f"   Result: {result['greeting']}")


def main():
    """Run all examples."""
    # Create the custom skill
    skill, skill_md, skill_code = create_custom_skill()
    
    # Save to a temporary directory for demo
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        save_skill_to_directory(skill, skill_md, skill_code, tmpdir)
    
    # Test the skill logic
    test_custom_skill()
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("   1. Use 'skillhub create <name>' to scaffold a new skill")
    print("   2. Edit SKILL.md to add metadata")
    print("   3. Implement execute() in skill.py")
    print("   4. Validate: skillhub validate ./<skill-name>")
    print("   5. Share your skill!")


if __name__ == "__main__":
    main()
