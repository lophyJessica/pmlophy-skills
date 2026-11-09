# DESIGN.md：AI Agent 视觉约束层

## 问题

反重力跨会话/跨模块生成 UI 时，配色、字体、圆角漂移。昨天 PO 列表页 13 个配色 bug 就是没有视觉约束导致的。

## 解法

项目根目录放 `DESIGN.md`（Google Labs Code 开源格式），YAML front matter 定义 token（颜色/字体/圆角/间距），Markdown 正文写 rationale。

## 四层约束体系

| 层级 | 文件 | 管什么 |
|:--|:--|:--|
| 🏗 业务 | `context/` | 做什么/不做什么/规则/术语 |
| 📋 文档 | `AGENTS.md` | PRD怎么写/已知坑/走查标准 |
| 🎨 视觉 | `DESIGN.md` | 颜色/字体/圆角/间距/组件(token级) |
| 🚦 执行 | 五段曲红线禁止 | 本次任务边界/不改什么 |

## 给反重力的指令

在五段曲红线禁止中加：
> 配色/字体/圆角只引用项目根根目录 DESIGN.md 中的 token，不自造。

## 示例

见 `/root/review/进销存Traininng/DESIGN.md`——强盛科技进销存项目完整 DESIGN.md。

## 开源地址

https://github.com/google-labs-code/design.md
npm: @google/design.md（含 lint/diff/export 工具）
