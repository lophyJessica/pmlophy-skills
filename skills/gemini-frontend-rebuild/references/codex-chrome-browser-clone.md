# Codex @chrome 浏览器复刻能力

> 2026-07-19 — Codex 内置 `@chrome` 能力,可操控浏览器访问目标页面,自动抓取布局/配色/交互,生成 React 代码复刻前端页面。

## 用法

在 Codex 中输入 `@chrome https://目标URL` → Codex 自动:
1. 打开浏览器访问目标页面
2. 分析 DOM 结构、CSS 样式、交互行为
3. 生成 React + Tailwind 复刻代码
4. 支持多页面批量复刻

## 对比传统 UI 微调

| 传统方式(Gemini) | Codex @chrome |
|---|---|
| 用户截图→文字描述→Gemini猜→改歪→再描述 | 直接读取页面→生成代码 |
| 多轮迭代,每轮都有偏差 | 一次生成,接近原版 |
| 依赖用户描述准确性 | 依赖页面可访问性 |

## 其他 Agent 的浏览器控制

| Agent | 浏览器能力 | 需要配置 |
|-------|----------|---------|
| Codex | 内置 `@chrome` | 零配置 |
| Claude Code | browser-use MCP / Playwright MCP | 需安装和配置 |
| Cursor | browser-use MCP | 需配置 |
| 反重力 | 无内置 | 需 browser-use 桥接 |

## Forge 项目应用

- copy-wms: Codex @chrome 参考 WMS 系统页面,生成 React 复刻版(v1.0 已部署)
- 可用于快速克隆竞品页面做产品分析
- 面试演示:展示"用 AI 复刻竞品系统"的能力
