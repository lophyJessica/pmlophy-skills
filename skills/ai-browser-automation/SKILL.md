---
name: ai-browser-automation
description: AI/Agent 浏览器自动化工具生态与使用——ego (lite)（Agent-Native Browser，登录态继承+Space隔离+省token）、对比 Browser Use/agent-browser/ChatGPT Atlas/Perplexity Comet、skill 安装机制（~/.agents/skills 标准目录多家通用）。当用户提到"ego/ego-browser/AI浏览器/Agent浏览器/浏览器自动化/登录态自动化"时使用。
category: software-development
---

# AI/Agent 浏览器自动化（ego 生态）

## 触发场景
- 用户研究/使用 ego (lite)、ego-browser skill
- 让 Agent（Codex/Cursor 等）用登录态操作网页、抓登录墙数据
- 对比 AI 浏览器方案（Comet/Atlas/agent-browser/Browser Use）

## 生态定位（2026-08 查证）

```
AI 浏览器分两派：
① 人用 + AI 内嵌：Perplexity Comet（2025.7，活着但艰难）、
   OpenAI ChatGPT Atlas（2025.10，已废弃 deprecated——AI 想当主驾驶太超前）
② Agent 专用（Agent-Native Browser）：ego (lite)——浏览器是 Agent 的执行工具，
   人只在登录/确认时介入（Space 隔离），贴合"人在回路"
```

**产品判断（用户洞察）**：Atlas 死因=太过超前，现实是 AI 还是工具、人类必须是主驾驶；ego 处处体现人主驾驶（提交前停/验证码交给人/Space 隔离），所以能活。这是用户认可的 PM 叙事素材。

## ego (lite) 核心机制

1. **登录态继承**：基于 Chromium，一键导入 Chrome 配置（书签/密码/扩展/Cookie/登录会话）→ Agent 直接用你的登录态，不过验证码/SSO
2. **Space 隔离**：Agent 在自己 Space 跑任务，不碰用户标签页；用户可随时切进 Space 看/接管（登录、验证码、提交确认）
3. **省 token**：几行 JS 连续执行多个操作（对比 Playwright 一次一个调用），比 agent-browser 快最多 3.45x；语义 Snapshot 在定制 Chromium 引擎内（能访问跨域 iframe/Shadow DOM/Stripe/Salesforce/React Portal——web fetch/JS shim 拿不到的）
4. **免费 Mac 版**，数据全本地不收集

## skill 安装机制（关键：为什么"一份文件多家通用"）

- ego 首次启动 onboarding 时往**标准 skill 目录**写 ego-browser skill：`~/.agents/skills`（Agent Skills 开放规范）
- **实测（用户 Mac 2026-08-27）**：写一份，Codex / Claude Code / Cursor（新版本兼容标准目录）/ WorkBuddy / 反重力 全能用（`/ego-browser` 补全）——2025 后主流 Agent 普遍兼容读该目录
- 不被写入的：Trae（私有目录 ~/.trae/builtin_skills）、~/.antigravity（无此目录）
- skill 是"说明书"：ego 应用是本地服务端（浏览器本体），skill 只是让 Agent 知道怎么调它——删 skill 文件不影响应用
- **在 VPS 上的 Hermes 用不了用户 Mac 的 ego**（跨机器）——ego 只对"Agent 跑在同一台 Mac 本地"生效

## 使用要点

- Codex 里输入 `/ego-browser` + 指令；Codex 需给 **Full access** 权限（skill 要启动 Mac 本地 ego 应用，沙箱外执行）
- **503 Service Unavailable = ego (lite) 应用没启动/启动失败**（不是 skill 问题）：Cmd+Q 完全退出重开 ego → 重启 Agent 会话再试；还不行查系统设置隐私权限
- 首次跑给简单任务验证链路（如"打开某官网总结内容"），再上真实业务（登录墙抓取）

## 用户适合场景（PM + 视障 + forge 项目）

```
① 登录态内容获取（最实用）：飞书/DS 后台等 web_extract 拿不到的页面，
   Agent 用登录态读+总结成文字 = 视障用户的"眼睛"
② 业务调研抓取：竞品社媒（X/LinkedIn）近 7 天帖子/互动量榜单
③ 网页自动化测试：forge 系统前端按用例点流程（登录态继承），用户做最终判断
④ 求职投递：自动填表停在提交前（用户当前阶段用不上，将来换工作可用）
```

## 给指令加 ego 的原则（条件触发式，不每条都加）

```
加：登录态网页操作 / JS 渲染 iframe / 需真实操作（点击填表）/ 竞品社媒数据
不加：纯代码开发 / API 可得数据（Tavily/web_search 能拿）/ VPS 侧任务（跨机器无效）
写法示例："数据获取优先级：API/web 检索 > ego-browser（遇登录墙或 JS 渲染页时
用 ego-browser 继承本机登录态，不许伪造）"
```

## 详细资料

- `references/ego-lite.md` —— ego 官网/文档要点、与 Browser Use / Vercel agent-browser 对比、完整使用场景清单

## 状态（2026-08-27 收尾）

- 503 已修复（ego 应用重启），链路打通；用户确认"5 家 Agent 全覆盖"并拍板**条件触发式集成方向**：等一个真实业务任务实测跑通后，把"数据获取优先级：API/web 检索 > ego-browser（登录墙/JS 渲染页时用）"写进 Codex/Cursor 的项目 AGENTS.md——未跑通前不预写规则
- 姐夫（Windows）暂用不了 ego（仅 Mac 版，Windows 候补中）
- 与 Parallels Desktop 27 无关（那是 VM 内本地 AI 加速，SME2 要 M4+ 芯片；LOL 等 DirectX 游戏不受益）
