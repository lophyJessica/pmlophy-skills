#!/bin/bash
# 把 pmlophy-skills 仓库里的 skill 软链到 Mac 上所有本地 agent 的 skill 目录。
#
# 用法：
#   bash sync-skills-mac.sh                    # 链到默认中枢 ~/.agents/skills
#   bash sync-skills-mac.sh --discover         # 只探查：列出本机所有可能的 agent skill 目录（不改动）
#   bash sync-skills-mac.sh --auto --dry-run   # 对探查到的全部目录做演练
#   bash sync-skills-mac.sh --auto             # 对探查到的全部 agent 目录真跑（不碰 ~/.hermes）
#   bash sync-skills-mac.sh ~/.agents/skills ~/.qoder/skills   # 只链到指定目录
#
# 只做两件事：① 为仓库里每个 skill 建软链（已存在且指向正确的跳过） ② 清掉指向仓库内已不存在 skill 的断链。
# 不删除任何真实目录；遇到同名真实目录会跳过并提示。演练模式不创建任何目录或链接。

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

DRY=0
DISC=0
AUTO=0
REPLACE=0
HUBS=()
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --discover) DISC=1 ;;
    --auto) AUTO=1 ;;
    --replace-real) REPLACE=1 ;;
    *) HUBS+=("$a") ;;
  esac
done

# 已知的 agent skill 目录（按 2026-11-09 在用户 Mac 上实测到的位置整理）
KNOWN=(
  "$HOME/.agents/skills"
  "$HOME/.cursor/skills"
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.trae/skills"
  "$HOME/.trae-cn/skills"
  "$HOME/.workbuddy/skills"
  "$HOME/.workbuddy-ai/skills"
  "$HOME/.qoder/skills"
  "$HOME/.gemini/antigravity/skills"
  "$HOME/.gemini/config/skills"
  "$HOME/.zcode/skills"
)

discover() {
  # 已知位置 + 主目录内 4 层以内、名字为 skills 且位于隐藏配置目录下的路径
  {
    for d in "${KNOWN[@]}"; do [ -d "$d" ] && echo "$d"; done
    find "$HOME" -maxdepth 4 -type d -name skills \
      -not -path "*/node_modules/*" -not -path "*/.git/*" \
      -not -path "*/Library/Caches/*" 2>/dev/null \
      | while IFS= read -r p; do
          rel="${p#$HOME/}"
          case "$rel" in
            .*|*/.*) ;;                 # 只保留隐藏配置目录下的
            *) continue ;;
          esac
          # 排除应用内置资源、项目内自带、应用私有缓存目录
          case "$rel" in
            .hermes/*|.hermes|*/builtin/*|*/builtin|*/design_libraries/*|*/connectors/*|*/security-resources/*|*/memories/*|*/tests/*|*/.hermes/*|*/项目*|*/个人文件/*|*/Documents/*|*/Desktop/*|*/Downloads/*|*/Library/*) continue ;;
          esac
          echo "$p"
        done
  } | sort -u
}

if [ "$DISC" = "1" ]; then
  echo "本机探查到的 agent skill 目录："
  found=0
  while IFS= read -r d; do
    printf "  %-52s 现有子项 %s 个\n" "${d/#$HOME/~}" "$(ls -A "$d" 2>/dev/null | wc -l | tr -d ' ')"
    found=$((found+1))
  done < <(discover)
  echo "合计 $found 个。要全部同步就加 --auto。"
  exit 0
fi

if [ "$AUTO" = "1" ]; then
  while IFS= read -r d; do HUBS+=("$d"); done < <(discover)
fi

if [ ${#HUBS[@]} -eq 0 ]; then
  HUBS=("$HOME/.agents/skills")
fi

# 去重
declare -a UNIQ=()
for h in "${HUBS[@]}"; do
  dup=0
  for u in "${UNIQ[@]:-}"; do [ "$u" = "$h" ] && dup=1 && break; done
  [ "$dup" = "0" ] && UNIQ+=("$h")
done
HUBS=("${UNIQ[@]}")

echo "仓库: $REPO_ROOT"
echo "目标目录（${#HUBS[@]} 个）:"
for h in "${HUBS[@]}"; do echo "  ${h/#$HOME/~}"; done
if [ "$DRY" = "1" ]; then echo "模式: 演练（不改动）"; fi

total_created=0
total_refreshed=0
total_skipped=0
total_removed=0
total_replaced=0
_BACKUP_DIR="$HOME/.agents/_backup-skills-$(date +%Y%m%d-%H%M%S)"

for HUB in "${HUBS[@]}"; do
  echo "== 处理 ${HUB/#$HOME/~}"
  if [ "$DRY" = "0" ]; then mkdir -p "$HUB"; fi

  created=0
  refreshed=0
  skipped=0
  removed=0
  replaced=0

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
      if [ "$REPLACE" = "1" ]; then
        bk="$_BACKUP_DIR/$name"
        if [ "$DRY" = "0" ]; then
          mkdir -p "$_BACKUP_DIR"
          mv "$dst" "$bk"
          ln -s "$src" "$dst"
          echo "  已备份并替换为软链: $name -> 备份在 $_BACKUP_DIR"
        else
          echo "  [演练] 将备份并替换为软链: $name"
        fi
        replaced=$((replaced + 1))
      else
        echo "  跳过（同名真实目录，不覆盖，可加 --replace-real）: $name"
        skipped=$((skipped + 1))
      fi
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

  echo "  新建 $created / 刷新 $refreshed / 替换真实目录 $replaced / 跳过 $skipped / 清断链 $removed"
  total_created=$((total_created + created))
  total_refreshed=$((total_refreshed + refreshed))
  total_skipped=$((total_skipped + skipped))
  total_removed=$((total_removed + removed))
  total_replaced=$((total_replaced + replaced))
done

echo "----------------"
echo "合计：新建 $total_created / 刷新 $total_refreshed / 替换真实目录 $total_replaced / 跳过 $total_skipped / 清理断链 $total_removed"
if [ "$total_replaced" -gt 0 ]; then echo "被替换的旧目录已备份到: $_BACKUP_DIR"; fi
echo "完成。若某个 agent 不读上述目录，把对应目录加进它的 skill 搜索路径即可。"
