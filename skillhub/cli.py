#!/usr/bin/env python3
"""SkillHub CLI.

Command-line interface for skill management using Typer.

Usage:
    skillhub init <name>           # Create new skill directory structure
    skillhub list                  # List all installed skills
    skillhub install <name>        # Install skill from registry
    skillhub search <query>        # Search for skills
    skillhub info <skill>          # Show skill details
    skillhub uninstall <skill>     # Uninstall a skill
    skillhub validate <path>       # Validate a skill
    skillhub update <skill>        # Update a skill
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from .core import Skill, SkillRegistry, SkillValidator

app = typer.Typer(
    name="skillhub",
    help="🔧 Skill Management Platform - 创建、分享、管理 AI Agent Skills",
    add_completion=False,
)

console = Console()


def get_registry(local_dir: Optional[Path] = None) -> SkillRegistry:
    """Get SkillRegistry instance with optional local directory."""
    # Set official_dir to the bundled skills directory
    official_dir = Path(__file__).parent.parent / "skills"
    return SkillRegistry(local_dir=local_dir, official_dir=official_dir)


# ============================================================================
# Command: init
# ============================================================================
@app.command("init")
def cmd_init(
    name: Annotated[str, typer.Argument(help="Skill name (e.g., my-awesome-skill)")],
    dir: Annotated[
        Optional[Path],
        typer.Option("--dir", "-d", help="Output directory (default: current dir)")
    ] = None,
    author: Annotated[
        Optional[str],
        typer.Option("--author", "-a", help="Author name")
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option("--description", "--desc", help="Skill description")
    ] = None,
    template: Annotated[
        str,
        typer.Option("--template", "-t", help="Template type: basic, advanced")
    ] = "basic",
):
    """
    Create a new skill directory structure.
    
    Creates a complete skill skeleton with:
    - SKILL.md (metadata + documentation)
    - skill.py (main skill implementation)
    - README.md (usage guide)
    - tests/ (optional test directory)
    
    Examples:
        skillhub init my-skill
        skillhub init my-skill --author "John Doe" --description "A cool skill"
        skillhub init my-skill --template advanced
    """
    output_dir = dir or Path.cwd()
    skill_dir = output_dir / name
    
    # Validate skill name
    if not name.replace("-", "").replace("_", "").isalnum():
        console.print(f"[red]❌ Invalid skill name: {name}[/red]")
        console.print("   Use only letters, numbers, hyphens, and underscores")
        raise typer.Exit(1)
    
    if skill_dir.exists():
        console.print(f"[red]❌ Directory already exists: {skill_dir}[/red]")
        raise typer.Exit(1)
    
    # Create directory structure
    skill_dir.mkdir(parents=True)
    
    if template == "advanced":
        (skill_dir / "tests").mkdir()
        (skill_dir / "examples").mkdir()
    
    # Create SKILL.md
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(f"""---
name: {name}
version: 0.1.0
description: {description or "A new skill"}
author: {author or "Your Name"}
tags: []
dependencies: []
license: MIT
---

# {name}

{description or "Description of what this skill does."}

## Usage

```
Example usage here
```

## Features

- Feature 1
- Feature 2

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| - | - | - | - |
""")
    
    # Create skill.py
    skill_py = skill_dir / "skill.py"
    skill_py.write_text(f'''"""{{name}} skill.

{description or "A skill for..."}
"""
from __future__ import annotations

from typing import Dict, Any


SKILL_INFO = {{
    "name": "{name}",
    "version": "0.1.0",
    "description": "{description or "A new skill"}",
}}


def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the skill.
    
    Args:
        params: Skill parameters
    
    Returns:
        Execution result
    """
    # TODO: Implement skill logic
    return {{
        "success": True,
        "message": "Skill executed successfully",
        "data": params,
    }}
