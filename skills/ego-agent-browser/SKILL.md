---
name: ego-agent-browser
description: ego (lite) Agent 浏览器——让 Mac 上的 Codex/Claude Code/Cursor 等 Agent 用真实登录态跑浏览器自动化。安装机制/支持范围/用法/坑/指令场景。
trigger:
  - 用户提到 ego / ego-browser / lite.ego.app
  - Agent 需要登录态网页操作（登录墙/JS 渲染/真实点击填写）
  - 用户在 Mac 上研究"AI 浏览器/浏览器自动化"方向
---

# ego (lite) — Agent 浏览器（Mac）

## 是什么

ego (lite) 是免费 Mac 浏览器（Chromium），核心不是给人用，而是**给 AI Agent 用**：
- Agent 通过 `ego-browser` skill 指挥它操作网页
- 继承用户 Chrome 登录态（一键迁移书签/密码/扩展/Cookie/登录会话）→ Agent 操作登录后网站不用重新验证
- Space 隔离：Agent 在自己的工作区跑任务，不碰用户标签页、不抢鼠标
- 主打省 token：语义 Snapshot 在定制 Chromium 引擎内（可进 iframe/Shadow DOM/第三方 SDK 组件），几行 JS 连续执行多操作，比 Playwright 类快最多 3.45 倍

## 架构本质（解释"为什么一个应用能给所有 Agent 用"）

```text
ego 应用 = 本地服务端（浏览器能力长在应用里，独立于任何 Agent）
ego-browser skill = 使用说明书（纯文件：告诉 Agent 应用在哪、怎么调、命令格式）
Agent = 会跑 shell 的顾客（读说明书 → 调应用）
```

- skill 是 onboarding 时 ego **自动拷贝**到 Agent 标准 skill 目录的，用户不用主动装
- 删除 skill 文件不影响 ego 应用本体

## 支持范围（共享机制=ego 官方一键分发，非用户逐个实测）

| Agent | 生效 | 机制 |
|---|---|---|
| Codex | ✅ | ~/.agents/skills/ego-browser |
| Claude Code | ✅ | ~/.claude/skills/ego-browser |
| Cursor（新版） | ✅ | 兼容读 ~/.agents/skills（不用单独装！） |
| WorkBuddy | ✅ | 兼容读 ~/.agents/skills |
| 反重力 Antigravity | ⚠️ | Mac ✅ 兼容读 ~/.agents/skills；**Windows 版不生效**，绕过办法见下方坑 |
| Trae | ❌ | 私有目录（~/.trae/），不读标准目录 |

**一份 skill 文件（~/.agents/skills）多 Agent 通用**——究竟是 ego onboarding 时把 skill **自动拷贝**进各 Agent 的标准 skill 目录（官方一键分发机制），不是用户在每个 Agent 里逐个手动验证的。描述共享时只归因到"ego 官方分发机制"，**不要把它说成用户亲手实测过**。查目录：`for d in ~/.agents/skills ~/.claude/skills ~/.cursor/skills ~/.cursor/rules ~/.gemini/config/skills ~/.workbuddy/skills; do [ -d "$d" ] && echo "== $d ==" && ls "$d" | head -3; done`

## 用法（用户 Mac）

1. 下载安装：lite.ego.app → DMG → 拖入应用 → **走完 onboarding**（此时自动写 skill + 可选迁移 Chrome 数据，可能要输密码）
2. Agent 里输入 `/ego-browser` + 指令（如"用 ego-browser 打开 XX 网站，总结 YY"）
3. **Codex 需 Full access 权限**（skill 要启动 ego 应用=沙箱外执行）
4. 运行中：ego (lite) 右上角 Space 面板可看 Agent 执行过程（蓝色光晕=Agent 的 Space），登录/验证码时人介入

## 坑

| 坑 | 现象 | 修 |
|---|---|---|
| **503 Service Unavailable** | Agent 报"审批服务连续返回 503，命令未执行" | **ego 应用没启动**——Cmd+Q 完全退出重开（走完 onboarding），再重启 Agent 会话。与 Codex 无关。0827 用户已修复跑通 |
| **Chrome 被搞坏嫌疑** | ego onboarding 迁移 Chrome 数据/改浏览器设置后，Chrome 某些网页功能异常（0827 实例：罗宾实时语音 AudioWorklet 在 Chrome 不工作，Firefox/手机正常；用户怀疑与当天装 ego 有关） | 排查此类问题时把"装过 ego"列入变量清单；对比测试 Firefox/其他浏览器先隔离是 Chrome 特有还是通用 |
| **VPS 跨机器用不了** | 杰西卡（VPS Hermes）无法用用户 Mac 的 ego | ego 是 Mac 本地应用，Agent 必须跑在同一台 Mac 本地。VPS 上 skill 无效 |
| skill"没看到" | 用户 ls 目录以为没装 | skill 是文件系统目录（~/.agents/skills/ego-browser），不是 App 界面里的东西；Codex 里输入 /ego-browser 有补全=已生效 |
| **反重力 Windows 不认这个 skill** | skill 放在 `~/.gemini/config/skills/` 和 工作区 `项目根/.agents/skills/` 两处都试过，SKILL.md 的 name/description 合规，重启 IDE、开 New Chat 后输入 `/ego` 仍显示 No matching results | 反重力的 skill 列表只在会话初始化时扫描一次不热重载，且对该第三方 skill 就不认。**绕过：这个 SKILL.md 的实质内容只有一条命令 `ego-browser skill`（打印匹配当前安装版本的使用指南）**——不用管 skill 加载，每次开反重力会话第一句让它先执行 `ego-browser skill` 并照输出做即可。若命令 not found，是 ego lite 没进 PATH |
| **反重力国内慢** | 界面响应、执行都磨洋工 | 走新加坡出口的网络问题，与 skill 加载/配置无关（skill 是本地文件不联网也能读）。慢时改派 Cursor 取证 |

