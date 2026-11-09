---
name: make-com-automation
description: Make.com（原 Integromat）自动化平台搭建——无代码工作流串联 AI 模型/飞书/Webhook。当用户帮他人（如姐夫）搭新媒体运营自动化、问 make 支持哪些大模型、配置场景（触发→AI→表格）、评估"某个自动化用 make 能不能做"时使用。核心事实：make 原生 AI 模块=OpenAI/Claude/Gemini/Stability/xAI；DeepSeek 有第三方应用（DeepSeek AI by Synergetic——Make an API Call 模块直接调，URL 只填相对路径 /chat/completions）；原生 OpenAI/Anthropic 模块不能自定义 base URL。
---

# Make.com 自动化平台搭建

## ⚠️ 项目级方向变更（2026-08-24 用户决策）：forge-scrm 自动化层弃 Make 选 n8n

**背景**：forge-scrm（姐夫新媒体运营系统）一期 MVP 不含自动化平台（AI 生成/分析全部 FastAPI 后端内置直调 DeepSeek，同步执行）；自动化平台是二期的事（自动采集/定时任务/跨系统联动）。

**用户决策**（2026-08-24）：二期自动化走 **n8n 社区版（自托管，开源免费）**，弃用 Make。理由：
- Make 手动配置麻烦（每次调流程要去它界面拖节点/配 API/处理 webhook），用户明确"对我来说太麻烦了，还要去手动配置"
- Make 读不了 DS 分享链接（AWS WAF 防护），数据在第三方、凭据也在它平台
- n8n 社区版（GitHub 自托管）= 免费、无执行次数限制、含 Webhook/HTTP/定时/代码节点(JS/Python)/所有节点/Git 版本控制；只有云托管（$20+/月）和企业版（$800/月）收费——单人使用社区版够
- 符合用户"数据自持/属于我"的方法论（同 Hermes 的"拥有 vs 租用"哲学）
- 4C8G VPS 上跑 n8n 毫无压力
- 配置可代码化：工作流定义可用 JSON 导入导出并 git 版本管理，不用手动拖拽

**影响**：8/16 已交付的 Make 场景 1/2（选题/脚本 → 飞书）作为过渡方案留档；后续 forge-scrm 的二期自动化（采集→入库→AI 分析→推送）不再扩展 Make 场景，优先评估 n8n 自托管。**给姐夫类系统出自动化方案时先问"要不要自托管 n8n"再谈 Make**——除非用户明确要用 Make 的 SaaS 便利（免运维、有账号）。

本 skill 其余内容（Make 平台操作细节）仍有效，适用于：继续维护已交付的 make-form 场景、或用户明确点名用 Make 的场景。

**n8n 部署/使用细节**：见 `n8n-workflow-automation` skill（独立子域名反代、secure cookie、闭环验证三步法、与 forge-scrm 集成）。

## 用户协作纪律与场景推进（2026-08-21 强化）

- **一次只推进一个场景的一步**：每次操作前先明确“当前场景 / 当前模块链 / 这一步只改哪个模块 / 完成标准”，不要同时改场景 1 和场景 2，也不要把 ERP、视觉模型等无关问题混入 Make 排查。
- **先读权威笔记，再操作**：恢复旧 Make 任务时，先完整读取最新 notes-vault 手册；不要凭会话记忆猜模块编号、目标表、通道或凭据。场景 1 与场景 2 的编号会重复，描述必须带“场景 X”。
- **用户只看业务视角时，不输出 Make 内部噪音**：交付给非技术用户的手册只写“飞书配置/网页输入/飞书结果”，不写 Make 模块、token、Webhook、HTTP 细节；另出内部技术文档供维护者使用。
- **“下次生成”必须解释触发器**：修改飞书提示词配置表不会自动触发生成；用户保存后，必须下一次打开 VPS 表单并点击生成按钮，表单才触发 Webhook，Make 在本次新运行中重新读取最新提示词。正在运行的任务不受修改影响。
- **Make 是串行 Bundle 流**：不要说模块并行。上游数组经 Iterator 后由下游按 Bundle 逐个处理；Filter 只放行匹配 Bundle。分页、Iterator、Filter 都是同一条串行链。
- **不要误删职责不同的 HTTP 模块**：场景 1/2 读取 Wiki Bitable 配置表的标准链路是：获取 tenant token → wiki `get_node` 获取 `obj_token` → records 读取 → 分页（若分页已合并，则在 records HTTP 内配置分页）。只有确认两个模块职责和 URL 完全重复后才合并/删除。
- **下游依赖上游输出时必须完整 Run once**：单独 Run 下游 HTTP/Iterator 可能拿不到上游 token、obj_token 或数组，即使映射配置正确也会报空值/缺 token。优先从 Webhook 用完整 Run once 验证整条链。
- **官方资料优先于猜测**：模块名称、所在分类和配置方式先查 Make 官方文档。通用 Iterator 的正式位置是 `Tools → Flow control → Iterator`；DeepSeek `Make an API Call` 与 HTTP 模块配置模型不同，不得把 HTTP 的 `Data structure` 选项想当然套到 DeepSeek。
- **DeepSeek 动态长提示词的正确模式**：不要把动态提示词直接替换整个 Body，也不要在 Raw JSON 中盲目手写 `escapeJSON()`。用 `JSON → Create JSON` 构建完整 `{model,messages[]}` 请求体：system.content 映射过滤后的 `fields.提示词`，user.content 保留原有业务输入；DeepSeek 模块发送 Create JSON 的完整输出。场景 1 的 AI 输出是 JSON 数组，需保留其 Parse JSON 链；场景 2 输出一篇脚本，不需要 Parse JSON。
- **结构化字段是半自动，不是动态无限扩展**：提示词内容可以由用户在飞书配置表修改并自动用于下一次新任务；场景 2 网页的核心输入契约仍是 `type/topic/info/action` 四字段。新增/删除输入字段必须同步网页、Webhook 数据结构、User Prompt 映射和结果规则，先告知用户，不承诺自动识别。
- **当前项目的对外交付要分层**：非技术用户只收到用户视角手册和表单/飞书入口；维护者才需要 Make 技术文档。用户手册必须清楚区分：飞书《提示词配置表》负责维护生成规则，VPS 表单负责触发，飞书结果表负责查看结果。

详细的本轮场景链、错误截图对应关系和验证清单见 `references/prompt-config-table-scenario-pattern.md`。


## Architecture Boundary: MVP Automation vs Long-Term Operations System

Make + Feishu Bitable + DeepSeek is appropriate for validating an MVP content-production loop, but do not let the Bitable become the long-term business system by accident.

Use this separation:

```text
Operations system = business facts, configuration, statuses, permissions, audit history
Make = workflow orchestration and automation
DeepSeek = generation and analysis capability
Feishu = optional collaboration/notification surface
```

When the workflow grows beyond a few tables and fixed fields, recommend an owned application with a stable API and MySQL rather than adding more fragile Bitable fields, views, and scenario mappings. Prefer:

```text
Make -> HTTP API -> backend -> MySQL
```

Do not let Make write database tables directly when a backend contract can enforce permissions, validation, state transitions, idempotency, and audit logging. Store media in object storage; keep URLs and metadata in MySQL.

For a current-state summary, produce a standalone delivery document when the user asks for a document. Do not put it into the user's notes vault unless the user explicitly asks to save it as a note. The summary must distinguish completed scenarios from planned scenarios and label test-only paths (such as Telegram) separately from the current delivery path.

A useful current-state summary covers: platform responsibilities, completed scenario chains, input/output contracts, verified results, unresolved scenarios, known connector/platform limits, and the migration path from Bitable MVP to an owned operations system.

- Make.com（原 Integromat）：无代码可视化自动化平台，3000+ 连接器，场景=触发→模块链→输出。
- 免费版 1000 次操作/月（MVP 够用）；付费按需（$9-16/月起）。LLM 费用按你的 provider key 计（make 只收场景操作额度）。
- UI：登录 → Create a new scenario（场景编辑器画布）→ 点 "+" 添加模块 → 搜索应用（如 OpenAI/Anthropic/HTTP/Webhooks）→ Create a connection（填 key）→ 配置字段 → Run once 测试 → Save → 开 Scheduling/Webhook。

## 大模型接入矩阵（2026-08 查证）
| 模型 | make 原生模块 | 接入方式 |
|------|--------------|----------|
| OpenAI (GPT-5.x) | ✅ 有（OpenAI/ChatGPT 应用） | 自带 OpenAI key，或 Make AI Provider（make 内置付费，免自己的 key） |
| Anthropic Claude (Opus 5/Sonnet) | ✅ 有 | 自带 Anthropic key（需绑卡）；或 Make AI Provider |
| Google Gemini (3.6 Flash 等) | ✅ 有 | 自带 Gemini key |
| Stability AI (图像) | ✅ 有 | 自带 key |
| xAI (Grok) | ✅ 有（官方应用） | 自带 key |
| DeepSeek | ✅ 有第三方应用（**DeepSeek AI by Synergetic**——make 认证开发者，非官方但可用） | 搜 \"DeepSeek\" 找到 → Create a connection 填 DS API key → 用 **Make an API Call** 模块直接调 |
| 其他 OpenAI 兼容端点（Go 通道等） | ❌ 无原生 | 同上（HTTP 或 OpenRouter） |

**⚠️ 关键坑：make 原生 OpenAI/Anthropic 模块【不能自定义 base URL】**——模块写死连官方端点，没有 URL 覆盖字段。所以"不手搓用 DeepSeek"在 make 里没有原生直连，只能走 OpenRouter 中转（多一层注册/充值）或 HTTP 模块。注册后实际打开 OpenAI 模块的 Create a connection 界面确认有无 base URL 字段（make 更新快，万一加了就省事）。

## DeepSeek 接入实测（2026-08-15 跑通——修正早期结论）

**结论：make 有 DeepSeek 第三方应用（"DeepSeek AI by Synergetic"——make 认证开发者），不用 HTTP 手搓、不用 OpenRouter！** 在场景编辑器点 "+" 搜 "DeepSeek" 即出现，模块三个：
- **List Models**（列表模型——返回模型清单，不是干活的）
- **Get Balance**（余额查询）
- **Make an API Call**（发起 API 调用——核心，调 chat/completions 用）

**配置步骤**：
1. 场景 "+" → 搜 "DeepSeek" → 选 DeepSeek AI → 选 "Make an API Call" 模块
2. Create a connection → 填 DS API key（platform.deepseek.com 创建——测试充 10-20 元够）
3. **URL 字段只填【相对路径】`/chat/completions`**——⚠️ 不要填完整地址！应用自动加 `https://api.deepseek.com` 前缀，填完整地址会双重拼接（`https://api.deepseek.comhttps://api.deepseek.com/chat/completions`）→ `ENOTFOUND` 连接失败（界面提示原文："Enter a path relative to https://api.deepseek.com. For example, /models"）
4. Method: POST；Headers: Content-Type: application/json（应用预填）；Body: `{"model": "deepseek-v4-flash", "messages": [{"role":"user","content":"你好"}]}`
5. Save → Run once 测试

