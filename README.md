<div align="center">

# 水仙.skill

### 你说过的话，慢慢长成能回应你的另一个自己。

聊天记录、日记、随笔 → 你的说话方式 → 和自己聊聊。

**[打开体验入口 ↗](https://cyh29hao.github.io/shuixian-skill/)** · [带入我的记录](#聊天记录怎么带进来) · [让 agent 帮我开始](#让-agent-帮你开始) · [手动安装](#手动安装) · [English](README_EN.md)

已收录于 [colleague-skill Gallery](https://titanwings.github.io/colleague-skill-site/gallery/shuixian-skill/) · [EverythingSkill](https://everythingskill.net/skills/shuixian-skill)

</div>

> 你：“我本来想整理文件，结果整理出了三个新建文件夹。”
>
> 水仙：“文件还没归位，安置房先盖了三套。”

[合成语料真实试聊节选](docs/experiments/corpus-onboarding-2026-10-27.md#陌生-agent-从候选技能开始的一次上手)。它想接住的是你的说法，而不是给每句话套一句通用安慰。

<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="assets/corpus-hero-mobile-v1.png" />
    <img src="assets/corpus-hero-v1.png" alt="把自己的话说回给自己：个人语料、自己的语气、可以对话的水仙" width="760" />
  </picture>
</p>

**自己的语料是主角。** 从你选好的记录里，整理节奏、措辞和接话习惯，保存成可调用、可纠正的镜像。朋友、恋人或共思伙伴由你选；没有语料时的公开预设只是试看。

## Star History

谢谢愿意给水仙一颗星的人。下面复用 Star History 的日期折线，数据由服务更新，可能有缓存延迟。

<a href="https://www.star-history.com/#Cyh29hao/shuixian-skill&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Cyh29hao/shuixian-skill&amp;type=Date&amp;theme=dark" />
    <img src="https://api.star-history.com/svg?repos=Cyh29hao/shuixian-skill&amp;type=Date&amp;theme=light" alt="Cyh29hao/shuixian-skill 的 GitHub Star 历史折线图" width="620" />
  </picture>
</a>

[图表打不开时查看 Star History](https://www.star-history.com/#Cyh29hao/shuixian-skill&Date) · [查看当前 Star](https://github.com/Cyh29hao/shuixian-skill/stargazers)


## 让 agent 帮你开始

把下面的话发给能操作本机文件的 Codex 或 Claude Code；文件路径和“我叫谁”换成自己的即可。

```text
帮我安装 https://github.com/Cyh29hao/shuixian-skill ，在当前项目里用。
我选好的聊天记录在 D:/我的语料/，里面“青禾”是我。
从我的发言整理说话方式，做个水仙让我和自己聊天。
先只保存表达习惯，原件保留。缺什么一次问清，准备好就开始聊。
```

只知道“记录在微信里”也可以这样告诉 agent：它应先帮你判断取数路径，不让你先填一张人物设定表。已有可读导出最快；加密微信数据库仍有版本与取数限制，不能承诺所有客户端一键成功。[具体范围](references/wechat-import.md)

## 聊天记录怎么带进来

**先选手边已有的，不必把全部历史重新整理一遍。**

| 我手上有什么 | 最轻的走法 |
| --- | --- |
| 一份或一文件夹聊天导出 | 给 agent 文件/目录，它先列出说话人，你认一下自己，再继续 |
| Telegram / ChatGPT 等 JSON，或常见聊天 CSV / TSV | 用轻入口识别可读格式，预览条数和发言者；具体兼容范围见[导入指南](docs/importing.md) |
| 日记、随笔、复制出来的一段文字 | 保存为 TXT / Markdown，明确“这些都是我写的”；无需伪装成双人聊天 |
| 只有微信客户端或原始数据库 | 先走[微信说明](references/wechat-import.md)，取得可读导出后使用同一个入口 |
| 截图 | 给能看图的 agent 先转写并确认说话人，再作为文本导入；脚本不自带 OCR |

愿意手动操作，也只需从已安装的构建器运行：

```sh
python .agents/skills/create-shuixian/tools/import_chat.py "D:/我的语料"
```

Claude Code 把 `.agents` 换成 `.claude`。跟着预览选出自己，工具整理转录和画像，再给出可直接发给 agent 的下一步；已有输出不会被覆盖。它整理材料，不会靠一次统计就“学完你”。[格式、粘贴材料、批量导入与例子 →](docs/importing.md)

## 从语料到对话

<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="assets/corpus-flow-mobile-v1.png" />
    <img src="assets/corpus-flow-v1.png" alt="带来自己的语料、分清本人发言、整理表达习惯、开始与镜像对话" width="920" />
  </picture>
</p>

1. **选定材料**：聊天记录、日记、随笔或长文。多种场景比重复同一句口头禅更有用；不必把全部历史一次交出。
2. **认准本人**：你的话、对方的话、转述和复制内容分开处理。对方的口吻不会直接成为“你的个性”。
3. **整理表达**：先统计和索引，再分批读实际语句，提炼句长、节奏、措辞、玩笑和不同场景里的说法。词频报告只是线索。
4. **和自己聊**：保存镜像后试聊；哪里不像，指出具体一句。需要长期保留的纠偏写回文件并保留版本。

这是用 skill 和选定材料引导宿主模型表达，不会训练出一套新的模型权重。关系也由你选：可以先同自己聊天，朋友、共思伙伴、恋人或家人式陪伴是独立选项。

[12,000 条合成消息的实际导入与试聊 →](docs/experiments/corpus-onboarding-2026-10-27.md) 本人和另一方各 6,000 条；工具处理时间、模型试聊和未验证部分分别记录，不把合成实验当作真人相似度证明。

## 手动安装

需要 Git、Python 3.9+ 和对应 agent。基本导入、生成、更新无需额外 Python 包。从打算聊天的项目目录执行对应的一条命令：

**Codex**

```sh
git clone https://github.com/Cyh29hao/shuixian-skill .agents/skills/create-shuixian
```

然后在该项目聊天中输入：

```text
$create-shuixian
用我指定的语料创建自己的镜像。先确认哪位发言者是我，再整理说话方式。
```

**Claude Code**

```sh
git clone https://github.com/Cyh29hao/shuixian-skill .claude/skills/create-shuixian
```

然后在该项目中输入：

```text
/create-shuixian
用我指定的语料创建自己的镜像。先确认哪位发言者是我，再整理说话方式。
```

Codex 会检测 skill 变化；未出现时重开项目或重启。Claude Code 新目录可用 `/reload-skills` 刷新。已有同名目录时，`git clone` 会停止，先核对旧安装，不要删除自己的镜像来重试。

全局安装、Windows 路径、生成镜像的位置与检查步骤见[安装指南](docs/installation.md)；Claude 的调用及验证范围见[Claude Code 指南](docs/CLAUDE.md)。普通网页聊天能否读取本机文件，取决于宿主能力。

## 不对味，直接改

```text
刚才太像情感专家了。我平时会先吐槽那件具体的事，不会上来总结感受。
只改这里，其他语气保留。先重试一句。
```

想以后也保留，就请 builder 把纠偏写进刚创建的镜像，替换冲突的旧规则，并告诉你实际保存的目录、调用名和版本。**这轮改口了**和**已写回 skill**需要分别确认。[更新、重试和回滚步骤 →](docs/quickstart.md#6-保存纠偏并确认没有改坏其他地方)

## 手边还没有语料？也可以先试玩

[读几段真实接话](docs/try-it.md)，或运行公开预设；它们只演示气质，没有学过你的个性。

```sh
python .agents/skills/create-shuixian/tools/demo_builder.py --preset close-friend-same-form --base-dir .agents/skills
```

实际调用名以命令输出为准。Claude Code 把两处 `.agents` 换成 `.claude`。其他预设和少量样本的尝试见[使用指南](docs/quickstart.md)。

## 材料和保存范围

通用文本、Markdown、JSON、JSONL 是主要导入入口。微信原始数据库、iMessage 和截图各有格式、平台或宿主要求，见[渠道说明](references/import-channels.md)。

每个水仙是可读的 `SKILL.md`、语气、思路、关系和可选外观文件，更新保留版本。大量记录先在本地整理，再按选定范围供模型阅读；原文归档单独选择。`style-only` 表示只保留抽象表达习惯，不等于工具自动替你脱敏。

宿主读到的材料可能发送到其模型服务，本地文件不代表离线运行。它不会验证人格、转移意识或自动拥有你的全部记忆。是否像自己，由实际聊天来判断。[隐私与边界 →](references/privacy-and-safety.md)


## 社区收录与分享

感谢这些地方让更多人遇见水仙。这里区分目录收录和第三方分享，不把它们写成商业合作背书。

| 去哪里看看 | 与水仙的关系 |
| --- | --- |
| [colleague-skill Gallery](https://titanwings.github.io/colleague-skill-site/gallery/shuixian-skill/) | 社区 Skill 合集收录，列出作者并链接本仓库 |
| [EverythingSkill](https://everythingskill.net/skills/shuixian-skill) | Skill 目录收录；页面含较早版本介绍，安装步骤以本仓库为准 |
| [Socialistic 分享页](https://socialistic.ai/en/skill/shuixian-skill-7137db/) | 社区作者制作的第三方在线入口，[来源是 Issue #1](https://github.com/Cyh29hao/shuixian-skill/issues/1)；页面可访问，未验收登录后的模型对话 |

第三方站点独立运行，有各自的登录和数据规则。本站体验入口与第三方入口分别标注，不会自动把你的语料转给它们。

## 继续了解

- [第一次使用与验收](docs/quickstart.md)：语料、创建、纠偏与回滚。
- [真实试聊](docs/try-it.md)：实际回复与有限的结论。
- [公开对话样例](docs/dialogue-examples.md)：标明为设计示例。
- [工程实验](docs/experiments/2026-10-25-polish.md)与[历史版本](docs/releases/v0.1.3.md)。

> 那些停顿、拐弯、嘴硬和心软，值得被认真记住。

MIT licensed. 导入层曾借鉴 MIT 项目 `npy-skill` 的实现思路；宿主、渠道工具与相关项目的权利归各自作者。
