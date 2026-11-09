# A2A 执行—验证闭环（Hermes ⇢ Codex/反重力 ⇢ git 同步验证）

Hermes 出五段式指令，用户在本机(Mac)用 Codex/反重力 执行并 push，Hermes 在 VPS 拉取并复验。2026-07 forge-wms 实战验证。

## 闭环步骤（每一批）
1. Hermes 出模块级五段式指令（含红线）。
2. 用户在 Mac 用 Codex/反重力 跑 → 它 commit + push 到 GitHub。
3. 用户说"推好了/可以拉了"。
4. Hermes 在 VPS **先检查、再 pull**：
   - `git fetch origin main`（只读，不动工作区）
   - 快进核验：`git merge-base --is-ancestor HEAD origin/main`（否则已分叉 → 停，别盲 pull）
   - 范围核验：`git diff --stat / --name-only HEAD origin/main` —— 只该动预期文件；**红线：不得动前端代码/db/api**
   - 落地：`git merge --ff-only origin/main`（非快进直接拒绝，绝不产生糊涂合并）
   - **内容复验**：读改动文件确认改对了（不只看 diff stat），并 grep 残留（旧 snake / 旧枚举 / 裸竖线等）
5. 把"待确认/系统性"项整理成低负担选择题给用户裁决。

## 关键纪律与坑
- **"先检查再 pull"是用户硬要求**：永远 fetch→核范围→ff-only，不 blind pull。
- **git 对非 ASCII(中文)路径做八进制转义并加双引号**（行尾变 `.md"`）。用 `grep '\.md$'` 或按中文名 grep 会**假阴性/假"越界"**。核范围时看 raw 清单 + 眼判模块，别只信正则；grep 加 `-a`。
- **VPS 只能 pull 不能 push**（无 gh / 无凭据 helper / 无 SSH key，HTTPS remote）。推送一律走 Mac 的 Codex/反重力。**若 Hermes 误在 VPS 提交了 → `git reset --hard origin/main` 回滚**，避免与 Mac 后续推送分叉埋雷（回滚前告知用户，内容可重来才回滚）。
- **并行规则**：只读"报告指令"可并发（不写文件、无冲突，用户开两个 chat 更干净）；写指令必须操作**物理独立文件**——碰同一批文件的（如全局 SKU 替换 vs 模块命名）绝不同时跑。

## 反重力(Gemini)加固红线
反重力本能是"生成前端页面 + 跑得快爱动手"。派它做纯文档/mock 任务时，红线要额外压两条：
- "本次只改 .md，不生成/改动任何前端页面或代码"（明确按住，否则它顺手碰 front-prototype）。
- "先出报告后动手，别一把梭全改"（防它把系统性问题一次改塌）。
- 五段式指令工具无关，Codex/反重力 通用；只需针对反重力补这两条。

## 打样 + 报告先行（大规模重构）
大改（数百处、数十文件）先打样一个模块验证规范、锁定后再批量；侵入性改动先出零改动影响面报告、人工审批映射后再执行。审计/规范化方法见 `pm-prd-code-alignment/references/naming-mock-normalization.md`。
