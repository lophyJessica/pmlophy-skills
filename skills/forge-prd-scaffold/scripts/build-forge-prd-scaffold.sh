#!/usr/bin/env bash
# =============================================================================
# Forge PRD 目录脚手架生成器  (WMS 分层重建 + ERP 退货单套件补全)
#
# 作者思路：PM 超前一版设计——现有单据归位，规划中的单据先搭空架子，
#           每个占位文件带"待补充"标记 + 填充指引，避免一盘散沙。
#
# 特性：
#   - 幂等：可重复运行，已存在的文件绝不覆盖
#   - 非破坏：只 新建目录/新建占位文件/移动现有主PRD，不删除任何东西
#   - 支持 git mv（在 git 仓库内自动保留历史），否则退回普通 mv
#   - --dry-run 预览模式，先看清楚再真跑
#
# 用法（在 Mac 上）：
#   1) 改下面两个 ROOT 路径为你的实际项目路径，或用参数/环境变量传入
#   2) 预览：  ./build-forge-prd-scaffold.sh --dry-run
#   3) 执行：  ./build-forge-prd-scaffold.sh
#   参数形式： ./build-forge-prd-scaffold.sh --wms ~/dev/forge-wms --erp ~/dev/forge-erp
# =============================================================================
set -uo pipefail

# ---------- 配置：改成你 Mac 上的真实路径（留空则跳过该项目）----------
FORGE_WMS_ROOT="${FORGE_WMS_ROOT:-}"
FORGE_ERP_ROOT="${FORGE_ERP_ROOT:-}"
DRY_RUN="${DRY_RUN:-0}"
# --------------------------------------------------------------------

# ---------- 参数解析 ----------
while [ $# -gt 0 ]; do
  case "$1" in
    --wms) FORGE_WMS_ROOT="$2"; shift 2 ;;
    --erp) FORGE_ERP_ROOT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

C_OK=$'\033[32m'; C_ADD=$'\033[36m'; C_MV=$'\033[33m'; C_SKIP=$'\033[90m'; C_HL=$'\033[1;35m'; C_R=$'\033[0m'
say(){ printf '%s\n' "$*"; }
is_dry(){ [ "$DRY_RUN" = "1" ]; }

# mkdir -p（幂等）
mkd(){
  local d="$1"
  if [ -d "$d" ]; then return; fi
  if is_dry; then say "  ${C_ADD}[DIR ]${C_R} $d"; else mkdir -p "$d" && say "  ${C_ADD}[DIR ]${C_R} $d"; fi
}

# 生成占位 md（仅当不存在；绝不覆盖）
# 用法: stub <文件路径> <角色> <类型说明> <参照套件>
stub(){
  local f="$1" role="$2" typ="$3" ref="$4"
  local base; base="$(basename "${f%.md}")"
  if [ -e "$f" ]; then say "  ${C_SKIP}[keep]${C_R} $f"; return; fi
  if is_dry; then say "  ${C_OK}[file]${C_R} $f  (${role})"; return; fi
  cat > "$f" <<EOF
# ${base}

> 状态：🕳️ 待补充（脚手架占位，未开写）
> 角色：${role}　|　类型：${typ}
> 权威层级：context/ > templates/ > 本文件（改业务规则须回溯 context/）
> 参照套件：${ref}

<!-- 本文件由 build-forge-prd-scaffold.sh 生成。开始写作前删除本行注释。 -->
<!-- 填充指引：先读 context/ 相关章节 + templates/ 对应模板 + 上面的参照套件，再动笔。 -->
EOF
  say "  ${C_OK}[file]${C_R} $f  (${role})"
}

# 移动现有文件进目标目录（git mv 优先）
movein(){
  local src="$1" destdir="$2" root="$3"
  [ -e "$src" ] || { return; }
  local name; name="$(basename "$src")"
  local dest="$destdir/$name"
  [ -e "$dest" ] && { say "  ${C_SKIP}[keep]${C_R} 目标已存在，跳过: $dest"; return; }
  mkd "$destdir"
  if is_dry; then say "  ${C_MV}[move]${C_R} $src  ->  $dest"; return; fi
  if git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1 && \
     git -C "$root" ls-files --error-unmatch "$src" >/dev/null 2>&1; then
    git -C "$root" mv "$src" "$dest" && say "  ${C_MV}[gmv ]${C_R} $src  ->  $dest"
  else
    mv "$src" "$dest" && say "  ${C_MV}[move]${C_R} $src  ->  $dest"
  fi
}

