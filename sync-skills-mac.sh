#!/bin/bash
# 把 pmlophy-skills 仓库里的 skill 软链到 Mac 的各个 agent skill 目录，供本地 agent 共用。
#
# 用法：
#   bash sync-skills-mac.sh --dry-run
#   bash sync-skills-mac.sh ~/.agents/skills ~/.cursor/skills ~/.claude/skills ~/.codex/skills
#
# 只做两件事：① 为仓库里每个 skill 建软链（已存在且指向正确的跳过） ② 清掉指向仓库内已不存在 skill 的断链。
# 不删除任何真实目录；遇到同名真实目录会跳过并提示。演练模式不创建任何目录或链接。

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

DRY=0
HUBS=()
for a in "$@"; do
  if [ "$a" = "--dry-run" ]; then
    DRY=1
  else
    HUBS+=("$a")
  fi
done
if [ ${#HUBS[@]} -eq 0 ]; then
  HUBS=("$HOME/.agents/skills")
fi

echo "仓库: $REPO_ROOT"
echo "目标目录: ${HUBS[*]}"
if [ "$DRY" = "1" ]; then echo "模式: 演练（不改动）"; fi

total_created=0
total_refreshed=0
total_skipped=0
total_removed=0

for HUB in "${HUBS[@]}"; do
  echo "== 处理 $HUB"
  if [ "$DRY" = "0" ]; then mkdir -p "$HUB"; fi

  created=0
  refreshed=0
  skipped=0
  removed=0

  while IFS= read -r skill_md; do
    src="$(dirname "$skill_md")"
    name="$(basename "$src")"
    dst="$HUB/$name"
    if [ -L "$dst" ]; then
      cur="$(readlink "$dst")"
      if [ "$cur" != "$src" ] && [ "$DRY" = "0" ]; then
        rm -f "$dst"
        ln -s "$src" "$dst"
      fi
      refreshed=$((refreshed + 1))
    elif [ -e "$dst" ]; then
      echo "  跳过（同名真实目录，不覆盖）: $name"
      skipped=$((skipped + 1))
    else
      if [ "$DRY" = "0" ]; then ln -s "$src" "$dst"; fi
      created=$((created + 1))
    fi
  done < <(find "$REPO_ROOT/skills" -maxdepth 3 -name SKILL.md -type f)

  while IFS= read -r link; do
    [ -L "$link" ] || continue
    target="$(readlink "$link")"
    case "$target" in
      "$REPO_ROOT"/*)
        if [ ! -e "$link" ]; then
          if [ "$DRY" = "0" ]; then rm -f "$link"; fi
          removed=$((removed + 1))
        fi
        ;;
    esac
  done < <(find "$HUB" -maxdepth 1 -type l 2>/dev/null)

  echo "  新建链接: $created   已存在/刷新: $refreshed   跳过: $skipped   清理断链: $removed"
  total_created=$((total_created + created))
  total_refreshed=$((total_refreshed + refreshed))
  total_skipped=$((total_skipped + skipped))
  total_removed=$((total_removed + removed))
done

echo "----------------"
echo "合计：新建 $total_created / 刷新 $total_refreshed / 跳过 $total_skipped / 清理断链 $total_removed"
echo "完成。若某个 agent 不读上述目录，把对应目录加进它的 skill 搜索路径即可。"
