# DESIGN.md 模板

基于 Google Labs Code 的 `design.md` 格式。用于给 Coding Agent 持久化视觉约束。

## 结构

两层：YAML front matter（机器可读 token）+ Markdown 正文（人类可读 rationale）

## 必含字段

```yaml
---
name: 项目名
colors:
  primary: "#hex"
  success: "#hex"
  warning: "#hex"
  danger: "#hex"
  neutral-50 ~ 900: "#hex"
  status-xxx-bg/status-xxx-text: 各状态标签配色

typography:
  fontFamily: "PingFang SC, Microsoft YaHei, sans-serif"

rounded:
  card/button/badge/input: rem值

components:
  button-primary/button-outline/button-danger/status-badge/card/table:
    引用 {colors.xxx} token
---
```

## 强盛科技进销存项目实战

见 `/root/review/进销存Traininng/DESIGN.md`
