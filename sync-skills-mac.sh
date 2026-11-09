#!/bin/bash
# 把 pmlophy-skills 仓库里的 skill 软链到 Mac 的中枢目录，供各本地 agent 共用。
# 用法：bash sync-skills-mac.sh [中枢目录] [--dry-run]
# 默认中枢：$HOME/.agents/skills
# 只做两件事：① 为仓库里每个 skill 建软链 ② 把指向已不存在 skill 的断链清掉。
# 不会删除任何真实目录，遇到同名真实目录会跳过并提示。

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
HUB="${1:-$HOME/.agents/skills}"
DRY=0
for a in "$@"; do [ "$a" = "--dry-run" ] && DRY=1; done
[ "${HUB:0:1}" = "-" ] && HUB="$HOME/.agents/skills"

echo "仓库: $REPO_ROOT"
echo "中枢: $HUB"
[ "$DRY" = "1" ] && echo "模式: 演练（不改动）"
mkdir -p "$HUB"

created=0; refreshed=0; skipped=0; removed=0

# 1) 建链 / 刷新链
while IFS= read -r skill_md; do
  src="$(dirname "$skill_md")"
  name="$(basename "$src")"
  dst="$HUB/$name"
  if [ -L "$dst" ]; then
    cur="$(readlink "$dst")"
    if [ "$cur" = "$src" ]; then
      refreshed=$((refreshed+1)); continue
    fi
    [ "$DRY" = "0" ] && rm -f "$dst"
    [ "$DRY" = "0" ] && ln -s "$src" "$dst"
    refreshed=$((refreshed+1))
  elif [ -e "$dst" ]; then
    echo "跳过（同名真实目录，不覆盖）: $name"
    skipped=$((skipped+1))
  else
    [ "$DRY" = "0" ] && ln -s "$src" "$dst"
    created=$((created+1))
  fi
done < <(find "$REPO_ROOT/skills" -maxdepth 3 -name SKILL.md -type f)

# 2) 清理指向仓库内已不存在 skill 的断链
while IFS= read -r link; do
  [ -L "$link" ] || continue
  target="$(readlink "$link")"
  case "$target" in
    "$REPO_ROOT"/*) [ -e "$link" ] || { [ "$DRY" = "0" ] && rm -f "$link"; removed=$((removed+1)); } ;;
  esac
done < <(find "$HUB" -maxdepth 1 -type l)

echo "----"
echo "新建链接: $created"
echo "已存在/刷新: $refreshed"
echo "跳过(同名真实目录): $skipped"
echo "清理断链: $removed"
echo "完成。若你的 agent 不读 $HUB，请把该目录加进对应 agent 的 skill 搜索路径。"
