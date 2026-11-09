# A2A 大重构执行与验证闭环（PRD/mock 规模化返修）

当任务是"对一个跨机器 A2A 项目（用户 ⇢ Hermes ⇢ Codex/反重力）做规模化返修/规范化"时（几十文件、上百处改动，如字段命名统一、mock 数据重定基、跨单据引用链对齐），按本闭环走。经 Forge WMS 全项目返修验证。

## 1. 拓扑与分工（本用户的刻意设计）

```
用户(决策) → Hermes/VPS(审查+出五段曲指令) → Codex/Mac(只改文件) → 反重力/Mac(负责 push GitHub) → Hermes/VPS(git pull 验证)
```

- **VPS 侧默认 pull-only**（无 gh CLI / 无 token / 无 SSH key，remote 走 HTTPS）。这是用户刻意的分工：改动在 Mac 生成、由**反重力统一 push**，Hermes 只负责拉下来验。**不要假设 VPS 能 push；不要在聊天里向用户索要 PAT**（有泄漏顾虑）。若用户哪天想让 VPS 直推，那是一次性配凭据的事，不是墙——但别主动推进。
- Mac 与 VPS 是同一 GitHub 仓库的两份 checkout，靠 git 同步。Hermes 在 VPS 改了东西却推不上去时，**不要留本地提交制造分叉**：`git reset --hard origin/main` 回滚（内容可重来），把改动改走 Mac→反重力 那条路。

## 2. 安全拉取铁律（用户明令："别犯傻，先检查，再 pull"）

绝不 `git pull` 盲拉。固定动作：
```bash
git fetch origin main
git merge-base --is-ancestor HEAD origin/main   # FF 判定：HEAD 是 origin 祖先=干净快进；否则已分叉，停
git log  HEAD..origin/main --oneline            # 远程多了哪些提交
git diff --stat      HEAD origin/main           # 改了哪些文件/规模
git diff --name-only HEAD origin/main | grep -v '<本次应改的目录>'   # 红线：越界文件
git merge --ff-only origin/main                 # ff-only：非快进直接拒绝，绝不产生糊涂合并
```
- ⚠️ **中文文件名 grep 陷阱**：`git diff --name-only` 会把非 ASCII 路径**八进制转义并用双引号包裹**，行尾变成 `.md"`（带引号），所以 `grep '\.md$'` / `grep '入库管理'` 会**误报"越界"**。别信 grep 结论，看 raw 清单人工核对模块归属。
- 落地后逐项验证（见 §7）。

## 3. 打样先行（Pilot-first）

大批量套约定前，**先拿 1 个中等模块打样**，深验产出，再推广其余。打样专抓"约定本身的漏洞"。
- 实战收获：入库打样时发现 Agent 把**枚举值也 camelCase 了**（`pendingReceive`），而全项目约定是**枚举值 UPPER_SNAKE**（`PENDING_RECEIVE`，对齐代码 `ENABLED/DRAFT/COMPLETED`）。打样一抓，省了后面 6 个模块同样返工，并借机把规范写死。

## 4. 立规范再套用（Standard-doc-first）

当返修跨几十文件、且经影响面盘点发现**多数字段在代码里查不到对应**（本次 400 字段里 69% 无代码对应），那它就**不是"对齐代码"，而是"给项目定一套命名规范"**。
- 先写一份治宪文档 `context/NN-命名规范.md`（camelCase 字段 / UPPER_SNAKE 枚举 / 单号=语义前缀+No / 商品=product 系 / 数量保留业务粒度 / 时间 createdAt 等），设为 SSOT。
- 再逐模块下"严格按 context/NN 套用"的指令。规则驱动、DRY、跨模块一致，且 Agent 出错点收敛到"是否读懂规范"。

## 5. 侵入式/系统性改动 → 先出"影响面报告"

产品重定基、跨单据引用链对齐这类会牵动全项目 mock 的改动，**先下只读的"影响面报告"指令**（零改动）：列全量引用清单(文件+行) + 建议映射表 + 风险点，人工审批映射后**再另下执行指令**。杜绝 Agent 几十文件盲改、你审不过来。报告指令再大也安全（不动文件），可放心并行跑。

## 6. 并行执行规则

- **不同模块 = 不同目录 = 无文件冲突 = 可并行多 chat**（封顶按你审查带宽，本用户由 Hermes 验则可放宽到 5）。
- **并行 chat 禁止各自 commit/push**：多个 Agent 同时对一个仓库跑 git 会抢 `.git/index` 锁、提交打架。指令里写死一条红线：`本次只改文件，不执行任何 git 操作(不 commit、不 push)`；全部跑完后由用户**统一提交一次**（本用户：Codex 只改、反重力统一 push）。
- **同一批文件的两种改动必须串行**：如"字段命名(C1)"与"商品重定基(C2)"都会碰库存查询，别并发；不同目录才并行。

## 7. 每批验证清单（Hermes 侧）

pull 落地后按**模块目录**逐项核（不看 commit 边界，一个 commit 装多模块也照样按目录验）：
- 残留旧模式计数=0（如 `grep -rEo '\b[a-z]+_[a-z_]+\b' prd-docs/<模块>/ | wc -l` 应为 0）
- 枚举值全 UPPER_SNAKE、字段编码全 camelCase（二者不可混）
- 单号=语义+No、跨单引用=source+语义+No
- 数量字段保留业务粒度（没被塌成 Demo 简化字段）
- 红线：未碰前端代码/context/其它模块/字段清单结构

## 8. 判断题一律锚 SSOT，不拍脑袋

映射/标准有疑义时，锚定仓库内既有 SSOT，先查证再提议：
- 命名标准样板：已 camelCase 的 `库区字段清单`/`商品档案字段清单`。
- 商品事实源：`商品档案` + 前端 seed 的 `SKU001~00N` 口径（本次三套乱 SKU 收敛到它）。
- 具体属性裁决：如"回形针带批次"冲突，用 `商品档案` 的 `batchManaged` 布尔值裁定（谁=true 谁才可带批次）。
