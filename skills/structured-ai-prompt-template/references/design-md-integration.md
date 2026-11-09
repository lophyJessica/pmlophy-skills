# DESIGN.md 集成 — 四层约束体系

Google Labs 开源的 DESIGN.md（github.com/google-labs-code/design.md）给 Coding Agent 提供持久化设计规范。与 AGENTS.md 分工：

| 文件 | 管什么 |
|------|--------|
| context/ | 业务事实、范围、规则 |
| AGENTS.md | 文档规范、已知坑、走查六维 |
| DESIGN.md | 颜色/字体/圆角/间距/组件 token |
| 五段曲红线禁止 | 本次任务边界 |

DESIGN.md 结构：YAML front matter（机器可读 token）+ Markdown 正文（人类可读 rationale）。

## 实战应用

进销存项目 DESIGN.md 定义 6 个状态标签配色（草稿灰/待审核橙/待入库蓝/部分入库浅蓝/已完成绿/已作废红），反重力生成 PR/PRO/PI 时直接引用 token，杜绝配色漂移。

## 反重力指令集成

每次前端生成/修改指令的红线禁止加入：
```
- 配色/字体/圆角只引用根目录 DESIGN.md token，不自造
- 修改设计前先确认是否需更新 DESIGN.md 源文件
```
