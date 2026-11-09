---
name: forge-prd-scaffold
description: Build or extend the Forge PRD documentation hierarchy (prd-docs/模块/单据/套件) using an idempotent, non-destructive scaffold script. Use when adding a new module or 单据 to forge-wms / forge-erp, when restructuring flat PRD files into the module/单据/suite layout, when pre-building folders for planned (二期) modules like 调拨/盘点, or when completing a "空架子" 单据 (only 主PRD) into a full suite. Mirrors the ERP prd-docs standard as the reference.
---

# Forge PRD 目录脚手架

刘龙飞的 **Forge** 作品集(GitHub: `lophyJessica/forge-erp` + `forge-wms`)用统一的
「模块 / 单据 / 套件」PRD 目录结构。这个 skill 用一个幂等脚本快速搭架或扩架,
遵循 **PM 超前一版设计** 的思路:现有单据归位,规划中的单据先搭空架子(带占位文件),避免一盘散沙。

> 📋 **做任何 Forge 操作前，先扫一眼产品架构全景图**：[references/forge-产品架构图.md](references/forge-产品架构图.md) — 包含两系统所有模块、完成度、关键设计决策，避免脑补模块或搞错期次。

## 何时用

- forge-wms / forge-erp 要加新模块或新单据,需要建对应的文件夹 + 套件占位
- 某项目 prd 文件还平铺着,要重建成 `prd-docs/模块/单据/套件` 分层
- 某个单据只有主PRD(空架子),要补齐成完整套件
- 二期模块(调拨/盘点等)开写前先把架子搭好

## 核心概念

### 权威层级(改规则前必读)
```
context/  >  templates/  >  prd-docs/
```
prd-docs 是生成物,**不是规则源**。改业务规则须回溯 context/,别只改 PRD。

### 4 种套件类型(决定一个单据文件夹里放哪几个文件)

| 类型 | 适用 | 文件套件 |
| :--- | :--- | :--- |
| **业务单据** `suite_biz` | 采购订单、波次、调拨单、报损单 | 主PRD·字段清单·业务规则规格·业务流程推演·用例数据推演·Demo(列表/**新增编辑**/详情) = 8 件 |
| **执行作业单** `suite_exec` | 采购入库单、收货/上架/拣货/复核/交运/盘点单(PDA 作业) | 同上,但 Demo 用 **执行页** 代替新增编辑页 = 8 件 |
| **查询页** `suite_query` | 即时库存查询、库存流水、库存预警 | 主PRD·字段清单·业务规则规格·业务流程推演·用例数据推演·Demo(**仅列表页**) = 6 件。**无状态机**,主PRD 状态机章节写"不适用" |
| **档案/主数据** `suite_archive` | 仓库/库区/货位/商品/供应商档案 | 主PRD·字段清单·**前端Demo版PRD** = 3 件 |

判断业务单据 vs 查询页:能否创建记录(能=单据)、有无状态字段(有=单据)、库存/应付是否变动(变=单据)。

### 一期/二期边界怎么查(两项目形态不同,面试/走查易踩)

被问「这项目二期规划是什么」时,别硬找一份「二期规划总览」——两个项目的二期是嵌进不同位置的:

- **forge-wms**:二期用「**新增模块**」式。一期 6 模块(基础数据/入库/出库/库存/盘点/PDA)已交付;二期是往里加 **调拨管理(调拨单 TR)+ 报损管理(报损单 BL)** 两个新模块,已按超前一版设计把 PRD 套件搭好。二期标识写在单据主PRD 开头 `> 本模块为二期规划`;范围/边界看该主PRD 的「功能范围(2.1 一期不做 / 2.2 二期做)」+ 结尾「局限/NIS」章。WMS 二期典型待补:ERP 调拨下发接口协议、超收处理规则(实收>调出先阻断)。\n- **forge-erp**:二期用「**功能深化**」式。8 模块一期全上;二期 = 各模块的 **Out Scope 清单**,散在两处——`context/04`(每模块逐条 In/Out Scope 分界)+ `context/07`「二、下期项目范围(Out Scope)」的汇总。要答 ERP 二期,直接扫这两个文件的 Out Scope 条目(采购决策/信用硬强控/审批流/高级仓储/复杂财务/高级分析/渠道扩展…)。\n- **⚠️ 跨项目陷阱:调拨/报损在两系统里期次相反**。WMS 里是**二期**(仓间实物调拨执行 + 在途不可销售管控,6 仓库间库存平衡);ERP 里是**一期 In Scope**(门店↔后仓的账面轻调拨,`context/04` 库存管理模块 + `context/07` 已列)。**不是笔误**——两个产品定位不同:WMS 管货(实物执行+在途),ERP 管账(账面调拨)。被问「WMS 二期才做调拨,ERP 一期怎么就有了」时,用这套「一个管货、一个管账」的口径答。

