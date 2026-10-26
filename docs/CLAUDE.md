# 在 Claude Code 使用水仙

水仙使用通用 `SKILL.md` 格式，导入和保存工具是本地 Python 脚本。Claude Code 与 Codex 的主要区别是 **skills 目录和调用前缀**。

在准备对话的项目目录执行：

```sh
git clone https://github.com/Cyh29hao/shuixian-skill .claude/skills/create-shuixian
```

在 Claude Code 聊天中调用：

```text
/create-shuixian
用我指定的聊天记录还原我的说话方式，让我和自己的镜像聊天。
先确认哪些发言是我写的，再提炼表达习惯，不把对方的话算成我的。
```

构建器的 frontmatter 名称是 `create-shuixian`，因此使用 `/create-shuixian`。不再把 `/shuixian` 当作另一个默认别名。

个人安装的位置是 `~/.claude/skills/create-shuixian/`。完整步骤、无 Git 时的文件布局和检查方法见[安装说明](installation.md)。

## 镜像也要放在 Claude Code 的目录中

把 `--base-dir` 明确设为当前项目的 `.claude/skills`。例如，下面只列出这个项目已有的镜像，脚本路径以项目内安装为例：

```sh
python .claude/skills/create-shuixian/tools/skill_writer.py --action list --base-dir .claude/skills
```

创建后应得到 `.claude/skills/shuixian-<slug>/SKILL.md`，调用名为 `/shuixian-<slug>`。不要照抄 Codex 示例中的 `.agents/skills` 和 `$shuixian-<slug>`。

若构建器装在个人目录，使用实际安装位置的完整脚本路径，输出目录仍指向当前项目。已有镜像不要覆盖；更新和回滚也使用同一个 `--base-dir`。

## 未出现或未更新时

Claude Code 会监听已有 skills 目录的 `SKILL.md` 变更。如果 `.claude/skills` 在本次会话开始时还不存在，执行 `/reload-skills` 后检查 `/skills`。权限、组织配置、bare/safe mode 等仍可能限制加载；文件存在不能证明当前宿主已加载。

这份说明针对本地 Claude Code。仅装进本机 `~/.claude/skills`，不会让 Claude 网页聊天、Cowork 或云端会话自动得到它。

安装位置、命名与刷新方式来自[Claude Code 官方 skills 文档](https://code.claude.com/docs/en/skills)。本会话的 PATH 未找到 `claude` 命令，未启动真实 Claude Code；已验证的文件与工具结果不能代替 Claude 主机发现或模型试聊。
