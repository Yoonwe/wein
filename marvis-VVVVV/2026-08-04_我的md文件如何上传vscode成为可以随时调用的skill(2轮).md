# 我的md文件如何上传vscode成为可以随时调用的skill

- 会话 ID：`conv_19fcad4a4eb_c9f36fa79c04`
- 状态：completed
- 开始时间：2026-08-04 11:32:42
- 结束时间：2026-08-04 11:34:31
- 对话轮次：2

---

### [用户 · 2026-08-04 11:32:42]

我的md文件如何上传vscode成为可以随时调用的skill

### [Marvis · 2026-08-04 11:32:49]

老板，这个问题涉及两个层面：把 md 文件变成可复用的 skill，以及在 VS Code 里随时调用。我先确认一下你指的是哪种场景，避免给你错的方向。

先说结论框架，再按你的选择细化：

**两种常见理解**

| 场景 | 含义 | 落地方式 |
|------|------|----------|
| A. 把 md 当"提示词/指令库" | 在 VS Code 里随时调出这份 md 的内容作为 AI 对话上下文 | 用 VS Code 的 Copilot Custom Instructions，或装一个 Markdown 速调插件 |
| B. 把 md 变成真正的"Skill/扩展" | 像插件一样被命令触发、自动加载 | 写成 VS Code Extension 或 Claude Code / Cursor 的 skill 目录 |

为了给你最贴合的步骤，需要你确认一点：

你用的是 **VS Code + GitHub Copilot**，还是 **VS Code + Claude Code / Cursor** 这类带 Agent 能力的工具？另外这份 md 是"操作指南/流程文档"还是"代码片段合集"？

告诉我这两点，我直接给你可执行的配置步骤和文件模板。

### [用户 · 2026-08-04 11:34:21]

Copilot

### [Marvis · 2026-08-04 11:34:31]

老板，明白了，你用的是 **VS Code + GitHub Copilot**。下面分两种用法，按需取用。

## 用法一：把 md 设为 Copilot 的"常驻指令"（最省事，推荐）

适合让 Copilot 每次对话都参考这份 md 的规范/流程。

**项目级（只对本项目生效）**
1. 在项目根目录新建 `.github/copilot-instructions.md`
2. 把你那份 md 的内容复制进去（或让 Copilot 自动读取，见下）
3. 在 VS Code `设置` 里搜索 `github.copilot.chat.codeGeneration.useInstructionFiles`，勾选启用

**全局级（所有项目生效）**
- 打开设置 → `GitHub Copilot` → `Chat` → 找到 `Instructions` 输入框，直接粘贴你的规范要点；或指向一个固定 md 路径。

> 注意：Copilot 的 instruction file 目前主要自动读取 `.github/copilot-instructions.md`，全局自定义路径支持有限。最稳的做法是项目内放这份文件。

## 用法二：随时"调出" md 内容当上下文（按需引用）

不想常驻，只想写代码时随手把这份 md 喂给 Copilot：

| 方式 | 操作 |
|------|------|
| 拖拽引用 | 在 Copilot Chat 输入框把 md 文件从资源管理器拖进去，自动作为附件上下文 |
| `#` 提及 | 输入框打 `#` 选文件（部分版本支持 `#file` 引用） |
| 工作区索引 | 装 **Cline** 或 **Continue** 插件，可把整个 md 目录纳入语义检索，对话时自动召回 |

## 用法三：做成可命令触发的"真 Skill"

Copilot 原生没有"自定义 skill"机制，但可以用 **Task / 代码片段 + 指令文件** 模拟：

1. 把 md 内容拆成若干"任务提示词"
2. 用 VS Code **User Snippets**（`文件 → 首选项 → 配置用户代码片段`）为每段存一个 snippet，前缀如 `skill-规范A`
3. 写代码时输入前缀 → 展开成完整提示词 → 发给 Copilot Chat

---

**我的建议**：如果只是让 Copilot 遵守你的规范，用法一最干净；如果想"随时调用不同模块"，用法三的 snippet 方案最灵活。

需要我帮你做两件事之一吗：
- 把你的 md 内容改写成适配 `copilot-instructions.md` 的格式（直接可用）
- 按模块拆成 VS Code snippet 模板（`.code-snippets` 文件，导入即用）

把 md 路径发我，或贴内容，我直接产出文件。
