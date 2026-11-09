# ego (lite) 详细资料（2026-08-27 查证）

来源：https://lite.ego.app/zh-cn + https://lite.ego.app/document/zh/docs/quick-start

## 一句话定位

"ego (lite) 只是一款浏览器；ego 才是你跨设备的个人 Agent"——lite 版是给 Agent 用的免费浏览器（Mac），完整版 ego（跨设备个人 Agent）在候补名单。

## 官网承诺的能力

- 与 Chrome 一样基于 Chromium：地址栏/标签页组/书签/配置文件/扩展/下载/隐身模式行为一致
- 一键导入 Chrome：标签页组、书签、密码、扩展、Cookie、登录会话、浏览器配置文件
- Agent 继承登录态：Gmail/Notion/LinkedIn/内部工具不用重新验证
- Space 机制：Agent 在自己 Space 跑任务（右上角 Space 面板可见，蓝色光晕=Agent 正在操作）；不接管鼠标、不占用户标签页；用户可随时切换进去帮 Agent 登录/验证
- 省 token 三来源：①几行 JS 连续执行多操作（非一次一调用）②语义 Snapshot 在定制 Chromium 引擎内（跨域 iframe/Shadow DOM/Stripe/Salesforce/Intercom/React Portal）③避免对不存在内容反复重试
- 多任务并行：每个任务独立 Space 不冲突
- 数据安全：不收集任何数据（历史/cookie/密码/页面全在本地）；设置过程只记录"是否选择 Chrome 数据迁移"这一件事
- 开源：GitHub citrolabs/ego-lite（14k star）；Discord 5eGZVvHbTq

## 支持的使用场景（官方列）

社交媒体抓取/发布（X/LinkedIn/Threads/Reddit/Instagram/Facebook，API 拿不到的用登录态）、求职自动申请（LinkedIn/Wellfound/YC，进 ATS 填表停在提交前）、房产/金融/购物（Redfin/Zillow 房贷计算器、Amazon 比价）、预订（机票/酒店/餐厅到支付页前停）、SaaS 后台（HubSpot/Salesforce/Notion/Airtable/Linear/Stripe/GA4/Search Console/Mixpanel 批量操作）、内部工具（管理后台/staging/QA）、AI 浏览器测试。

## 与竞品对比（官网口径 + 查证）

| 维度 | ego (lite) | Browser Use | Vercel agent-browser | ChatGPT Atlas | Perplexity Comet |
|---|---|---|---|---|---|
| 形态 | 真浏览器 + skill | 自治 Agent 框架 | CLI（无浏览器） | AI 内嵌浏览器 | AI 浏览器 |
| 登录态 | 继承用户日常会话 | 独立实例，默认无扩展 | 不共享日常会话 | - | - |
| 收费 | 免费 | 自有定价层 | - | 已废弃（2025.10 出，deprecated） | $200/月订阅争议 |
| 多任务 | ✓ Space 并行 | - | - | - | - |

## 兼容 Agent（官网列表）

ego、Claude Code、Codex、Cursor、Continue、Gemini CLI、Hermes Agent、OpenClaw、OpenCode——任何能跑 shell 的 Agent。

## 实测记录（用户 Mac 2026-08-27）

- `ls ~/.agents/skills/` 和 `~/.claude/skills/` 都有 ego-browser（onboarding 自动写入）
- Cursor / WorkBuddy / 反重力 实测也能识别（`/ego-browser` 补全）——兼容读 ~/.agents/skills 标准目录
- Trae（~/.trae/builtin_skills）未写入；~/.antigravity 目录不存在
- Codex 首次调用报 503 → 修复方式：ego (lite) 应用完全重启（Cmd+Q 重开）→ 重启 Agent 会话
- Codex 需 Full access 权限（skill 要启动 Mac 本地应用）

## 产品判断记录

- Atlas 死因：AI 想当主驾驶，脱离"AI 是工具、人主驾驶"的现实 → OpenAI 自己砍
- ego 活因：人在回路产品化（提交前停/验证码交人/Space 隔离）
- 定位：Agent-Native Browser = 浏览器即 Agent 基础设施（区别于"人用浏览器+AI 内嵌"）