# ---- 套件生成器（按 AGENTS.md 的 PRD 套件规范）----
# 业务单据类：主PRD + 字段清单 + 业务规则规格 + 业务流程推演 + 用例数据推演 + Demo(列表/新增编辑/详情)
suite_biz(){ local dir="$1" n="$2" ref="$3"; mkd "$dir"
  stub "$dir/${n}主PRD.md"          "主PRD"        "业务单据" "$ref"
  stub "$dir/${n}字段清单.md"        "字段清单(SSOT)" "业务单据" "$ref"
  stub "$dir/${n}_业务规则规格.md"   "业务规则规格"  "业务单据" "$ref"
  stub "$dir/${n}_业务流程推演.md"   "业务流程推演"  "业务单据" "$ref"
  stub "$dir/${n}_用例数据推演.md"   "用例数据推演"  "业务单据" "$ref"
  stub "$dir/${n}_Demo_列表页.md"    "Demo·列表页"   "业务单据" "$ref"
  stub "$dir/${n}_Demo_新增编辑页.md" "Demo·新增编辑页" "业务单据" "$ref"
  stub "$dir/${n}_Demo_详情页.md"    "Demo·详情页"   "业务单据" "$ref"
}
# 执行/作业类（PDA 作业单）：Demo 用 执行页 代替 新增编辑页
suite_exec(){ local dir="$1" n="$2" ref="$3"; mkd "$dir"
  stub "$dir/${n}主PRD.md"          "主PRD"        "执行作业单" "$ref"
  stub "$dir/${n}字段清单.md"        "字段清单(SSOT)" "执行作业单" "$ref"
  stub "$dir/${n}_业务规则规格.md"   "业务规则规格"  "执行作业单" "$ref"
  stub "$dir/${n}_业务流程推演.md"   "业务流程推演"  "执行作业单" "$ref"
  stub "$dir/${n}_用例数据推演.md"   "用例数据推演"  "执行作业单" "$ref"
  stub "$dir/${n}_Demo_列表页.md"    "Demo·列表页"   "执行作业单" "$ref"
  stub "$dir/${n}_Demo_执行页.md"    "Demo·执行页"   "执行作业单" "$ref"
  stub "$dir/${n}_Demo_详情页.md"    "Demo·详情页"   "执行作业单" "$ref"
}
# 查询页类：无状态机、无新增编辑，通常只列表
suite_query(){ local dir="$1" n="$2" ref="$3"; mkd "$dir"
  stub "$dir/${n}主PRD.md"          "主PRD"        "查询页" "$ref"
  stub "$dir/${n}字段清单.md"        "字段清单(SSOT)" "查询页" "$ref"
  stub "$dir/${n}_业务规则规格.md"   "业务规则规格"  "查询页" "$ref"
  stub "$dir/${n}_业务流程推演.md"   "业务流程推演"  "查询页" "$ref"
  stub "$dir/${n}_用例数据推演.md"   "用例数据推演"  "查询页" "$ref"
  stub "$dir/${n}_Demo_列表页.md"    "Demo·列表页"   "查询页" "$ref"
}
# 档案/主数据类：主PRD + 字段清单 + 前端Demo版PRD
suite_archive(){ local dir="$1" n="$2" ref="$3"; mkd "$dir"
  stub "$dir/${n}主PRD.md"          "主PRD"        "档案主数据" "$ref"
  stub "$dir/${n}字段清单.md"        "字段清单(SSOT)" "档案主数据" "$ref"
  stub "$dir/${n}_前端Demo版PRD.md"  "前端Demo版PRD"  "档案主数据" "$ref"
}

