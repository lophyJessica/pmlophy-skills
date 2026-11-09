---
name: codex-delivery-pipeline
description: Codex 交付管道管理——指令模板（五段式+部署通道+自检报告）、"报告到了代码没到"断层问题、验收顺序（报告→代码实锤→线上实锤→亲测）。当给 Codex 写修复/开发指令或核验 Codex 交付时加载。
---

# Codex 交付管道

## Codex 运行位置（铁律，2026-09-27 用户纠正）

**Codex 跑在用户 Mac 本地，VPS 上无法调起 Codex 会话**——不要提议"VPS 直接给 Codex 跑"这类方案（用户原话提醒"别忘了"）。审计/修复类任务的标准分工：Hermes/VPS 侧**只负责写指令文件 + 检查/核验结果**，用户在 Mac 本地开 Codex 会话、喂指令文件执行。给指令时执行位置明确写"Mac 本地 Codex 会话"，不写 VPS。

**指令文件目录（forge-crm 口径）**：指令存项目内 `08-相关资料/提示词合集/`（目录名用"提示词合集"，不用"prompt"——用户 2026-09-27 纠正）；forge-scrm 沿用根 `prompt/` + `NN-名称-指令.md` 序号格式。

## 指令模板（五段式，全部放在一个 ```plaintext 代码块内）

1. **Context**：项目位置（Mac 路径）、工作分支、任务背景、现状要点（文件+行号）、边界声明
2. **Request**：按编号列修复项，每项含文件路径 + 具体对策；最后一条固定是"禁止扩界"
3. **Output format**：最小改动 + build/compileall 验证命令 + 自检报告路径与命名
4. **红线禁止**：不 pull 不改文件 / 不动 context、prd-docs、requirements / 不 commit、push、deploy / 禁伪造构建结果 / 密钥不入日志
5. **Checkpoint**：自检报告 curl 上传命令（逐字给出）+ 汇报清单

指令全文存仓库 `prompt/` 目录（PRD 存 `prd-docs/modules/`），便于 git 化追溯。

**指令文件命名规范（用户 0828 纠正）**：prompt/ 下指令文件必须 `NN-名称-指令.md` 序号格式（NN 两位连续，新增续号，如 21-报告删除与卡片真折叠-指令.md）。禁止无序号散文件或带日期后缀——曾从 16 号起丢了序号被用户纠正，返工重命名 8 个文件。建新指令前先 `ls prompt/` 看最大序号。

## 已知坑：报告到了、代码没到

**现象**：Codex 上传自检报告到 ai-reports 管道成功，但代码留在 Mac 本地未 commit/push（指令红线"禁止 commit/push"被忠实执行）→ VPS 侧拉不到代码，报告与代码断层。

**预防**：指令 Checkpoint 段明确写"代码保持本地未提交状态，由用户提交推送"，且汇报清单里单列此项。验收流程固定为：报告到管道 → 助手读报告核内容 → **提醒用户 commit/push（附提交备注 body）** → 助手 VPS 拉取 grep 实锤 → 部署 → 用户亲测。

**更省事的默认写法：让 agent 改完自己 `commit` 到本地分支、但不 push。** 红线里的"不 commit、不 push"只要保留 push 那一半就够——完全禁止 commit 的结果是每一轮都要多绕一次：报告说改完了、VPS 拉下来还是旧字节数、grep 不到新内容，再补一条提交命令。指令的 Request 末尾固定加一句「改完 `git add <显式文件清单>` + `commit` 到本地分支，不 push」，代码随 pull 到达，push 和部署仍由用户/助手控。**验收一律以 pull 后的字节数／内容特征为准，不信报告里的"已修改"。** 大文件（pptx、xlsx）尤其要核字节数差异，只核份数和页数看不出改没改。

## 用户提交习惯

用户在 Cursor/Antigravity 界面提交，**只要备注 body 不要标题**——助手交付时附上完整提交备注文本供粘贴。

但多线并行/工作区混合了用户自己改动时，口径反转为**直接给可整段粘贴的 git 命令块**（用户：「这种并行跑的 git 我不操作了，你给我 git 指令」）；注：提交时仍需分两批（用户自己那批 vs agent 这批）。完整命令块写法与分批纪律见 `ai-agent-delivery-review` 的「用户偏好（提交与反馈）」节。

## 自检报告是过程产物，验完即止（不要长期入库）

自检报告的生命周期只有三段：**Agent 自检上传 → 助手核验通过 → 结束**。它不是交付物也不是项目资产，长期堆在仓库里只会让审计目录变成杂物间，还让后来的人误以为那是需要维护的文档。