**验证（Run once 后怎么看结果）**：
- 执行日志 4 步全绿（Initialization/Operation/Commit/Finalization）+ 状态码 200 = 请求成功
- 回复文本在 OUTPUT → Body (Collection) → **choices[0] → message → content**（DS 的回答）；旁边 reasoning_content 是推理过程（DS V4 带思考——正常）
- 注意 Body 显示 "(Collection)" 是折叠的——点开 choices 数组才能看到 content；回复确实存在（"1.3 KB" 输出大小）
- 取数路径（后续场景引用）: `body.choices[0].message.content`

**模型**: `deepseek-v4-flash`（便宜 + 快——测试期省钱；DS 8/17 起峰谷定价——高峰时段贵一倍，批量任务排空闲时段）

## 常用模块
- **Webhooks → Custom webhook**：手动触发（生成 URL，外部 POST 触发场景）
- **Tools → Set schedule**：定时触发（如每周日晚 8 点）
- **HTTP → Make a request**：手搓调任意 API（无原生模块的端点——如 Go 通道）
- **DeepSeek AI（by Synergetic）→ Make an API Call**：调 DeepSeek（见上节——URL 只填相对路径 `/chat/completions`）
- **Anthropic Claude → Create a completion**：AI 生成（System Prompt + User Prompt 字段——提示词预置）

## ⚠️ 飞书连接器真相（2026-08-15 实踩——make 无官方免费飞书连接！）

**make 上搜 "Lark" 或 "Feishu"（拼音/英文指向同一个）——点任何结果（Lark Base / Feishu Base / Feishu Drive / Feishu Document / Feishu Group Robot）——Create a connection 全是同一家第三方付费应用【AI超级斜杠】的表单**：
- 要填：App ID（飞书开放平台应用凭证）+ App Secret（飞书应用密钥）+ **超级会员订单号**（slashx.cn 买 **365 元**会员才有）
- 判断：make **没有**官方免费的飞书连接器——全是第三方付费（有 Verified 徽章 ≠ 官方免费，只是第三方认证）
- 红线：❌ 不填 App ID/Secret/会员号、❌ 不买 365 元会员（冤枉钱）

**替代方案（4 选 1）**：
- **A. 飞书自建应用 + HTTP 模块**（免费——姐夫必须用飞书多维表格时）: open.feishu.cn 免费创建自建应用 → 拿 App ID/Secret → make HTTP 模块调飞书多维表格 API（写数据）——要"手搓"HTTP 请求体（模板可复用），但零成本
- **B. 换存储**（最省事——接受非飞书时）: make 原生免费支持 Airtable / Google Sheets（授权登录式，不手搓）
- **C. 飞书群机器人 webhook**（最轻——只要"结果发群里看"时）: HTTP POST 到群机器人 webhook——免费——但只能发消息不能读/写多维表格
- **D. Telegram Bot 接收**（✅ 2026-08-15 用户实测选定——测试期最省事）: make 原生 Telegram Bot 连接器（Verified 官方——免费——授权即用不手搓）——AI 生成结果发到自己的 Telegram（手机看）——**测试期验证"Webhook→AI→发送"链路用这个最合适**，跑通后交付时再定最终存储（飞书/Sheets）

**本轮场景1提示词配置表链路（2026-08-21最终确认）**：HTTP 25=获取 tenant_access_token；HTTP 28=调用 wiki get_node，拿提示词配置表的 bitable obj_token；HTTP 29=读取 records；HTTP 30=处理 records 分页。四个 HTTP 都是必要模块，不得误判为重复或删除。整体仍是串行 bundle 流：Webhook 22 → HTTP 25 → HTTP 28 → HTTP 29 → HTTP 30 → Iterator/筛选场景1 → DS 7 → 原有后续链路。

**Working rule for Make tasks: authoritative-source first.** Before operating or diagnosing a Make/Feishu workflow, read the user's current project note or handoff document in full; do not reconstruct module numbers, scenario-to-table mappings, credentials, or prior decisions from memory. Treat the latest user-provided source as the SSOT and keep Scenario 1/Scenario 2 state separate. When a Feishu/wiki URL is supplied, resolve the wiki node to `data.node.obj_token` before calling Bitable APIs. Reuse the exact Feishu app identity previously proven for the workflow; an HTTP 99991672 permission error may mean the wrong App ID was used, not that permissions were removed. Never print or write App Secrets/API keys; verify credentials only with redacted presence/status checks. Before changing Make, report the current scenario, target table, module chain, and the single next operation; do not mix scenarios or redesign a previously settled flow.

**Prompt configuration table workflow (verified 2026-08-21):** For a `提示词配置表` wiki bitable, do not call Bitable tables/records APIs with the wiki token directly. In the active scenario, add the steps serially before the existing DeepSeek module: (1) HTTP POST `/auth/v3/tenant_access_token/internal` using the previously proven Feishu app; (2) HTTP GET `/wiki/v2/spaces/get_node?token=<wiki_token>` with `Authorization: Bearer` plus the token from step 1; (3) only after step 2 returns `data.node.obj_token` and `obj_type=bitable`, add the Bitable table/record read step and filter the `场景` record. Validate each step with Run once before adding the next. Keep existing downstream modules unchanged until the read path is proven. The verified wiki response shape is `data.node.obj_token` (not `data.obj_token`). Use the actual module numbers from the current canvas, not remembered numbers; never configure both scenarios in one operation. The correct historical Feishu app identity for this workflow is the one documented in the handoff note; do not substitute the Hermes gateway's separate Feishu app identity.

用户选定方案 B 思路（姐夫用飞书多维表格做数据管理中枢——输入+管理都在飞书），开始手搓。**前提**：用户本人就是飞书重度用户（就在飞书里跟助手对话）——**不需要问"有没有飞书账号"**（问了会被骂废话）。

**飞书侧（一次性配置——open.feishu.cn）**：
1. open.feishu.cn 登录（个人飞书账号即可）→ 创建企业自建应用（填名字+描述，图标可跳过）
2. 应用后台 → 凭证与基础信息 → 拿 **App ID + App Secret**（手搓 HTTP 用）
3. 权限管理 → 搜 "bitable" → 开通两个权限（都显示"免审权限"绿色标签——不用审核——快）：
   - `bitable:app`（查看、评论、编辑和管理多维表格——**写场景必须**——readonly 不够）
   - `bitable:app:readonly`（只读——读场景用）
4. 版本管理与发布 → 创建版本（如 1.0.0）→ 提交发布（**权限变更后要重新发布新版本才生效**）
5. 飞书客户端 → 云文档 → 新建多维表格（Bitable）→ 建数据表（字段对应场景输出——如选题库: 选题类型/视频标题/核心角度/流量潜力/状态）→ 复制表格链接（URL 里有 app token——API 要用）
   - ⚠️ 用户可能不会玩多维表格——给保姆级步骤（新建→改表名→加字段→选类型→分享→复制链接），或先用默认表验证 API 通不通再精调字段

**make 侧（2026-08-16 已在 VPS 用 curl 全程验证——命令模板见 `references/feishu-bitable-api.md`）**：
1. **拿 token**：`POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal`（Body: app_id+app_secret）→ `tenant_access_token`（2 小时有效——每次调用前重新取）
2. **wiki 链接转 base token**：用户给的表格链接若是 `wiki/<wiki_token>` 格式（知识库里建的表格），先 `GET https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token=<wiki_token>`（Bearer token）→ 返回 `obj_token`（= base 的 app_token）+ `obj_type: bitable`。**此接口需要 `wiki:node:read` 权限**——没开报 99991672 Access denied（补开权限后即可，无需重新发布——2026-08-16 实测权限变更即时生效）
3. **读表格列表**：`GET https://open.feishu.cn/open-apis/bitable/v1/apps/<app_token>/tables` → 拿 table_id
4. **写记录**：`POST https://open.feishu.cn/open-apis/bitable/v1/apps/<app_token>/tables/<table_id>/records`（Body: `{"fields":{"字段名":"值"}}`）

**⚠️ Wiki 多维表格权限排查实测（2026-08-21）**：用户提供 `my.feishu.cn/wiki/<wiki_token>` 链接时，先调用 `GET /open-apis/wiki/v2/spaces/get_node?token=<wiki_token>`。正确响应结构是 `data.node.obj_token`、`data.node.obj_type`、`data.node.title`，不是 `data.obj_token`。拿到 `obj_type=bitable` 和 `obj_token` 后，再调用 `/bitable/v1/apps/<obj_token>/tables`。若返回 `99991672 Access denied`，说明自建应用身份尚未开通 `bitable:app:readonly`、`bitable:app` 或 `base:table:read`。后续需要写入时优先开 `bitable:app`，并创建/更新并发布应用版本；同时将应用加入该多维表格的协作者，至少给可编辑/可管理权限，否则可能读通写不通或返回 91403。排查顺序固定为：tenant_access_token → wiki node → tables → fields → records。权限未通过前，不改 Make 场景。

**⚠️ HTTP 模块 Authorization 头必须带 "Bearer " 前缀（2026-08-16 实踩——99991661）**：make 的 HTTP 模块（Make a request）调飞书写记录接口时，Headers 加 `Authorization`，Value 必须 = **`Bearer `（含空格）+ 点选 token**（如 `Bearer {{10.data.tenant_access_token}}`）。只点选 token 不加 Bearer 前缀 → 飞书报 `{"code":99991661,"msg":"Missing access token for authorization"}`。Authentication type 保持 No authentication（用 Header 手动带 token 是正确方式）。判断引用是否正确：点开模块 A 输出展开 Data 确认 token 实际路径（飞书 tenant_access_token 就在顶层 data 里——`data.tenant_access_token` 路径对——模块号以场景实际编号为准）。

**⚠️ 单测下游模块 = 上游引用全空（2026-08-16 实踩）**：右键 "Run this module" 单独跑下游模块（如写飞书的 HTTP-B）时——它引用的上游输出（模块 A 的 token）**不在本次运行里**——报"缺 token/值空"≠ 配置错。正确验证顺序：①先单独 Run 上游模块 A（拿 token）②再 Run 下游 B（引用有值）；或直接 Run once 从 Webhook 完整链路跑（Run once 总是从场景第一个模块开始）。同理配 Telegram Text 映射时点选不到 DS 输出结构 = DS 还没跑过（没输出样本就没有结构可点选）——先让 DS 跑一次再点选。

**本次场景1新增确认（2026-08-21）**：读取飞书提示词配置表的链路包含 Webhook → HTTP 25（tenant token）→ HTTP 28（wiki get_node）。HTTP 28 的 Authorization 映射即使配置正确，单独运行 HTTP 28 仍会因 HTTP 25 没有在同一轮执行而拿不到 token；必须点击底部 **Run once**，从 Webhook 22 开始跑完整链路，才能让 HTTP 25 先执行并把 token 传给 HTTP 28。后续读取表格 records、映射提示词到 DS 也沿用这一原则：不要用单独 Run 下游模块判断链路配置是否正确。