## 设计工具取证（Figma 等）：先勘察结构、再读主组件，不读画板实例

用 agent 浏览器把一个设计库（Figma 组件库）抓成可用的规范数据时，顺序固定，且有一个最容易翻车的点：**读的是画板上的实例不是主组件**。实例只带当前那一份取值（常只有一个状态、字号可能抓到标题图层），主组件才有 Variants 全集和设计 token。

- 第一步只做**文件结构勘察**：Pages 列表 + 每个 page 下的组件分组层级 + 有没有批次/Done 标记。这一步最便宜也最有价值，能直接拿来做 gap 对照。
- 第二步**只取样 2 个**代表组件（一个表单控件 + 一个数据展示），把结构化格式发给用户确认，确认后才批量。
- 第三步才全量，且逐组件点进**主组件**看右侧属性面板的 Variants。
- 抓不到的项（外间距、某些状态的字体）一律写「未取得」，**不许拿通用设计规范去补**——补出来的数值比缺着更危险，它会被当成权威写进项目规范。
- 完整流程、三个「假数据」的识别特征、与项目规范库做 gap 对照的口径 → `references/figma-design-extraction.md`

**时长与规模，先把预期说清**：一个 30 组件的设计库，从零抓结构 + 取样 + 色板，半小时量级是正常的（canvas 应用只能逐页点、逐字段读）。**十几分钟没出结果不是挂了，别中途换工具重开**——换一次就是从头再来。真嫌慢不是换 agent，是换取数方式：

- **规模大就不要再扒 UI**：Figma 是 canvas 应用，DOM 里没有结构化数据，agent 只能从右侧属性面板的文字往上凑，慢且容易取错层（把画板尺寸当组件尺寸、把标题字号当正文字号）。整库要数据时应走 **Figma REST API**（URL 里的 file key + 个人 access token，一次拿到 component / variant / style 的结构化 JSON）或让设计侧用 tokens 导出插件出一份 colors/fonts/radius 的 JSON。
- **取证与归纳要分给不同的人**：跑得快、取数准但推理弱的那一类（快模型 + ego lite）只让它做**取证**——原文摘录、坐标、变体清单，明确写“不许归纳、不许总结、不许给建议”；“这些数值意味着什么、规范该怎么改”留给有推理能力的环节。混在一起派，取证准的那方会顺手给出一堆错结论。

## 模型切换联动（2026-08-27）

主模型切 GLM-5.3-Flash 后，Codex 内置的 "5.6 Sol 高" 档位显示的是 Codex 自身模型档，与 ego 无关——ego 只是 skill 徽章（蓝色 Ego Browser 出现在输入框上方 = 已激活）。指令照常发即可。

## 指令场景（条件触发式，用户 0827 定方向）

不是每个指令都加 ego——判据：

```text
✅ 加：需要登录态的网页操作（飞书/DS 后台/公众号/抖音后台）
✅ 加：JS 渲染/iframe/Shadow DOM（web_extract 拿不到）
✅ 加：需要真实操作（点击/填表/批量更新，停在提交前等确认）
✅ 加：竞品社媒数据抓取（X/LinkedIn，API 拿不到）
❌ 不加：纯代码开发/文档生成
❌ 不加：API 直接可得的数据（Tavily/web_search 能拿）
❌ 不加：VPS 侧任务（跨机器无效）
```

指令写法示例："数据获取优先级：API/web 检索 > ego-browser（遇到登录墙或 JS 渲染页面时用 ego-browser 继承本机登录态获取，不许伪造）"

## 行业定位（产品视角，用户 0827 判断）

- AI 浏览器两派：**人用 AI 内嵌**（Perplexity Comet 2025.7 活着但难、OpenAI ChatGPT Atlas 2025.10 推出已废弃）vs **Agent 专用浏览器**（ego = Agent-Native Browser）
- Atlas 死因=太过超前（AI 想当主驾驶，现实是 AI 还是工具、人必须主驾驶）
- ego 活因=人在回路产品化：提交前停、验证码拉人回来、Space 隔离——人判断、Agent 执行
- 这个判断本身是用户 PM 面试素材（谁死谁活为什么）

## 用户业务结合点

- forge-scrm 对标账号采集遇登录墙 → ego 补位（Tavily 拿不到的用登录态拿）
- 用户视障：Agent 用 ego 读登录后页面 → 返回文字总结 = "眼睛伸进登录后的页面"