- **不给自检报告建独立子目录**（如 `审计报告/自检报告/`）。目录一建就会持续累积；新报告直接落 `08-相关资料/审计报告/` 根层，AGENTS.md 里的落点也应这么写。
- 核验通过后**按批清理，不要逐个挑**：先 `find <报告目录> -name "*自检报告*" -type f` 一次列全——散在子目录、`历史版本/`、根层平铺的同名文件最容易被漏。曾清理完子目录下 66 个，根层还躺着 5 个。
- **要长期留的是审计/走查/评估类报告**（结论会被后续工作引用），别和自检报告混着删；清理前把两类分开列给用户看。
- 删前仍按「删除范围复述」的规矩：先列删什么/留什么，等用户点头再 `git rm`。

## 部署门禁（forge-scrm 口径）

- deploy.sh 不自动 git pull：部署前先 `git log` 对远程 HEAD，Mac 源码落后 = build 出旧 bundle 白部署
- 有 alembic 新迁移：部署后必须 `alembic upgrade head` 再 restart，验 `alembic current` 到 head
- 前端验 bundle：grep dist 内容特征（React inline style 是 JS 形式 maxWidth:720），不用文件时间戳（rsync -a 保留源 mtime 误导）
- 远端实锤：SSH grep 后端关键代码行数 + curl 内部端口看鉴权响应

## 沙箱网络兜底

Codex 沙箱 DNS 常解析不了 pmlophy.com（curl exit 6）→ 报告改存 check-reports/ 并如实汇报"未上传管道"，禁止重试超过 1 次。助手侧可在 VPS 读取并代传。

## 目标 VPS 无 SSH / 只有 HTTP 时，上传通道改 HTTP POST（0906 公司 VPS 实证）

air自家管道默认 `rsync -e ssh` 上传 zip + curl 传报告——但目标 VPS 若**部署了 Hermes/娜美、却 SSH 被防火墙拦、只有 HTTP 可达**（典型大公司办公 VPS，无 root、仅 Web UI/HTTP 隧道、SSH 被拦），rsync 走不通。此时上传通道改成 **HTTP POST**：

- VPS 上起一个收文件接口（agent 能 `curl -X POST -F "file=@产物.zip"` 传），产物/报告都走 HTTP
- 五段式指令末尾照旧逐字给两条 HTTP 命令（`curl -X POST -F file=@<产物.zip> <上传端点>` + `curl -X POST -F file=@<报告>.md`），agent 照命令执行
- **搭之前先确认三件**：① VPS 能不能挂 HTTP 上传接口 ② 产物上传后能不能通过网址访问（用于预览）③ SSH 是否确实不可用——能才搭，别凭想象先起服务

## 部署 ≠ 上传（0906 用户纠正，勿再当"agent 全自动部署"）

**agent"自动上传 zip 到 incoming / 自动交自检报告"只到"上传"为止**——上传 ≠ 部署。真实部署 = **用户确认后助手手动跑 `deploy.sh / deploy-all.sh --deploy <项目>`**；cron/`--check` 只做"检测新 zip + 提醒"，不是自动部署。任何把这些说成"agent 自动部署"都是误解。给 agent 写指令时，红线段固定写"不 commit / 不 push / 不部署"，部署由用户在验收后单独拍板；给用户介绍管道时按"agent 上传 → 用户确认 → 助手部署"口径说，别说成全自动。

## 会话丢失账面 → 重审计而非信记忆

经历 /new 或长会话后，助手记忆里的缺口清单（如 G1-G15 状态）不可靠。标准打法：让 Codex 做**全量只读复审**（逐项 grep 代码现状给三态判定：已闭环/部分完成/未做，每项带文件:行号证据），产出复审报告后按真实账面排单。复审报告是后续所有指令的依据，历史审计报告只作对照不作结论。

## 高性价比排单：先做"后端就绪只补前端"

复审出的"部分完成"项（后端接口/字段已在，缺前端展示）比"未做"项便宜得多——按性价比排序：部分完成打包 → 机械小件（排序/规范补行）→ 未做大件。用户拍板"现在就消化"时优先出这类指令。打包原则：**文件域不重叠**（如 collection/research vs reports vs backend routers），可多 Codex/Cursor 会话真并行。

## 复审发现的执行缺口要二次核验

Codex 自检报告说"某处因缺字段保留原排序"≠问题解决——它可能是"报告了但没改"。用户拍板 A 方案（用现有时间字段映射而非加字段）后，**核验时必须实际 grep 对应文件**确认映射落地。曾实测：报告称 4 处保留，实际 2 处该按 A 方案改的没改。核验用实锤 grep（功能代码行号、红线字样全扫、order_by 计数），不引用报告结论。

## 并行会话合并提交

用户嫌逐 commit 麻烦时允许多会话改动合并为一个 commit（备注 body 分段列各块内容），但前置门禁：①助手先核验全部报告与红线 ②用户认可才 commit+push ③不认可整体 reset 回滚 ④部署放最后单独拍板。

