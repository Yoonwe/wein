# AI 对话沉淀仓库

个人 AI 助手对话记录的集中沉淀库。将各个 AI 助手（Marvis、元宝等）的历史聊天记录按统一规范导出、脱敏、归档到本仓库，形成可持续积累的个人数据资产。

## 目录结构

```
wein/
├── README.md                 # 本说明（仓库总览 + 整理规范）
├── marvis-VVVVV/             # Marvis 对话沉淀（已导入，405 个会话）
└── <AI名>-<本机名>/          # 其他 AI 沉淀（规划中）
```

目录命名规则：`<AI名>-<本机名>`（如 marvis-VVVVV、yuanbao-VVVVV）。每个 AI 一个独立目录，互不干扰。

## 文件命名规范

每个对话会话单独导出一个 Markdown 文件：

```
<开始日期>_<主要主题>(<对话轮次>).md
```

示例：
- `2026-05-23_帮我在同花顺里看人形机器人概念板块(1轮).md`
- `2026-09-04_目前社会层面对于五十岁左右男性就业者及其不友好(6轮).md`

字段说明：
- **开始日期**：会话首条消息日期，格式 `YYYY-MM-DD`
- **主要主题**：会话首条用户消息内容提炼，压缩至 30 字以内
- **对话轮次**：该会话中用户消息条数

## 文件内容格式

每个 `.md` 文件包含会话元信息与完整对话正文：

```markdown
# <主题>

> 会话元信息
> - 时间范围：2026-05-23 10:15 ~ 2026-05-23 11:02
> - 对话轮次：4 轮

---

### [用户 · 2026-05-23 10:15:12]
<用户消息原文>

### [Marvis · 2026-05-23 10:15:20]
<AI 回复原文>
```

## 整理方式（沉淀流程）

### 1. 数据定位

AI 助手本地数据通常位于用户目录下的数据文件中（Marvis 为 SQLite 数据库）：

```
%APPDATA%\Tencent\Marvis\User\<用户ID>\database\data.db
```

关键表：`conversations`（会话列表）、`messages`（消息明细）。

### 2. 导出

- 按会话聚合消息，时间字段转为 UTC+8
- 只导出用户与 AI 的可见对话（user / assistant 角色），跳过工具调用等过程消息
- 按上述命名规范生成 Markdown 文件
- 每个 AI 导出到独立目录，如 `marvis-VVVVV/`

### 3. 敏感信息脱敏（必做）

对话中常含真实凭据（API Key、App Secret、Token、JWT 等），GitHub 安全扫描（secret scanning push protection）会拦截含有效凭据的推送（报错 `GH013`）。推送前必须打码：

- 识别常见凭据模式：`github_pat_`、`ghp_`、`sk-`、`AKIA`、飞书 `App Secret` / `app_token`、JWT（`eyJ...`）、HMAC secret、Telegram Bot Token 等
- 将真实值替换为前缀 + `***REDACTED***`，如 `cPVQ***REDACTED***`
- 打码后全量扫描验证无残留

### 4. 推送（本仓库 main 分支规则）

main 分支受仓库规则保护，**禁止直接 push**（会报 `GH013`），需走分支 + PR：

```bash
git clone https://github.com/Yoonwe/wein.git
git checkout -B <导入分支名> origin/main
# 拷贝导出目录，git add + commit
git push https://x-access-token:<TOKEN>@github.com/Yoonwe/wein.git <导入分支名>
```

再通过 GitHub API 创建并合并 PR：

```
POST /repos/Yoonwe/wein/pulls   { head: <导入分支名>, base: main }
PUT  /repos/Yoonwe/wein/pulls/<PR号>/merge   { merge_method: squash }
```

### 5. 收尾

- 删除远端临时分支
- 清除本地 git 仓库 remote URL 中的 token
- `git reflog expire --expire=now --all && git gc --prune=now` 清除本地残留的含凭据对象

## 多 AI 沉淀规划

| AI 助手 | 目录 | 数据来源 | 状态 |
|---------|------|----------|------|
| Marvis | marvis-VVVVV | 本地 SQLite data.db | 已导入（405 会话） |
| 腾讯元宝 | yuanbao-<本机名> | 待定位（客户端/网页端数据导出） | 规划中 |
| 其他 AI | <AI名>-<本机名> | 按各自数据形态评估 | 规划中 |

各 AI 数据形态不同（本地库 / 导出功能 / 网页抓取），沉淀前需先定位各自数据来源并评估脱敏点。格式统一遵循本规范，便于日后检索与统计。

## 备注

- 本仓库为个人备份用途，请勿将 token、密钥明文提交
- 如导出内容包含打码凭据，属正常脱敏，不影响对话内容阅读
