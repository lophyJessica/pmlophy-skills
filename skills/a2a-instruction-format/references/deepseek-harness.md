# DeepSeek Harness (dsh) — 接入与使用（2026-08-14 实测）

DeepSeek 官方的开源 Agent Harness（MIT，`github.com/deepseek-ai/deepseek-harness`），2026-08-13 发布 v0.1 开发者预览版，理念"一切皆插件"（内核 Cordis，来自 Koishi 聊天机器人框架——插件热插拔 + 可逆副作用）。定位 = Agent 基建/平台，不是又一个 Claude Code——四个官方模式只是四份插件配置清单。

## 安装与启动（Mac 本地，不走 VPS）

```bash
node -v        # 需 v18+（用户 Mac v22.23.1 OK）
npx @deepseek-ai/dsh web    # 首次启动拉包慢（国内直连 npm）——下载类操作先切机场加速
# 启动后浏览器打开 http://127.0.0.1:3080
```

- **只在本机跑**（127.0.0.1）——dsh 能读写工作区文件，暴露公网=灾难（无鉴权）。
- 每次启动都要 npx（临时执行）。想省事：`npm install -g @deepseek-ai/dsh` 后 `dsh web`；或做桌面双击脚本。不建议常驻（Node 进程占内存，用户"按需跑"原则）。

## 四种模式（= 四份插件清单，不是四个产品）

| 模式 | 内容 | 用在哪 |
|---|---|---|
| 标准模式 | 完整工具集（文件/shell/搜索/技能/计划/子agent/工作流） | 日常——小白无脑选 |
| PTC 模式 | 标准能力 + 模型写一段 TS 代码一次组合 N 次工具调用 | 多步骤/可并行操作，省 token 省往返；调试难，先别碰 |
| 极简模式 | 只留 bash + 文件编辑器 2 工具，固定极简 system prompt | 模型裸能力基准测试，日常没法用 |
| 创造模式 | 标准能力 + 检查运行时/内存试验 Cordis 插件/造新模式 | 最核心——Agent 现场造插件插自己（"发现没扳手→现场造一把插手上"） |

## 模型接入（关键：用户退款了 DS API——接 Go 通道白嫖）

dsh 默认要求 DeepSeek API key，但**支持自定义 OpenAI 兼容端点**——接 OpenCode Go：

```
Settings → Models → 添加自定义提供商:
  Base URL: https://opencode.ai/zen/go/v1
  API Key:  <OpenCode Go key>（opencode.ai 控制台复制）
  模型:     deepseek-v4-flash（或 mimo-v2.5 等 Go 模型）
```

验证：选工作区（项目目录）→ 发消息"读取当前目录结构"→ 能回复即通。实测 dsh 会读 AGENTS.md 红线（不 commit/push、报告归档 check-reports/），理解准确。

## 社区插件（24h 内 288 个仓库——dsh-plugin topic 可发现）

实用推荐：
- `dsh-at-file` — 输入框 @ 调文件
- `dsh-genui` — 回复里渲染图表/表格/Diff/Mermaid
- `dsh-automation` — 补自动化能力
- `DSH-better-sidebar` — VS Code 式侧边栏（文件/终端/Git/Diff）
- `ModLens` — 给纯文本模型补视觉（桥接 OpenAI 兼容视觉模型）

有趣的生态现象（理解即可）：皮肤/桌宠/小游戏插件、广告插件 vs 去广告插件互相攻防、dsh-cc-tui 把界面换成 Claude Code 风格、可导入 Claude Code 会话历史续聊——本质是"harness 品类开源化"，不卖缰绳卖地基。

## 注意

- v0.1 预览版：破坏性变更预期，**生产依赖不要用**——当玩具/研究工具，主力仍是反重力(UI)/Codex(批量)/Cursor(审计)。
- Trajectory 追记式会话日志（模型看到的一切可复盘/分叉/回放）——做研究/调试有价值。
- 官方文档：deepseek.com/harness/ ；`npx @deepseek-ai/dsh web` 一分钟起。
