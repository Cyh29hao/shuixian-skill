# 微信聊天记录导入

把微信里的**本人表达**用于水仙，需要先有可读记录，再整理说话方式。已经导出的文本和“直接从正在运行的微信取数”是不同步骤。

## 先看你已经有什么

| 现有材料 | 建议入口 | 当前范围 |
| --- | --- | --- |
| TXT / Markdown / JSON / JSONL 导出 | `transcript_importer.py` → `mirror_profiler.py` → builder | 主要路径；支持常见消息结构，先核对条数和本人标签 |
| 兼容旧式 schema 的明文数据库 | `wechat_importer.py` | 查找 `MicroMsg.db` 和 `MSG*.db` / `msg_*.db`，读取旧式 `Contact` / `MSG` 表及相应列 |
| 只有正在运行的微信或加密数据 | 先确认客户端版本、选定账户/时间/联系人范围和可用导出办法 | 不保证自动取数；没有完整微信 4.x 适配和实机成功证据 |

不要把“安装技能”当成“已经拿到微信记录”。有现成导出时可以快速继续；需要解密、等待用户导出或补权限时，不能承诺几分钟全部完成。

## 1. 使用已经导出的记录

以下脚本路径以仓库根目录为例；安装后使用构建器的实际路径。输出保存到选定的工作目录，不覆盖导出原件：

```sh
python tools/transcript_importer.py --input "./chosen-wechat.json" --output "./chosen-transcript.txt"
python tools/mirror_profiler.py --input "./chosen-transcript.txt" --self-name "青禾" --output "./mirror-profile.md"
```

把“青禾”替换为导出中本人准确的发言标签。多个本人别名可重复 `--self-name`。先看归一化后的几条消息及 `Identified User Messages`；为 0 时先修正归属，不能把对方的话补成自己的特征。

导出并没有统一格式。若结构不支持，保留原件，另做 UTF-8 标准消息副本；纯日记或无说话人标签的文字，要先确认单一作者。之后按[语料流程](corpus-workflow.md)分批读本人语句、创建镜像并试聊。

## 2. 使用已经准备好的旧式明文数据库

只读你选择的数据库副本，不在客户端正使用的数据库上实验。先查看指定范围的联系人，再提取一个明确对象：

```sh
python tools/wechat_importer.py --list-contacts --db-dir "./chosen-plaintext-db"
python tools/wechat_importer.py --extract --db-dir "./chosen-plaintext-db" --target "<选定联系人名称或wxid>" --output "./chosen-transcript.txt"
python tools/mirror_profiler.py --input "./chosen-transcript.txt" --self-name "我" --output "./mirror-profile.md"
```

这里的“我”对应当前适配器给自己发言写出的标签，仍应打开结果确认。若你选择了更广的联系人分析范围，可以用 `--contact-report --output "./chosen-contact-report.md"` 生成报告；不默认把整份联系人表留给镜像。

本轮只用自编的 `Contact` / `MSG` 明文 SQLite 验证过文件、表和列契约，没有在真实微信客户端验收。只有 `contact.db`、`message_0.db` 等其他布局时，当前适配器会拒绝或需要另行转换；改文件名不等于完成新版适配。

## 3. 加密微信记录：先核对方案，不直接承诺

仓库保留 `wechat_decryptor.py` 作为旧版实验代码，**不作为推荐的自动导入第一步**：

- Windows 自动取钥依赖旧进程、模块和内存布局；macOS 自动取钥没有完整实现。
- 当前 `test_key` 以一个解密分组非全零作判断，没有可靠的数据库结构或 HMAC 验证。它输出“looks valid”也不能证明密钥正确。
- 本轮环境缺少 `pycryptodome`，未执行真实取钥/解密，也没有安装依赖或读取私人数据库来补成功记录。

不要把这个判断作为继续批量解密、归档或宣告成功的依据。优先使用用户已有的导出；确需第三方工具时，核对当前版本支持、许可、权限和数据去向，由用户选择是否安装，密钥不得写进日志或发给模型。若无法取得可读记录，说明实际缺口，保留现有进度。

曾查阅的成熟方案与限制：

- [WeChatMsg 上游](https://github.com/LC044/WeChatMsg)已声明不再持续维护，不能拿项目名当作所有版本的兜底。
- [PyWxDump 的 4.0+ 支持问题](https://github.com/xaoyaoo/PyWxDump/issues/203)说明旧路线有版本断点。
- [独立 WeChatMsg-4x 分支的适配说明](https://github.com/chenanhan230-del/WeChatMsg-4x/blob/main/doc/%E5%BE%AE%E4%BF%A14.x%E9%80%82%E9%85%8D%E8%AF%B4%E6%98%8E.md)列出目录、进程、库表及压缩正文等差异；本项目只查阅其说明，没有把它安装或验证为依赖。

## 4. 从记录创建水仙

导入工具只负责整理文件，画像工具只提供统计线索。builder 还需要阅读选定的本人语句，提炼可执行的表达习惯，再保存并真实试聊。

Codex 镜像放在项目 `.agents/skills`，Claude Code 放在 `.claude/skills`。保留原文归档与只保存抽象风格是分别选择的范围；不要把聊天、联系人、数据库或密钥提交到公开仓库。宿主读取的材料可能发送到其模型服务，本地处理不代表全程离线。

[本轮合成实验与未验证部分](../docs/experiments/corpus-onboarding-2026-10-27.md) · [首次使用](../docs/quickstart.md)