## 脚本用法(在 Mac 上,项目在 git 仓库内会自动 git mv 保留历史)

脚本见 `scripts/build-forge-prd-scaffold.sh`(把它拷到项目父目录或任意位置)。

```bash
chmod +x build-forge-prd-scaffold.sh
# 1) 先预览,绝不改动:
./build-forge-prd-scaffold.sh --wms ~/dev/forge-wms --erp ~/dev/forge-erp --dry-run
# 2) 确认无误再真跑:
./build-forge-prd-scaffold.sh --wms ~/dev/forge-wms --erp ~/dev/forge-erp
```
特性:**幂等**(已存在文件绝不覆盖,可反复跑)、**非破坏**(只新建目录/占位 + 移动现有主PRD,不删任何东西)。
只传 `--wms` 或只传 `--erp` 都行,留空则跳过该项目。

## 如何扩架(加模块 / 加单据)

编辑脚本里 `build_wms()`(或 `build_erp()`),按类型调对应函数,格式:
`suite_<类型> "<单据文件夹路径>" "<单据名>" "<参照套件说明>"`

例:二期给出库管理加一个"退货入仓单"(PDA 作业类):
```bash
suite_exec "$P/出库管理/退货入仓单" "退货入仓单" "$REF_EXEC"
```
模块级概览 PRD(如"入库管理主PRD")放模块文件夹根,用 `movein` 把现有平铺文件搬进去。

## 生成的占位文件长啥样(自解释,给后续填内容引导)
```
# 收货单主PRD
> 状态：🕳️ 待补充（脚手架占位，未开写）
> 角色：主PRD | 类型：执行作业单
> 权威层级：context/ > templates/ > 本文件
> 参照套件：ERP:采购管理/采购入库单套件（最全 8 件）
<!-- 填充指引：先读 context/ 相关章节 + templates/ 对应模板 + 参照套件，再动笔。 -->
```

## 验证步骤(改造后必做)
1. 现有主PRD 内容未丢:`head -1` 看每个模块 `主PRD.md` 首行还在
2. 旧平铺位已清空:`find prd-docs -maxdepth 1 -name '*主PRD.md'` 应无输出
3. 幂等:再跑一次,**只抓 `[file]/[move]/[gmv]` 实际动作行**(用 `grep -E '\[(file|move|gmv)'`),
   应为空。⚠️ 别统计整行 `[keep]` 计数——结尾的"图例行"含 `[file]/[move]/[keep]` 字样会污染计数,造成"假 bug"

## 坑

- **模块级主PRD ≠ 单据级主PRD**:WMS 的"入库管理主PRD"是模块概览,放模块夹根;
  ERP 的 prd-docs 里没有模块级主PRD,直接进单据文件夹。两种并存不冲突。
- **档案类文件套件更轻**(3 件,用 `_前端Demo版PRD`),别套用 8 件业务单据套件。
- **查询页无状态机**,别脑补"草稿/已审核";主PRD 状态机章节写"不适用 + 原因"。
- **⚠️ 最危险的坑:凭常识/惯性脑补单据,不先读 context 就搭文件夹。** 本会话实打实踩了一次:把「质检」当独立单据建了 `质检单/` 文件夹,但 context/03(单据链 RCV→PUT)、context/04(单据设计只列 RCV/PUT)、context/09(无 QC 前缀)三处一致规定「质检=收货单内环节」。删错、返修、连锁污染——全可避免。**加任何新模块/新单据/新文件夹前,先通读对应 context/ 相关章节 + context/03(模块清单)+ context/09(命名规则),确认该单据真实存在于地基设计里再搭。** 允许「规划中的单据先搭空架子」(如盘点/调拨在 context/03、07、08 已立项),但绝不允许搭「context 根本不认」的单据。\n- **商品/供应商档案在 WMS 里是同步自 ERP** 的,可能只做只读引用,不一定要全套 PRD——架子先搭,不需要就删。
- **遗留物脚本只提示不自动删**(如旧 `prd/` 目录、`front-prototype/front-prototype` 嵌套),
  在 git 仓库里手动确认后再处理,避免误删。
