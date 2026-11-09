# React 手搓后台迁移到 Ant Design + ProComponents

## 适用场景

现有 React + TypeScript + Vite 项目业务可运行，但 UI 由 Tailwind、自制 Table/Form/Pagination/Layout 组成；目标是在不推翻业务和数据层的前提下迁移到 Ant Design + ProComponents。

## 先审计，后编码

1. `git log -5 --oneline` 与 `git status --short`，只报告未提交内容，不清理。
2. 读取当前项目 `package.json`、锁文件、路由、布局、目标模块、公共组件、类型、API/Dexie。
3. 读取参照项目 `package.json` 和代表页面，区分“真实技术参照”与“仅视觉/信息架构参照”。
4. 列业务对象、路由、字段、规则、数据源和缺口；推荐一个复杂度适中的样板对象。

## 样板选择

优先选择：
- 业务边界明确，不涉及跨系统 SSOT 争议；
- 有列表、查询、新增、编辑、详情、状态切换；
- 有一层主数据引用，能验证下拉候选和保存校验；
- 复杂度适中，可复制到同模块其他对象。

避免首个样板：双层级联、库存占用、跨系统同步、复杂状态机。

## 第一轮只改模块页面

- 正式把 `antd`、`@ant-design/pro-components`、`@ant-design/icons` 写入应用 package.json/锁文件。
- ConfigProvider 只接入浅色主题和 locale。
- 列表用 PageContainer + ProTable。
- 新增/编辑用同一个 ProForm 页面；编码编辑态只读。
- 详情用 ProDescriptions。
- 保留原路由模式、业务服务和唯一数据源。
- 暂不迁移全局 Sidebar/TopNav/AppShell，避免页面和框架同时变化导致截图难定位。

## 本地验收闭环

Agent 修改并 build → 用户在 Mac 本地浏览器依次截图列表、新增、编辑、详情 → Hermes 根据截图出下一轮指令。样板阶段不反复压缩 dist、上传 VPS 或部署。

## 推广顺序

样板通过 → 同模块其余对象 → 核心业务模块 → 全局布局/主题/公共组件 → Cursor 全量审计 → 本地完整验收 → 统一构建与部署。

多项目迁移时单线程：先把一个项目做成成熟 AntD 样板，再用已验证的主题和组件规范迁移第二个项目；不要两个项目并行试错。

## 红线

- 不创建第二套 Mock、Dexie 或路由树。
- 不顺手补未确认业务规则。
- 不修改参照项目。
- 不清理未跟踪文件或未提交改动。
- 不 commit/push，不部署，除非用户明确授权。
