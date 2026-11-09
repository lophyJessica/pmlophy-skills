# DESIGN.md — AI 视觉约束层

Google Labs Code 开源格式。用一份 DESIGN.md 给 Coding Agent 持久化设计规范，防止跨会话 UI 风格漂移。

## 结构

- YAML front matter: token 级设计值（颜色/字体/圆角/间距）
- Markdown 正文: 设计 rationale（为什么用这个色、怎么用）

## 在约束体系中的位置

```
context/ → AGENTS.md → DESIGN.md → 红线禁止
  业务        文档        视觉        边界
```

第一次锁视觉，后面各模块配色天然一致。

## 与 AGENTS.md 的分工

AGENTS.md 管"怎么跑"（命令/规范/已知坑），DESIGN.md 管"长什么样"（配色/字体/圆角）。

## 项目实战

进销存 DESIGN.md 锁定了 6 种状态标签色 + 主操作色 + 字体栈 + 组件规格。反重力后续模块引用同一份，配色不再张冠李戴。