**写死 Body vs 动态需求（2026-08-16 用户问——诚实回答原则）**：DS Body 写死示例数据 = **测试期方便的设计，不是需求**。姐夫真实需求是【动态输入】：场景1 Webhook 收《市场机会简报》→ DS 分析；场景2 Webhook 收 4 变量；场景3 定时读表格；场景4 Webhook 收 CSV。**写死=验证链路+提示词效果；交付必须是动态引用（Webhook 变量/表格数据）**。被问到时如实说明，别把测试设计说成需求。

**连接创建坑（2026-08-15 实踩）**：点 Create a connection 后可能"没跳转"（一直转圈 "Creating a connection..."）——**是浏览器弹窗拦截**（make 要弹授权窗口）——看地址栏弹窗拦截图标 → 允许 make.com 弹窗 → 重试 → 授权页（open.feishu.cn）在新标签打开。

## Telegram Bot 接入（2026-08-15 实测——测试期接收端最优）

**用途**：make 原生 Telegram Bot 连接器（Verified 官方——免费——授权即用）——AI 生成结果发到自己的 Telegram——测试期验证链路用（不用飞书/Sheets/HTTP 手搓）。用户有现成 bot（"找书机器人"）直接用 token。

**Bot Token 获取**：Telegram 搜 @BotFather → /newbot → 起名 → 拿 token（`123456789:AAH...` 格式）——已有 bot 找回：@BotFather → /mybots → 点 bot → API Token。

**make 连接步骤**：
1. 场景 "+" → 搜 "Telegram" → 选 "Telegram Bot"（绿色纸飞机图标，Verified）→ 选模块 "Send a Text Message or a Reply"
2. Create a connection → 填 Bot Token → Save（连接名显示 bot 名即成功）
3. 配置字段：
   - **Chat ID**（必填）——⚠️ 不是 bot token！是【你和 bot 的对话 ID】。获取：①Telegram 里先给 bot 发条消息（"hi"——**bot 隐私模式只回主动找过它的人**，没发过消息 make 发不出去）②浏览器开 `https://api.telegram.org/bot<TOKEN>/getUpdates` ③返回 JSON 找 `"chat":{"id": 数字}` —— 数字就是 Chat ID
   - **Text**（必填）：要发的消息内容（测试先填"测试消息"，正式场景映射 DS 输出 `body.choices[0].message.content`）
   - Parse Mode：可选（Markdown/HTML——要加粗/链接时用）

**⚠️ 坑**：getUpdates 返回 404 = token 复制错了（长串大小写易错——手打必串，复制粘贴）；返回 `{"ok":true,"result":[]}` = bot 没收到消息（先去 TG 给 bot 发一条再刷新）。
**⚠️ Chat ID 必须数字——不接受 @用户名**：填 `@PMLophy` 报错 "Telegram couldn't find the chat in the Chat ID field. Use a real chat ID, not @PMLophy"。拿数字 ID：Telegram 里给 **@userinfobot（认准蓝色✓验证徽章官方版——搜出来一堆仿冒：@userinfobot3bot/@userinfobot_subot 等都是假的）** 发消息 → 返回 "Your user ID: 数字" → 填 make。
**⚠️ bot 已有 webhook 时 getUpdates 报 409**（"can't use getUpdates while webhook is active"——如找书机器人在用 webhook）——但 **make 发消息走 sendMessage API 不受 webhook 影响，不用删 webhook 直接绕过**。
**⚠️ bot 隐私模式**：bot 只能回复主动找过它的人——测试前先在 TG 给 bot 发条消息激活对话，否则发不出去。

## 新媒体运营自动化（姐夫场景——2026-08 评估）
目标：视频号商业 IP（中小微企业获客）全流程自动化。10 节点流程：选题生成→脚本初稿→录制→后期→发布→数字人批量→矩阵分发→投放监控→评论运营→数据复盘。

**评估结论**：
- ✅ make 擅长（AI 生成类）：选题分析/脚本初稿/数据复盘（Claude/GPT 原生模块 + 飞书存储）
- ⚠️ 半自动（要人/国内工具）：数据抓取（新榜/友望手动导出 CSV→Webhook 上传——绕开 API 门槛，聪明）、发布（视频号原生后台）
- ❌ 难做（国内平台无官方连接器）：视频号/抖音/小红书/剪映/蚁小二——make 是海外平台，国内平台官方连接器基本没有；视频号 API 要企业认证+类目审核（个人拿不到）
- 💰 成本叠加：新榜/友望 300-800/月 + AI key + Make 付费 + HeyGen（数字人）+ 蚁小二（矩阵）——MVP 可能 1000-2000/月
- **MVP 建议**：只做 1-2+10 节点（选题/脚本/数据复盘——AI 生成类）——验证 AI 内容质量值不值再上数字人/矩阵/投放

## 场景配置实战坑（2026-08-15 搭 Webhook→DeepSeek→Telegram 全链路实测）

**1. Webhook 触发后"一直转圈"是正常的**：Webhook 是触发模块——Run once 时它在等外部请求，转圈=在等数据不是卡死。触发方法：浏览器新标签打开 Webhook URL（GET 即触发）→ 流程往下走；或 curl POST 带数据（`curl -X POST <url> -H "Content-Type: application/json" -d '{"data":"..."}'`）。
**1.5. curl 触发报 "There is no scenario listening for this webhook" = 场景【没激活】**：Webhook URL 建了但场景没激活（Activate scenario）时，外部 curl/浏览器触发会收到这个报错。**激活入口**：右上角 "..."（三点菜单）里找 Activate scenario，或退回场景列表页点该场景的开关（变绿/On=激活）。⚠️ 底部那个 "Immediately as data arrives" 开关不是场景激活——它只是运行模式（数据一到就跑）。**测试阶段可不激活**：直接用底部紫色 Run once 按钮测（DS Body 写死数据时不依赖 webhook 输入，Run once 就能跑通全链）；激活后场景常驻会消耗操作额度（免费版 1000 次/月），测试完可 Deactivate。

**2. DeepSeek Body 必须是【单行合法 JSON】**：多行粘贴/中文引号/格式破坏 → make 把 Body 当字符串而不是 JSON 对象 → 报 `400 Failed to deserialize the JSON body: invalid type: string "...", expected struct ChatCompletionRequest`。修法：整段单行粘贴、英文双引号、无多余换行。Body 里引用 Webhook 数据用 `{{1.webhook.data}}` 类映射——**若报 \"references non-existing module [ID]\"** 说明模块 ID 写错（手打容易错——用点选面板展开模块选字段，别手打引用）。

**3. Telegram Text 字段【必须映射 DS 输出】不是写死文字**：Text 填"测试消息"就会一直发测试消息（用户实测踩坑）。正式配置：点 Text 字段 → 输入 `/` 或点下拉 → 展开 DeepSeek AI 模块 → Body → choices → message → content（**make 自动填 `{{7.body.choices.message.content}}`——⚠️ 不带 `[0]`，make 的点选系统自动处理数组**；数字 7 是该模块的场景 ID，以实际为准）。判断 DS 是否真的返回了：看该模块运行日志右侧 Status code 200 + Body 里有 choices[] 数组（回复就在 choices[0].message.content）。

**3.4. ⚠️⚠️ 数组映射【禁止手动加 [0]】——2026-08-15 用户拍板（全场最贵的坑，原地打转 2 小时的根因）**：make 点选生成的引用是 `7.body.choices.message.content`（**没有 `[0]`**）——make 的字段选择器自动处理数组，手动改成 `choices[0].message.content` 反而引用错 → 运行时值为空 → Telegram 报 `The mapped value from module 7 was empty`。**铁律：Text 字段的映射一律用 make 的点选面板自动生成（点选 DeepSeek → Body → choices → message → content），绝不手打/手改引用语法**。用户原话："这个位置不需要加【0】"——加 [0] 是错的，去掉后立刻通（"通了啊，我 TG 收到了选题了"）。同理 `{{1.webhook.data}}` 类引用也别手打（模块 ID 手打必错——报 "references non-existing module [ID]"），一律点选。**2026-08-16 用户再次纠正："不需要带「0」，我们之前实验过的，不要再提这个了"——[0] 这个话题已封板，任何时候不要再建议/讨论加 [0]，直接给不带 [0] 的点选方案。**
**⚠️ 封板适用边界（2026-08-16 澄清——别过度泛化）**：封板只针对【TG Text 字段的映射】（点选自动处理数组）。**Parse JSON 的 json 字段是例外**——make 官方 Possible fixes 明确提示 "Use a fixed item path instead of choices[] if needed"，即用 `choices[0]` 取单个 JSON 字符串。两种场景：TG Text = 点选无 [0]；Parse JSON json = 官方建议 choices[0]（escapeJSON 包裹）。下轮别再一刀切说"所有地方不加 [0]"——按场景区分（详见 Parse JSON 排查记录）。

**3.5. Telegram 单条消息上限 4096 字符（2026-08-15 实踩）**：DS 输出全文超过 4096 → 报 `Sent too much text in Telegram: SendReplyMessage... The Text field passed the full DeepSeek output, and Telegram rejected it`。修法（按优先级）：①**提示词限长度最干净**——DS 的 system 提示词末尾加"输出必须精简紧凑，总长度控制在2500字以内，每个标题不超过20字"（Telegram 消息有长度限制）→ DS 生成时就短；②改输出格式更紧凑（每行一个选题：序号.标题，不要核心角度/流量潜力列）；③make 里截断 `{{7.body.choices[0].message.content.slice(0,3000)}}`——会截断不完整，不推荐。

**3.6. Text 映射停在【数组层】会报 empty/too long**：映射时点到了 `{{7.body.choices}}`（整个 choices 数组）而不是 content——报 `The mapped Text field used {{7.body.choices}}, and the result was too long for Telegram`（数组是对象不是文本）或 `The required text field was empty after mapping`。**必须点选到最深层 content**：choices → message → content（⚠️ 无 `[0]`——见 3.4，make 自动处理数组；显示为两个蓝色标签 `7.Body.choices` + `message.content` 即正确形态）。对照右侧模块输出面板（DeepSeek 运行日志展开 Body 看 choices[0].message.content 的实际值）就是导航图。判断映射是否正确：Text 字段里是**蓝色标签（引用）**而非纯文本——引用错了会显示红色/警告或运行时报 empty。

**4. 验证链路三段式**：①Webhook 单独触发（绿✓）②DeepSeek 单独看返回（200 + choices 有内容）③Telegram 收到【映射后的内容】——三者都过才算场景通。只看到"测试消息"= Text 没映射；只看到模块绿= 连接配置对但没验证数据流。
1. 确认范围（MVP 场景清单：选题建议/脚本初稿/每周数据报告）
2. 定 AI 通道（原生模块哪个/DeepSeek 走第三方应用——见矩阵——**DeepSeek 有 by Synergetic 应用，直接建连接填 DS key 即可，不用 HTTP/OpenRouter**）
3. 定存储：⚠️ 飞书无官方免费连接（见上）——**测试期首选 Telegram Bot 接收**（make 原生免费，AI 结果发自己 TG 手机看——验证链路最省事）；跑通后交付时再定最终存储（飞书 API/Sheets/群机器人）
4. make 上逐个配场景（Webhook 触发 → DeepSeek 生成 → Telegram 发送），Run once 验证数据传递
5. 交付：跑通后转交姐夫自管（他自己的 key 他自己的钱）

