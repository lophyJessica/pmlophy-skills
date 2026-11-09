# 全局 UI 统一调整指令（B 端 antd 裸拼 → 统一规范）

> 用途：用户吐槽"UI 丑/像手搓的"时，给 Cursor（快模型如 Grok 4.6）的全局 UI 统一指令。
> 使用前：确认参照目标路径（写死，如 `~/个人文件/copy-wms`）+ 参照设计主色（copy-wms = 紫色 #7c3aed）。
> 跑法：先贴主题项确认全站变色 → 再分批贴操作栏/表格/表单项，每批 build 验证。

```text
Context：你在 <项目路径>/frontend。
当前前端是基础 antd 5 裸拼风格，操作栏混乱、Tag 颜色不统一、观感像手搓的。
参照目标：<参照项目绝对路径> 的 UI 设计——<主色描述，如：紫色主色（#7c3aed / violet-600）、
卡片化布局、清爽状态色>。动手前先打开参照项目的页面源码看一遍它的视觉语言（主色、卡片、
圆角、状态色用法），再回来改本项目。
本轮做【全局 UI 统一调整】，不动业务逻辑，只统一视觉和交互规范。

Request（请全局扫描 frontend/src/ 下所有页面，统一以下规范）：

1. 全局主题（最重要，先做）：
   - 在应用入口（App.tsx 或 main.tsx）给 antd ConfigProvider 配主题：
     colorPrimary: '<主色十六进制>'（对齐参照项目），borderRadius: 6，
     全站按钮/链接/选中态/焦点变主色系；
   - 侧边栏/菜单保持深色，选中态用主色。

2. 操作栏统一：
   - 表格操作列：编辑/删除按钮统一 Button size="small" 间距 8px；
   - 删除按钮统一 danger（红色文字/边框）；
   - Switch 类开关移到状态列内（状态列 = Tag + Switch）；
   - 操作按钮超过 2 个用 Dropdown「更多」收纳。

3. 状态 Tag 统一色板（全局一致）：
   - 启用/已通过/已生效/已完成 → green
   - 停用/已废弃/失败 → red
   - 待审核/待筛选/进行中/执行中/检索中/整理中 → orange
   - 草稿/待执行 → default；部分成功 → gold
   - 所有页面状态 Tag 必须用这套色板，不允许每页自定义颜色。

4. 列表页骨架统一（保持基础 antd，不引入 ProComponents）：
   - 页面 = Card（title 页面名）+ 顶部筛选区（Space 包裹，查询/重置）+ Table + 分页；
   - 长文本列（正文/描述）ellipsis + Tooltip；分页靠右；列宽合理设置。

5. 表单页统一：Form layout="vertical" + maxWidth 720；提交按钮右下，取消在左。

6. 弹窗统一：Modal 宽度常规 520 / 多字段 720，footer 右对齐。

红线：
- 只改 frontend/src/ 下页面 JSX 样式/布局/组件用法 + 入口主题配置；
- 禁止改业务逻辑、API、状态机、数据结构、路由；
- 禁止新增依赖（不上 ProComponents，除非用户明确要求）；
- 每改一类跑一次 npm run build 确保不报错；
- 不 commit/push。

Output：
1) 改了哪些页面清单；2) 每类统一做了什么（附主色主题生效说明）；3) build 结果。
自检结果存 check-reports/2026-08-26-全局UI统一自检报告.md。
```
