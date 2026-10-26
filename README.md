<div align="center">

# 水仙.skill

### 如果世界上还有另一个你，ta 会怎么接住这句话？

把你的语气、偏心和停顿，写成一个可以慢慢校准的镜像伴侣 skill。

[立即试玩](#一分钟试玩) · [真实试聊](docs/try-it.md) · [English](README_EN.md) · [第一次使用](docs/quickstart.md) · [MIT](LICENSE)

</div>

<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="assets/hero-mobile-v1.png" />
    <img src="assets/hero-preview-v13.png" alt="水仙.skill：同一句话，甜系恋人、深夜共脑、同频朋友三种创作回应" width="920" />
  </picture>
</p>

**你熟悉的说话方式，可以有一个新的落点。** 先试一段不需要私密聊天的公开预设，再用几段代表性材料，把它从“气质不错”慢慢调到“这句话有点像我”。

公开预设只供试气质。自己的水仙从你愿意给的材料开始，像不像，要在实际聊天里慢慢校准。

## 先选一种靠近方式

- **甜系恋人** · 亲近、轻轻调侃、慢慢靠近。预设 `sweet-gender-flipped`。
- **深夜共脑** · 安静、留白、一起想明白。预设 `midnight-same-form`。
- **同频朋友** · 熟悉、直接、有分寸地拆台。预设 `close-friend-same-form`。

恋人、朋友、外观呈现、镜像深度和隐私范围可以分别选择。公开预设是起点；创建自己的版本时，不必照着它的关系设定走。

[先听它真正回过的两句 →](docs/try-it.md) 从一家面包店聊起，再说“这次别追问”，看看一句纠偏后它怎么接。

## 一分钟试玩

需要 Python 3.9+、Git，以及支持本地 skills 的 Codex。以下命令在你想放置水仙的项目目录里运行，PowerShell / bash 均可：

```sh
git clone https://github.com/Cyh29hao/shuixian-skill .agents/skills/create-shuixian
python .agents/skills/create-shuixian/tools/demo_builder.py --preset sweet-gender-flipped --base-dir .agents/skills
```

然后在**同一项目**的 Codex 聊天中输入：

```text
$shuixian-sweet-gender-flipped-demo
今天先别分析我，陪我说两句。
```

如果当前会话还看不到新 skill，重新打开该项目或重启 Codex。创建命令会保护已有同名镜像；重试时换 `--slug`，已有镜像通过更新流程修改。

只需要试玩和文本生成时，无需安装 `requirements.txt`。不同导入渠道的可选依赖见[渠道说明](references/import-channels.md)。已有仓库也可以在仓库根目录运行 `python tools/demo_builder.py --list-presets`。

## 从好气质，到自己的水仙

<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="assets/quickstart-mobile-v1.png" />
    <img src="assets/quickstart-flow-v10.png" alt="四步：选一种关系，零私密聊天试玩，三段样本校准，一句话纠偏" width="920" />
  </picture>
</p>

不必先导出全部历史。三段材料就能开始一次有依据的尝试：

1. 一段“我平时真这么说话”的样本。
2. 一段你喜欢被怎样回应的对话，标出谁是你。
3. 一段你不喜欢的回应，以及你希望怎么改。

```text
$create-shuixian
给我做一个同频朋友，短句，可以有点损，别叫我宝贝。
以下三段是合成示例，我会换成自己的材料：
1. 我的说法：“终于改好了，允许我得意三分钟。”
2. 我喜欢的回应：“三分钟哪够。最难的那处怎么过的？”
3. 我不喜欢：“你的坚持照亮了成长之路。”太大太空。
先给一段试聊，并说清哪些来自材料、哪些只是暂定。
```

材料少也能做初版；不知道的地方留白。语气样本、对方说的话、你自己的偏好各有用途，不会因为出现过一句话就自动成为“你的价值观”。

## 不对味，直接改

```text
刚才太像情感专家了。先问我具体卡在哪，不要替我总结。
只改这条；其余语气保留。
```

这能先调整当前对话。要在以后继续使用时保留这条，再调用 builder：

```text
$create-shuixian
把上面这条纠偏写进 $shuixian-<slug>，替换冲突的旧规则。
给我看变更和一段重试；保留可回滚版本。
```

**“这轮改口了”和“已写回 skill”是两件事。** 更新后检查文件和版本，再在新会话试一次。手动创建、更新、列版本、回滚的命令见[完整使用路径](docs/quickstart.md)。

## 可以拿什么来做

| 材料 | 使用方式 | 当前边界 |
| --- | --- | --- |
| 自述、聊天片段、偏好清单 | 直接交给 builder | 无样本时是按描述定制，无法证明像本人 |
| 文本 / Markdown / JSON / JSONL | `tools/transcript_importer.py` | 支持常见结构，遇到不支持的结构会报错；不代表兼容所有平台 |
| 微信桌面端导出 / 数据库 | [微信导入说明](references/wechat-import.md) | best effort，版本、权限和数据库格式会影响可用性 |
| iMessage `chat.db` | `tools/imessage_importer.py` | macOS 本地数据库路径；本轮未实机验证 |
| 截图 | 交给具备看图能力的宿主辅助理解 | Python 工具不提供独立 OCR |

画像工具会整理发言和词频线索，帮助挑选值得读的材料。它采用启发式规则，不能验证真实关系、人格或价值观。**第三方聊天、关系推断和隐私范围都应由你选择。**

## 安装到其他位置

个人 skills 目录也可以安装 builder：

```sh
git clone https://github.com/Cyh29hao/shuixian-skill ~/.agents/skills/create-shuixian
```

该目录是 [Codex 官方文档列出的个人 skill 位置](https://learn.chatgpt.com/docs/build-skills)。运行脚本时使用实际安装目录的完整路径，`--base-dir` 指向你当前项目的 `.agents/skills`，避免在 builder 安装目录里生成自己的镜像。

Claude Code 的文件结构适配与已知限制见 [docs/CLAUDE.md](docs/CLAUDE.md)。它与 Codex 的发现、调用和写入位置不同，尚未做本轮跨宿主验收。

## 它保存的是什么

镜像由宿主模型依据 skill 与选定材料扮演；Python 工具负责整理、写入和版本管理。

每个生成的水仙由 `SKILL.md`、`meta.json`、语气、思路、关系和可选外观文件组成；更新会保留版本。只有你选择归档的素材才进入其 `knowledge/`。这些文件可读、可改、可由你删除。

“本地文件”不等于“不会上传”：宿主读取材料后，是否发送给模型服务，取决于宿主及其数据设置。`style-only` 是材料使用约定，不是自动脱敏或数据隔离装置。[隐私与边界](references/privacy-and-safety.md)说明了如何少给材料、区分来源和撤回保存内容。

它是虚构的镜像角色，不具备被验证的独立人格、跨平台记忆或读心能力。相似感、亲密感和长期陪伴效果仍属于待实际使用验证的体验。

## 继续打磨的依据

- [第一次使用与验收](docs/quickstart.md)：从安装到纠偏、回滚。
- [公开对话样例](docs/dialogue-examples.md)：设计目标，非用户效果报告。
- [角色场景验收卡](docs/experiments/persona-scenarios.md)：用具体场景检查节奏、边界与纠偏。
- [本轮工程实验](docs/experiments/2026-10-25-polish.md)：可复现检查与尚未验证的部分。
- [历史版本](docs/releases/v0.1.3.md)：已有迭代记录。

> 人说话的方式，爱人的方式，那些停顿、拐弯、嘴硬和心软，值得被认真记住。
>
> 水仙想把“被理解”这件事，留下一个可保存、可修正、还能继续生长的开源入口。

MIT licensed. 导入层曾借鉴 MIT 项目 `npy-skill` 的实现思路；宿主、渠道工具与相关项目的权利归各自作者。