''')
    
    # Create README.md
    readme = skill_dir / "README.md"
    readme.write_text(f"""# {name}

{description or "A new skill"}

## Installation

```bash
skillhub install {name}
```

## Usage

```python
from {name} import execute

result = execute({{"param": "value"}})
print(result)
```

## API

### execute(params)

Execute the skill.

**Parameters:**
- `params` (dict): Skill parameters

**Returns:**
- `dict`: Execution result

## License

MIT
""")
    
    # Create pyproject.toml for advanced template
    if template == "advanced":
        pyproject = skill_dir / "pyproject.toml"
        pyproject.write_text(f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.1.0"
description = "{description or 'A new skill'}"
authors = [
    {{name = "{author or 'Your Name'}"}}
]
license = "MIT"
requires-python = ">=3.10"

[project.optional-dependencies]
dev = ["pytest>=7.0"]
''')
        
        # Create test file
        test_file = skill_dir / "tests" / "test_skill.py"
        test_file.write_text(f'''"""Tests for {name} skill."""
import pytest
from skill import execute


def test_execute_basic():
    """Test basic execution."""
    result = execute({{}})
    assert result["success"] is True


def test_execute_with_params():
    """Test execution with parameters."""
    result = execute({{"input": "test"}})
    assert result["success"] is True
    assert result["data"]["input"] == "test"
''')
        
        # Create example file
        example_file = skill_dir / "examples" / "basic.py"
        example_file.write_text(f'''"""Basic example for {name} skill."""
from skill import execute

# Example usage
result = execute({{
    "param1": "value1",
    "param2": "value2",
}})

print(f"Result: {{result}}")
''')
    
    # Print success message
    console.print(Panel(
        f"[green]✅ Created skill: {skill_dir}[/green]\n\n"
        f"[bold]Files created:[/bold]\n"
        f"  - SKILL.md (metadata + docs)\n"
        f"  - skill.py (main implementation)\n"
        f"  - README.md (usage guide)"
        + (f"\n  - pyproject.toml\n  - tests/test_skill.py\n  - examples/basic.py" if template == "advanced" else ""),
        title=f"📦 {name}",
        border_style="green",
    ))
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  1. Edit [cyan]SKILL.md[/cyan] to add metadata")
    console.print(f"  2. Implement skill logic in [cyan]skill.py[/cyan]")
    console.print(f"  3. Validate: [cyan]skillhub validate {skill_dir}[/cyan]")
    console.print(f"  4. Test locally: [cyan]cd {skill_dir} && python -m pytest[/cyan]" if template == "advanced" else "")


# ============================================================================
# Command: list
# ============================================================================
@app.command("list")
def cmd_list(
    local_dir: Annotated[
        Optional[Path],
        typer.Option("--local-dir", help="Local skills directory")
    ] = None,
    all: Annotated[
        bool,
        typer.Option("--all", "-a", help="Include official and community skills")
    ] = False,
    tags: Annotated[
        bool,
        typer.Option("--tags", "-t", help="Group skills by tags")
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output as JSON")
    ] = False,
):
    """
    List all installed skills.
    
    Shows locally installed skills by default. Use --all to include
    official and community skills from the registry.
    
    Examples:
        skillhub list
        skillhub list --all
        skillhub list --tags
        skillhub list --json
    """
    registry = get_registry(local_dir)
    
    if tags:
        # List by tags
        skills = registry.list_local()
        by_tag: dict[str, list] = {}
        
        for meta in skills:
            for tag in meta.tags or ["untagged"]:
                if tag not in by_tag:
                    by_tag[tag] = []
                by_tag[tag].append(meta)
        
        if not by_tag:
            console.print("[yellow]No skills installed[/yellow]")
            raise typer.Exit(0)
        
        console.print("\n[bold]Skills by tag:[/bold]\n")
        for tag in sorted(by_tag.keys()):
            console.print(f"  [cyan][{tag}][/cyan]")
            for meta in by_tag[tag]:
                console.print(f"    • {meta.name} [dim]({meta.version})[/dim]")
        
        return
    
    # Get skills to display
    local_skills = registry.list_local()
    
    if all:
        official_skills = registry.list_official()
        all_skills = local_skills + official_skills
    else:
        all_skills = local_skills
    
    if not all_skills:
        console.print("[yellow]No skills found[/yellow]")
        console.print("\n[dim]Install a skill: skillhub install <name>[/dim]")
        console.print("[dim]Create a skill: skillhub init <name>[/dim]")
        raise typer.Exit(0)
    
    if json_output:
        data = [s.to_dict() for s in all_skills]
        console.print(json.dumps(data, indent=2))
        return
    
    # Create table
    table = Table(title=f"\nInstalled Skills ({len(all_skills)})")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Version", style="green")
    table.add_column("Description", style="dim")
    table.add_column("Tags", style="yellow")
    
    for meta in all_skills:
        desc = meta.description[:50] + "..." if len(meta.description) > 50 else meta.description
        tags_str = ", ".join(meta.tags[:3]) if meta.tags else "-"
        table.add_row(meta.name, meta.version, desc, tags_str)
    
    console.print(table)


