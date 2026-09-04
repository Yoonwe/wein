# 用hermes（产品经理人格）+opencode丢个参考的github这样的方式怎么操作

> 会话元信息
> - 时间范围：2026-08-11 17:07 ~ 2026-08-11 17:09
> - 对话轮次：3 轮

---

### [用户 · 2026-08-11 17:07:02]

用hermes（产品经理人格）+opencode 丢个参考的github这样的方式怎么操作

### [AI · 2026-08-11 17:07:09]

Hermes问的是如何用OpenCode（一个AI编程工具）配合产品经理思维，像丢GitHub参考仓库那样来操作。这是个工具使用+方法论的问题。

OpenCode是一个终端AI编程助手。用户想了解：
1. OpenCode是什么，怎么用
2. 如何"丢GitHub仓库"作为参考 —— 应该是说把GitHub仓库作为上下文/参考，让AI基于它来开发

我需要给一个实操指南：安装OpenCode，然后用它来克隆/参考GitHub仓库，基于那个仓库做开发。

让我搜索一下OpenCode的最新信息。

### [AI · 2026-08-11 17:07:15]

Let me get more specific details about how OpenCode handles GitHub repository references and the workflow of "throwing a GitHub repo as reference."

### [AI · 2026-08-11 17:07:21]

Now I have a good picture. Let me also check the References feature more closely, and the TUI for @ file references.

### [AI · 2026-08-11 17:07:44]

## OpenCode：用产品经理思维 + GitHub 仓库做参考的实操指南

### 一句话理解

OpenCode 是终端里的 AI 编程助手，核心卖点是支持**把 GitHub 仓库作为"参考源码"丢给它**，然后用自然语言（产品经理口吻）告诉它你要什么，它基于参考仓库来写代码。

---

### 第一步：安装 OpenCode（Windows）

```powershell
# 方式一：npm（推荐）
npm install -g @opencode-ai/opencode

# 方式二：直接下载 exe
# 从 https://opencode.ai 下载 Windows 安装包
```

安装后配置 API Key（选一个模型供应商）：

```powershell
opencode auth login
# 按提示选 Anthropic / OpenAI / GitHub Copilot 等，填入 Key
```

---

### 第二步：理解 References 机制（这恰好是你说的「丢 GitHub 仓库」）

OpenCode 的 **References** 功能正是为这个场景设计的。在项目根目录创建 `opencode.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "references": {
    "参考项目别名": {
      "repository": "GitHub用户名/仓库名",
      "branch": "main",
      "description": "告诉AI什么时候该参考这个仓库"
    }
  }
}
```

**支持的形式**：

| 形式 | 示例 | 说明 |
|------|------|------|
| GitHub 简写 | `"Effect-TS/effect"` | 最常用 |
| 完整 Git URL | `"git@github.com:user/repo.git"` | 私有仓库 |
| GitLab 等 | `"gitlab.com/platform/sdk"` | 其他托管平台 |
| 本地目录 | `"../design-system"` | 本地已有代码 |

配置后 OpenCode 会自动 clone 到 `~/.local/share/opencode/repos/github.com/用户名/仓库名`，每次启动时自动 fetch + reset 到指定分支。

---

### 第三步：实际操作流程（产品经理模式）

```bash
# 1. 进入你的空项目目录
cd D:\my-new-project

# 2. 创建 opencode.json，声明参考仓库
#    比如想参考 shadcn/ui 做一个组件库
```

