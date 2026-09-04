# AI-Dialogue-Backup

AI 对话记录一键沉淀工具：将本地 AI 客户端对话记录导出为 Markdown、脱敏后自动推送 GitHub。

## 文件说明

| 文件 | 用途 |
|------|------|
| `ai-backup.ps1` | 一键脚本：定位数据源 → 导出脱敏 → clone → 分支提交 → push → PR squash 合并 |
| `export.py` | 导出引擎：读 SQLite（conversations/messages）生成 `日期_主题(轮次).md`，正则打码明文凭据 |
| `config.example.json` | 配置模板，复制为 `config.json` 后填入真实值（token 为 GitHub PAT，需 repo 权限） |

## 用法

```powershell
# 首次：复制模板并填写 repo / token / user_name / user_email
Copy-Item config.example.json config.json
notepad config.json

# Marvis 全量沉淀（自动发现数据源）
powershell -ExecutionPolicy Bypass -File ai-backup.ps1

# 仅导出不推送（调试）
powershell -ExecutionPolicy Bypass -File ai-backup.ps1 -SkipPush
```

## 约定

- 仓库目录：`<AI名>-<主机名>/`（如 `marvis-VVVVV/`），每个会话一个 md 文件
- 文件命名：`开始日期_主题(用户轮数).md`，同日同名自动追加 `-2/-3`
- 脱敏：`github_pat_` / `sk-` / `AKIA` / 飞书 App Secret 等明文凭据替换为 `***REDACTED***`
- 每次运行以当批导出为准精确同步远端目录（自动删除已下架会话）
- main 禁直推：脚本自动走新分支 + GitHub API PR squash merge
- 环境要求：git 需配置 `http.sslBackend=openssl` 并通过可用代理访问 github.com