**边跑边沉淀（用户工作方式 2026-08-15）**：用户偏好"先跑通整体，边跑边沉淀，最后自成完整笔记"——每步配置/坑/技巧同步写进 notes-vault（学习/盒子的搭建笔记），交付时即成完整手册。别等最后一次性补笔记。

**自查纪律（2026-08-15 用户强调）**：遇到"某连接器好像不行/要付费"——先系统性自查（换关键词搜——如 Bitable/Feishu/Lark、看开发者是谁、看 Most popular 列表有没有、确认是否官方免费）——确认没有才定替代方案，别急着下"做不了"结论或急着付钱。

**交付方式（2026-08-15 用户定——方案 A）**：make 的连接（Connection）与场景（Scenario）分离——**换飞书 = 场景里新建连接让姐夫扫码授权 → 飞书模块切换连接**（5 分钟，不用重建场景）；姐夫没有自己 make 账号时用此方案。若姐夫有自己的 make 账号 → 方案 B：场景导出/克隆给他，他独立授权。

**交付范围（2026-08-16 用户定）**：最终交付 = **4 个场景全通**（选题/脚本/周报/分析）——但按序做，不是同时交付：**先 1+2（内容生产闭环——选题+脚本）跑通交付让姐夫能用起来 → 再 3+4（数据分析——周报+市场分析）迭代补**。交付前每个场景都要真实数据验证过（用户验收原则：亲测才算数）。

**费用归属（2026-08-15 用户定）**：帮别人搭（如姐夫）测试期费用用户先垫——但 AI key 用谁的要说清：**姐夫自己注册 key 自己花钱**（用户不掏自己的 Go 通道给姐夫用——除非自愿赞助）。测试期省钱：DS Flash（便宜）+ Make 免费版 1000 次/月——月成本接近 0。

## 场景2：脚本初稿生成（2026-08-16 已跑通——飞书写入《脚本库》全链路）

**已跑通验证（两版）**：
- TG 版：Webhook → DS（脚本提示词）→ TG——TG 收到完整口播脚本——黄金钩子（"投5万只换1个咨询？你的广告费正在被平台吃掉。"）/痛点拆解（80%老板给平台打工）/解法交付（三层次：买"问题"不买流量·用"文案"不用"广告"·让客户说"这就是我"）/行动指令（"评论区扣'获客'或私信我"）——四段式完整、商业语言无黑话、有数据感、促行动——文档标准 100% 落地。
- **飞书版（最终形态）**：Webhook → DS（脚本提示词）→ **Create JSON（构建 Body——自动转义换行）→ HTTP-A（拿 token）→ HTTP-B（写飞书《脚本库》）**——飞书表格出现真实脚本记录（选题类型=成本计算类 + 脚本全文=DS 生成的四段式口播脚本）——**脚本自动入库飞书全链路通**。关键：多行文本进 JSON Body 必须走 Create JSON 模块（详见下方"多行文本进 JSON Body 的坑"），HTTP-B 的 Body 字段【点选引用 Create JSON 输出】不手打。

配 TG 的 Text 字段时若点选不到 DS 输出结构（choices.message.content）——先 Run once 让 DS 跑一次，有输出样本后才能点选映射（make 机制：没跑过就没有结构可点）。

**文档标准（《脚本初稿生成.txt》）**：
- **独立场景**（不是多选批量）——Webhook 手动输入【单个选题的 4 个输入变量】→ DS 生成 1 个脚本 → 输出
- 模块链：Webhook（接收 选题类型/核心主题/关键信息/目标行动）→ AI（System Prompt=口播脚本生成提示词 V1.1 / User Prompt=合并 Webhook 变量）→ 输出（文档写飞书文档《脚本库》——测试期用 TG 替代）
- 用户决策：先写死测试（变量值写死在 Body——跑通链路）→ 后期迭代成"可输入可配置"（Webhook 引用 4 变量——点选映射——见坑 3.4）

**《脚本提示词》结构（文档原文——四段式爆款模板）**：
```
角色设定: 资深商业IP口播脚本撰写专家（服务"中小微企业线上获客专家"）
写作信条: ①只讲老板能听懂的商业语言（拒绝黑话）②每个观点必须有数据/案例支撑（无废话）③终极目的=让"张总"产生"这人能帮我解决获客问题"并行动
输入变量: 选题类型[成本计算类/平台真相类/案例拆解类/避坑指南类] + 核心主题 + 关键信息 + 目标行动[引导评论/私信/看主页]
输出格式: 1.黄金钩子(15-25字一句话) 2.痛点拆解(50-80字) 3.解法交付(150-200字分3点) 4.行动指令(20-30字)
自我检查: ①钩子能让刷到的老板停吗 ②有"正确的废话"吗删掉 ③张总知道下一步做什么吗
⚠️ 占位符: [此处嵌入《IP人设说明书》+《口播语言风格卡》]——姐夫还没给——测试期先去掉占位符
⚠️ TG 适配: 加"输出总长≤2000字，只输出脚本正文"（TG 4096 上限）
```

**交付兜底（2026-08-16 用户定）**：飞书 API 手搓失败 → **给姐夫一个 Telegram 账号让他自己玩**（TG bot 超好弄：@BotFather → /newbot → token → make 建连接 → @userinfobot 拿 chat id——全程 <10 分钟，非技术用户自己都能搞定）。⚠️ 交付时给姐夫【新 bot】——不能把用户自己的"找书机器人"长期给姐夫（数据混一起）。

## 场景3/4 文档标准（2026-08-16 从 zip 读到——待搭建）

**场景3：每周数据报告生成**（文档《每周数据报告生成.txt》）：
- 触发：**定时**（Schedule - Set schedule——每周日晚8点）
- 模块链：Schedule → 飞书多维表格 Search records（读《视频数据周报》本周记录）→ AI 复盘（System Prompt=数据复盘报告生成提示词 / User Prompt=合并表格数据）→ 飞书文档 Create a document（写《每周复盘》）
- ⚠️ 测试期没有飞书表格读——数据源未定：方案A 写死示例数据（验证复盘生成）方案B Webhook 手动传数据（真实但麻烦）——**定时等数据源定了再加**（先 Webhook 验证复盘能力）

**场景4：市场分析报告生成**（文档《市场分析报告生成.txt》）：
- 触发：Webhook（**手动上传 CSV/TXT 文件**）
- 模块链：Webhook（接收 CSV/TXT）→ AI 分析（System Prompt=市场分析报告生成提示词 / User Prompt=合并文件内容）→ 飞书多维表格 Create a record（写《每周市场分析》）
- 数据来源（《市场调研AI助手操作卡》）：新榜/友望数据（视频号数据分析平台，月费¥300-800）→ 近90天 → 按点赞降序 → **导出前20条 CSV**（标题/发布时间/播放量/点赞/评论/转发/时长——文件名 `日期_账号名_数据.csv`）→ 评论区前10条高赞评论手动记 TXT → 一起上传 Webhook
- ⚠️ 文档里用 Claude——我们用 DS（便宜）——提示词照文档的

**场景触发频率提醒**：场景3 定时每周跑1次 + 场景4 手动按需——免费版 1000 次/月完全够。

**飞书 vs TG 定位（2026-08-16 用户问——本质区别）**：飞书=**数据管理中枢**（多维表格结构化/团队协作/境内合规/不翻墙）；TG=**通知通道**（聊天式消息流/单机看结果/境外访问需翻墙/数据出境）。测试期 TG 够（验证 AI 生成质量+链路）；姐夫正式用推荐飞书（数据要"管"起来——手搓 API 值得）；飞书真搞不定 → TG 兜底。

**make 分类定位（2026-08-16 用户问——workflow 型 vs 插拔型）**：make = **Workflow 型**（流程编排——场景=预定义流水线——模块按顺序串联——数据左到右流——决策靠路由器/过滤器/迭代器）；对比 DSH（DeepSeek Harness）= **插拔型**（一切皆插件——核心+插件自由组合）。make 适合流程确定的自动化（选题→生成→发送固定链路）；流程变了要改场景（改逻辑=改编排）。

## DS 批量输出 → 飞书表格逐条写入（2026-08-16 场景2 已完成；场景1 进行中）

**需求**：AI 生成 15 个选题 → 飞书《每周选题库》写 15 条记录（不是一条整段）。

**⚠️ 一条 vs 十五条（用户问过——为什么场景2 不用迭代器）**：场景2（脚本）DS 输出【1 条】→ Create JSON 包一条直接写（不用 Parse JSON/迭代器）；场景1（选题）DS 输出【15 条】→ 必须 Parse JSON（JSON 字符串→数组）+ 迭代器（数组→15 条逐条写，姐夫才能在表格里逐行勾选）。迭代器 = 拆快递（把 15 条拆成 15 个独立记录）。别把两个场景的结构搞混——这决定了模块链复杂度。

**⚠️ Parse JSON 报错 \"json field uses 7.content, but that value is empty\" 的根因 = DS 输出不是 JSON（2026-08-16 实踩）**：不是引用路径错——是 DS 还在用【文本格式 Body】输出（`1|成本计算类|...`）。修法：①确认 DS Body 是 JSON 输出版（system 提示词含\"以JSON数组格式输出\"）②**右键 DS → Run this module 重新生成**——DS 模块面板可能显示旧 Body 的文本输出（旧运行缓存——Body 改 JSON 版后面板仍显示上次文本版结果，看起来像\"没生效\"）——重新 Run 后 content 才变成 `[{"type":...}]` 数组。验证标准：content 以 `[{"type":` 开头。③再 Run Parse JSON → 成功解析成数组。

**⚠️ 迭代器选不到 Parse JSON 的数组 = Parse JSON 还没跑过**（同上机制——没输出样本就没结构可点选）。顺序：先 Run DS(7)（生成 JSON）→ Run Parse JSON(15)（解析出数组）→ 配迭代器(17)（Array 输入 + Map 开关打开 = 输入数组，点选 15 的输出）→ 下游才能引用。Run this module 会弹 Mappings 确认框（引用路径显示 + OK 按钮）——点 OK 即运行。

**⚠️ 场景↔通道映射（用户纠正——别记混）**：场景1（选题生成）= TG 收 15 选题（已跑通）；场景2（脚本生成）= TG 收脚本（已跑通）。飞书写入是【两个场景后续各自加】：场景1 → 《每周选题库》表格（15条），场景2 → 《脚本库》表格（1条整段）。用户原话纠正："场景 1 是用的电报，不是飞书"——改飞书前先确认当前在哪个场景、目标哪个表，别把场景 1/2 的通道搞反。

