# pmlophy-skills Windows 同步脚本（PowerShell 主体）
# 作用：把仓库 skills/ 里每个 skill 以 Junction 形式挂到各 agent 的 skill 目录
# 特性：重建式同步；真实目录先备份不删除；自动清理指向已删 skill 的僵尸 Junction；永不触碰 ~/.hermes
# 用法：由 sync-skills-windows.bat 调用，或直接 powershell -ExecutionPolicy Bypass -File sync-skills-windows.ps1

param(
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$src  = Join-Path $repo 'skills'
if (-not (Test-Path $src)) { $src = Join-Path $repo '.agents\skills' }
if (-not (Test-Path $src)) { Write-Host "[FAIL] 找不到 skill 真源（skills/ 或 .agents\skills）" -ForegroundColor Red; exit 1 }

$home_ = $env:USERPROFILE
$hub = Join-Path $home_ '.agents\skills'

# 目标目录：中枢 + 各 agent 的用户级 skill 目录（存在才纳入）
$candidates = @(
    $hub,
    (Join-Path $home_ '.cursor\skills'),
    (Join-Path $home_ '.codex\skills'),
    (Join-Path $home_ '.claude\skills'),
    (Join-Path $home_ '.trae\skills'),
    (Join-Path $home_ '.trae-cn\skills'),
    (Join-Path $home_ '.workbuddy\skills'),
    (Join-Path $home_ '.workbuddy-ai\skills'),
    (Join-Path $home_ '.gemini\config\skills')
)
$targets = @()
foreach ($c in $candidates) {
    if ($c -eq $hub) { $targets += $c; continue }
    if (Test-Path $c) { $targets += $c }
}

# 收集 skill（递归，含子目录，识别 SKILL.md）
$skills = Get-ChildItem -Path $src -Directory -Recurse |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }

$stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
$backup = Join-Path $home_ ".agents\_backup-skills-$stamp"

Write-Host ''
Write-Host '=== pmlophy-skills Windows 同步 ==='
Write-Host "真源: $src"
Write-Host "skill 数: $($skills.Count)"
Write-Host "目标目录: $($targets.Count) 个"
foreach ($t in $targets) { Write-Host "  $($t.Replace($home_,'~'))" }
if ($DryRun) { Write-Host '模式: 演练（不改动）' -ForegroundColor Yellow }
Write-Host ''

$sumCreated = 0; $sumRefreshed = 0; $sumBacked = 0; $sumRemoved = 0

foreach ($t in $targets) {
    Write-Host "== 处理 $($t.Replace($home_,'~'))"
    if (-not $DryRun -and -not (Test-Path $t)) { New-Item -ItemType Directory -Path $t -Force | Out-Null }

    $created = 0; $refreshed = 0; $backed = 0; $removed = 0

    foreach ($s in $skills) {
        $dst = Join-Path $t $s.Name
        $isLink = $false
        $existing = $null
        if (Test-Path $dst) { $existing = Get-Item $dst -Force -ErrorAction SilentlyContinue }
        if ($existing -and ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint)) { $isLink = $true }

        if ($existing) {
            if ($isLink) {
                if (-not $DryRun) { cmd /c rmdir "$dst" 2>$null }
                $refreshed++
            } else {
                if (-not $DryRun) {
                    if (-not (Test-Path $backup)) { New-Item -ItemType Directory -Path $backup -Force | Out-Null }
                    $bkDst = Join-Path $backup $s.Name
                    if (Test-Path $bkDst) { $bkDst = "$bkDst-$stamp" }
                    Move-Item -LiteralPath $dst -Destination $bkDst
                    Write-Host "  [备份] $($s.Name) -> $bkDst"
                } else {
                    Write-Host "  [演练] 将备份并替换: $($s.Name)"
                }
                $backed++
            }
        } else {
            $created++
        }

        if (-not $DryRun) {
            New-Item -ItemType Junction -Path $dst -Target $s.FullName -ErrorAction SilentlyContinue | Out-Null
            if (-not (Test-Path $dst)) { Write-Host "  [FAIL] $($s.Name)" -ForegroundColor Red }
        }
    }

    # 清理僵尸 Junction（目标已不存在）
    if (Test-Path $t) {
        foreach ($e in Get-ChildItem -Path $t -Force -ErrorAction SilentlyContinue) {
            if ($e.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                $tgt = $e.Target
                if ($tgt -and -not (Test-Path $tgt)) {
                    if (-not $DryRun) { cmd /c rmdir "$($e.FullName)" 2>$null }
                    Write-Host "  [清理] 僵尸链接 $($e.Name)"
                    $removed++
                }
            }
        }
    }

    Write-Host "  新建 $created / 刷新 $refreshed / 备份替换 $backed / 清僵尸 $removed"
    $sumCreated += $created; $sumRefreshed += $refreshed; $sumBacked += $backed; $sumRemoved += $removed
}

Write-Host '----------------'
Write-Host "合计：新建 $sumCreated / 刷新 $sumRefreshed / 备份替换 $sumBacked / 清僵尸 $sumRemoved"
if ($sumBacked -gt 0) { Write-Host "被替换的真实目录已备份到: $backup" -ForegroundColor Yellow }
Write-Host '不涉及项目目录，不触碰 ~/.hermes（杰西卡自己的 skill）。'
Write-Host '完成。'