# ============================================================================
# Command: install
# ============================================================================
@app.command("install")
def cmd_install(
    skill: Annotated[str, typer.Argument(help="Skill name or GitHub repo (owner/repo)")],
    version: Annotated[
        Optional[str],
        typer.Option("--version", "-v", help="Version to install")
    ] = None,
    local_dir: Annotated[
        Optional[Path],
        typer.Option("--local-dir", help="Local skills directory")
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Force reinstall if already installed")
    ] = False,
):
    """
    Install a skill from registry or GitHub.
    
    Can install from:
    - Official registry (skill name)
    - GitHub repository (owner/repo)
    
    Examples:
        skillhub install weather
        skillhub install owner/skill-repo
        skillhub install weather --version 1.0.0
        skillhub install weather --force
    """
    registry = get_registry(local_dir)
    
    # Check if already installed
    installed_dir = registry.local_dir / skill.split("/")[-1]
    if installed_dir.exists() and not force:
        console.print(f"[yellow]⚠️  Skill already installed: {skill}[/yellow]")
        console.print("   Use --force to reinstall")
        raise typer.Exit(1)
    
    # Force reinstall: remove existing
    if force and installed_dir.exists():
        shutil.rmtree(installed_dir)
    
    console.print(f"[bold]📦 Installing skill: {skill}[/bold]")
    
    with console.status("[bold green]Installing..."):
        try:
            installed_skill = registry.install(skill, version=version)
        except ValueError as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            raise typer.Exit(1)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Git clone failed: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]❌ Failed: {e}[/red]")
            raise typer.Exit(1)
    
    console.print(Panel(
        f"[green]✅ Installed: {installed_skill.meta.name} v{installed_skill.meta.version}[/green]\n\n"
        f"[dim]Description:[/dim] {installed_skill.meta.description}\n"
        f"[dim]Location:[/dim] {installed_dir}",
        title="Installation Complete",
        border_style="green",
    ))


