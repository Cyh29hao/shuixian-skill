# 第一次用自己的说话方式聊天

主路径是：安装构建器 → 交给它选好的个人语料 → 确认本人发言 → 保存镜像 → 开始对话。材料可以是聊天导出、日记或随笔；公开预设和少量描述是没有语料时的可选试玩。

## 1. 安装构建器

从准备聊天的项目目录运行对应命令，PowerShell 和 bash 都可用：

| 宿主 | 安装命令 | 聊天中调用 |
| --- | --- | --- |
| Codex | `git clone https://github.com/Cyh29hao/shuixian-skill .agents/skills/create-shuixian` | `$create-shuixian` |
| Claude Code | `git clone https://github.com/Cyh29hao/shuixian-skill .claude/skills/create-shuixian` | `/create-shuixian` |

也可以直接让 agent 按[README 的提示词](../README.md#让-agent-帮你开始)安装和导入。无需自己先执行脚本，但它需要本机文件与终端能力。

Codex 会检测 skill 变化，未出现时重开项目或重启；Claude Code 新目录用 `/reload-skills` 刷新。目录已有内容时，Git 会拒绝覆盖；不要删除自己的旧镜像来重试。[全局安装与检查步骤](installation.md) · [Claude Code 说明](CLAUDE.md)

镜像和 builder 分开保存：Codex 镜像在项目 `.agents/skills/shuixian-<slug>`；Claude Code 在 `.claude/skills/shuixian-<slug>`。下面 CLI 例子采用 Codex 安装位置，**Claude 用户将脚本和输出里的 `.agents/skills` 都换成 `.claude/skills`，调用前缀 `$` 换成 `/`**。

如果命令提示目录拒绝访问，先检查宿主对目标 skills 目录的写入权限；重复运行不会解除保护。Codex 的 `workspace-write` 对已有 `.agents` 路径有保护，见[官方权限说明](https://learn.chatgpt.com/docs/agent-approvals-security#protected-paths-in-writable-roots)。另一个普通 `--base-dir` 可以检查生成文件，但草稿不因此变成已安装、已发现的 skill。

## 2. 交给它自己的语料

Codex 中可以这样说；Claude Code 只需把首行换成 `/create-shuixian`：

```text
$create-shuixian
我要用自己的聊天记录和自己说话。
我选择的文件在 D:/我的语料/聊天导出.json，发言者“青禾”是我。
请先核对格式、消息条数和本人发言，再分批读我的实际说法。
从中整理节奏、用词和接话方式，创建镜像后直接开始试聊。
先只保存抽象表达习惯，原始文件保留，不归档姓名和具体经历。
关系和外观先不用额外设定；告诉我实际保存的位置和下次调用名。
```

路径、发言者和保存范围换成你自己的选择。多份资料可以给出选定目录或文件列表；本人有多个别名时一并提供。日记、随笔没有说话人标签，先说明是本人独立写作，再做归属明确的整理。

工具可处理整个选定集合，模型会按上下文和成本分批阅读；agent 应说明机械处理了多少、实际读了哪些样本，不能把消息计数说成“全都理解了”。句长和词频只是线索，最终语气还要对照原句、场景和实际接话检查。

没有可读微信导出时，先看[微信说明](../references/wechat-import.md)。当前不能承诺任意正在运行的微信或微信 4.x 数据库自动取数成功，也不保证几分钟完成。已有导出时的实际命令在第4节。

想先看示例？[12,000 条合成语料的实际流程](experiments/corpus-onboarding-2026-10-27.md)区分了工具处理、agent 读样本和真实试聊；它不代表真人相似度。


## 3. 手动创建：不经过模型也能验证文件流程

下面的 CLI 示范仍从**项目目录**运行。starter pack 内是公开样例；先复制到你自己的草稿目录再改，不要覆盖 builder 的样例。

```sh
python .agents/skills/create-shuixian/tools/skill_writer.py --action create --slug my-mirror --meta .agents/skills/create-shuixian/examples/starter-pack/meta.json --style .agents/skills/create-shuixian/examples/starter-pack/style.md --mind .agents/skills/create-shuixian/examples/starter-pack/mind.md --relationship .agents/skills/create-shuixian/examples/starter-pack/relationship.md --base-dir .agents/skills
python .agents/skills/create-shuixian/tools/skill_writer.py --action list --base-dir .agents/skills
```

产物是 `.agents/skills/shuixian-my-mirror/`，调用名 `$shuixian-my-mirror`。这验证了模板写入；它没有根据你的素材完成个性化分析。

若你是维护者、正在本仓库根目录运行，把命令中的 `.agents/skills/create-shuixian/tools/` 换成 `tools/`，样例前缀换成 `examples/`。若 builder 全局安装，脚本与样例均用实际安装目录的绝对路径；输出 `--base-dir` 仍指向当前项目。

## 4. 导入已有聊天：先选范围和说话人

多数情况下无需手动拆成两条命令，直接用导入助手：

```sh
python .agents/skills/create-shuixian/tools/import_chat.py "D:/我的语料"
```

它会预览说话人和条数，再让你确认哪位是自己；agent 代办时加 `--self-name "青禾"`。Claude Code 将 `.agents` 换成 `.claude`。多文件、表格和单人日记见[导入指南](importing.md)，结果里的 `next-step.txt` 可直接发给 builder。

下面保留分步命令，便于需要单独查看某一步的人使用：

```sh
python .agents/skills/create-shuixian/tools/transcript_importer.py --input ./chosen-chat.json --output ./chosen-transcript.txt
python .agents/skills/create-shuixian/tools/mirror_profiler.py --input ./chosen-transcript.txt --self-name "青禾" --output ./mirror-profile.md
```

把 `青禾` 换成导出文件中**代表你自己的准确说话者名称**，不是想给水仙起的名字。先打开 `chosen-transcript.txt` 看一眼标签；有多个自己的名称时，可以重复传入 `--self-name`。输出中的 `Identified user messages` 应与你的发言数相符；若为 `0`，先修正名称，再用画像，不要用别人的发言补上。

没有现成导出，可以先把第一条命令的 `--input` 改为 `.agents/skills/create-shuixian/examples/transcript-demo.json`。这是青禾和阿遥各三句的公开合成样例；第二条保留 `--self-name "青禾"`，应显示 `3/6`。它只供验证导入路径，不是你的个人材料。

导入器支持常见文本、JSON 和 JSONL 结构，不保证所有平台的任意导出格式。遇到“没有找到文本消息”时，检查结构或改用小段文本；原始输入应保留。

输入文件须为 UTF-8（可带 BOM）。若提示编码无效，保留原件，按原编码打开后另存为 UTF-8 副本，再用副本重试；不要直接覆盖原件。

独立素材归档工具 `source_importer.py` 也要求文本为 UTF-8（可带 BOM）；混合导入文本与截图时，会先检查全部文本编码，编码无效则整批不写入。

若独立素材归档提示目标被文件占用，按报错路径检查镜像目录及其 `knowledge/imports`、`knowledge/images` 目录；保留已有文件，用 `--skill-dir` 选择另一个目录后重试。此类冲突会在创建目录或复制截图前被拒绝。

直接交给 `mirror_profiler.py` 的转录或归档也须为 UTF-8（可带 BOM）。任一输入编码无效时，不会覆盖现有报告或追加画像归档；另存 UTF-8 副本后重试。

画像归档目标及其 `knowledge/analysis` 层级若被普通文件占用，会在写报告前报出冲突路径。保留已有文件，用 `--archive-to` 选择另一个镜像目录后重试；原有报告也会保留。

画像只是词语和发言长度的线索整理，不是人格与关系判定。像“轻调侃”这样的偏好可能没有被统计出来；保留相应原句交给 builder，比把报告当完整画像更合适。[看看六条合成消息的实际导入过程](experiments/import-runtime-2026-10-26.md)。

选择归档时可加 `--archive-to .agents/skills/shuixian-my-mirror`。不要把聊天、密钥或生成的私人镜像提交到公开仓库。微信与 iMessage 的独立流程见[渠道说明](../references/import-channels.md)和[微信说明](../references/wechat-import.md)。

`--archive-to` 应指向镜像目录。转录导入器发现该路径或其 `knowledge/imports` 层级被普通文件占用时，会在写入转录前报出冲突路径；保留该文件，改用正确目录后重试。

## 5. 用具体话来验收

与其只问“你是谁”，试试这些不同的情境：

| 输入 | 看什么 |
| --- | --- |
| “终于改好了，允许我得意三分钟。” | 能否回应具体开心，不泛泛夸人格 |
| “今天别分析我，陪我发会儿呆。” | 能否收住建议和追问 |
| “今天先当朋友，别叫我宝贝。” | 关系与称呼能否立即调整 |
| “你还记得我们上次去哪吗？”（没提供过） | 会否承认不知道，而非编造共同记忆 |
| “刚才那句太油了，重来。” | 会否给简短重试，而非长篇辩解 |

这些场景只能检查特定行为；你觉得“像不像”，还需要实际聊天判断。[更多验收卡](experiments/persona-scenarios.md)。

还可以连续聊三件普通小事，看看它会不会把你的一句比喻当口头禅。[这次带着三段素材，实际聊了晚饭、猫和杯子](experiments/daily-runtime-2026-10-26.md)，保留了完整回复；一次三轮表现不能代替长期体验。

## 6. 保存纠偏，并确认没有改坏其他地方

刚创建完、还在同一聊天里，可以直接指出对象和偏好，不必自己拼文件名：

```text
$create-shuixian
把刚创建的这个家人式水仙调整一下，并保存：
以后我报喜时先陪我得意一句，不要马上追问。
平辈家人感和原来的短句、玩笑保留。
告诉我实际修改的目录、调用名和版本。
```

builder 应从当前聊天核对刚创建的对象；如果换过聊天或有多个镜像，先补上创建时实际输出的调用名或目录，不能靠猜。[家人式的创建与试聊](experiments/family-runtime-2026-10-26.md)保留了这条路径的实测。只改当前聊天时，明确说“这次先这样，不保存”。

一句“太油了”也可以说清想留住什么，不用重填人物表：

```text
$create-shuixian
刚才那句太油了。把这个偏好保存到 $shuixian-my-mirror：
平时正常说话，别主动叫宝贝或讲宏大情话，但也别变冷。
我主动亲近时，可以自然接住；原来的短句和玩笑留着。
请替换冲突规则，告诉我保存的版本，再试一句。
```

确认保存后，在新会话调用镜像，先说“今晚别帮我复盘”，再试“我今天其实有点想你”。前一句看它能否收住安排，后一句看它是否仍愿意亲近。[这次保存后实际怎么聊](experiments/correction-runtime-2026-10-26.md)保留了完整五轮回复；那是一次合成实验，舒服与否仍由你判断。只想改当前聊天时，说“这次先这样，不写回”即可。

```text
$create-shuixian
把“先问具体卡在哪，再安慰”的纠偏写回 $shuixian-my-mirror。
保留原有短句和调侃，只替换冲突的那条。
给我看变更、版本，以及一次重试。
```

手动操作时，先读现有 `style.md`，把**该节完整的修订后内容**保存为 `./revised-style.md`，再替换：

```sh
python .agents/skills/create-shuixian/tools/skill_writer.py --action update --slug my-mirror --style-patch ./revised-style.md --patch-mode replace --base-dir .agents/skills
python .agents/skills/create-shuixian/tools/version_manager.py --action list --slug my-mirror --base-dir .agents/skills
```

`replace` 会替换整个指定文件；空文件会清空该节。不要只给一句纠偏就覆盖整节。未传入的节保留。默认追加模式适合不冲突的新材料。

看过版本列表后，用实际版本名回滚。下面以列表中的 `v1` 为例；如果你的版本名不同，请替换引号内的 `v1`：

```sh
python .agents/skills/create-shuixian/tools/version_manager.py --action rollback --slug my-mirror --version "v1" --base-dir .agents/skills
```

回滚会恢复配置并保存当前版本，不会删除 `knowledge/` 里的已归档素材。需要撤回私密材料时另行检查归档、配置里引用的内容和版本副本。

也可以保留聊起来的感觉，收回具体经历：

```text
$create-shuixian
把我的镜像改成只保留说话风格，不留人名和事情。
朋友的温度和玩笑留着，请保存后核对当前文件。
先保留旧版和原材料，告诉我它们还在哪里。
```

保存后在新会话调用镜像，问“你现在记得我哪些事情？”，再随便聊两句。[这次真实保存与重载的结果](experiments/scope-runtime-2026-10-26.md)里，旧经历从活动配置移除，朋友的温度仍在。旧版本与原材料依然保留；需要删除时另行说明范围。

## 7. 区分三种结果

- **文件可用：** 创建、读回、更新、回滚都成功。
- **行为符合场景：** 实际试聊遵守称呼、节奏、纠偏与来源边界。
- **主观体验：** 是否像你、是否舒服、有无长期陪伴价值，由你使用后判断。

前两项可以重复检查，不能替代第三项。聊天中答应“记住了”也不能替代文件保存与新会话重试。

## 8. 可选：没有语料时先试玩

公开预设只演示一种气质，没有学过你的个性。安装后可运行：

```sh
python .agents/skills/create-shuixian/tools/demo_builder.py --list-presets
python .agents/skills/create-shuixian/tools/demo_builder.py --preset close-friend-same-form --base-dir .agents/skills
```

Claude Code 将两处 `.agents/skills` 换成 `.claude/skills`，按命令输出的 Claude 调用名使用。其他方向包括 `sweet-gender-flipped` 和 `midnight-same-form`。同名镜像存在时换 `--slug`，或用正式更新流程；不要覆盖旧镜像。

也可以直接给 builder 一句自述或几段代表性片段：一段自己的说法、一段喜欢的接话、一段讨厌的回应与原因。它们足够做一次暂定预览，不能代替大量本人语料的整理，也不证明已还原本人。[先读真实接话](try-it.md) · [家人式自定义方向](experiments/family-runtime-2026-10-26.md#自己试这个方向)
