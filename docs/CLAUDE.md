# Claude Code 适配

这一版开始加入 Claude 适配，但目前仍然是“简单适配版”。

## 推荐安装方式

全局安装：

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Cyh29hao/shuixian-skill ~/.claude/skills/shuixian
```

项目内安装：

```bash
mkdir -p .claude/skills
git clone https://github.com/Cyh29hao/shuixian-skill .claude/skills/shuixian
```

## 推荐调用方式

优先尝试：

```text
/shuixian
```

如果你的 Claude 版本更依赖 `SKILL.md` frontmatter 名称，也可以尝试：

```text
/create-shuixian
```

## 当前适配范围

- 仓库结构保持简单，便于直接放进 `.claude/skills/`
- README 已加入 Claude 安装和调用说明
- Skill 主体逻辑不依赖 Codex 专属脚手架才能阅读
- 导入工具仍然是本地 Python 脚本，可直接运行

## 目前还没有承诺的部分

- 不承诺所有 Claude 版本上的 slash 命令行为完全一致
- 不承诺已经针对 Claude 的上下文策略做过深度打磨
- 不承诺已经加入专门的 Claude-only prompt 变体

## 后续计划

1. 补一版更明确的 Claude 调用别名策略
2. 补一版更适合 Claude 长对话的提示结构
3. 如果必要，再拆出 Claude 定制入口
