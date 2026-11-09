---
name: forge-project-management
description: Forge 项目(ERP+WMS)的部署、A2A并行开发、PRD审计等工作流规范。当用户提到"部署forge""A2A并行""PRD审计""四维对齐""反重力指令"时加载。
---

# Forge 项目管理

## 项目列表

| 项目 | GitHub | 部署路径 | 技术栈 |
|------|--------|---------|--------|
| forge-erp | lophyJessica/forge-erp | /var/www/pmlophy.com/project/forge-erp/ | React+TS+Tailwind+Vite |
| forge-wms | lophyJessica/forge-wms | /var/www/pmlophy.com/project/forge-wms/ | React+TS+Tailwind+Vite |
| forge-crm | lophyJessica/forge-crm | (待部署) | React+TS+Tailwind+Vite |
| forge-scrm | lophyJessica/forge-scrm | scrm.pmlophy.com（uvicorn 8647 + nginx 反代,0824 上线） | React+FastAPI+MySQL17表 |

> **QS-JXC 框架升级（forge-crm 试点，2026-09-12）**：升级项目框架到维他命 QS-JXC 的 00-99 分层 + 版本化 + 字段TSV + 权威源规则。目标结构、方法论核心（三层各管各/变化分层改/版本化迭代）、forge-crm 差距与升级路线，见 `references/qs-jxc-framework.md`。

### forge-scrm：姐夫新媒体运营系统（0823 从零调研阶段）

