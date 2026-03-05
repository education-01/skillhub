#!/usr/bin/env python3
"""Basic usage example for SkillHub.

Demonstrates:
- Creating a registry
- Searching for skills
- Installing skills
- Listing installed skills
- Getting skill details
"""
from pathlib import Path
from skillhub import SkillRegistry


def main():
    """Run basic usage examples."""
    print("=" * 60)
    print("SkillHub Basic Usage Example")
    print("=" * 60)
    
    # 1. Create a registry
    print("\n1. Creating a registry...")
    registry = SkillRegistry()
    print(f"   Local skills directory: {registry.local_dir}")
    
    # 2. Search for skills
    print("\n2. Searching for skills...")
    results = registry.search("weather")
    print(f"   Found {len(results)} skills for 'weather'")
    
    for result in results:
        print(f"\n   📦 {result.name} v{result.version}")
        print(f"      {result.description[:50]}...")
        print(f"      Source: {result.source}")
        print(f"      Author: {result.author}")
    
    # 3. List installed skills
    print("\n3. Listing installed skills...")
    installed = registry.list_local()
    print(f"   {len(installed)} skills installed locally")
    
    for meta in installed:
        print(f"   - {meta.name} ({meta.version})")
    
    # 4. Install a skill
    print("\n4. Installing a skill...")
    try:
        # Note: This will fail if no official skills are available
        skill = registry.install("weather")
        print(f"   ✅ Installed: {skill.meta.name}")
    except ValueError as e:
        print(f"   ℹ️  {e}")
    
    # 5. Get skill details
    print("\n5. Getting skill details...")
    skill = registry.get("weather")
    if skill:
        print(f"   Name: {skill.meta.name}")
        print(f"   Version: {skill.meta.version}")
        print(f"   Description: {skill.meta.description}")
        print(f"   Author: {skill.meta.author}")
        print(f"   Tags: {', '.join(skill.meta.tags) or 'None'}")
        print(f"   Files: {len(skill.files)}")
        
        # Show files
        for f in skill.files:
            print(f"      [{f.file_type}] {f.path}")
    else:
        print("   Skill not found")
    
    # 6. List official skills
    print("\n6. Listing official skills...")
    official = registry.list_official()
    print(f"   {len(official)} official skills available")
    
    for meta in official:
        print(f"   - {meta.name} ({meta.version})")
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
