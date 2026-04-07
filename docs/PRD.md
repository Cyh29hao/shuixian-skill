# 水仙.skill PRD

## 1. 产品一句话

从用户自己的语言样本、聊天记录、关系偏好和最少量设定里，生成一个可以和用户谈恋爱的自我镜像伴侣 Skill。

## 2. 这一版目标

这一版的重点不是重新发明产品，而是把它往“公开可用项目”再推一步：

- 开始加入 Claude 适配
- 开始加入多个信息导入渠道
- 开始补可展示的效果示例
- 保持 README 和项目说明更像一个正在持续迭代的公开 skill 仓库

## 3. 当前能力

### Builder Skill

`create-shuixian` 负责：

- intake
- 读取材料
- 生成 preview
- 写入 skill
- 管理版本
- 导入 transcript

### Generated Skill

`shuixian-<slug>` 负责：

- 以固定恋爱镜像 persona 和用户继续对话
- 在边界内稳定输出
- 对私密范围保持一致口径

## 4. 导入渠道

当前支持：

- prompt-only
- 手动粘贴文本
- 导出聊天文本
- 微信桌面端数据库导入
- iMessage `chat.db`
- 通用文本 / JSON / JSONL transcript
- 截图 / 图片补充

产品上要强调：

- 平台专用导入是“便利层”
- transcript 归一化才是“稳定层”
- 任何复杂平台都应该有 generic transcript fallback

## 5. Claude 适配策略

这一版采取轻适配策略：

- 仓库结构可以直接 clone 到 `.claude/skills/`
- README 明确 Claude 安装方式
- 提供推荐调用名 `/shuixian`
- 保留 `SKILL.md` 主入口，不急着拆出 Claude-only 变体

后面再决定是否要补更深的 Claude 专用 prompt 结构。

## 6. 内容展示策略

既然是公开仓库，就不能只有“会跑的脚本”，还要有：

- 几个看起来就知道大概效果的示例
- 一眼能懂的安装方式
- 较克制但明确的边界
- “持续更新中”的姿态

## 7. 后续 roadmap

1. 继续补更多聊天平台适配
2. 深化 Claude 体验
3. 增加更完整的公开示例和截图
