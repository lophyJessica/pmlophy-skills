---
name: agent-browser-automation
description: Agent 浏览器自动化（ego lite 等 agent-native browser）——安装机制/skill 目录兼容/故障排查/AI 浏览器方向。当用户提到 ego/ego-browser/agent browser/AI 浏览器/浏览器自动化时使用。
---

# Agent 浏览器自动化（ego lite）

## 核心概念（2026-08-27 查证+实测）

**ego (lite) = agent-native browser（给 AI Agent 用的浏览器）**，与"人用的 AI 浏览器"（Perplexity Comet / ChatGPT Atlas）是两类：

```
Comet / Atlas = 浏览器 + AI 内嵌（主视角是人，AI 辅助人浏览）
ego (lite)    = Agent 专用浏览器（主视角是 Agent：浏览器是 Agent 的执行工具，
               人只在登录/确认时介入——Space 隔离）
```

- **本质**：独立 Mac 应用（Chromium）+ 本地服务；`ego-browser` 是 skill（说明书文件），让 Agent 认识并调用它。能力在应用本体，skill 只是适配层——"不装 skill 的 Agent 根本不知道有 ego"。
- **价值**：继承用户真实登录态（Cookie/SSO/验证码不再拦 Agent）；Space 隔离（Agent 干活不打扰用户）；语义 Snapshot 在定制引擎内（跨域 iframe/Shadow DOM/React Portal 可访问）省 token。
- **方向判断**（用户洞察，面试可讲）：AI 浏览器方向 2025-2026——Comet 活着（艰难）、ChatGPT Atlas 已废弃（OpenAI 自己砍了）、ego 刚起步 14k star。**Atlas 死因 = AI 想当主驾驶，超前于现实；当前 AI 是工具、人必须主驾驶**。ego 设计处处"人主驾驶"（提交前停、验证码交人、Space 隔离）——符合"人在回路"理念的才能活。

## 安装与兼容（实测）

- **自动安装**：首次启动 onboarding 时扫描本机 Agent，把 `ego-browser` skill 写入标准 skill 目录：`~/.agents/skills` + `~/.claude/skills`
- **实测兼容**（读 `~/.agents/skills` 标准目录的都能用，一份文件全家通用）：Codex / Claude Code / Cursor（新版）/ WorkBuddy / 反重力 / Claude
- **不兼容**：Trae 等不读标准目录的
- **验证是否写入**：`ls ~/.agents/skills/ 2>/dev/null; echo '---'; ls ~/.claude/skills/`
- **Cursor 没被自动写时手动补**：`mkdir -p ~/.cursor/skills && cp -r ~/.agents/skills/ego-browser ~/.cursor/skills/`
- 注意：skill 是**文件系统里的目录**，不是某个 App 界面里的东西——用户"没看到 skill"≠ 没装，先 ls 目录再判断

### 多 Agent Skill 目录对照 + 软链接共享（2026-09-07）

要给**多个 agent 共用同一份 skill** 时，别每处各装一份（改一处要同步多处）。完整对照表（Cursor/Claude Code/Codex/Antigravity/ZCode/WorkBuddy/TRAE 七家的用户级 skill 目录）+ 共享方案见 `references/multi-agent-skill-directories.md`。要点：**唯一源选 `~/.agents/skills/`**（Codex 官方入口 + Cursor 也读，共享度最高）→ 支持软链的软链指过去（Claude Code/Codex/ZCode/Cursor）、官方未明确支持软链的用复制兜底（Antigravity/WorkBuddy/TRAE）。反向统一也成立：ego 能把 skill 分发进各 agent，反过来也能统一到一处（都是文件系统操作）。

## 使用

- Agent 对话框输入 `/ego-browser` + 指令；Codex 需给它 **Full access** 权限（skill 要启动本机应用，沙箱外执行）
- 场景：登录态内容获取（web_extract 拿不到的）、社媒抓取/发布、SaaS 后台操作、求职投递（停在提交前等确认）、AI 浏览器测试

## 故障排查

- **503 Service Unavailable（审批服务）** → ego (lite) 应用本体没启动：Cmd+Q 完全退出 → 重开（走完 onboarding）→ 重启 Agent 会话再发指令
- **skill 已装但 Agent 无反应** → 重启 Agent 会话（skill 会话启动时加载）；或该 Agent 不读标准 skill 目录
- **跨机器无效**：ego 是用户 Mac 本地浏览器——VPS 上的 Hermes/Agent 调不了（杰西卡在 VPS 上用不了）

## 指令集成（条件触发式——用户 2026-08-27 定方向）

给 Agent 的指令按场景**条件加 ego 段**，不是每个指令都带：

```
加 ego：需登录态网页操作 / JS 渲染页面 / 真实操作（点击填表）/ 社媒数据抓取
不加：纯代码开发 / API 直接可得（Tavily/web_search 能拿）/ VPS 侧任务（跨机器无效）
写法示例："数据获取优先级：API/web 检索 > ego-browser（遇到登录墙或 JS 渲染
页面时，用 ego-browser 继承本机登录态获取，不许伪造）"
```

**先实测再进指令体系**：ego 链路（skill → 应用 → 浏览器 → 返回）跑通一个真实任务后，再把条件触发段写进项目 AGENTS.md / 指令模板。

## 自主涌现实例（2026-08-28 forge-scrm——条件触发的价值实证）

Codex 执行"查证飞书卡片 2.0 collapsible_panel 组件结构"指令时，**无人提示**自主调用 ego 查飞书开放平台官方文档（交互式组件文档 curl 抓不到 → 自己判断需要真实浏览器）。结果：拿到官方字段集（header 双向交互、icon_expanded_angle 旋转反馈等），实现一次通过且零臆造字段。这验证了条件触发式集成的价值：工具给够，判断力是模型自己长出来的。给 Agent 的查证类指令可显式写"用 ego 查官方文档"提高触发率，但即便不写，装了 skill 的 Agent 也可能自发调用。
