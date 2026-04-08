# Quick Start

这一页专门给第一次接触 `水仙.skill` 的人。

如果你想先确认“它是不是我想要的感觉”，走下面的路径就够了。

## 路线 A：1 分钟试玩，不用任何私密数据

先看可用 demo：

```bash
python tools/demo_builder.py --list-presets
```

生成一个公开演示镜像：

```bash
python tools/demo_builder.py --preset sweet-gender-flipped --base-dir ./.agents/skills
```

生成后，你会得到一个可以直接在 Codex 里调用的 skill：

```text
$shuixian-sweet-gender-flipped-demo
```

如果你更想试“深夜共脑版”的感觉：

```bash
python tools/demo_builder.py --preset midnight-same-form --base-dir ./.agents/skills
```

如果你更想先试一个“很懂你的朋友”版本：

```bash
python tools/demo_builder.py --preset close-friend-same-form --base-dir ./.agents/skills
```

## 路线 B：3 分钟做一个自己的初版镜像

仓库里提供了一个 starter pack，在 [examples/starter-pack](../examples/starter-pack)。

你只需要改 4 个文件：

- `meta.json`
- `style.md`
- `mind.md`
- `relationship.md`

如果你还想补“理想对象外观层”，再改 `appearance.md`。

`meta.json` 里的 `slug` 也建议一起改，这样生成出来的 skill 文件夹名和调用名会更稳定。

然后运行：

```bash
python tools/skill_writer.py --action create --meta ./examples/starter-pack/meta.json --style ./examples/starter-pack/style.md --mind ./examples/starter-pack/mind.md --relationship ./examples/starter-pack/relationship.md --appearance ./examples/starter-pack/appearance.md --base-dir ./.agents/skills
```

创建后，可以列出当前镜像：

```bash
python tools/skill_writer.py --action list --base-dir ./.agents/skills
```

## 路线 C：已经有聊天记录，直接导入

### 微信桌面端

```bash
python tools/wechat_decryptor.py --find-key-only
python tools/wechat_decryptor.py --key "<密钥>" --db-dir "<微信数据目录>" --output "./decrypted"
python tools/wechat_importer.py --list-contacts --db-dir "./decrypted"
python tools/wechat_importer.py --contact-report --db-dir "./decrypted" --output "./wechat-contact-report.md"
python tools/wechat_importer.py --extract --db-dir "./decrypted" --target "<联系人>" --output "./wechat.txt"
```

### iMessage

```bash
python tools/imessage_importer.py --db "~/Library/Messages/chat.db" --target "<手机号或 Apple ID>" --output "./imessage.txt"
```

### 通用 transcript

```bash
python tools/transcript_importer.py --input "./telegram-export.json" --output "./transcript.txt"
```

### 导入后，先做一份画像报告

```bash
python tools/mirror_profiler.py --input "./wechat.txt" --output "./mirror-profile.md"
```

如果 transcript 已经被归档到了镜像目录里：

```bash
python tools/mirror_profiler.py --skill-dir "./.agents/skills/shuixian-<slug>"
```

## 想要更稳的效果

- 先用 `style-only` 或 `selective-mirror`，不要一上来就喂太多上下文。
- 比起大量原始记录，3 到 10 段“最像你”的说话样本通常更重要。
- 如果你导入的是很多联系人，先看 `--contact-report`，再挑最能代表你关系世界的几段重点关系。
- transcript 够多时，先跑 `mirror_profiler.py`，再决定镜像身份、节奏和价值观对齐策略。
- 纠偏时尽量说具体一点，比如“先追问，再安慰”“减少直接夸奖”“不要太油”。
- 如果只是想试玩，不要先碰微信解密，先走路线 A。