## VPS 侧 pull 卡 stash 坑

VPS 有未跟踪构建产物（如 tsconfig.app.tsbuildinfo）时 `git pull --ff-only` 会静默停在旧 HEAD（"Updating.." 却不前进、git status 显示 behind）。解法：`git stash && git merge --ff-only origin/main && git stash pop`；stash pop 冲突的构建产物用 `git checkout --theirs` + `git add` 收尾。**每次 pull 后必须 `git rev-parse HEAD` 确认真到了远程 HEAD 再开始核验**。

## 审核字样红线口径（forge-scrm 持续生效）

前端永不展示"审核/抽查/待审核/转审核"字样或入口（二期默认通过，审核仅后端预留）。写指令时作为固定红线段落；涉审核 UI 的缺口项（如 G14）一律搁置并在自检报告标注。核验时除扫本轮新文件外，还要确认已有展示被顺手移除、并列出**存量**违规清单交用户拍板（不擅自动历史代码）。

## 审计型收尾（两线并行打法）

长迭代收口时的标准打法见 `references/audit-pattern.md`：A 功能审计（P0/P1/P2 分级 + "已核通过"基线）与 B 标准审计（先立标准成文再走查违规）两个 leaf 子代理并行，产出合并为一条编号修复指令。UI"丑/随意"类反馈的根因通常是标准未成文——先写 UI-DESIGN.md 类规范文件（AGENTS.md 只留指针），修完沉淀进仓库。

## PRD ↔ 代码对齐审计（产品层收口）

代码质量审计之外的第三条线：PRD↔前端页面的**双向 diff**（超前/缺口/偏差三类），指令模板见仓库 `prompt/20-PRD与前端对齐审计-指令.md`（forge-scrm 实例）。关键纪律：

- **判定依据严格限定**：context/ > prd-docs/ 主PRD+字段清单+MVP验收清单；draft/、requirements/ 不算依据——"缺口"必须引用 PRD 原文位置，PRD 没写的不许算缺口
- **"代码领先文档"不是回退信号**：用户拍板过的功能（如报告删除）上线了但 PRD 没回写，审计会标"超前"——处置是**回写 PRD** 而非回退代码，否则下个 Agent 会按旧 PRD 把功能拆掉
- **拆分修复优先级**：MVP 阻塞（context 明确冲突）立即修；"文档回写"半小时单独一批（防未来 Agent 拆家）；大功能缺口（二期 P0/P1 链路）进待办池排期，不混进修复轮
- 审计产出自带"建议处置"列，但最终拍板必须经用户——"回退 vs 补 PRD"是产品决策不是技术决策

## 状态修复后必须全链路回归已修项

状态机类修复（如"已推送不可删"）上线后，用户可能在**同一页面发现相邻的旧规则漏洞**（如"报告列表也没有删除"）。此时区分：是漏实现（查 PRD 是否承诺过）还是 PRD 明确不做（如 forge-scrm 数据报告主PRD:331"默认不提供删除"）——**后者是产品决策点**：给用户 A（尊重 PRD 不加）/ B（修订 PRD 补功能）两选项，拍板后修订 PRD 口径再开发，禁止按代码现状默认。

## 核验手段升级：Playwright 服务器端取证

grep 源码/bundle 验证不了"运行时到底渲染成什么样"时（如样式 props 有但 DOM 无、UI 表现与代码矛盾），在 VPS 装 Playwright（`npm i playwright@1.49.1 && npx playwright install chromium`，放 /tmp/pwtest）无头登录实测：读 form 元素 `getAttribute('style')`、`el.style instanceof CSSStyleDeclaration`、React fiber `memoizedProps`、computed style，与用户截图现象交叉定位。比让用户反复截图/换浏览器试错快得多。完整模板与判读见 `frontend-dom-shadowing-pitfalls` skill 的 `references/playwright-evidence.md`。

**重要教训（bundle grep 误判）**：Rollup 会把共享 token 提升到 chunk 前部，"使用点附近 grep 不到字面量"≠引用缺失——应查 `style:变量名` 引用链。曾因这个误判差点错怪构建产物，实际根因是 DOM named control 遮蔽（见 frontend-dom-shadowing-pitfalls）。

## agent 修复多轮无效 → 收窄到运行时证据再出下一轮指令

同一 UI bug 第二轮修复（agent 的"根因推断+修复"）仍无效时，停止让 agent 再猜。助手自己上 Playwright 拿运行时铁证（fiber props 层 vs DOM 层的差异），把证据直接写进下一轮指令的 Context（"已排除清单+决定性证据"），并**明令禁止 agent 重复已排除的排查路径**。案例：forge-scrm 脚本列表卡片 bug 三轮才结案，第三轮靠"el.style.setProperty is not a function"这一条证据直指 Form.Item name="style" 遮蔽 HTMLFormElement.style。
