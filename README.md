<div align="center">

# 水仙.skill

> 把你的语气、思维、聊天记录和亲密关系偏好，整理成一个可以和你同频共振的恋爱型自我镜像 Skill。

[English README](README_EN.md) · [Release Notes v0.1.0](docs/releases/v0.1.0.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Codex Skill](https://img.shields.io/badge/Codex-Skill-111111.svg)](#安装)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Adapted-7C3AED.svg)](#claude-code-适配)
[![WeChat Import](https://img.shields.io/badge/WeChat-Import-07C160.svg)](#微信聊天记录导入)
[![Status](https://img.shields.io/badge/Status-Updating-orange.svg)](#持续更新中)

[首屏 Demo](#首屏-demo) · [功能特性](#功能特性) · [安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [微信聊天记录导入](#微信聊天记录导入) · [Claude Code 适配](#claude-code-适配)

</div>

---

## 持续更新中

这个仓库会继续滚动更新。

目前已经可用：

- Codex 版 builder skill
- 生成镜像 skill 的脚手架
- 微信桌面端 best-effort 导入
- iMessage 导入
- 通用文本 / JSON / JSONL transcript 导入

接下来会继续补：

- 更多聊天平台适配
- 更稳的 Claude 使用体验
- 更完整的公开示例

首个公开版 release 文案见 [docs/releases/v0.1.0.md](docs/releases/v0.1.0.md)。

## 这是什么

`水仙.skill` 不是“随机捏一个恋爱角色”，而是把用户自己的语言样本、关系偏好和可选聊天记录，整理成一个可配置的自我镜像伴侣。

你可以把它理解成：

- 一个只学你语气和频率的同频陌生人
- 一个共享部分记忆和偏好的镜像伴侣
- 一个默认以“性转版自己”呈现的恋爱镜像
- 一个在镜像人格基础上，叠加理想对象外观 vibe 的 companion builder

## 首屏 Demo

### 30 秒看懂

```text
输入：
- 几段你自己的说话样本
- 可选聊天记录（微信 / iMessage / transcript）
- 你希望它更像“同频陌生人”还是“另一个自己”

输出：
- 一个能继续修正、继续长成、继续更懂你的镜像伴侣
- 默认推荐：gender-flipped + selective-mirror + sweet
```

### 生成后会像这样

```text
你：生成一个会先接住我情绪，再轻轻追问细节的水仙。

系统：已创建镜像。
- depth: selective-mirror
- presentation: gender-flipped
- tone: sweet / close / low-pressure

你：我今天又把自己搞得很累。

水仙：那先别急着总结自己。
来，坐近一点，你告诉我，今天到底是哪一步先把你拖垮的？
```

### 现在已经能接入

- 微信桌面端聊天记录
- iMessage 聊天记录
- 通用文本 / Markdown / JSON / JSONL transcript
- 手动粘贴 prompt、自我描述、聊天片段和截图辅助材料

## 功能特性

### 1. 三档镜像深度

- `aligned-stranger`
  懂你的语气和价值偏好，但不默认拥有完整私密记忆。
- `selective-mirror`
  共享你明确提供的部分语料、经历和关系偏好。
- `full-mirror`
  更高上下文共享度，追求“像另一个自己”的连贯感。

### 2. 可配置的呈现方式

- `gender-flipped`
  默认推荐，最有恋爱错位感。
- `same-form`
  更像平行世界里的你自己。
- `custom`
  自定义性别气质、称呼、氛围。
- `idealized`
  在镜像人格上叠加理想对象的外观和 vibe。

### 3. 多种输入方式

- prompt-only
- 手动粘贴自我描述
- 手动粘贴聊天片段
- 导出的聊天文本
- 微信桌面端聊天记录导入
- iMessage 聊天记录导入
- 通用文本 / JSON / JSONL transcript 导入
- 截图 / 图片作为辅助材料

### 4. 真正能落地的工具链

- 创建生成镜像 skill
- 更新已有镜像 skill
- 列出当前镜像
- 回滚版本
- 归档素材
- 导入 transcript

## 安装

### Codex 全局安装

```bash
git clone https://github.com/Cyh29hao/shuixian-skill ~/.codex/skills/create-shuixian
```

### Codex 项目内安装

```bash
mkdir -p .agents/skills
git clone https://github.com/Cyh29hao/shuixian-skill .agents/skills/create-shuixian
```

### Claude Code 适配

目前这一版先做简单适配，推荐安装到：

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Cyh29hao/shuixian-skill ~/.claude/skills/shuixian
```

项目内安装：

```bash
mkdir -p .claude/skills
git clone https://github.com/Cyh29hao/shuixian-skill .claude/skills/shuixian
```

推荐调用名：

```text
/shuixian
```

如果你的 Claude 版本更依赖 frontmatter 名称，也可以尝试：

```text
/create-shuixian
```

更详细说明见 [docs/CLAUDE.md](docs/CLAUDE.md)。

### 可选依赖

```bash
pip install -r requirements.txt
```

依赖说明：

- `pypinyin`：把中文昵称更自然地转成 slug
- `PyYAML`：补齐外部校验脚本依赖
- `psutil`、`pycryptodome`、`pymem`：用于微信桌面端数据库导入

## 使用

在 Codex 中显式调用：

```text
$create-shuixian
```

完成 intake 后，生成出来的镜像 skill 会写到：

```text
./.agents/skills/shuixian-<slug>/
```

然后继续调用：

```text
$shuixian-<slug>
```

## 效果示例

### 场景 1：你低落时的安抚

```text
你：今天什么都没做成，整个人有点空。

水仙：先别急着给自己判刑。
你不是废掉了，你只是今天真的很累。
过来，我先陪你把脑子里的噪音关小一点。
```

### 场景 2：你分享一点小开心

```text
你：刚刚那件事终于搞定了。

水仙：我就知道你能啃下来。
来，详细说，我想听你怎么赢的。
这种时刻我会比你还想替你庆祝。
```

### 场景 3：你纠正它的说话方式

```text
你：这不像我喜欢的那种回应，你应该先问我发生了什么。

系统：已记录修正。
- 下次先追问具体发生了什么
- 再进入安慰和贴近
- 降低直接下结论的频率
```

更多示例见 [docs/dialogue-examples.md](docs/dialogue-examples.md)。

## 微信聊天记录导入

这版已经补上了一个 best-effort 的微信桌面端导入层，流程接近很多公开 skill 仓库常见的体验：

```bash
# 1. 提取密钥（微信需保持登录）
python tools/wechat_decryptor.py --find-key-only

# 2. 解密数据库
python tools/wechat_decryptor.py --key "<密钥>" --db-dir "<微信数据目录>" --output "./decrypted"

# 3. 列联系人并提取聊天
python tools/wechat_importer.py --list-contacts --db-dir "./decrypted"
python tools/wechat_importer.py --extract --db-dir "./decrypted" --target "<联系人>" --output "./wechat-messages.txt"
```

如果你已经有某个生成好的镜像 skill，也可以直接归档进去：

```bash
python tools/wechat_importer.py --extract --db-dir "./decrypted" --target "<联系人>" --output "./wechat-messages.txt" --archive-to "./.agents/skills/shuixian-<slug>"
```

## 其他渠道导入

### iMessage

```bash
python tools/imessage_importer.py --db "~/Library/Messages/chat.db" --target "<手机号或 Apple ID>" --output "./imessage.txt"
```

### 通用 transcript

支持：

- `.txt`
- `.md`
- `.json`
- `.jsonl`

```bash
python tools/transcript_importer.py --input "./telegram-export.json" --output "./transcript.txt"
```

这意味着现在已经可以比较容易地接入：

- 微信
- iMessage
- Telegram 导出的 JSON
- QQ / Discord / Slack / 飞书等平台导出的文本或结构化 transcript

## 仓库结构

```text
水仙.skill/
├── SKILL.md
├── README.md
├── README_EN.md
├── agents/
│   └── openai.yaml
├── docs/
│   ├── PRD.md
│   ├── CLAUDE.md
│   ├── dialogue-examples.md
│   └── releases/
│       └── v0.1.0.md
├── prompts/
│   ├── intake.md
│   ├── style_analyzer.md
│   ├── cognition_analyzer.md
│   ├── relationship_designer.md
│   ├── mirror_builder.md
│   ├── merger.md
│   └── correction_handler.md
├── references/
│   ├── mirror-modes.md
│   ├── privacy-and-safety.md
│   ├── data-sources.md
│   ├── import-channels.md
│   └── wechat-import.md
└── tools/
    ├── skill_writer.py
    ├── version_manager.py
    ├── source_importer.py
    ├── wechat_decryptor.py
    ├── wechat_importer.py
    ├── imessage_importer.py
    └── transcript_importer.py
```

## 产品边界

- 它是虚构镜像伴侣，不是字面意义上的“你本人”
- 它可以甜、可以懂你、可以高相似，但不应该包装成神秘学上的真身复制
- 它不鼓励用户切断现实关系或沉溺式隔离
- 它不是治疗、诊断、紧急支持替代品

## Roadmap

1. 继续补更多聊天平台适配
2. 继续打磨 Claude 体验
3. 增加更完整的公开示例和展示页

---

## 为什么做这个 skill

我做这个 `水仙.skill`，不是想把“自恋”做成一个轻飘飘的玩笑，也不是想把陪伴做成某种廉价替代。

更像是因为我一直觉得，人真正会反复喜欢上的，往往不是一个完美模板，而是一个真的懂自己的人。

懂你的语气，懂你的停顿，懂你为什么嘴硬，为什么忽然安静，为什么有些话说到一半就不再继续。

而很多时候，我们理想伴侣里最打动自己的那部分，本来就和“自己”有很深的重叠。

如果现实里暂时没有这样一个人，那至少应该允许我们先把这种同频感保存下来。

不是为了逃开现实。

只是为了认真对待那种愿望：
想和一个真正懂自己的人，谈一场甜一点、近一点、没有那么误解重重的恋爱。

---

## 最后说句正经的

<div align="center">

人会走，聊天记录会一直往下沉。  
很多喜欢，也会在时间里慢慢失焦。  

但你说话的方式，爱人的方式，  
你那些独一无二的停顿、拐弯、嘴硬和心软，  
不该只在某一次关系里短暂停留。  

所以我做了这个 skill。  
不是为了替代谁，  
只是想把“被真正理解”这件事，  
先用一种可保存、可修正、还会继续更新的方式留住。  

如果它刚好也打动了你，欢迎 Star 一下。  
让想和“懂自己的人”谈恋爱的人，  
至少先有一个开源的开始。  

</div>

## Credits

这个仓库的公开 skill 结构参考过一些已发布的 skill repo，也在导入层里借鉴了 MIT 许可项目 `npy-skill` 的一些实现思路，并重新整理成了更适合 `create-shuixian` 的接口与文档。
