# SkillHub

**Skill Management Platform** - 创建、分享、管理 AI Agent Skills

一个轻量级的 Skill 管理平台，支持：

- 🔧 **Skill 发现** - 自动发现目录中的 Skills
- 📦 **安装管理** - 从官方/社区/GitHub 安装
- ✅ **验证** - 确保 Skills 符合规范
- 📦 **分享** - 通过 CLI 分享 Skills

- 🏪 **包管理** - 打包相关 Skills

## 安装

```
pip install skillhub
```

或从源码：
```
git clone https://github.com/education-01/skillhub
cd skillhub
pip install -e .
```

## 快速开始
```python
from skillhub import SkillRegistry

# 创建注册表
registry = SkillRegistry()

# 搜索 Skills
results = registry.search("weather")
for result in results:
    print(f"{result.name} - {result.description}")

# 安装 Skill
registry.install("weather")

# 列出已安装
for skill in registry.list_local():
    print(f"{skill.name} ({skill.version})")
```

## CLI 使用
```bash
# 搜索 Skills
skillhub search weather

# 安装 Skill
skillhub install weather

# 查看详情
skillhub info weather

# 创建新 Skill
skillhub create my-skill --author "Your Name" --description "A cool skill"
```

## 创建自己的 Skill
```bash
# 交互式创建
skillhub create my-awesome-skill

# 錙入元数据
Name: my-awesome-skill
Version: 0.0.1
Description: A cool skill
Author: Your Name
...
```

## 开发
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check skillhub/
```

## 内置 Skills
| Skill | 描述 |
|-------|------|
| weather | 天气查询 (免费 API) |
| calculator | 数学计算 |

## 目录结构
```
skillhub/
├── cli.py              # CLI 入口
├── core/
│   ├── __init__.py
│   ├── registry.py   # 注册表
│   └── skill.py       # Skill 定义
├── skills/             # 官方 Skills
│   ├── calculator/
│   └── weather/
└── tests/
```

## License

MIT