# ============================================================================
# Command: search
# ============================================================================
@app.command("search")
def cmd_search(
    query: Annotated[str, typer.Argument(help="Search query")],
    local_dir: Annotated[
        Optional[Path],
        typer.Option("--local-dir", help="Local skills directory")
    ] = None,
    tag: Annotated[
        Optional[str],
        typer.Option("--tag", "-t", help="Filter by tag")
    ] = None,
    author: Annotated[
        Optional[str],
        typer.Option("--author", "-a", help="Filter by author")
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output as JSON")
    ] = False,
):
    """
    Search for skills in registry.
    
    Searches skill names, descriptions, and tags.
    
    Examples:
        skillhub search weather
        skillhub search web --tag api
        skillhub search python --author "John"
        skillhub search all --json
    """
    registry = get_registry(local_dir)
    
    with console.status(f"[bold green]Searching for '{query}'..."):
        results = registry.search(query)
    
    # Apply filters
    if tag:
        results = [r for r in results if tag.lower() in [t.lower() for t in r.tags]]
    
    if author:
        results = [r for r in results if author.lower() in r.author.lower()]
    
    if not results:
        console.print(f"[yellow]No skills found matching '{query}'[/yellow]")
        console.print("\n[dim]Try a different search term or browse available skills:[/dim]")
        console.print("[dim]  skillhub list --all[/dim]")
        raise typer.Exit(0)
    
    if json_output:
        data = [
            {
                "id": r.skill_id,
                "name": r.name,
                "description": r.description,
                "version": r.version,
                "author": r.author,
                "tags": r.tags,
                "source": r.source,
            }
            for r in results
        ]
        console.print(json.dumps(data, indent=2))
        return
    
    # Create results table
    console.print(f"\n[bold]Found {len(results)} skill(s) matching '{query}':[/bold]\n")
    
    table = Table()
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Version", style="green")
    table.add_column("Source", style="magenta")
    table.add_column("Description", style="dim")
    
    for r in results:
        desc = r.description[:45] + "..." if len(r.description) > 45 else r.description
        source_icon = {"local": "📁", "official": "🏢", "community": "👥", "github": "🔗"}.get(r.source, "📦")
        table.add_row(r.name, r.version, f"{source_icon} {r.source}", desc)
    
    console.print(table)
    
    console.print(f"\n[dim]Install with: skillhub install <name>[/dim]")


# ============================================================================
# Command: info
# ============================================================================
@app.command("info")
def cmd_info(
    skill: Annotated[str, typer.Argument(help="Skill name")],
    local_dir: Annotated[
        Optional[Path],
        typer.Option("--local-dir", help="Local skills directory")
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output as JSON")
    ] = False,
):
    """
    Show detailed information about a skill.
    
    Examples:
        skillhub info weather
        skillhub info my-skill --json
    """
    registry = get_registry(local_dir)
    skill_obj = registry.get(skill)
    
    if not skill_obj:
        console.print(f"[red]❌ Skill not found: {skill}[/red]")
        raise typer.Exit(1)
    
    if json_output:
        console.print(json.dumps(skill_obj.to_dict(), indent=2))
        return
    
    meta = skill_obj.meta
    
    # Create info panel
    info_text = f"""
[bold cyan]{meta.name}[/bold cyan] [dim]v{meta.version}[/dim]

[dim]Description:[/dim] {meta.description}
[dim]Author:[/dim]      {meta.author}
[dim]License:[/dim]     {meta.license}
[dim]Python:[/dim]      >={meta.min_python}"""

    if meta.tags:
        info_text += f"\n[dim]Tags:[/dim]       {', '.join(meta.tags)}"
    
    if meta.dependencies:
        info_text += f"\n[dim]Dependencies:[/dim]\n  • " + "\n  • ".join(meta.dependencies)
    
    if meta.homepage:
        info_text += f"\n[dim]Homepage:[/dim]   {meta.homepage}"
    
    if meta.repository:
        info_text += f"\n[dim]Repository:[/dim] {meta.repository}"
    
    if skill_obj.files:
        info_text += f"\n\n[bold]Files ({len(skill_obj.files)}):[/bold]"
        for f in skill_obj.files[:10]:  # Show first 10 files
            info_text += f"\n  • [{f.file_type:8}] {f.path}"
        if len(skill_obj.files) > 10:
            info_text += f"\n  ... and {len(skill_obj.files) - 10} more"
    
    console.print(Panel(info_text, border_style="cyan"))


