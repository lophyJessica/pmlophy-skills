# Figma MCP 速查 (2026-07)

## 一键安装
```bash
npx @anthropic/figma-mcp --scope user
```

## 认证(Claude Code)
1. 开 Claude Code → `/mcp` → 选 "figma" → "authenticate"
2. 浏览器弹窗授权 → 完成
3. 不需要 API Key,OAuth 全自动

## 验证
在 Agent 粘贴 Figma 链接: "读取这个 Figma 文件: https://..."

Agent 应能列出页面、Frame、组件。

## 可用Agent
Claude Code / Cursor / VS Code / GitHub Copilot / Gemini CLI / Codex 等 10+ MCP 兼容 Agent。
Hermes 原生不支持 MCP 协议。

## 85% 规则
Agent 生成设计准确度约 85%:
- 正确:布局/层级/文字/基本颜色
- 需手动修:间距(2-4px偏差)、字重、圆角、图层命名

## 最大坑
不加约束 Agent 会硬编码所有颜色和间距 → 必须让 Agent 引用设计系统 Variables,不能写死 hex 值。
