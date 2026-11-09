# 强盛科技 DESIGN.md — 视觉约束文件

## 什么时候加

- 任何超过 3 个页面的前端项目，在第一次生成前端之前创建
- 放在项目根目录，与 AGENTS.md 同级

## 文件结构

YAML front matter（机器可读 token）+ Markdown 正文（人类可读 rationale）。

最小必须包含：
- `colors` — 主色/成功/警告/危险/中性色阶 + 各状态标签配色
- `typography` — 字体栈/h1/h3/正文/标签/表头/金额字号
- `components` — 按钮/卡片/表格/标签/Tab 的 token 引用

## 使用方法

1. 参照已有前端实际代码提取颜色值
2. 按 DEMO PRD 的状态配色表填入状态标签颜色
3. 在反重力指令的红线禁止段中加一行：
   `- 配色/字体/圆角只引用根目录 DESIGN.md 中的 token，不自造`

## 与 AGENTS.md 的分工

| 文件 | 管 | 
|:--|:--|
| AGENTS.md | 项目怎么跑、别碰什么、PRD怎么写 |
| DESIGN.md | 颜色/字体/圆角/间距/组件风格 |

## 完整示例

见 `/root/review/进销存Traininng/DESIGN.md`（强盛科技进销存实际使用的 DESIGN.md）
