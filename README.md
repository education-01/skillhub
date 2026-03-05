# SkillHub

<div align="center">

**Skill Management Platform for AI Agents**

创建、分享、管理 AI Agent Skills

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 目录

- [简介](#简介)
- [特性](#特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [CLI 命令](#cli-命令)
- [创建 Skill](#创建-skill)
- [API 文档](#api-文档)
- [内置 Skills](#内置-skills)
- [开发指南](#开发指南)
- [贡献](#贡献)
- [License](#license)

---

## 简介

SkillHub 是一个轻量级的 **Skill 管理平台**，专门为 AI Agent 设计。它提供了一套标准化的方式来：

- **发现** - 自动发现目录中的 Skills
- **安装** - 从官方仓库、社区或 GitHub 安装 Skills
- **验证** - 确保 Skills 符合规范要求
- **管理** - 轻松管理已安装的 Skills
- **分享** - 通过 CLI 打包和分享 Skills

## 特性

- 📦 **统一管理** - 集中管理本地、官方和社区 Skills
- 🔍 **智能搜索** - 按名称、描述、标签搜索 Skills
- ✅ **自动验证** - 确保 Skills 符合规范
- 🚀 **简单安装** - 一键从官方仓库或 GitHub 安装
- 🛠️ **CLI 工具** - 完整的命令行工具支持
- 📝 **标准化格式** - 基于 SKILL.md 的标准格式
- 🔒 **安全执行** - 沙箱环境运行 Skills

---

## 安装

### 使用 pip

```bash
pip install skillhub
```

### 从源码安装

```bash
git clone https://github.com/education-01/skillhub
cd skillhub
pip install -e .
```

### 开发模式

```bash
pip install -e ".[dev]"
```

---

## 快速开始

### Python API

```python
from skillhub import SkillRegistry

# 创建注册表
registry = SkillRegistry()

# 搜索 Skills
results = registry.search("weather")
for result in results:
    print(f"📦 {result.name} v{result.version}")
    print(f"   {result.description}")
    print(f"   Source: {result.source}")

# 安装 Skill
skill = registry.install("weather")
print(f"Installed: {skill.meta.name}")

# 列出已安装的 Skills
for meta in registry.list_local():
    print(f"  - {meta.name} ({meta.version})")

# 获取 Skill 详情
skill = registry.get("weather")
print(f"Author: {skill.meta.author}")
print(f"Tags: {skill.meta.tags}")
```

### CLI

```bash
# 搜索
skillhub search weather

# 安装
skillhub install weather

# 查看详情
skillhub info weather

# 列出已安装
skillhub list
```

---

## CLI 命令

### `skillhub search`

搜索 Skills。

```bash
# 基本搜索
skillhub search weather

# JSON 输出
skillhub search weather --json

# 按标签过滤
skillhub search --tag utility

# 按作者过滤
skillhub search --author "SkillHub Team"
```

### `skillhub install`

安装 Skill。

```bash
# 从官方仓库安装
skillhub install weather

# 从 GitHub 安装
skillhub install owner/repo-name

# 指定版本
skillhub install weather --version 1.0.0
```

### `skillhub uninstall`

卸载 Skill。

```bash
skillhub uninstall weather
```

### `skillhub list`

列出 Skills。

```bash
# 列出已安装
skillhub list

# 包含所有（官方+社区）
skillhub list --all

# 按标签分组
skillhub list --tags

# JSON 输出
skillhub list --json
```

### `skillhub info`

查看 Skill 详情。

```bash
# 基本信息
skillhub info weather

# JSON 输出
skillhub info weather --json
```

### `skillhub create`

创建新 Skill。

```bash
# 交互式创建
skillhub create my-skill

# 指定参数
skillhub create my-skill \
  --author "Your Name" \
  --description "A cool skill" \
  --dir ./skills
```

### `skillhub validate`

验证 Skill。

```bash
skillhub validate ./my-skill
```

### `skillhub update`

更新 Skill。

```bash
# 更新单个
skillhub update weather

# 更新所有
skillhub update --all
```

---

## 创建 Skill

### 方法一：使用 CLI

```bash
skillhub create my-awesome-skill \
  --author "Your Name" \
  --description "Does something awesome"
```

这会创建以下结构：

```
my-awesome-skill/
├── SKILL.md      # 元数据和文档
├── skill.py      # Skill 实现
└── README.md     # 用户文档
```

### 方法二：手动创建

#### 1. 创建目录结构

```bash
mkdir my-skill
cd my-skill
```

#### 2. 创建 SKILL.md

```markdown
---
name: my-skill
version: 1.0.0
description: What this skill does
author: Your Name
tags:
  - utility
  - automation
dependencies: []
license: MIT
---

# My Skill

Detailed description of what this skill does.

## Usage

```python
from my_skill import execute

result = execute({"param": "value"})
print(result)
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| param | string | "" | Description |

## Examples

### Example 1
```python
execute({"param": "value"})
```
```

#### 3. 实现 skill.py

```python
"""My Skill - What it does."""
from typing import Dict, Any


SKILL_INFO = {
    "name": "my-skill",
    "version": "1.0.0",
    "description": "What this skill does",
}


def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the skill.
    
    Args:
        params: Skill parameters
    
    Returns:
        Execution result
    """
    # Your logic here
    param = params.get("param", "default")
    
    return {
        "success": True,
        "result": f"Processed: {param}",
    }


if __name__ == "__main__":
    # Demo
    result = execute({"param": "test"})
    print(result)
```

#### 4. 验证

```bash
skillhub validate ./my-skill
```

### Skill 规范

#### SKILL.md

SKILL.md 是 Skill 的核心文件，包含：

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| name | string | ✅ | Skill 名称（小写、连字符） |
| version | string | ✅ | 版本号（语义化版本） |
| description | string | ✅ | 简短描述 |
| author | string | ❌ | 作者 |
| tags | list | ❌ | 标签列表 |
| dependencies | list | ❌ | 依赖包 |
| license | string | ❌ | 许可证（默认 MIT） |
| homepage | string | ❌ | 主页 URL |
| repository | string | ❌ | 仓库 URL |

#### execute() 函数

每个 Skill 必须实现 `execute()` 函数：

```python
def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the skill.
    
    Args:
        params: 参数字典
    
    Returns:
        结果字典，至少包含 'success' 字段
    """
    return {
        "success": True,
        "data": "...",
    }
```

---

## API 文档

### SkillRegistry

Skill 注册表，管理 Skills 的发现、安装和卸载。

```python
from skillhub import SkillRegistry

registry = SkillRegistry(
    local_dir=Path("~/.skillhub/skills"),      # 本地 Skills 目录
    official_dir=Path("/path/to/official"),    # 官方 Skills 目录
    community_dir=Path("/path/to/community"),  # 社区 Skills 目录
)
```

#### 方法

##### `search(query: str) -> List[SearchResult]`

搜索 Skills。

```python
results = registry.search("weather")
for r in results:
    print(f"{r.name} ({r.source})")
```

##### `install(skill_id: str, version: str = None) -> Skill`

安装 Skill。

```python
# 从官方仓库安装
skill = registry.install("weather")

# 从 GitHub 安装
skill = registry.install("owner/repo")
```

##### `uninstall(skill_id: str) -> bool`

卸载 Skill。

```python
registry.uninstall("weather")
```

##### `get(skill_id: str) -> Optional[Skill]`

获取 Skill 详情。

```python
skill = registry.get("weather")
if skill:
    print(skill.meta.description)
```

##### `list_local() -> List[SkillMeta]`

列出已安装的 Skills。

```python
for meta in registry.list_local():
    print(f"{meta.name} v{meta.version}")
```

##### `list_official() -> List[SkillMeta]`

列出官方 Skills。

```python
for meta in registry.list_official():
    print(f"{meta.name}")
```

##### `update(skill_id: str) -> Skill`

更新 Skill。

```python
registry.update("weather")
```

### Skill

Skill 对象，包含元数据、文件和文档。

```python
from skillhub import Skill, SkillMeta

meta = SkillMeta(
    name="my-skill",
    version="1.0.0",
    description="Description",
    author="Author",
    tags=["utility"],
)

skill = Skill(meta=meta)
```

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| skill_id | str | 自动生成的 ID |
| meta | SkillMeta | 元数据 |
| files | List[SkillFile] | 文件列表 |
| readme | str | README 内容 |
| installed_at | datetime | 安装时间 |

#### 方法

##### `to_dict() -> Dict`

序列化为字典。

##### `from_dict(data: Dict) -> Skill`

从字典创建。

### SkillValidator

Skill 验证器。

```python
from skillhub.core import SkillValidator

validator = SkillValidator()
errors = validator.validate(skill)

if errors:
    for e in errors:
        print(f"Error: {e}")
else:
    print("Valid!")
```

### SkillPack

Skill 打包，用于批量安装相关 Skills。

```python
from skillhub.core import SkillPack

pack = SkillPack(
    name="dev-tools",
    skills=["git", "docker", "pytest"],
    description="Development tools",
)

results = pack.install(registry)
```

---

## 内置 Skills

| Skill | 版本 | 描述 |
|-------|------|------|
| [weather](skills/official/weather) | 1.0.0 | 天气查询（使用 wttr.in 免费API） |
| [calculator](skills/official/calculator) | 1.0.0 | 数学计算和单位转换 |

### Weather Skill

```python
from weather import execute

# 获取天气
result = execute({"location": "Beijing"})
# {"success": True, "temperature": "15°C", ...}

# 获取预报
result = execute({"location": "Shanghai", "action": "forecast", "days": 3})
```

### Calculator Skill

```python
from calculator import execute

# 计算
result = execute({"expression": "2 + 2 * 10"})
# {"success": True, "result": 22}

# 单位转换
result = execute({"value": 100, "from": "km", "to": "mi"})
# {"success": True, "result": 62.14}
```

---

## 开发指南

### 项目结构

```
skillhub/
├── skillhub/
│   ├── __init__.py
│   ├── cli.py              # CLI 入口
│   └── core/
│       ├── __init__.py
│       ├── registry.py     # 注册表
│       └── skill.py        # Skill 定义
├── skills/
│   └── official/           # 官方 Skills
│       ├── calculator/
│       └── weather/
├── tests/
│   ├── test_skill.py
│   └── test_registry.py
├── examples/
│   ├── basic_usage.py
│   └── custom_skill.py
├── pyproject.toml
└── README.md
```

### 运行测试

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 特定测试文件
pytest tests/test_skill.py

# 覆盖率
pytest --cov=skillhub
```

### 代码风格

```bash
# 检查
ruff check skillhub/

# 自动修复
ruff check --fix skillhub/

# 格式化
ruff format skillhub/
```

### 添加新的官方 Skill

1. 在 `skills/official/` 下创建目录
2. 添加 SKILL.md 和 skill.py
3. 编写测试
4. 提交 PR

---

## 贡献

欢迎贡献！请查看 [Contributing Guide](CONTRIBUTING.md)。

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## License

[MIT License](LICENSE)

---

<div align="center">

**Made with ❤️ by SkillHub Team**

</div>