**标准模式（make 处理"AI 生成 N 项 → 表格 N 行"的通用套路）**：
1. **DS Body 提示词要求 JSON 数组输出**（关键：改 system 提示词，不是 user）——在 system 末尾加：
   `输出要求：以JSON数组格式输出15个选题对象，不要输出任何其他文字、代码块标记或解释，严格按此格式：[{"type":"选题类型","title":"视频标题","angle":"核心角度","potential":"高/中/低"},...] 共15个对象。`
   - ⚠️ 提示词里的 JSON 示例必须用【英文双引号】（值里中文没问题）
   - 验证：Run once 后 content 应以 `[{"type":` 开头、纯 JSON 无杂质（有 reasoning_content/多余文字会解析失败——加"只输出JSON"强化）
   - ⚠️ **Body 改 JSON 版后模块面板可能仍显示旧文本输出**（如 `1|成本计算类|...`——那是上次运行的缓存）——不是没生效，**必须右键 Run this module 重新生成**，content 才会变成 JSON 数组。Parse JSON 报 "json field empty" 时先查这个：DS 到底输出的是 JSON 还是旧文本。
2. **加 Parse JSON 模块**：DS 模块右侧 "＋" 拉新支路（保留 TG 那条不动）→ 搜 "JSON" → Built-in → Transformers → **"Parse JSON"**（输入 = DS 输出的 choices.message.content，点选映射）→ 输出 15 个对象的数组
   - ⚠️ **弹出的 "Add data structure" 弹窗可直接关掉跳过**——make 原话："If you don't create a data structure, Make will try to infer the structure from the data during the manual run"（不建结构会在 Run once 时自动推断）。关弹窗 → 确认 JSON string 输入是 DS 输出引用 → Save。
3. **加迭代器（可能不需要！）**：Parse JSON 后面加 "Iterator"（Flow Control 类）→ 输入 = JSON 解析的数组 → 输出每条（type/title/angle/potential 单独字段）
   - ⚠️ **✅ 官方文档 + 最终实证：Parse JSON 解析数组自带输出多个 bundle——迭代器通常【多余】**（官方 apps.make.com/json 原文 "Parse JSON modules give the output in multiple bundles"；本会话场景1 最终【没加迭代器】也写入了多条记录）。**优先路线：Parse JSON（多条输出）→ Create JSON（每条构建）→ HTTP-B（逐条写）——不插迭代器**。只有 Parse JSON 输出确实没拆开时再加迭代器。\n   - ⚠️ **从旧场景复制/克隆的 Create JSON 会带旧数据结构**（实踩：场景2 的 Create JSON 克隆到场景1，数据结构还是"选题类型+脚本全文"——场景1 要"选题类型/视频标题/核心角度/流量潜力"）。加模块后先检查/改数据结构字段匹配目标表，值全部点选迭代器输出（type/title/angle/potential——不是写死）。\n4. **HTTP-B 写飞书**：迭代器后面接 HTTP-B（拿 token 的 HTTP-A 在迭代器前）→ Body 字段映射迭代器字段：`type→选题类型 / title→视频标题 / angle→核心角度 / potential→流量潜力` → 迭代器让 HTTP-B 自动跑 15 次（每次写一条）
- 分支结构：DS 后面可以同时接 TG（发通知给人看）和 JSON 解析（写飞书管数据）——两条支路并行，互不影响
- 简化版：若只需整段写一条（如场景2 脚本），不用 Parse JSON/迭代器——HTTP-B Body 直接映射 choices.message.content 放一个字段即可

**⚠️ 场景1 卡 Webhook 的最终解法（2026-08-16 会话末定——"断开连接测试"已证伪，见协作纪律）**：Run once 永远从 Webhook 开始（等数据转圈）——断开连接不改变起点。正确做法按优先级：①**删除 Webhook 模块**（右键 Delete——让 DS 变第一模块）→ Run once 直接从 DS 跑（写死 Body 生成 JSON）→ 完整链路可验证；测通后再加回 Webhook + 激活场景 + curl 触发正式用。②激活场景（场景列表开关）后 curl POST 触发。③"Detect new values" 按钮配合发请求（webhook 面板内）。

**✅ 场景1 全链已通（2026-08-16 会话末最终突破——多条写入成功）**：结构 `Webhook(22) → DS(7 JSON选题输出) → HTTP-A(20 拿token) → Parse JSON(24 拆数组) → Create JSON(16 构建Body) → HTTP-B(21 写《每周选题库》)`——**完整链路 curl 触发后飞书表格出现【多条记录】（第 9-18 行）——数组拆分生效了！** 但**每条内容一样**（写死值"成本计算类/企业培训获客成本怎么算"）——因为 **Create JSON(16) 的 4 个字段值还是【写死】**——没映射 Parse JSON 输出的 type/title/angle/potential。**最后一步（待做）**：打开 Create JSON(16) → 4 个字段值分别【点选】Parse JSON(24) 输出的 type/title/angle/potential（不写死）→ Save → curl 触发 → 飞书应出现 15 条【不同】选题。**验证信号**：表格出现多条【相同】内容 = 拆分通了只差字段映射；多条【不同】内容 = 全链完成。**排查过程回顾**：json 字段引用先后踩了 `7.content`（选错层——停在 DS 顶层，无 body 前缀）→ `choices[]`（停在数组层）→ 最终点选生成（不加 [0]）配合完整链路 curl 触发成功——真根因是【单独 Run 不带上游 + Webhook 未触发 DS 没跑】而非引用语法。

**✅✅ 场景1 100% 完成（2026-08-16 会话末用户截图确认）**：Create JSON(16) 的 4 个字段值改为【点选映射 Parse JSON(24) 的 type/title/angle/potential】后，完整链路 curl 触发 → 飞书《每周选题库》第 6-20 行 = **15 条【完全不同】的选题**（成本计算类×5/平台真相类×4/案例拆解类×4/避坑指南类×2——四类全覆盖、每条不同标题/角度/潜力）——**场景1 全自动闭环：触发 → DS 生成 → 数组拆分 → 逐条写入**。验证信号坐实：多条【不同】内容 = 全链完成。至此场景1（选题15条拆分写入）+ 场景2（脚本整段写入）两大内容生产场景全部跑通，可以交付。

**⚠️ 迭代器位置查证（2026-08-16 用户要求"不是我觉得，是要查证这样可行"——查官方社区后定稿）**：make 模块链机制 = **上游模块输出几个 bundle，下游每个模块就自动跑几次**（官方：API 返回列表 → 下游逐条处理）。推论：**拿 token 的 HTTP-A 必须放在【数组展开之前】**（DS 后面、Parse JSON 前面）——DS 输出 1 个 bundle → HTTP-A 只跑 1 次；若 HTTP-A 在 Parse JSON/迭代器【后面】，它会跟着 15 条 bundle 跑 15 次（15 次 token 请求——浪费）。**正确顺序：Webhook → DS → HTTP-A(拿token 1次) → Parse JSON(拆15条) → 迭代器(逐条) → Create JSON(每条构建) → HTTP-B(写15次)**。另注意：官方文档说 Parse JSON 解析数组本身输出多个 bundle（自带拆）——迭代器可能冗余，官方路线是 Parse JSON 多条输出直接连 Create JSON；两条路都验证过可行的话优先官方（少一个模块）。

**⚠️ 删触发模块后场景报 "not connected to the flow"（2026-08-16 实踩——删 Webhook 的副作用）**：删掉 Webhook 后 Run once 不卡了，但 DS 模块报橙色警告 "This module is not connected to the flow. This module and everything after it will be skipped during execution"——**场景必须有触发模块**，删掉触发模块后第一个动作模块"没连进流程"（没有入口线），整条链被跳过（DS 不跑 → HTTP-A 没拿 token → HTTP-B 报缺 token）。所以"删 Webhook 测试"只对了一半：能跑但 DS 可能被跳过。**更稳的测试路径：保留 Webhook + 激活场景（流程无错时能激活）+ curl POST 带数据触发**；或 Webhook 面板 "Detect new data" + 浏览器/curl 发请求。删触发模块是最后手段且要知道可能整链被跳过。

**⚠️⚠️ 99992402 "fields is required" 根因 = Create JSON 数据结构缺 fields 包裹层（2026-08-16 实踩——场景1 全链绿了只剩这步）**：飞书写记录 Body 必须是 `{"fields":{"字段名":"值"}}`。用 Create JSON 模块构建时，**数据结构根必须是 `fields`（Type 选 Collection/对象）**，4 个字段（选题类型/视频标题/核心角度/流量潜力）作为**子项嵌在 fields 里面**（缩进在 fields 下）。若字段平铺在根（输出 `{"核心角度":"算清账才不白投",...}` 无 fields）→ 飞书报 `99992402 field validation failed - "fields" is required`。**另一个坑：子字段 Type 误设成 Collection**——如"选题类型"选成 Collection 且嵌套了同名 Text 子项 → 输出 `{"fields":{"选题类型":{"选题类型":"成本计算类"}}}`（对象嵌套——飞书也不认）。**子字段一律 Text**，值直接填 Default value。修复：删掉 4 个平铺字段 → + Add item 加 fields（Type=Collection）→ 在 fields 里面 + Add item 加 4 个子项（Type=Text）→ Save。验证：右键 Run Create JSON 看输出以 `{"fields":{` 开头。

**写死 Body 隔离测试法（2026-08-16 实战——先证 B 再修 16）**：HTTP-B 反复报错时，把 Body 从"引用 Create JSON 输出"临时改成【写死 JSON】`{"fields":{"选题类型":"成本计算类",...}}` → Save → Run once → 写入成功 = HTTP-B 本身（URL/token/Headers/Body 格式）全对，问题只在 Create JSON 的数据结构 → 单独修 16 再改回动态引用。分步定位，不纠缠。

**⚠️⚠️ Create JSON 模块的 Data structure 下拉必须【明确重新选中】正确结构（2026-08-16 场景1 全链通的最后一脚）**：数据结构编辑器里 fields 结构改对了（fields Collection → 4 个 Text 平级）、Save 也点了、curl 触发了——但 Create JSON 输出还是旧平铺结构（无 fields）→ 飞书持续报 99992402。**根因：Create JSON 模块的 Data structure 下拉引用的是【旧结构】**——编辑数据结构 ≠ 模块引用刷新。修法：打开 Create JSON 模块 → Data structure 下拉【点开重新选"场景1-JSON-构建Body"】（或选另一个再选回——强制刷新模块引用）→ Save 模块 → 右键 Run 模块看输出以 `{"fields":{` 开头 → 才接 HTTP-B 测。**改数据结构后必须检查模块下拉引用的是不是它**——这是"改了没生效"的隐藏原因。

**make 模块不能改名（2026-08-16 实踩）**：已创建的模块无法 Rename（用户原话"已创建过的无法更名，真坑"）。维护手段：**用模块编号 + 笔记映射表**（编号↔用途，如场景1 的 7=DS选题生成/16=Create JSON/20=HTTP-A拿token/21=HTTP-B写飞书）。注意**跨场景模块编号会重复**（场景1 和场景2 都有 10/11 等）——标注"场景X的N号"才唯一。用户提议的命名规范（场景X-用途）只能用于新模块的数据结构名（如"场景1-JSON-构建Body"可做 Data structure name），模块本身名不可改。