# =============================================================================
# 一、Forge-WMS：把平铺 prd-docs 重建为「模块/单据/套件」分层
# =============================================================================
build_wms(){
  local ROOT="$1"; local P="$ROOT/prd-docs"
  say ""
  say "${C_HL}==================== Forge-WMS 分层脚手架 ====================${C_R}"
  say "项目根: $ROOT"
  [ -d "$ROOT" ] || { say "  ⚠️  路径不存在，跳过 WMS。"; return; }
  mkd "$P"

  local REF_ARCH="ERP:基础资料/仓库管理/仓库档案套件"
  local REF_BIZ="ERP:采购管理/采购订单套件"
  local REF_EXEC="ERP:采购管理/采购入库单套件（最全 8 件）"
  local REF_QRY="ERP:库存管理/即时库存查询套件（查询页 6 件）"

  # ---- 1. 基础数据管理（多为同步/档案类）----
  say "${C_HL}-- 模块：基础数据管理 --${C_R}"
  suite_archive "$P/基础数据管理/仓库档案"   "仓库档案"   "$REF_ARCH"
  suite_archive "$P/基础数据管理/库区管理"   "库区"       "$REF_ARCH"
  suite_archive "$P/基础数据管理/货位管理"   "货位"       "$REF_ARCH"
  suite_archive "$P/基础数据管理/商品档案"   "商品档案"   "${REF_ARCH}（注：同步自 ERP，可能只做只读引用）"
  suite_archive "$P/基础数据管理/供应商档案" "供应商档案" "${REF_ARCH}（注：同步自 ERP）"

  # ---- 2. 入库管理（收货 RCV → 质检 → 上架 PUT）----
  say "${C_HL}-- 模块：入库管理 --${C_R}"
  mkd "$P/入库管理"
  movein "$P/入库管理主PRD.md" "$P/入库管理" "$ROOT"   # 现有模块概览 PRD 归位
  suite_exec "$P/入库管理/收货单" "收货单" "$REF_EXEC"
  suite_exec "$P/入库管理/质检单" "质检单" "$REF_EXEC"
  suite_exec "$P/入库管理/上架单" "上架单" "$REF_EXEC"

  # ---- 3. 出库管理（波次 WAVE → 拣货 PICK → 复核 CHECK → 包裹 PKG → 交运 DSH）----
  say "${C_HL}-- 模块：出库管理 --${C_R}"
  mkd "$P/出库管理"
  movein "$P/出库管理主PRD.md" "$P/出库管理" "$ROOT"
  suite_biz  "$P/出库管理/波次"   "波次"   "$REF_BIZ"
  suite_exec "$P/出库管理/拣货单" "拣货单" "$REF_EXEC"
  suite_exec "$P/出库管理/复核单" "复核单" "$REF_EXEC"
  suite_exec "$P/出库管理/包裹"   "包裹"   "$REF_EXEC"
  suite_exec "$P/出库管理/交运单" "交运单" "$REF_EXEC"

  # ---- 4. 库存管理（查询/流水/预警，多为查询页）----
  say "${C_HL}-- 模块：库存管理 --${C_R}"
  mkd "$P/库存管理"
  movein "$P/库存管理主PRD.md" "$P/库存管理" "$ROOT"
  suite_query "$P/库存管理/库存查询" "库存查询" "$REF_QRY"
  suite_query "$P/库存管理/库存流水" "库存流水" "$REF_QRY"
  suite_query "$P/库存管理/库存预警" "库存预警" "$REF_QRY"

  # ---- 5. 盘点管理（盘点单 CK → 差异调整）规划中 ----
  say "${C_HL}-- 模块：盘点管理（规划中，先搭架）--${C_R}"
  suite_exec "$P/盘点管理/盘点单"     "盘点单"     "$REF_EXEC"
  suite_biz  "$P/盘点管理/差异调整单" "差异调整单" "$REF_BIZ"

  # ---- 6. 调拨管理（调拨单）规划中（context/08 已定义）----
  say "${C_HL}-- 模块：调拨管理（规划中，先搭架）--${C_R}"
  suite_biz "$P/调拨管理/调拨单" "调拨单" "$REF_BIZ"

  # ---- 遗留清理：只提示，不自动删（在你的 git 仓库里手动决定）----
  say "${C_HL}-- 遗留物检查（不自动处理，仅提示）--${C_R}"
  [ -d "$ROOT/prd" ] && say "  ${C_MV}⚠️  发现旧目录 $ROOT/prd（含 PRD-01-入库管理.md + 空模块夹）→ 建议归并入 prd-docs 后删除，或移到 _archive/"
  [ -d "$ROOT/front-prototype/front-prototype" ] && say "  ${C_MV}⚠️  发现嵌套 front-prototype/front-prototype → 疑似误操作，手动确认后处理"
}

# =============================================================================
# 二、Forge-ERP：把两个空架子退货单补成完整套件（保留现有主PRD）
# =============================================================================
build_erp(){
  local ROOT="$1"; local P="$ROOT/prd-docs/采购管理"
  say ""
  say "${C_HL}==================== Forge-ERP 退货单套件补全 ====================${C_R}"
  say "项目根: $ROOT"
  [ -d "$ROOT" ] || { say "  ⚠️  路径不存在，跳过 ERP。"; return; }

  # 采购退货单：单据类（对采购订单，但补全 规则/流程/用例）
  say "${C_HL}-- 采购退货单（补全套件，保留现有主PRD）--${C_R}"
  suite_biz "$P/采购退货单" "采购退货单" "ERP:采购管理/采购订单 + 采购入库单"

  # 采购退货出库单：执行类（对采购入库单）
  say "${C_HL}-- 采购退货出库单（补全套件，保留现有主PRD）--${C_R}"
  suite_exec "$P/采购退货出库单" "采购退货出库单" "ERP:采购管理/采购入库单（执行类 8 件）"
}

# =============================================================================
main(){
  say "${C_HL}Forge PRD 脚手架$( is_dry && echo '（DRY-RUN 预览，不改动任何文件）' )${C_R}"
  [ -n "$FORGE_WMS_ROOT" ] && build_wms "$FORGE_WMS_ROOT"
  [ -n "$FORGE_ERP_ROOT" ] && build_erp "$FORGE_ERP_ROOT"
  if [ -z "$FORGE_WMS_ROOT" ] && [ -z "$FORGE_ERP_ROOT" ]; then
    say "⚠️  未指定项目路径。用 --wms <路径> / --erp <路径>，或编辑脚本顶部的 ROOT 变量。"
    exit 1
  fi
  say ""
  say "${C_OK}✅ 完成。$( is_dry && echo '（这是预览，去掉 --dry-run 才真正执行）' )${C_R}"
  say "   图例：[DIR]新建目录  [file]新建占位  [move/gmv]移动现有  [keep]已存在跳过"
}
main