# ============================================================================
# Command: uninstall
# ============================================================================
@app.command("uninstall")
def cmd_uninstall(
    skill: Annotated[str, typer.Argument(help="Skill name")],
    local_dir: Annotated[
        Optional[Path],
        typer.Option("--local-dir", help="Local skills directory")
    ] = None,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation")
    ] = False,
):
    """
    Uninstall a skill.
    
    Examples:
        skillhub uninstall weather
        skillhub uninstall weather -y
    """
    registry = get_registry(local_dir)
    
    # Check if installed
    skill_obj = registry.get(skill)
    if not skill_obj:
        console.print(f"[red]❌ Skill not installed: {skill}[/red]")
        raise typer.Exit(1)
    
    # Confirm
    if not yes:
        confirm = typer.confirm(f"Uninstall {skill}?", default=False)
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)
    
    try:
        registry.uninstall(skill)
        console.print(f"[green]✅ Uninstalled: {skill}[/green]")
    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


# ============================================================================
# Command: validate
# ============================================================================
@app.command("validate")
def cmd_validate(
    path: Annotated[Path, typer.Argument(help="Skill directory path")],
):
    """
    Validate a skill directory.
    
    Checks for required files and proper metadata format.
    
    Examples:
        skillhub validate ./my-skill
        skillhub validate /path/to/skill
    """
    if not path.exists():
        console.print(f"[red]❌ Directory not found: {path}[/red]")
        raise typer.Exit(1)
    
    skill = Skill.from_dir(path) if hasattr(Skill, 'from_dir') else None
    
    # Manual loading if from_dir doesn't exist
    if not skill:
        from .core.skill import SkillLoader
        loader = SkillLoader(path.parent)
        skill = loader.load(path.name)
    
    if not skill:
        console.print(f"[red]❌ Invalid skill directory: {path}[/red]")
        console.print("   Make sure it contains a SKILL.md file")
        raise typer.Exit(1)
    
    validator = SkillValidator()
    errors = validator.validate(skill)
    
    if errors:
        console.print(f"[red]❌ Validation failed:[/red]\n")
        for error in errors:
            console.print(f"   • {error}")
        raise typer.Exit(1)
    else:
        console.print(Panel(
            f"[green]✅ Valid skill: {skill.meta.name} v{skill.meta.version}[/green]\n\n"
            f"[dim]All checks passed![/dim]",
            title="Validation Complete",
            border_style="green",
        ))


# ============================================================================
# Command: update
# ============================================================================
@app.command("update")
def cmd_update(
    skill: Annotated[
        Optional[str],
        typer.Argument(help="Skill name to update")
    ] = None,
    local_dir: Annotated[
        Optional[Path],
        typer.Option("--local-dir", help="Local skills directory")
    ] = None,
    all: Annotated[
        bool,
        typer.Option("--all", "-a", help="Update all installed skills")
    ] = False,
):
    """
    Update a skill to latest version.
    
    Examples:
        skillhub update weather
        skillhub update --all
    """
    registry = get_registry(local_dir)
    
    if all:
        skills = registry.list_local()
        if not skills:
            console.print("[yellow]No skills installed[/yellow]")
            raise typer.Exit(0)
        
        console.print(f"[bold]Updating {len(skills)} skills...[/bold]\n")
        
        success_count = 0
        for meta in skills:
            console.print(f"Updating [cyan]{meta.name}[/cyan]...")
            try:
                registry.update(meta.name)
                console.print(f"  [green]✅ Updated[/green]")
                success_count += 1
            except Exception as e:
                console.print(f"  [red]❌ Failed: {e}[/red]")
        
        console.print(f"\n[bold]Updated {success_count}/{len(skills)} skills[/bold]")
        return
    
    if not skill:
        console.print("[red]❌ Specify skill name or use --all[/red]")
        raise typer.Exit(1)
    
    try:
        updated = registry.update(skill)
        console.print(f"[green]✅ Updated: {updated.meta.name} v{updated.meta.version}[/green]")
    except Exception as e:
        console.print(f"[red]❌ Failed: {e}[/red]")
        raise typer.Exit(1)


# ============================================================================
# Main entry point
# ============================================================================
def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