**Schedule 不是独立模块（2026-08-16 用户纠错——"你查文档了吗？确认有这个工具吗？"）**：搜索"Schedule"在模块列表里找不到（只有第三方 Schedule post 等）——因为 **Schedule 是场景工具栏的【调度设置】（Schedule settings——控制触发模块多久跑一次）**，不是可添加的模块（官方 help.make.com/schedule-a-scenario）。别建议"加 Schedule 模块"当触发替代——触发模块只能是 Webhook/定时器等真正的触发类模块，Schedule settings 只是给触发模块配频率。

## ⚠️ Parse JSON 官方文档要点（2026-08-16 查证 apps.make.com/json——用户要求"查官方文档不要猜"）

反复修不好 Parse JSON 时，用户明确要求查官方文档别猜（2026-08-16 原话："查一下资料，官方的，不要猜"）。官方文档关键原文：
- **"Parse JSON modules give the output in multiple bundles"**——Parse JSON 解析【数组 JSON】时输出【多个 bundle】（每条一个）！**这意味着迭代器可能多余**——Parse JSON 自带拆数组。官方推荐模式：Parse JSON（多条输出）→ Create JSON（每条构建）→ HTTP-B（逐条写），中间**不插迭代器**。方向3（去迭代器）是官方路线——本会话结束时仍卡在 json 字段引用，继续排查时优先验证官方路线（去掉迭代器 17，Parse JSON 直接连 Create JSON）。
- "Transform to JSON": "map the Array[] item output from the **Array aggregator** module"——数组处理官方用 Array aggregator（聚合器）。
- "If you don't provide the Data structure, you may manually run the module and Make will build the structure from the provided JSON"——Add data structure 弹窗可跳过（Run once 自动推断）。

**Parse JSON 的 json 字段引用坑（2026-08-16 排查——关键进展记录）**：json 字段引用报错。排查过程（避免下轮重走）：
- ①DS 输出不是 JSON（旧 Body 缓存——右键 Run this module 重新生成，content 应变成 `[{"type":...}]`）——已解决，DS 输出确认是 JSON 数组
- ②报错从"json field is empty"变为"mapping points to escapeJSON(7.body.choices[].message.content), but that result wasn't valid"——**escapeJSON 生效了但 choices[] 返回的是【数组】不是单个字符串**，escapeJSON(数组) 无效。make 官方 Possible fixes 原文："**Use a fixed item path instead of choices[] if needed**"——即用 `choices[0]` 固定路径取第一个元素（⚠️ 注意：这是 Parse JSON 场景，与 TG Text 字段不加 [0] 是两回事——见 3.4 封板说明的适用边界）
- ③按官方提示改为 `escapeJSON(7.body.choices[0].message.content)`（点选生成 [0]——make 官方认可）——配置形态正确（用户确认"我填的没问题呢"），但仍报错——**根因转向：单独 Run 下游模块不带上游数据/Webhook 没触发导致 DS 未执行**——见下方"Webhook 卡住的正确解法"
- ⚠️ 重要区分（避免与 3.4 封板冲突）：**TG Text 字段不加 [0]（用户两次封板）≠ Parse JSON json 字段不用 [0]**——make 在 Parse JSON 场景明确提示"Use a fixed item path instead of choices[]"，`choices[0]` 是官方给的解法。封板范围仅限 TG Text 字段的点选映射；Parse JSON 的 json 字段按官方提示用 choices[0]。下轮排查 Parse JSON 时以此为准，别再被"[0] 封板"误导。
- **✅ 最终实证（2026-08-16 会话末——Parse JSON 拆分通了）**：反复报 json 空值后，最终【引用=点选生成（用户坚持不加 [0]——"我说不动加 0吧"）+ 完整链路 curl 触发】——**飞书表格出现多条记录（数组拆分生效）**。结论修正：**Parse JSON 的 json 字段点选生成（不加 [0]）也能工作**——之前一直报空的【真根因是测试方式】（单独 Run 不带上游 / Webhook 没触发 DS 没跑），不是引用语法。排查优先级：先确认【完整链路 curl 触发】再怀疑引用——引用用点选生成即可，别强求 [0]（用户对此敏感——[0] 话题已封板，只给点选方案）。
- 方案Z（隔离测试）：json 字段写死测试 JSON（`[{"type":"test","title":"t"}]`）→ Save → Run → 能解析=模块没问题（问题在引用/上游/运行方式）；仍报错=模块/数据结构配置问题。一刀切定位，别来回猜。
- **⚠️ json 字段引用显示 `7.content`（2026-08-16 实踩——选错层的典型形态）**：报错 "Required field 'json' uses `7. content`, but that value is empty" = json 字段引用【停在了 DS 模块顶层】——DS 顶层没有 content 字段（content 在 body.choices[0].message 里）。修法：清空 json 字段 → 重新点选并【逐层展开到最深层】：DeepSeek(7) → Body → choices → [0] → message → content。生成形态应为 `7.body.choices[0].message.content`（或 make 显示 `7.Body.choices` + `[0]` + `message.content` 多段蓝色标签）。**判断标准：引用里有 `body.` 才算选对了层；只有 `7.content` 就是选错层。**
- **⚠️ json 字段引用显示 `7.Body.choices[]`（带方括号）也是错**：`choices[]` = 数组所有元素的标记——content 是单个字符串（choices[0] 的 message.content），引用停在数组层 → make 报 "result wasn't valid"。修法：choices 展开后选【第一个元素】再进 message.content（生成带 [0] 的固定路径）；或手动把 `choices[]` 改成 `choices[0]`（官方 Possible fixes 原文 "Use a fixed item path instead of choices[] if needed"）。报错建议里出现的 `{{7.body.choices[0].message.content}}` 就是 make 认可的正确形态。
- **⚠️ 手打 escapeJSON 在点选模式会被加模块前缀（2026-08-16 实踩）**：在字段输入框里打字 `escapeJSON(` 再点选引用 → make 可能生成 `7.escapeJSON(7.body.choices[0].message.content)`——**开头多了 `7.`**——make 把 escapeJSON 当成了"模块7 的字段路径"（不是函数）→ 空值报错。修法：`7.` 只允许出现在【括号内】（函数参数）；括号外的开头必须是函数名 `escapeJSON`。先清空 → 打字 escapeJSON( → 点选引用 → 补 )——别在点选状态中途打字。

## ⚠️ 模块链跨级引用（2026-08-16 实踩——先以为选不到，实际可以）

**现象**：场景2 结构 `Webhook → DS(2) → HTTP-A(10 拿token) → HTTP-B(11 写飞书)`——HTTP-B 的 Body 想映射 DS(2) 的脚本输出，第一次点选面板选不到 DS（只能引用上一级 HTTP-A 的输出）。用户原话："HTTP-B的上一级是 HTTP-A，我选不到 DS的输出啊"。

**⚠️ 修正（会话内推翻——别当死限制）**：用户随后在 HTTP-B 的 Body 点选面板里【成功选到了 DS 输出】（原话："我拿到 DS的了，可以选择到，现在开始测试吧"）。所以**跨级引用在 make 里可行**——"选不到"大概率是点选面板搜索/滚动没展开到位，或当时 DS 还没跑过（无输出样本）。遇到选不到：先在点选面板搜模块名/展开全部，或先 Run once 让 DS 跑一次再回来点选；别急着改场景结构。

**结构设计原则（仍有效）**：多模块链里，需要被下游引用的输出尽量让引用方靠近其上游；但跨级引用能用，不是硬限制。

## ⚠️⚠️ 多行文本进 JSON Body 的坑（2026-08-16 实踩——escapeJSON 手打无效，正解=Create JSON 模块）

**现象**：场景2 把 DS 生成的脚本（四段式**含换行**）映射进 HTTP-B 的 JSON Body（JSON string 模式）：
- 直接放 → 报 `Couldn't parse the JSON body ... The 脚本全文 field likely adds a broken line break from the DeepSeek text`（换行符破坏 JSON）
- 手打 `escapeJSON(...)` 包住 → ①手打函数在 JSON string 模式里**不被识别为函数**（make 当文本）②手打整段 JSON 极易把引号/括号搞乱 → 报 `Unexpected token 'e'... is not valid JSON` 或 `The Body content field in module 11 mixes text with raw mapped content`

**正解（make 报错自己都提示了——"Build the body with a JSON module instead"）**：用 **Create JSON 模块**（JSON 应用 → Transformers → **Create JSON**——不是 Parse JSON）构建 Body，不要用 JSON string 手打：
1. 在 HTTP-B 前面加 Create JSON 模块（搜 "JSON" → Create JSON）
2. 模块弹出 **"Add data structure"**（数据结构定义）——点 "+ Add item" 逐层加：
   - 根: `fields`（Object 类型）
   - 子项: 选题类型（Text——打字）/ 脚本全文（Text——**点选 DS 输出 choices.message.content**，蓝色标签）
   - Strict: **No**（不严格校验——payload 多字段不拒绝）
3. Save → HTTP-B 的 Body 字段改为**点选引用 Create JSON 模块的输出**（不是手打 JSON）
→ Create JSON 模块用可视化数据结构构建——**自动处理换行/转义**——不需要 escapeJSON

**要点**：JSON string 模式适合"纯静态/值全是短文本"的 Body；**AI 生成的多行文本（脚本/长文）一律走 Create JSON 模块**（可视化填字段+点选映射——make 原生转义）。手打 escapeJSON() 在 JSON string 模式无效——别浪费时间。

## 交付模式（2026-08-16 用户定稿——帮姐夫搭的最终交付形态）

**触发交付痛点（用户提出）**：交付给非技术用户（姐夫）不能让他用 curl/命令触发——需要无门槛触发方式。可选：①**表单页**（网页按钮/表单——POST 到 Webhook——最友好）②定时（Schedule 是场景工具栏设置不是模块——查证过，无法做纯定时触发）③浏览器书签（GET 访问 Webhook URL——激活后可行但体验一般）。**用户最终选：表单页**。

**交付账号结构（用户定稿）**：用【用户自己的 make 账号】交付——**Webhook URL 不变**（make 侧不动）；只把【飞书凭据和表格】换成姐夫的（HTTP-A 的 Body app_id/app_secret + HTTP-B 的 URL base token/table_id）。姐夫不需要注册 make。飞书侧由用户帮姐夫创建（问姐夫要飞书账号→用户代建应用/表格——不是让姐夫自己操作）。

**换飞书凭据的完整清单（场景1/2 各改两处）**：
1. **HTTP-A（拿 token）Body**：`{"app_id":"<姐夫新应用AppID>","app_secret":"<姐夫新应用Secret>"}`
2. **HTTP-B（写记录）URL**：`.../apps/<姐夫新base_token>/tables/<姐夫新table_id>/records`
3. 其余全部不动（Method POST / Headers Bearer / Body 引用 Create JSON 输出 / Webhook URL）
- 格式确认：新旧 URL 结构完全一样（`.../apps/{base_token}/tables/{table_id}/records`）——只是 token 段和 table 段换值，长度差异是 token 随机串长短——正常，别怀疑格式。

