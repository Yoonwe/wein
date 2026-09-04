<#
.SYNOPSIS
AI 对话记录一键沉淀：定位数据 -> 导出 md -> 脱敏 -> 推送 GitHub（分支 + PR 自动合并）
.DESCRIPTION
用法示例：
  .\ai-backup.ps1                       # Marvis 全量沉淀（自动发现数据源）
  .\ai-backup.ps1 -AiName yuanbao       # 其它 AI（需 -DbPath 或数据源已适配）
  .\ai-backup.ps1 -AiName marvis -DbPath "D:\xxx\data.db"
  .\ai-backup.ps1 -SkipPush             # 仅导出与脱敏，不推送
.EXAMPLE
  .\ai-backup.ps1
#>
param(
    [string]$AiName = "marvis",
    [string]$DbPath = "",
    [switch]$SkipPush,
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.json"),
    [string]$WorkDir = (Join-Path $env:TEMP "ai-dialogue-backup")
)

# 不用全局 EAP=Stop（PS5.1 会把 git stderr 进度当终止错误）；关键 cmdlet 显式 -ErrorAction Stop
$api = "https://api.github.com"
$PythonCmd = "python"

function Read-Config {
    param($Path)
    if (-not (Test-Path $Path)) { throw "找不到配置文件: $Path （请先配置 config.json 的 repo/token）" }
    return (Get-Content $Path -Raw | ConvertFrom-Json)
}

function Find-MarvisDb {
    $patterns = @(
        (Join-Path $env:APPDATA "Tencent\Marvis\User\*\database\data.db"),
        (Join-Path $env:APPDATA "Tencent\Marvis\User\*\data.db")
    )
    foreach ($p in $patterns) {
        $f = Get-ChildItem $p -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($f) { return $f.FullName }
    }
    return $null
}

function Invoke-GitHub {
    param($Uri, [string]$Method = "Get", $Body = $null, $Headers)
    $params = @{ Uri = $Uri; Method = $Method; Headers = $Headers; ErrorAction = "Stop" }
    if ($Body) { $params.Body = ($Body | ConvertTo-Json -Depth 5); $params.ContentType = "application/json" }
    return Invoke-RestMethod @params
}

# ---------- 0. 配置 ----------
$cfg = Read-Config $ConfigPath
if (-not $cfg.token) { throw "config.json 缺少 token" }
$hostName = if ($cfg.host_name) { $cfg.host_name } else { $env:COMPUTERNAME }
$folder = "$AiName-$hostName"
$repoFull = $cfg.repo
$headers = @{ Authorization = "token $($cfg.token)"; "User-Agent" = "MarvisBackup"; "X-GitHub-Api-Version" = "2022-11-28" }

# ---------- 1. 定位数据源 ----------
if (-not $DbPath) {
    if ($AiName -eq "marvis") { $DbPath = Find-MarvisDb }
    if (-not $DbPath) { throw "未找到 $AiName 的数据源，请用 -DbPath 指定数据库路径" }
}
Write-Host "[1/6] 数据源: $DbPath"

# ---------- 2. 导出 + 脱敏 ----------
$outRoot = Join-Path $WorkDir "out"
Remove-Item (Join-Path $outRoot $folder) -Recurse -Force -ErrorAction SilentlyContinue
& $PythonCmd (Join-Path $PSScriptRoot "export.py") --db $DbPath --out $outRoot --name $folder
if ($LASTEXITCODE -ne 0) { throw "导出失败 (exit=$LASTEXITCODE)" }
$mdFiles = Get-ChildItem (Join-Path $outRoot $folder) -Filter *.md -ErrorAction SilentlyContinue
if (-not $mdFiles -or $mdFiles.Count -eq 0) { throw "导出结果为空" }
Write-Host "[2/6] 导出完成: $($mdFiles.Count) 个会话 -> $folder"

if ($SkipPush) {
    Write-Host "已跳过推送。导出目录: $(Join-Path $outRoot $folder)"
    exit 0
}

# ---------- 3. 克隆仓库基线 ----------
$cloneDir = Join-Path $WorkDir "repo"
if (Test-Path $cloneDir) { Remove-Item $cloneDir -Recurse -Force }
$cloneUrl = "https://github.com/$repoFull.git"  # 仓库公开时可匿名 clone；推送仍需 token URL
$env:GIT_TERMINAL_PROMPT = "0"
git clone $cloneUrl $cloneDir 2>(Join-Path $WorkDir "clone-err.log")
if ($LASTEXITCODE -ne 0) { $e = (Get-Content (Join-Path $WorkDir "clone-err.log") -ErrorAction SilentlyContinue | Select-Object -Last 3) -join " | "; throw "git clone 失败: $e" }
Write-Host "[3/6] 克隆基线完成"

# ---------- 4. 建分支提交 ----------
$stamp = Get-Date -Format "yyyyMMddHHmmss"
$branch = "backup-$AiName-$stamp"
git -C $cloneDir checkout -B $branch origin/main 2>$null
$dest = Join-Path $cloneDir $folder
Remove-Item $dest -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item "$($mdFiles[0].DirectoryName)\*.md" $dest -Force
git -C $cloneDir add $folder
git -C $cloneDir -c user.name="$($cfg.user_name)" -c user.email="$($cfg.user_email)" commit -m "$folder dialogue backup ($($mdFiles.Count) sessions)" 2>$null
if ($LASTEXITCODE -ne 0) { throw "git commit 失败（无变更或配置错误）" }
Write-Host "[4/6] 本地提交完成"

# ---------- 5. 推送 + PR + 合并 ----------
$pushUrl = "https://x-access-token:$($cfg.token)@github.com/$repoFull.git"
git -C $cloneDir push $pushUrl $branch 2>$null
Start-Sleep -Seconds 2
# push 判定改用 API 验证分支存在（避免网络中断导致误判）
try {
    Invoke-GitHub -Uri "$api/repos/$repoFull/branches/$branch" -Headers $headers | Out-Null
} catch {
    throw "推送失败：分支 $branch 未出现在远端（可能触发 GH013 安全拦截或网络问题）"
}
Write-Host "[5/6] 分支已推送: $branch"

$pr = Invoke-GitHub -Uri "$api/repos/$repoFull/pulls" -Method Post -Headers $headers -Body @{
    title = "$folder dialogue backup ($($mdFiles.Count) sessions)"; head = $branch; base = "main"; body = "由 ai-backup 一键脚本自动导入"
}
$merge = Invoke-GitHub -Uri "$api/repos/$repoFull/pulls/$($pr.number)/merge" -Method Put -Headers $headers -Body @{ merge_method = "squash" }
Write-Host "[6/6] PR #$($pr.number) 已合并: $($merge.sha)"

# ---------- 6. 收尾 ----------
try { Invoke-GitHub -Uri "$api/repos/$repoFull/git/refs/heads/$branch" -Method Delete -Headers $headers | Out-Null } catch {}
git -C $cloneDir remote set-url origin "https://github.com/$repoFull.git"
git -C $cloneDir reflog expire --expire=now --all 2>$null
git -C $cloneDir gc --prune=now 2>$null

Write-Host ""
Write-Host "=== 完成 ==="
Write-Host "仓库: https://github.com/$repoFull/tree/main/$folder"
Write-Host "新增: $($mdFiles.Count) 个会话文件"