`opencode.json` 内容：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "references": {
    "shadcn": {
      "repository": "shadcn-ui/ui",
      "branch": "main",
      "description": "参考其组件结构和样式方案来构建类似的组件库"
    }
  }
}
```

```bash
# 3. 启动 TUI
opencode
```

在 TUI 中输入提示词时用 `@` 引用：

```
参考 @shadcn 的组件架构和代码风格，帮我搭建一个电商后台的 UI 组件库。
先列出项目结构和核心组件清单，确认后我再让你逐个实现。
```

---

### 产品经理式提示词范例

关键是**描述结果，不描述实现**，把 OpenCode 当工程师用：

| 不好的说法（工程师思维） | 好的说法（PM 思维） |
|---|---|
| "用 React Hook Form + Zod 写一个登录表单" | "我需要一个登录页面，有邮箱和密码两个字段，输错要有校验提示，样式参考 @shadcn 里的表单组件" |
| "给我写一个 Express 路由，查 MongoDB" | "我需要一个用户列表接口，返回分页数据，URL 路径和返回格式参考 @参考项目 的 API 设计" |
| "用 playwright 写个测试" | "把 @参考项目 里的 e2e 测试用例结构移植过来，覆盖登录、注册、忘记密码三个场景" |

---

### 关键技巧总结

1. **References 是核心**：不靠手动 clone，OpenCode 自动管理参考仓库的拉取和更新
2. **description 字段很重要**：它决定了 AI 什么时候会自动参考该仓库——写清楚"这个仓库干什么用"
3. **`@别名` 触发**：在 TUI 里打 `@` 会弹出所有 reference 别名，选中后 AI 能直接看到仓库目录结构
4. **多仓库组合**：一个 `opencode.json` 可以配置多个 reference，比如 UI 参考一个、API 设计参考另一个
5. **非交互模式也支持**：`opencode run "参考 @shadcn 帮我做 XX"` 适合脚本化

这个概念和你说的"丢个 GitHub 仓库当参考"完全吻合。本质就是把 GitHub 仓库变成可索引的知识库，让 AI 在写代码时自动参照其架构、风格和实现模式。

### [用户 · 2026-08-11 17:08:41]

你是刻意忽略Hermes嘛

### [AI · 2026-08-11 17:08:44]

抱歉，Hermes。确实不该漏掉。

上一轮把焦点全放在 OpenCode 的技术细节上了，疏忽了。你继续问，这次注意。

### [用户 · 2026-08-11 17:08:57]

用hermes（产品经理人格）+opencode 丢个参考的github怎么做

### [AI · 2026-08-11 17:09:10]

Hermes，之前那轮确实不该漏称呼。直接说实操。

---

## OpenCode References：把 GitHub 仓库当模板丢给 AI

OpenCode 的 **References** 机制就是你要的东西——在 `opencode.json` 里声明一个 GitHub 仓库别名，AI 自动 clone 并索引，你在 TUI 里 `@别名` 就能让它参考着写代码。

### 完整操作流

**1. 安装**
```powershell
npm install -g @opencode-ai/opencode
opencode auth login    # 选 Anthropic / OpenAI，填 Key
```

**2. 在空项目目录创建配置**

```json
// D:\my-project\opencode.json
{
  "$schema": "https://opencode.ai/config.json",
  "references": {
    "ref": {
      "repository": "GitHub用户名/仓库名",
      "branch": "main",
      "description": "用自然语言写清楚这个仓库的参考价值"
    }
  }
}
```

支持 GitHub 简写、完整 Git URL、GitLab、本地路径四种形式。多仓库写多个 entry 即可。

**3. 启动，用产品经理口吻下需求**
```bash
cd D:\my-project
opencode
```

TUI 里打 `@` 弹出参考别名，选中后这样说话：

> 参考 @ref 的架构和代码风格，我要做一个 XX 系统。先给我列出项目结构和核心模块，确认后再逐个实现。

---

### PM 人格 vs 工程师人格的提示词区别

| 你说的（PM） | 不要说的（工程师） |
|---|---|
| 我需要一个用户管理后台，参考 @ref 的页面布局和数据表格样式 | 用 React + Ant Design 写个 table 组件 |
| 把 @ref 里的 API 接口设计规范移植过来，覆盖用户模块的 CRUD | 写 Express 路由，连 MongoDB |
| @ref 里的错误处理方式不错，我的项目里也用这套 | 加 try-catch 和全局 error middleware |

核心：**描述结果和约束，不描述实现手段**。目录结构、技术栈选型、代码风格——这些让 OpenCode 从 reference 仓库里自己推断。

---

有什么具体的 GitHub 仓库和项目方向想试？我可以直接帮你把 `opencode.json` 写出来。