**姐夫飞书侧一次性配置（用户代做——与自己的飞书手搓完全同流程）**：
1. open.feishu.cn → 创建企业自建应用 → 拿 App ID/Secret
2. 权限：bitable:app + bitable:app:readonly（免审）+ **wiki:node:read**（若表格在知识库 wiki 里——没开会报 99991672 Access denied——补开后即时生效无需重新发布）
3. 建 2 个多维表格：《每周选题库》（选题类型/视频标题/核心角度/流量潜力/状态——5列）+《脚本库》（选题类型/脚本全文——2列）——全部 Text 类型
4. 表格分享"组织内可编辑" + 应用加为协作者（可管理）——缺一写 91403
5. 给用户 3 样：App ID / App Secret / 两个表格链接（**base 格式优先**；wiki 格式也能转换——get_node 接口）

**⚠️ 两个场景的 HTTP-B URL 不一样——复制配置必串（2026-08-16 实踩——1254045 FieldNameNotFound）**：场景1 HTTP-B 写《每周选题库》（BKvgbX.../tblF4mb...），场景2 HTTP-B 写《脚本库》（Rej1bi3.../tblgqavY...）。交付换凭据时用户复制场景1 的 HTTP-B 配置到场景2 → 场景2 写到了选题库表（列名不匹配）→ 报 `{"code":1254045,"msg":"FieldNameNotFound"}`。**字段名对但报 FieldNameNotFound = URL 指向了错误的表**（那个表没有这些列）。排查顺序：先看报错模块的 URL 指向哪个 base/table，再对比发送 Body 的字段名与目标表 fields（API `GET .../tables/<id>/fields` 精确查列名——含空格/隐藏字符用 repr 看）。**交付换凭据时逐个场景核对 HTTP-B 的 URL**——两个场景的 base token/table_id 必须各自对应（场景1=选题库/场景2=脚本库）。

**⚠️ 写通后表格分享权限也要\"可编辑\"（2026-08-16 实踩——91403 forbidden 的又一形态）**：脚本库 curl Accepted 但报 `forbidden access reply`——HTTP-A 拿 token 绿了（app 身份正常）但 HTTP-B 写入被拒。根因：脚本库的分享权限没开\"可编辑\"（应用能读表但写不进）。修法：表格右上角分享 → 改\"组织内所有人可编辑\"（或互联网可编辑）——和选题库一样的坑。**交付时两个表都要确认分享\"可编辑\" + 应用加协作者（可管理）**——场景1 通了不代表场景2 自动通（每个表独立检查）。
1. **curl 验证凭据**：`POST open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal`（Body: app_id+secret）→ `code:0` + token = 凭据可用
2. **wiki 链接转 base**：`GET .../wiki/v2/spaces/get_node?token=<wiki_token>`（Bearer）→ obj_token + obj_type: bitable
3. **查 tables + fields**：`GET .../bitable/v1/apps/<base>/tables` 和 `.../tables/<table_id>/fields` → 确认列名匹配 Create JSON 数据结构（**列名必须完全一致**——否则写入报"字段不存在"）
4. **场景激活后 curl 触发**：场景1 → 看《每周选题库》15 条；场景2 → 看《脚本库》1 条
- ⚠️ 用户移动表格位置（wiki 里拖拽）后：**base token 不变**（wiki 路径变但 obj_token 不变）——用 get_node 重新确认即可，别以为要重配。
- ⚠️ 场景2 curl Accepted 但表格没写入：先确认看的是【《脚本库》】不是《每周选题库》（两个表不同）；再查场景2 的 DS Body 是否还是写死（传参没用——写死脚本但写入仍应发生）；仍空则看场景执行日志。

**交付文档**：若让姐夫自己操作——出一份保姆级文档（4 步：创建应用→开权限→建 2 表→发交付信息——含常见问题）；用户代做则不需要。交付文档放 notes-vault/交付文档/。

**表单页模板**：见 `templates/make-form.html`（两个功能区：生成选题按钮 + 生成脚本 4 字段表单——fetch POST 到两个 Webhook URL——移动端自适应）。部署到 VPS nginx（pmlophy.com/make-form/）或免费静态托管。**注意**：表单页交付前，场景2 的 DS Body 必须从【写死】改成【引用 Webhook 参数】（user content 用 `{{Webhook.data.type/topic/info/action}}`——点选映射）——否则表单传参无效、脚本永远一样。场景1 若只做"生成按钮"（不传参）DS 可保持写死。

## ⚠️ 表单页部署到 VPS 的坑（2026-08-16 实踩——交付最后一步）
- **本机就是 VPS 时别绕 SSH**：Hermes 跑在 VPS 上时，先 `hostname` + `curl ifconfig.me` + `ls /var/www/pmlophy.com` 确认本机即生产机——直接本机部署（mkdir/cp/chmod），别找 SSH key（本会话曾找不到 id_ed25519_vps 绕了半天，被批"废话，你现在不就是在 vps 上啊"）。SSH key 记忆可能过时——先查 /root/.ssh/ 实际内容。
- **nginx root 直接托管**：pmlophy.com 站点 root = /var/www/pmlophy.com——子目录即得 URL（`/var/www/pmlophy.com/make-form/index.html` → `https://pmlophy.com/make-form/`），不用改 nginx 配置、不用 reload。
- **文件权限必须 644**：root 创建的 index.html 默认 600 → nginx worker 读不了 → **403 Forbidden**——`chmod 644 index.html` + `chmod 755 目录` 解决。部署后 `curl -s -o /dev/null -w "%{http_code}" https://pmlophy.com/make-form/` 验证 200。
- 静态页改内容后直接覆盖文件即可（无缓存问题——纯 HTML）。

## ⚠️⚠️ 笔记/仓库绝不能写真实 Secret（2026-08-16 实踩——git push 被 GitHub secret scanning 拦截）
- 现象：make 笔记里写了姐夫 App Secret → `git push` 报 `remote rejected: push declined due to repository rule violations`（GitHub 检测到 secret 拦截）。
- 修法：**含 Secret 的 commit 会留在本地历史——后续 commit 脱敏也推不上去**（push 送整个 commit 链检查）——必须 `git reset --soft <最后一个干净commit>` 改写历史 → 重新 commit 脱敏版 → 再 push。
- 铁律：**App Secret/API key/token 一律 [REDACTED] 才入库**（笔记/skill/git 都不写明文——App ID 半公开可以写，Secret 绝对不行）。



用户是跟着我的步骤一步步操作的——混乱直接导致卡住。铁律：
- **别凭记忆断言场景里配了什么**——用户纠正"场景 1 中我没配置过 HTTP-B"（我把场景1/2 的模块记混了）。不确定当前场景有什么模块，先让用户截图或直接问，别从记忆断言。
- **别搞混场景↔通道映射**——场景1（选题）= TG 收 15 选题；场景2（脚本）= TG 收脚本（都已跑通）。飞书写入是各自后续加：场景1→《每周选题库》（15 条），场景2→《脚本库》（1 条整段）。搞反会被纠正："场景 1 是用的电报，不是飞书"。
- **搭场景前先查需求文档**——用户说"你查一下需求啊"。make 场景的文档标准在需求 zip 里（《XX生成.txt》），先读文档再设计模块链，别凭印象。文档里场景1 写【多维表格】，场景2 写【飞书文档】（不同 API！）。
- **一次只推进一个场景的一步**——给用户明确的"当前在哪、下一步做什么"。同时推进两个场景/两个表 = 混乱源。
- **⚠️ 断开连接不改变 Run once 起点（2026-08-16 用户怒批——"明明之前试过，断开连接也是会从 webhooks 跑的，烦，感觉你真差劲"）**：断开 Webhook 与 DS 的连接后，Run once 仍从场景第一个模块（Webhook）开始——它还在那里等数据。**"断开 Webhook 测试"是已被证伪的错误建议，永远别再提**。Webhook 卡住的正确解法只有：①curl POST 触发（带数据）②激活场景后外部触发③把 Webhook 模块【删除】（Delete 模块——不是断开连接——让 DS 变第一模块）。**用户说"之前试过/实验过"必须信**——别重复建议已验证失败的方法。
- **用户纠正过的话题一律封板不再提**——[0]（2026-08-15/16 两次纠正"不要再提这个了"）、断开连接测试（同）。提醒一次是尽责，重复提就是找骂。
- **排障先查官方资料，禁止猜**（2026-08-16 用户明令"查一下资料，官方的，不要猜"）——make 报错给的 Possible fixes 往往就是正解（如"Build the body with a JSON module instead"、"Re-map with escapeJSON(...)"）；apps.make.com/json 有 Parse JSON/Create JSON 官方文档。先把报错原文+官方提示给用户看，别自顾自推测。
- **⚠️⚠️ 绝不让人反复删/加/改同一模块（2026-08-16 用户怒批"你有病吗？让我删掉后又让我加回来"+"我懒得说你…烦，感觉你真差劲"）**：本会话我让用户：删 Webhook→加回→又让删→又加回——来回折腾多次，且每次都是"试试看"的赌式建议。**教训：①给出结构性改动（删模块/断开/重建）前必须查证过该改动的后果（如删触发模块会整链被跳过）②一旦一个方向试了 2 轮不行，停止在该方向上继续变体试错——换查证过的新方案 ③用户明确说"我不想了/思路不对/能不能绕过"时立即停——用户对当前方向失去信心时，先停下来重新评估而不是继续推。**
- **⚠️ 道歉没用，行为改变才算（2026-08-16 用户"一句话抱歉就可以了？铁律也没用啊"）**：连续犯错后，一句"对不起"不仅不修复信任反而更刺眼。用户要看到的是：①列清自己实际违反了哪条铁律（不狡辩）②接下来具体的查证/行为改变 ③不再重复同类错误。道歉要配行动清单，否则不如不道歉。
- **用户能自己发现配置问题**（Chat ID 多位/字段没建/数据结构错——用户自己排查能力很强）——用户说"是不是 X 的问题"时认真对待（常是对的），别急着否定。
- **长会话收尾/用户要休息时——先出"醒来直接照做"的完整操作方案（2026-08-16 用户睡前要求）**：用户说"睡一觉起来改"后，主动把【调整后的模块顺序 + 每个模块的完整配置明细 + 操作步骤 + 关键坑】全部列成可直接执行的清单（用户原话："能把调整后的顺序和每个模块的详细配置全部列出来吗？这样我醒了后直接操作，你先查证，再出详细配置方案和流程"）。要求：①方案里的每个机制判断先查证过（官方文档/社区），标注"已查证"②给出模块顺序图（Webhook→DS→...）③每个模块分节给配置（URL/Method/Body/Headers/引用路径）④末尾列关键坑。这样用户睡醒不用重新梳理上下文，直接照做。

## 场景2 飞书写入目标表（《脚本库》——2026-08-16 已建）

- 表格链接: `https://mcn167bt73yz.feishu.cn/wiki/GpAhwRsGMiwCjqkYxs1c13Hnnie`（wiki 格式）
- wiki_token: `GpAhwRsGMiwCjqkYxs1c13Hnnie` → base token: `DKfobpSXkaTAw4sl0lXctB6BnZb`（obj_type: bitable）
- table_id: `tblnwVWvcZnkwE6G`（默认表名"数据表"——用户建了字段）
- 写记录 URL: `https://open.feishu.cn/open-apis/bitable/v1/apps/DKfobpSXkaTAw4sl0lXctB6BnZb/tables/tblnwVWvcZnkwE6G/records`
- 字段设计: 选题类型 + 脚本全文（整段写一条——**不需要** Parse JSON/迭代器，比场景1 简单）