- **数据冲突时以简历为准**,不编造经历数据(见项目 AGENTS.md 核心规范)。
- **变量后紧跟中文/多字节字符,必须用 `${VAR}` 花括号**:如 `${REF_ARCH}（注…）`,裸写 `$REF_ARCH（` 在 macOS 某些 locale 下会把中文首字节吞进变量名,配合 `set -u` 报 `xxx?: unbound variable`。Linux 默认 UTF-8 不复现,只在 Mac 上炸——写脚本时凡是变量后接中文一律加花括号。

## macOS 运行坑(用户在 Mac 上跑)

- **`zsh: operation not permitted: ./脚本`**:飞书/浏览器下载的脚本被打了 quarantine 隔离标记。解法二选一:①直接 `bash 脚本.sh ...`(绕过);②`xattr -c 脚本.sh && chmod +x 脚本.sh` 后再 `./`。
- **`REF_ARCH?: unbound variable` 类报错**:见上一条"变量+中文加花括号";应急可临时 `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 bash 脚本.sh ...`,但根治靠花括号。
- dry-run 模式在建目录/写文件前就 return,**预览零副作用**,报错中断也不会留下半拉子文件,放心重跑。
- **飞书投递 `.sh` 附件常被拦**:MEDIA 发脚本时同时备一份 `脚本.sh.txt`,让用户下载后去掉 `.txt` 后缀;实在都收不到就把脚本贴成代码块。
- **git 把中文文件名显示成八进制转义**(`\345\205...`):`git config core.quotepath false` 即可显示可读中文。`git mv` 搬文件在 status 里是 `R`(rename,历史保留),`??` 是新增未跟踪,放心。

## 改造/迁移时的遗留文档核对(实战,务必做)

搭好脚手架、搬完现有文件后**别急着收工——先查有没有遗留的旧目录/重复文档**,否则会漏掉真正的正主(单体大PRD),或误删有用内容。

1. **扫遗留**:`find prd -type f`(及其它可疑旧目录)看还有什么散落文件、空模块夹。
2. **发现同名/同模块的两份文档,先对比再决定**,别直接删也别直接留:
   ```bash
   wc -l 旧文档.md 新结构/模块主PRD.md          # 比体量
   grep -nE '^#{1,3} ' 旧文档.md                # 比标题结构(谁更全)
   grep -nE '^#{1,3} ' 新结构/模块主PRD.md
   ```
   常见结局:旧的"单体大PRD"(几百行,含 Mermaid 流程图/时序图 + 各单据状态机+字段清单)反而比脚手架搬进来的精简 stub 完整得多——旧的才是正主。
3. **扶正更全的那份**(git 可回滚):`git mv -f 旧单体PRD.md "模块/模块主PRD.md"` 覆盖精简 stub(旧 stub 内容在 git 历史里可找回)。
4. **单体大PRD 里的各单据明细(状态机/字段清单)是后续拆分到单据文件夹的现成素材**,填内容时直接搬,不用重写。
5. **清理**:确认为空后删旧目录(`rmdir` 只删空目录更保险;`rm -rf` 用前先 `find -type f` 确认无文件)。嵌套夹/空夹在不同副本(如 VPS vs Mac)可能一个有一个没有,`ls -ld` 逐一确认,不存在就跳过。
6. 每一步**先 read-only 查看再动手**;破坏性操作前先 `git commit` 一个检查点,收工提醒用户 `git push`(用户容易忘同步)。

## 扫描项目全景（生成架构图/健康检查前必做）

要快速摸清一个 forge 项目的模块完整度（比如做产品架构图或走查前评估），别用裸 `search_files(pattern='*')` — 会把 `.git/objects/` 的海量哈希文件也扫出来，结果被截断。

正确姿势：
```bash
search_files(pattern='*.md', path='项目根目录', target='files')
```
`.git` 目录里没有 `.md` 文件，自然过滤掉。拿到 prd-docs/、prompt/、context/ 结构后再针对性读关键文件（AGENTS.md、context/03-04-07、模块主PRD）。

架构图生成套路：扫模块目录 → 读两系统 AGENTS.md → 读 context 关键章 → 合成结构化文档（Mermaid 图 + 表格 + 完成度进度条）。存到 `docs/产品架构图.md` 并同步为 skill reference。

