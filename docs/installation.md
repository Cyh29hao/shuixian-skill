# 安装到 Codex 或 Claude Code

水仙是一个可以交给本地 AI agent 使用的 skill。安装的是 `create-shuixian` 构建器；它读取你选定的语料，生成另一个用于和你对话的镜像 skill。构建器和私人镜像是两个不同目录。

## 让 agent 安装

把[仓库地址](https://github.com/Cyh29hao/shuixian-skill)和目标一起交给有本机文件、终端权限的 Codex 或 Claude Code，例如：

```text
请安装 https://github.com/Cyh29hao/shuixian-skill ，在当前项目中使用。
我想用自己的聊天记录还原我的说话方式，之后和自己说话。
先确认你使用的宿主，把构建器装到对应的 skills 目录；已有安装不要覆盖。
聊天记录由我指定文件或会话范围。若还没有可读导出，告诉我卡在哪里；
不要把预设或几句临时设定说成已经学会了我。
```

提供可读语料后，agent 还要区分你的发言和对方的发言，提炼表达习惯，保存镜像，再实际聊一轮。安装文件成功只是其中一步。直接读取本机微信还取决于客户端和数据格式，见[微信导入说明](../references/wechat-import.md)。

## 手动安装：项目内一条命令

先在终端进入你准备和水仙对话的项目目录。下面两条按你用的宿主选一条运行；Git 会创建缺失的父目录，不需要先执行 `mkdir`。

| 宿主 | 安装命令 | 在聊天中调用构建器 |
| --- | --- | --- |
| Codex | `git clone https://github.com/Cyh29hao/shuixian-skill .agents/skills/create-shuixian` | `$create-shuixian` |
| Claude Code | `git clone https://github.com/Cyh29hao/shuixian-skill .claude/skills/create-shuixian` | `/create-shuixian` |

需已安装 Git；运行导入和保存工具还需要 Python 3.9+。普通文本/JSON 导入及镜像文件生成使用 Python 标准库；微信解密有另外的条件和依赖，不属于这条安装命令。

安装整个仓库，不要只下载 `SKILL.md`：提示、参考说明、导入和保存脚本都在同一个包中。目标目录已存在时，Git 会拒绝覆盖；先使用已有版本，或检查差异后另行更新，不要为了安装删除私人镜像。

没有 Git 时可以下载仓库 ZIP，解压后把包含 `SKILL.md` 的那一层文件夹命名为 `create-shuixian`，放进对应的 skills 目录。正确结果是 `…/skills/create-shuixian/SKILL.md`，不是再多一层仓库目录。此 ZIP 路径未在本轮实测。

## 安装一次，在多个项目里用

把完整仓库放进个人 skills 目录：

| 宿主 | 个人构建器目录 |
| --- | --- |
| Codex | `~/.agents/skills/create-shuixian/` |
| Claude Code | `~/.claude/skills/create-shuixian/` |

`~` 指你的系统用户主目录。为了避免不同终端对 `~` 的展开差异，执行 `git clone` 时也可以使用该目录的完整路径，并给带空格的路径加引号。Codex 的上述个人路径来自当前官方 skills 文档；不要把 `CODEX_HOME` 配置目录当作这张表的替代路径。

个人安装只改变构建器的来源。运行脚本时，脚本用实际安装位置的完整路径，输出 `--base-dir` 仍指向当前项目的 skills 目录：Codex 用 `.agents/skills`，Claude Code 用 `.claude/skills`。不要把私人镜像写到构建器内部。

## 怎样知道真的能用了

1. **目录正确**：上述目录内有 `SKILL.md`、`tools/`、`prompts/` 和 `references/`。
2. **构建器出现**：Codex 的技能选择器中能找到 `create-shuixian`，或 Claude Code 的 `/skills` 中列出它；按表里的名字调用。
3. **工具可运行**：让 agent 从实际安装目录运行 `tools/transcript_importer.py --help`，然后按[快速开始](quickstart.md)导入你选定的可读语料。
4. **镜像能对话**：检查保存后的镜像目录和调用名，再用新镜像试聊。检查自己的用词、句子长短和接话方式；不像的地方具体指出来并保存纠偏。

Codex 通常自动检测 skill 变更；未显示时重新启动 Codex。Claude Code 通常在当前会话发现 skills 变更；如果顶层 `.claude/skills` 是这次才创建的，执行 `/reload-skills`。宿主权限拒绝写入时，应先解决该目标的权限，不要把普通草稿目录称作已安装。

这里讨论的是能访问你本机文件的 Codex / **Claude Code 本地会话**。Claude 网页聊天、Cowork 和云端会话的 skill 来源不同，不能把本机目录安装当作这些场景已经可用。

## 已检查到哪里

安装路径、调用名和刷新方式已对照[Codex 官方说明](https://learn.chatgpt.com/docs/build-skills)与[Claude Code 官方说明](https://code.claude.com/docs/en/skills)核对。文件安装和宿主实际加载是两项不同的验收；本会话的 PATH 未找到 `claude` 命令，因此未启动真实 Claude Code，也没有据此声称已完成 Claude 主机发现或模型实聊。