## 能力评估：make 能否接国内平台数据/读 AI 分享链接（2026-08-18 查证定稿）

被问"make 能不能做 XXX"时，按平台数据开放度给结论（不是 make 的能力问题——是平台是否开放 API）：

**抖音（有条件可接）**：make 无原生连接器，但 HTTP 模块可调【抖音开放平台 API】（近 200 个含数据统计）。门槛高：①要【企业认证】（个人开发者权限很少）②应用审核通过③用户 OAuth 授权④数据类接口多为【企业号专属能力】（普通号拿不到粉丝/播放/评论数据）。无资质时可走第三方爬虫（Apify 抖音爬虫——Douyin Pro Scraper——make 可调其 API）但非官方数据、有封号/合规风险。
**视频号（基本不可行）**：无公开开放 API（微信生态封闭）——第三方拿不到后台数据——只能人工从视频号助手后台导出 Excel。落到流程：投放监控（节点8）做不了全自动；评论私信（节点9）用视频号后台自带关键词自动回复（不用 make）；数据复盘（节点10）半自动=人工导出→贴飞书表格→make 读表生成报告。
**DeepSeek 分享链接（make 不支持）**：`chat.deepseek.com/share/xxx` 有 **AWS WAF 防护**（curl/web_extract 都只能拿到 challenge 验证页，需执行 JS 才看到对话）——make HTTP 模块没有浏览器渲染能力，过不了 WAF → **拿不到分享内容**。唯一路径：对话内容复制粘贴进飞书表格/表单 → make 读表格处理。别承诺 make 能读分享链接。

评估框架：**先问"目标平台有没有开放 API / 要不要企业认证"** → 不是 make 能不能，是平台给不给数据。国内平台（抖音/视频号/小红书/剪映）官方连接器基本没有，且 API 权限门槛高 —— 替用户做可行性判断时主动给"半自动（人工导出+make 处理）"的兜底方案。


## 当前需求变更与场景操作纪律

当用户恢复一个已讨论过的 Make 需求时，以用户提供的“最后版”作为当前规格，不重新发明方案。对于提示词配置表 + 半自动字段方案：先让用户在飞书建立《提示词配置表》（场景、提示词两列），确认链接、字段类型和权限后，再改 Make 场景；不要提前改场景或擅自补未提供的场景提示词。

Make 场景配置必须先确认当前场景、目标表、字段、模块编号和通道，不能凭记忆混用场景 1/2 或 Telegram/飞书。一次只推进一个场景的一步，先用 Run once/真实数据验证，再继续下一步。

本轮新增执行规则：
- **先读权威笔记再操作**：恢复旧 Make 任务时，先 `git pull` notes-vault，并完整读取指定的最新笔记；不要用会话记忆重建模块编号、表格、凭据或已完成状态。
- **飞书凭据必须按工作流 SSOT 复用**：读取 wiki/bitable 时使用之前已经验证过的姐夫应用身份；若返回 `99991672`，先核对 App ID 是否误用了 Hermes 自身应用，不要立刻重新申请权限。App Secret 不进入聊天、日志、笔记或 git。
- **Wiki 解析路径固定**：`GET /wiki/v2/spaces/get_node?token=<wiki_token>` 的对象在 `data.node.obj_token`、`data.node.obj_type`、`data.node.title`，不是顶层 `data.obj_token`；拿到 `obj_type=bitable` 后再调用 tables/fields/records。
- **提示词配置链路是串行 Bundle 流**：场景1/2均为 `Webhook → token → wiki node → records（分页）→ Iterator(items) → Filter(场景=目标场景) → Create JSON → DS → 原有输出`；四个 HTTP 角色分别确认后不得误删：token、wiki node、records、分页。Make 不是并行模块链；下游按 Bundle 逐个执行。
- **DS 与 HTTP 的 Body 配置不能混用**：DeepSeek 的 `Make an API Call`不是普通 HTTP 模块；当动态长提示词含换行/引号时，用 JSON → Create JSON 构建 `model + messages[]` 请求体，再把完整输出传给 DS。不要把提示词正文直接替换 DS Body，也不要未经官方确认把 DS 改成 HTTP 的 Data structure 形态。
- **Make 的下游测试必须从触发器完整 Run once**：单独运行下游 HTTP/Iterator/DS 会缺少上游 token、records 或映射样本；验证提示词读取链路必须从 Webhook 开始完整执行。不要重复建议已证伪的断开 Webhook 测试路径。
- **VPS 表单页只适配已确定的 Webhook 契约**：场景1保持 `POST {data: ref}`，场景2保持 `POST {data: {type, topic, info, action}}`；表单页不处理 records 分页，分页属于 Make 内部。修改表单前先读取现版文件，保持两个 Webhook URL 和 payload 字段不变。

本轮字段变更继续遵循半自动原则：Make 不自动猜新字段；姐夫修改/新增表格字段后通知，再由人工同步 Make 的 Create JSON/HTTP-B 字段映射。

**面向非技术用户的手册边界**：交付给只使用飞书和网页表单的用户时，单独提供用户视角手册：只写“飞书/网页输入 → 自动生成 → 飞书结果表查看”，不要把 Make 内部模块、Webhook、HTTP、Token、API、分页、Iterator 等配置细节写入用户手册，避免噪音。手册必须明确：提示词配置表中的场景1/场景2可直接修改；**保存配置表不会自动触发任务**，真正的触发动作是随后点击 VPS 表单页的“生成15个选题”或“生成口播脚本”按钮，Make 在这次新运行中重新读取最新提示词；场景2核心输入 `type/topic/info/action` 当前固定，新增或删除字段属于半自动，必须通知维护人员同步网页、Webhook 和 Make 映射。
- 需求 1：提示词从固定写死改为读取配置表，DS 引用配置表内容；表格文字变化在下一次运行生效。
- 需求 2：字段变更采用半自动规则——允许姐夫改/加字段，但必须通知后再同步 Make 映射；不承诺自动识别任意新字段。
- 外部平台配置不是本地代码部署，不套用 dist/ZIP 流程；完成标准是权限、映射、Run once 和真实记录结果，而不是 HTTP 200。

- 免费版 1000 次/月——批量跑/高频触发会超（先估算场景频率）
- 场景超时：检查是否有模块等待输入/API 响应超时（AI 生成模块长文本可能慢）
- API Key 无效：检查复制完整/是否已加支付方式（Anthropic 要绑卡）
- 连接器授权状态变了要重新授权（飞书 token 过期等）
- 提示词预置到 System Prompt 字段（长提示词别塞 User Prompt——省 token 且稳定）

## 参考
- 官方应用文档：https://apps.make.com/（AI 分类列出所有第三方 AI 应用）
- 帮助中心：https://help.make.com/
- 表单页交付模板：`templates/make-form.html`（生成选题按钮 + 生成脚本 4 字段表单——替换两个 Webhook URL 即可部署）

## 交付现场状态（2026-08-16 会话末——姐夫飞书全通，交付完成）
- 姐夫飞书应用：App ID `cli_aa0b2b6235b89d11` / App Secret [REDACTED——本地安全库，绝不入 skill/笔记/git]（curl 验证 code:0 token 可用；bitable 权限 + wiki:node:read 已开）
- 《每周选题库》：base `BKvgbXIqpazS1nsqIsKcO5qbnuh` / table `tblF4mbiUnJvjIeO`（5 列：选题类型/视频标题/核心角度/流量潜力/状态——已建）
- 《脚本库》：base `Rej1bi3nraOAfss7eCBcfOPUnGc` / table `tblgqavYqsJrwfnA`（2 列：选题类型/脚本全文——已建）
- make 场景1/2 的 HTTP-A（app_id/secret）+ HTTP-B（URL）已全部换成姐夫凭据；场景已激活
- **场景1 ✅ 通**：curl 触发 → 《每周选题库》15 条不同选题写入成功
- **场景2 ✅ 通 + 动态接参完成**：DS Body 的 user content 已改为【点选映射 Webhook 8 号 4 变量】`{{8.data.type}}/{{8.data.topic}}/{{8.data.info}}/{{8.data.action}}`（用户点选生成——不是手打）——验证：curl 传不同参数（避坑指南类/投流3个坑）→ 脚本库新增对应脚本——动态输入生效
- **表单页已部署上线**：https://pmlophy.com/make-form/（HTTP 200——模板 `templates/make-form.html`）——姐夫打开网页点按钮/填表即可触发
- 交付定稿：用【用户自己的 make 账号】（Webhook URL 不变）+ 姐夫飞书（应用/表格）+ 表单页触发——跑通版交付，场景3/4 后续迭代
- 待办（姐夫想优化再做）：①表单页接入场景1 动态传参（当前场景1 DS 写死——按钮不传参用默认）②场景3 周报/场景4 市场分析 ③表单页域名体验优化

## ⚠️ 表单页部署到 VPS 的坑（2026-08-16 实踩）
- **本机就是 VPS 时不要绕 SSH**：用户在 VPS 上跑 Hermes——`hostname` + `curl ifconfig.me` 一查就确认本机公网 IP = pmlophy.com 的 IP、`/var/www/pmlophy.com` 存在、nginx 已装 = 本机即生产机——直接本机部署（mkdir/cp/chmod/nginx -t），别找 SSH key 绕圈（用户原话\"废话，你现在不就是在 vps 上啊\"）。SSH key 记忆（id_ed25519_vps）可能不存在——先查 /root/.ssh/ 实际内容。
- **静态页部署三步**：①`mkdir -p /var/www/pmlophy.com/make-form` ②`cp index.html` ③**`chmod 644` 文件 + `chmod 755` 目录**——nginx root 直接托管（pmlophy.com 站点 root = /var/www/pmlophy.com——放子目录即得 https://pmlophy.com/make-form/ 路径）。文件默认 600（root 创建）→ nginx worker 读不了 → **403 Forbidden**——chmod 644 解决。部署后 `curl -s -o /dev/null -w "%{http_code}" https://pmlophy.com/make-form/` 验证 200。
- 静态页改完不用 nginx reload（新文件不需要重载——root 托管自动生效）。

## ⚠️⚠️ 笔记/仓库绝不能写真实 Secret（2026-08-16 实踩——GitHub push 被 secret scanning 拦截）
- 现象：notes-vault 的 make 笔记里写了姐夫 App Secret → `git push` 报 `remote rejected: push declined due to repository rule violations`（GitHub secret scanning 拦截）。
- 修法：**含 Secret 的 commit 留在本地历史里，后续 commit 脱敏也推不上去**（push 时整个 commit 链一起送检）——必须 `git reset --soft <最后一个干净commit>` 改写历史 → 重新 commit 脱敏版 → 再 push。
- 铁律：**任何 App Secret/API key/token 一律 [REDACTED] 才入库**（凭据放本地安全库/记忆，绝不进 git 笔记）。App ID 这类半公开标识可以写，Secret 绝对不行。