## 配套工作流经验(生成→走查→返修·实战)

- **生成新单据前先读 context 确认它是不是独立单据**:质检=收货单流程内一步、差异调整=盘点单一步——若 context「单据设计/单据体系」没列它 + context/09 无单号前缀 = 不是独立单据,别脑补成独立套件(否则走查必判「脑补单据」高阻断)。这类环节应归入其宿主单据(质检字段回收货单、差异调整并入盘点单)。
- **大批量 PRD 走查**:按项目/业务链拆 2-3 路并行 subagent(toolsets=['file','terminal']),各输出「问题清单(严重度+文件+修法)+ 地基级问题 + 已正确项」,父 agent 汇总。比逐个读省上下文,且能抓跨文档一致性。
- **地基(context)修复不用 Codex**:小而精准的 context 改动我直接改 + 发文件给用户替换,绕开 Codex/反重力瓶颈;只有 PRD 内容返修才交给它们。铁律:改规则回溯 context,不在 prd-docs 层改。
- **拉用户 repo 前**:先 `git status` 查工作区是否干净,**别用 `2>/dev/null` 吞掉 pull 报错**——本地未提交改动(我之前手动改过的 context/删过的目录)会静默挡住 pull,让你看成旧提交、以为用户没推。踩过一次。用户 git workflow:main 分支干活→合并到 master(两分支并存,故意的)。
- **非脚手架目录(Codex 从零建的)**:跑完必验目录结构(件数对不对/命名规范/有没有漏文件),没走过脚手架的最容易结构飘。
- **并行跑单据的坑**:顺序链(如出库 复核→包裹→交运)若并行生成,彼此看不到对方 mock,跨单引用(来源单号)易 drift,走查时重点核。

## 填内容(架子搭好之后)——给每个占位套件出 Codex 填充指令

架子只是空文件,内容交给 Codex/反重力填。做法:**一个单据一条五段式指令**(模板见
`templates/codex-单据填充指令模板.md`,五段式本体见 `structured-ai-prompt-template` skill)。

每条指令指向"两依赖 + 参照物 + 锚点":
- **两依赖**:context/ 相关章节 + templates/ 对应模板(WMS 若无 templates,写"结构照 AGENTS.md 的 PRD 套件章")
- **参照物**:同类型已完成套件(执行类照 采购入库单8件,单据类照 采购订单)
- **内容锚点**:已有主PRD 或模块主PRD(唯一事实来源)
- **红线**:直接从项目 `AGENTS.md` 的"AI 常见错误"表抽

关键打法(本会话实战):
1. **主PRD 已有则不改,只补其余套件**(如 ERP 退货单主PRD 是 V1.0 真内容,只补 7 件)。
2. **模块主PRD 很厚**(如 WMS 入库 252 行)时,指令写"从模块主PRD 拆出本单据内容",红线注明"引用+细化,不搬走删模块PRD"。
3. **过账时点/单号前缀/字段来源** 等我方拿不准的,一律进红线让 Codex"按 context、拿不准就标注",绝不替它拍板——防幻觉最有效。
4. **跑的顺序**:有上下游依赖的先跑上游(PR→PRO、RCV→质检→PUT、WAVE→PICK)。
5. **并行封顶 2-3 条,同项目内别同时改同目录**(会抢写、安全审查也会拦冲突)。
6. 生成的指令存进项目 `prompt/` 文件夹,命名 `{单据}_Codex填充指令.md`,Mac 上随手可调。
7. 填完做跨模块走查(AGENTS.md 六维),不过关不写前端。

## 填完之后:六维走查 → 返修回环

完整打法见 `references/走查与返修回环.md`。要点:
- 走查用 **2-3 路并行 `delegate_task`**(按业务链拆),只读审查、统一输出格式,省 context 又能抓跨文档矛盾。
- 合并问题后**按修复顺序分三层**:🔴地基(context) → 🟠PRD返修 → 🟡命名/Mock。
- **地基修复不需要 Codex**:主 agent 自己 patch context、发 corrected 文件给用户替换(Codex 额度耗尽时的续命招)。典型:出库实扣是「现存-N、释放占用-N」不是「可用-N」;扣减点单一化到「包装完成」。
- **PRD 返修出 `返修-并-{链名}` 指令**交给 Codex/反重力;涉及业务设计选择的先让用户拍板。
- 验收**grep 抽检关键几处**即可,别重读全部文件。