- **性质**：从零需求驱动的 Forge 新仓库（不是 ERP/WMS 那种已有代码项目）——`context/`(规则源) > `prd-docs/`(正式PRD) > `requirements/`(调研过程) > draft/docs/templates/prompt/check-reports
- **流程（0823 已跑通一轮）**：问卷(Word 填写版→姐夫回收) → `requirements/06-业务调研结论.md`（已确认✅/待确认⚠️分开） → context 六件套（01业务背景范围/02核心业务流程Mermaid/03业务实体关系erDiagram/04业务规则状态机/05术语字段SSOT/06系统边界角色权限） → prd-docs/主PRD.md（初稿）
- **⚠️ 产物归位铁律（0823 用户纠正）**：流程图/字段清单/业务关系/业务逻辑这些**业务事实**——产出到 `context/` 和 `prd-docs/`，**不要全部堆在 requirements/**（用户原话："不要产出到 requirements 目录了，需要产出到 context 和 prd吧"）。requirements 只放调研过程和未定稿结论。
- **字段 SSOT 在 context/05**：Demo/PRD/前端只引用不重复定义；未确认字段标 ⚠️，确认后回写 context 再更新 PRD
- **关键待确认（阻塞项）**：脚本是否必须基于选题（问卷 4.1 同时勾了"必须基于选题"和"可独立创建"——矛盾需姐夫拍板）、选题是否记录资料引用、脚本修改历史、脚本审核人、标签维度、角色权限——集中列在 prd-docs/主PRD §10
- **技术分工（0823 用户定）**：原型交给 Gemini/反重力（快、只做 UI 骨架）；后端（MySQL/API/状态机）交 Opus；批量文档/标准化执行交 Workbuddy；UI 收尾交 Cursor

### forge-scrm 二期开发/部署踩坑（2026-08-26）

- **前端 baseURL 与后端路由 prefix 必须全局一致（404 血泪）**：一期路由 prefix 全是 `/api`（topics/materials/prompts 都是 `/api/xxx`），前端 axios baseURL=`/api` + 路径 `/topics` = `/api/topics` 正常；二期 phase2.py 写了 `prefix="/api/v1"` → 前端请求 `/api/benchmark-accounts` → **404 Not Found**（页面能开、toast 报 Not Found）。修复：二期 prefix 对齐一期（去掉 /v1）。**教训：新模块路由 prefix 必须对齐既有约定（本项目无版本号惯例），前后端 baseURL/prefix 一致性是验收第一项**；症状特征=页面能打开但所有请求 404（后端 API curl 直测 401=路由存在，说明是前端路径拼接问题）。
- **生产 .env 运行时依赖清单（部署后功能失败根因）**：deploy.sh 排除 `.env`（sha256 保护），迁移后生产 .env 可能缺新模块的 key——二期研究助手需要 `DEEPSEEK_API_KEY`（DeepSeek 报告生成）+ `TAVILY_API_KEY`（检索），缺失时任务失败且错误信息明确（"DeepSeek API Key 未配置：请在 backend/.env 设置..."）。**部署验收清单：MySQL 凭据 + DEEPSEEK_API_KEY + TAVILY_API_KEY（+ 未来模块新 key）逐项 grep 生产 .env 确认存在**，再实测一条业务链路（研究任务完整跑通检索→报告）。
- **部署 = Mac 跑 `./deploy/deploy.sh`**（6 步：build→rsync dist→rsync 后端(排除 .env)→alembic upgrade→重启服务+nginx→HTTPS 验证）；搬瓦工 SSH：`ssh -i ~/.ssh/id_ed25519_forge -p 2222 root@45.78.70.160`，后端 uvicorn 127.0.0.1:8647（systemd forge-scrm-api）。
- **Codex 自报\"已部署\"≠ 完整部署（2026-08-26 实踩，用户被旧 UI 坑了两次）**：Codex 声称\"部署上来了\"，实际只 rsync 了部分后端代码——**alembic 迁移没跑**（`alembic current` 停在旧 head，新 seed 迁移 8f5d2a1c7b90 未执行 → 模板表空）、**前端 dist 是旧 bundle**（mtime 09:38，全模板化改造的前端没上去 → 用户看到旧 Radio/无保存按钮/截断）。**部署后必验三查（每次都要做，别信 Agent 自报）**：① `cd /opt/forge-scrm/backend && .venv/bin/alembic current` == 最新 head（git log 里最新迁移文件号）；② 前端 bundle mtime == 部署时间（`ls -la /opt/forge-scrm/frontend/dist/assets/`，旧时间=没部署前端）；③ 后端关键代码 grep（如新增路由 `grep -c 'research-tasks/{task_id}/report' phase2.py` = 1）。**三查不过 = 让用户重跑完整 deploy.sh**（Codex 的\"部署\"可能只是部分 rsync）。
- **Alembic 数据 seed 迁移的时序坑（2026-08-26 实踩：seed 静默跳过 → 表空）**：数据迁移（INSERT 模板/字典等）若依赖 `created_by` 外键查 user 表，而 admin 用户是**应用启动时创建**（seed.py，晚于迁移）→ 迁移执行时 user 表空 → 代码里 `if created_by is None: return` **静默跳过** → 表空且迁移已标记完成（不会再跑）。**部署后必须查数据表确认 seed 真的插入了**（`.venv/bin/python -c` 用 settings.database_url 连库 `SELECT count(*) FROM prompt_template`，不用 mysql 客户端拼密码——会触发命令 blocklist）。修复：手动补插（用应用代码的常量 + 首个 user id，幂等检查 task_type+name 已存在则跳过）；**治本：应用启动时加\"表空自动 seed\"逻辑（在 admin 创建之后），新环境不再踩**。
- **用户提交偏好（0826 用户明确纠正两次）**：代码提交用户自己在 Cursor/Antigravity 界面做——**只给【提交备注】（commit message body 文本，粘贴进备注区），不给标题/不给命名**（\"你不要给我命名，我都是用 cursor 或者 antigravity 提交的，只要给我备注信息就行了\"）。指令末尾附备注块（纯 body，无 subject）。git 命令只在用户没自己提交时给。
- **指令 push 节奏铁律（0826 用户纠正\"你不要push那么快\"）**：写指令/改文件后**不要立刻 commit+push**——先给用户看内容讨论（需求常中途澄清，如审核需求被推翻两次、UI 参照目标确认路径），等用户明确说\"可以 push/确认\"再推。需求讨论阶段的中间版本留在本地即可。已 push 的指令若需求变更，用新 commit 修正并删除旧文件（git rm），不留冲突版本。
- **prompt/ 指令文件序号化（0826 用户要求）**：指令存档按时间线加序号前缀（`01-第二步-xxx-指令.md` … `09-全模板化改造-指令.md`），**新增自动续号**（从 10 起），否则越堆越乱。给 Agent 执行时引用具体序号文件名。
- **前端调用了后端不存在的接口 → 404 弹错 + 兜底"碰巧"成功（审查盲区）**：ResearchReport.tsx 先调 `/research-tasks/{id}/report`（后端没这路由）→ 404 → client 拦截器 message.error("Not Found") → catch 里兜底调 `/research-reports/{id}` 成功 → **报告显示正常但每次进页面弹 Not Found**；且兜底"成功"是因为 report.id 恰好等于 task.id（第一条任务），数据多了必白屏。修复：后端补 `/research-tasks/{task_id}/report`（按任务查报告）。**审查教训：页面能显示 ≠ 所有请求都通——前端每个 API 调用路径要跟后端路由逐一核对（`grep '@router.get\|@router.post'` 对前端 grep 'http.get\|http.post' 的路径），404 弹错哪怕页面正常也要抓**。\n- **antd Select `optionLabelProp` 收起态只显示指定短字段——用户嫌\"选完就变成四个字了\"，要\"正常截断\"**：模板库下拉 options 设了 `optionLabelProp=\"shortLabel\"` + `shortLabel: task_type` → 收起后只显示\"选题生成\"四个字。用户要求：收起态显示完整内容的前 N 字（省略号截断），下拉展开完整显示。**修复：去掉 optionLabelProp（antd 默认用 label + CSS ellipsis 单行截断），保留下拉展开用 optionRender 多行完整显示 + Tooltip 悬浮全文**。教训：UI 交互细节别自作主张"精简显示"，用户要的是标准截断（省略号），不是字段切换。\n- **取消表单字段的正确姿势（数据库字段保留）**：用户\"取消有效期字段——页面不展示不填，数据库字段保留\"。前端删 Form.Item + 提交 payload 里的字段 + 编辑回填；**后端 schema 该字段改默认值兜底**（`valid_from: date = Field(default_factory=date.today)` / `valid_until: date = Field(default_factory=lambda: date.today()+timedelta(days=365))`）——满足数据库非空约束、零迁移。**模式：\"取消字段\"= 前端不展示 + 后端默认值兜底，不动数据库**（除非用户明确要求迁移）。\n- **DeepSeek 模型选择：`deepseek-v4-flash` 是推理模型（输出被 reasoning_content 占用，max_tokens 下 content 可能为空），不适合 forge-scrm 的 chat_json 报告生成——用 `deepseek-chat`（稳定输出 JSON）**。实测：同 key 下 deepseek-v4-flash 返回 200 但 content 空；deepseek-chat 正常返回。**选型规则：需要结构化/JSON 直出的业务生成用非推理模型；要深度推理才用 v4-flash/reasoner**（Hermes 主对话用 v4-flash 没问题——对话不需要 JSON 直出）。
- **菜单重复入口 = 旧页面残留（2026-08-26 用户发现：\"数据分析的提示词模板和权限管理的冲突\"）**：同功能在两处菜单都有入口（`/analysis/prompts` 旧页面 + `/admin/prompt-templates` 新版 P0 页面，都调同一 CRUD API）→ 用户困惑+维护双份。**修法：独立成模块——新增一级菜单（如\"模板管理\"）放新版页面，移除旧菜单入口 + 删旧路由（旧页面文件保留不删，防历史引用）；保留功能完整的那版（对比两页：有内置模板展示/删除保护/版本号的胜出）**。教训：交付新页面时检查菜单里是否已有同功能入口；用户报\"两个 XX 冲突/重复\"先 grep 菜单 + 路由找重复入口，再对比页面功能完整度决定留哪个。
- **\\\"取消/简化流程\\\"类需求必须先澄清三分法再写指令（2026-08-26 审核功能案例，第一版写错被推翻两次）**：用户\\\"把审核功能下了\\\" → 第一版按\\\"全部取消\\\"写（含脚本/分析审核）→ 用户澄清\\\"AI 生成结果可以审核，新建资料不需要\\\"→ 再澄清\\\"导入资料要审核\\\"。**最终形态=人工创建免审核、导入保留审核、AI 产物（回写资料/选题/脚本/分析）保留审核**。教训：凡涉及\\\"流程简化/权限调整\\\"，写指令前先列出现状清单（页面/路由/菜单/后端/状态机/规则文档），并主动问清三类来源（人工录入 / 批量导入 / AI 生成）各自怎么处理，别凭第一句需求推断全量范围。
- **模板启停用/删除与历史生成数据解耦（2026-08-26 forge-scrm 产品规则，用户确认）**：模板可启停用（PromptStatus 枚举已有 + PUT 支持 status；管理页加状态列 + 操作栏一键启停用 Switch）；**启停用/删除只影响未来生成的可选性，历史生成数据不受影响**——因为生成时已存 prompt 快照（content_snapshot），历史记录自带模板副本，不依赖模板表存活。实现要点：builtin 接口和生成默认模板查询只取 `status==启用`（无启用模板回退代码常量），显式指定 template_id 不拦截；删除保护（每 task_type 至少保留一条）不变；不清理/不修改任何历史生成记录。**模式：凡\"配置项启停用/删除\"类需求，先确认生成/引用路径是否已做快照（有快照=历史解耦天然成立），再写过滤逻辑。**
- **全局 UI 统一：参照 copy-wms 紫色主题（2026-08-26 forge-scrm，用户指定参照物）**：用户对 forge-scrm 基础 antd 5 裸拼 UI 不满（操作栏混乱/状态色不统一），要求参照 `~/个人文件/copy-wms`（字节 Figma 稿的 Codex 复刻版）的视觉语言全局统一。**实施模式（Cursor 执行，Grok 4.6 快模型可跑批量）**：① 入口 `ConfigProvider` 主题 token：`colorPrimary: '#7c3aed'`（violet-600）+ colorLink/colorInfo 同色 + borderRadius 6，侧栏深色 + `darkItemSelectedBg` 紫色；② 操作栏封装 `TableActions.tsx`（≤2 按钮并排间距 8px，>2 收 Dropdown「更多」，删除/废弃/驳回 danger）；③ 状态 Tag 全局色板映射（statusTagColor：启用/已通过/已生效/已完成=green，停用/已废弃/失败/已过期=red，待审核/待筛选/进行中/执行中/检索中/整理中/running/searching=orange，草稿/待执行/pending=default，部分成功/partial_success=gold）；④ 列表=Card+筛选+Table+分页靠右+长文本 ellipsis；表单 vertical+maxWidth 720；Modal 520/720。**教训：UI 统一类任务先问用户要参照物（\"想要 copy-wms 那个 UI 设计\"），确认路径写死进指令（\"或 forge-wms\"这种备选会让用户困惑）；UI 类任务给 Cursor 不给 Codex（Codex 功能行但审美差，用户分工铁律）。**


1. **用例数据推演是前端编码前的必过关卡** — PRD → 推演(全闭环) → 所有案例通过 → Demo → 前端
2. **单线程对话** — 不等状态不等进度，一个任务完成→确认→下一个

## 一、部署规范

### 目录结构
```
/var/www/pmlophy.com/
├── project/
│   ├── forge-erp/     ← ERP SPA
│   └── forge-wms/     ← WMS SPA
```

### vite base 配置
两个项目的 `vite.config.ts` 中 base 必须与 nginx 路径匹配:
```
ERP:  base: '/project/forge-erp/'
WMS:  base: '/project/forge-wms/'
```

### nginx 配置模板
每个项目独立 `location` 块,用 `alias` + `try_files`:
```nginx
location /project/forge-erp/ {
    alias /var/www/pmlophy.com/project/forge-erp/;
    try_files $uri $uri/ /project/forge-erp/index.html;
}
location /project/forge-wms/ {
    alias /var/www/pmlophy.com/project/forge-wms/;
    try_files $uri $uri/ /project/forge-wms/index.html;
}
```
**坑**:不要用 root 共用,不要合并 location 块,否则一个 404 导致循环重定向。

### 部署流程(方案 A)
1. 用户在 Mac 本地 `npm run build` → 打包 dist.zip
2. 用户通过飞书发送 dist.zip 到 Hermes
3. Hermes 在 VPS 上解压到对应目录
5. 清理 `__MACOSX` 垃圾文件和旧文件
6. `curl -sk -o /dev/null -w '%{http_code}' <url>` 验证 200
7. **React SPA 校验**: 用 `strings | grep -o 'basename[^,;]*'` 检查 JS 产物中的 basename 是否与 nginx 路径匹配(坑:build 缓存可能导致源码已改但产物未生效)

## 二、A2A 并行开发规范

### 核心铁律:一个 Session = 一个项目
Codex 和反重力并行时,两个项目绝不能混在一条 prompt 中:
- 禁止在 wms 目录开 session 喂 erp 指令
- 禁止一条 prompt 写"对两个项目分别执行"

后果:agent 会自作主张跨目录搜改文件(曾 wms 目录喂 erp 指令→跑去改 erp 文件夹)。

### 五段式指令模板
```
Context:          ← 项目背景、当前状态
Request:          ← 具体操作,分步骤
Output format:    ← 期望输出
红线禁止:          ← 不能做的事(边界锁定)
Checkpoint:       ← 成功/失败的下一步
```
格式要求:单个 plaintext 代码块、纯文本禁 emoji。

### 工具分工
| 工具 | 适合 | 不适合 |
|------|------|--------|
| Codex | 审计/分析、生成新文件、PRD/文档 | 修改已有页面、跨文件联动 |
| 反重力 | 修改已有页面、跨文件联动 | 联网搜索 |

Codex 红线多加"禁止修改源码文件"。反重力不加此限制。

## 三、PRD 生成:context 先行,PRD 后审,前端最后(铁律)

### 正确的开发顺序(不可跳过)

```
context 修改 → 用户评审 → PRD 生成 → 用户评审 → 前端实现
```

**绝对禁止: 在用户评审通过 PRD 之前,输出前端实现指令。**

踩坑记录(2026-07-29):供应商报价模块被定位成"采购员录入版",PRD写了4份套件、前端build了3轮——结果用户说:"这是供应商侧的报价工作台,不是采购员记事本。"PRD根就错了,前端全白做。

### 每个阶段的交付与用户确认点

| 阶段 | 交付物 | 用户确认什么 |
|------|--------|-------------|
| 1. context | context/04、05 | 模块名/单据定位/编码前缀 |
| 2. PRD | 主PRD+字段清单+Demo×2 | 业务定位是否正确(供应商 vs 采购员) |
| 3. 前端 | dist | 页面是否按 PRD 实现 |

### 常见 PRD 定位偏差(必须规避)

- 把"供应商自己的报价工作台"做成"采购员手动录入供应商报价的记事本"
- 把"供应商查看询价单并逐行报价"做成"采购员创建报价单独立存在"
- 设计采购员侧的字段(报价人/确认人/创建人)放到供应商侧 PRD

## 四、Agent git 铁律

**用户只在反重力/Cursor IDE 中做 git 操作,不在任何 CLI Agent 中提交代码。**

Agent(Workbuddy/Codex/反重力CLI/任何命令行Agent)只生成文件和代码,**永远不执行 git add/commit/push**。

原因:Agent 看不到项目全貌——改了什么文件、撞了谁的代码、漏了哪条规则——用户只能在 IDE 里 git diff 逐行审查。

指令模板中的 Checkpoint 字段写"npm run build → dist → 发我",不写"git commit"。

## 五、React Router SPA 部署校验(坑)

部署后除了 `curl` 验证 200,还需检查 JS bundle 中的 `basename` 是否正确:

```bash
# 部署后校验
curl -sk -o /dev/null -w "%{http_code}" https://pmlophy.com/project/forge-erp/
# 检查 basename
strings /var/www/pmlophy.com/project/forge-erp/assets/index-*.js | grep -o 'basename:[^,;]*' | head -3
```

**坑**: `BrowserRouter basename` 在源码中写了 `/project/forge-erp`,但 build 产物中可能仍是 `/`(因为旧缓存未清理)。排查方法:
```bash
cd front-prototype && rm -rf dist node_modules/.vite && npm run build
```

## 六、PRD 审计:四维对齐

当用户说"审计/对齐/检查一致性"时,按四个维度交叉对比:

### 审计维度
1. **Context 对齐**: context/ vs PRD/ 术语/单号前缀/边界约束
2. **PRD 与原型对齐**: Demo PRD vs pages tsx (筛选项/列/按钮/字段状态)
3. **流程对齐**: context流程 vs PRD状态机 (死状态/上下游状态引用)
4. **功能清单对齐**: context/03模块清单 vs prd-docs/目录 vs pages/页面

### 输出格式
P0/P1/P2 分级,每条:严重级|维度|项目|问题|源文件|目标文件|修复方向

### 审计后决策(人工,非 AI 自动)
- P0 要修但已知设计不修 → 标注为合理差异
- 页面有但 PRD 无 → 决定:补 PRD / 隐藏页面 / 接受(如 ERP 的销售/零售页面,memory 已标"无PRD依据")
- PRD 有但页面无 → 决定:补页面 / 删 PRD

### 常见误报(审计后要人工过滤)
- 基础资料缺流程图 → 主数据 CRUD 无状态流转,PRD 本不应有图
- 播种缺 PRD/页面 → 播种是出库链第 3 步,不是独立模块
- 调拨/报损标二期但已实现 → context 过时,更新 context 不删页面

## 七、三系统审计/返修生命周期（2026-08-21 实战）

forge-crm / forge-wms / forge-erp 三套是**独立进度的同类项目**，接"继续审计/返修"时先核对各自的进度阶段，别当统一状态处理：

```
阶段: 标注 → 对齐审计(只读) → 返修P0清零 → P1/P2收口
CRM:  完成 + P0 12/12清零 + P1/P2已收口
WMS:  完成 + P0 22/22清零 + P1/P2已收口
ERP:  审计未做（2026-08-21 首轮完成，32项=P0 8/P1 22/P2 2）→ 待返修
```

**要求"两个继续返修、一个先审计"时：**
- ERP 审计 = 只读（报告留本地用户发我看，或 rsync 到 VPS 独立目录 `/var/www/pmlophy.com/<proj>-audit-reports/`）
- CRM/WMS = P1/P2 收口返修（改代码+build+部署）
- 三个独立 Codex 会话、独立目录，可并行

**P1/P2 收口边界（用户确认的硬边界）：**
- ✅ 前端能补的：列表分页/高级筛选/状态动作矩阵/360°信息架构/UI/交互/字段/展示类
- ❌ 依赖真实后端的（真实 ERP/TMS/财务接口、服务端并发锁、离线同步、月末结算）
  → **维持"明确 Mock/未触发/服务端态"，不伪造业务事实**。这是阶段边界不是代码缺口。
判断口诀：这个需求放前端原型能否真实落账？否 → 标服务端态不伪造。

**报告/产物核验（重要）：**
自检报告说"已部署"≠ 真上线。码上核验：对比线上 bundle hash vs 报告声称、
`find <部署目录>/assets -name 'index-*.js' -printf '%TY-%Tm-%Td %TH:%TM %f\n' | sort -r` 看 mtime、
`grep '<项目>' /var/log/jarvis-deploy.log` 看当天部署记录。发现没上线 → 让对应会话补一次部署
（产物常留在其本地 `/tmp`），别当整轮都完成。

**审计报告目录单一来源（2026-09-27 用户纠正）**：审计报告统一放 `08-相关资料/audit-reviews/`，**不要另建"审计报告合集"等并行目录**——用户配置哲学：同一职责只保留一个目录，功能重复的新目录是冗余。新建目录前先 `ls` 看有没有已承担该职责的目录。

**报告"遗留风险/待确认"项 ≠ 待办事实（0824 用户纠正）：**
自检报告里的"待确认/待删除/遗留风险"是**触发信号**，不是核过的待办——同晚后续 commit 可能已解决
（实测：21:41 报告写"4 个旧单文件待删除"，21:45 的 commit 已删除并 commit message 写明）。
向用户汇报 pending（尤其新会话开场）前，先核对仓库现状三步：
1. `git log --format='%h %ad %s' --date=format:'%m-%d %H:%M' -8` — 报告之后是否有覆盖性提交
2. `git status --short` — 工作区未提交改动才是真 pending
3. `ls`/`find` 实测文件是否还在，不靠报告文字判断
用户主动说"这个待办不一定是真的，再检查下"时直接照做核实，不要辩解——大概率报告已被后续提交超越。
