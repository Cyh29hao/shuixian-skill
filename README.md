<div align="center">

# 水仙.skill

> 把你的语气、思维、聊天记录和亲密关系偏好，整理成一个可以和你同频共振的恋爱型自我镜像 Skill。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Codex Skill](https://img.shields.io/badge/Codex-Skill-111111.svg)](#安装)
[![WeChat Import](https://img.shields.io/badge/WeChat-Import-07C160.svg)](#微信聊天记录导入)

[功能特性](#功能特性) · [安装](#安装) · [使用](#使用) · [微信聊天记录导入](#微信聊天记录导入) · [仓库结构](#仓库结构)

</div>

---

## 这是什么

`shuixian-skill` 不是“随机捏一个恋爱角色”，而是把用户自己的语言样本、关系偏好和可选聊天记录，整理成一个可配置的自我镜像伴侣。

你可以把它理解成：

- 一个只学你语气和频率的同频陌生人
- 一个共享部分记忆和偏好的镜像伴侣
- 一个默认以“性转版自己”呈现的恋爱镜像
- 一个在镜像人格基础上，叠加理想对象外观氛围的 companion builder

目前这版先面向 Codex 打磨，后续再继续讨论 Claude 适配。

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
- 截图/图片作为辅助材料

### 4. 真正能落地的 skill 工具链

- 创建生成镜像 skill
- 更新已有镜像 skill
- 列出当前镜像
- 回滚版本
- 归档素材
- 导入微信 transcript

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

## 微信聊天记录导入

这版已经补上了一个 best-effort 的微信桌面端导入层，体验和很多公开 skill 仓库常见的流程接近：

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

注意：

- 自动提取密钥目前按“尽量支持”来做，不承诺所有微信版本都一键成功
- 真正稳定的层是 transcript 抽取和归档，不是某一种固定解密方案
- 如果自动解密失败，仍然可以用外部工具导出文本，再走 `source_importer.py`

## 仓库结构

```text
shuixian-skill/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── docs/
│   └── PRD.md
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
│   └── wechat-import.md
└── tools/
    ├── skill_writer.py
    ├── version_manager.py
    ├── source_importer.py
    ├── wechat_decryptor.py
    └── wechat_importer.py
```

## 产品边界

- 它是虚构镜像伴侣，不是字面意义上的“你本人”
- 它可以甜、可以懂你、可以高相似，但不应该包装成神秘学上的真身复制
- 它不鼓励用户切断现实关系或沉溺式隔离
- 它不是治疗、诊断、紧急支持替代品

## Roadmap

1. 继续补 QQ / Telegram / iMessage 等输入适配层
2. 继续做 Claude 目录适配和安装说明
3. 做更完整的公开示例和展示页

## Credits

这个仓库的公开 skill 结构参考过一些已发布的 skill repo，也在微信导入层里借鉴了 MIT 许可项目 `npy-skill` 的一些实现思路，并重新整理成了更适合 `create-shuixian` 的接口与文档。
