# Quick Start

这一页给第一次接触 `水仙.skill` 的人。

如果你只想先试感觉，可以直接玩 demo。
如果你想把它做成“根据聊天记录长出来的世界上另一个自己”，建议按下面这条经典流程走。

## 经典流程

1. 先试玩 demo，确认你喜欢这种方向。
2. 再上传最像你的聊天材料，不用一上来导全量。
3. 让 Codex 先给一份“当前水仙拟合度自评”。
4. 正式生成你的水仙。
5. 和它聊 5 到 10 句，感受它是不是已经开始像你。
6. 用明确纠偏把它再往你喜欢的版本推近一点。

---

## 路线 A：1 分钟试玩，不用任何私密数据

先看可用 demo：

```bash
python tools/demo_builder.py --list-presets
```

生成一个公开 demo：

```bash
python tools/demo_builder.py --preset sweet-gender-flipped --base-dir ./.agents/skills
```

然后在 Codex 里直接调用：

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

重要提醒：

- demo 只能帮你判断气质方向，不会真的像“聊天记录里蒸出来的另一个你”。
- 如果你想要更强的熟悉感、私密感、甚至那种聊几句就有点发酸的感觉，聊天材料几乎是必要条件。

---

## 路线 B：先喂最小但高价值的材料

别急着导全部。

最推荐先给这些：

- 3 到 10 段“最像你”的聊天片段
- 几段你被真正接住、真正被理解、或者最不喜欢别人怎么回你的聊天
- 能体现你如何对待亲密关系、朋友、家人、暧昧对象、前任的样本
- 你明确认可过的观点、表达、判断方式

如果你已经有导出的 transcript，也可以直接导：

```bash
python tools/transcript_importer.py --input "./transcript.json" --output "./transcript.txt"
```

如果你已经有微信桌面端数据：

```bash
python tools/wechat_decryptor.py --find-key-only
python tools/wechat_decryptor.py --key "<密钥>" --db-dir "<微信数据目录>" --output "./decrypted"
python tools/wechat_importer.py --list-contacts --db-dir "./decrypted"
python tools/wechat_importer.py --contact-report --db-dir "./decrypted" --output "./wechat-contact-report.md"
python tools/wechat_importer.py --extract --db-dir "./decrypted" --target "<联系人>" --output "./wechat.txt"
```

如果 transcript 已经有一定量，先做画像报告：

```bash
python tools/mirror_profiler.py --input "./wechat.txt" --output "./mirror-profile.md"
```

这个报告最适合用来先看：

- 哪些关系最值得借
- 哪些关系情绪很重，但未必适合拿来做模板
- 哪些价值观和雷区已经很清楚
- 现在的材料还会在哪些地方让水仙显得泛

---

## 路线 C：让 Codex 先自评，再生成

在 Codex 里调用：

```text
$create-shuixian
```

然后你可以直接这样说：

```text
我想做一个根据聊天记录长出来的水仙。
先别急着创建，先根据我给你的材料做一份当前拟合度自评：
- 现在有多像我
- 哪些地方已经高置信度
- 哪些地方还会显得泛
- 下一步最值得补什么
```

如果你更想明确一点，也可以这样说：

```text
这版我不要太像泛泛而谈的情感专家。
请优先学习我喜欢的人、喜欢的自己会怎么说话做事，
然后告诉我：现在水仙创造到什么程度了，还缺什么。
```

你应该期待它先给你：

- Voice fit
- Worldview fit
- Relationship fit
- Memory richness
- Genericness risk
- Best next upload

如果这一步它还说不清楚，那就说明材料还不够，不要急着创建。

---

## 路线 D：正式生成自己的水仙

### 方法 1：直接在 Codex 对话里让 builder 帮你生成

```text
$create-shuixian
```

然后说：

```text
现在开始创建。
我想要一个更像聊天记录里长出来的“另一个我”，不是一个温柔模板。
请优先贴着我的高置信度价值观、关系处理方式、说话节奏和喜欢被理解的方式来写。
```

### 方法 2：改 starter pack 后手动创建

仓库里已经附带 starter pack，在 [examples/starter-pack](../examples/starter-pack)。

你至少改这 4 个文件：

- `meta.json`
- `style.md`
- `mind.md`
- `relationship.md`

如果你还想补“理想对象外观层”，再改 `appearance.md`。

然后运行：

```bash
python tools/skill_writer.py --action create --meta ./examples/starter-pack/meta.json --style ./examples/starter-pack/style.md --mind ./examples/starter-pack/mind.md --relationship ./examples/starter-pack/relationship.md --appearance ./examples/starter-pack/appearance.md --base-dir ./.agents/skills
```

创建后可以列出当前镜像：

```bash
python tools/skill_writer.py --action list --base-dir ./.agents/skills
```

之后你会得到一个可以直接调用的技能：

```text
$shuixian-<slug>
```

---

## 路线 E：和它聊 5 到 10 句，再微调

第一次验收时，不要只问一句“你是谁”。

更推荐直接丢这些真实一点的句子进去：

- “今天我把这两天做的东西又改好了，我现在有点想得意一下。”
- “别安慰我，你先懂我。”
- “我现在不是没话说，是不想从第一句背景开始交代。”
- “今天先别走恋爱路线，先当我最懂我的朋友。”
- “你刚刚那句有点太像 AI 了，收一点。”

如果你感觉它不够像，你可以直接纠偏：

```text
这句不对，太像情感专家了。
你应该先接住我的潜台词，不要每次都分析我。
以后少一点总结，多一点像你已经认识我很久。
```

如果你想让它更贴近某一类人：

```text
往“我喜欢的人会怎么回我”那边再靠一点。
更像我喜欢的自己，不要像一个标准答案型的温柔 AI。
```

如果你想让 builder 把这轮对话正式写回 skill：

```text
$create-shuixian
请根据我和 $shuixian-<slug> 这段对话，给它打一轮补丁：
- 哪些话太泛
- 哪些地方已经对味
- 以后应该怎么改
```

---

## 想要更强“像我感”的几个经验

- 比起海量原始记录，最有价值的是“最像你”的几段。
- 比起普通闲聊，更有价值的是带情绪、带偏心、带关系处理方式的对话。
- 比起让它学会关心你，更重要的是让它学会“怎么理解你才像你想要的那种人”。
- 如果它已经开始懂你的停顿、潜台词、偏心、雷区、爱和不爱，那才是真正开始像了。
- 想要想哭的熟悉感，通常不是靠说很多，而是靠一句话里刚好记住了你。
