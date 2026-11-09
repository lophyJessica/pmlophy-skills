# WMS 全量梭哈指令模板

## 适用场景
基础资料样板验收通过后，将 WMS 剩余全部页面一次性迁移到 Ant Design + ProComponents。

## 关键原则
- 用 Sol 长目标模式：一条指令包含所有模块、所有页面、所有规范。
- 分为六个阶段顺序执行：全局布局 → 工作台 → 入库 → 出库 → 库存 → 操作支持 → 全局清理。
- 每个阶段明确列出所有页面、字段、组件、交互和红线。
- 禁止拆成多次碎片化请求。

## 指令结构
```
Context: 项目路径、基础资料完成状态、技术栈、参照物。

Request: 分六阶段。
一、ProLayout 全局布局（替换 AppShell/Sidebar/TopNav）
二、工作台（Dashboard 统计卡片 + 快捷入口）
三、入库管理（收货单列表/详情/新增/PDA 上架模拟）
四、出库管理（波次/拣货/复核/包装/交运）
五、库存管理（查询/流水/预警/盘点/报损/调拨）
六、操作支持 + 全局清理（删除旧 Tailwind 组件）

每阶段列出所有路由、字段、组件标准。

红线禁止:
禁止修改基础资料、HashRouter、Dexie 结构、业务规则。
禁止保留旧手搓组件。
禁止关闭 ProTable reload/density/setting。
禁止 toolBarRender={false}。
禁止新建项目或脚手架。

Checkpoint: 全部页面迁移完成、npm run build 通过、无旧组件残留。
```

## 标准配置模板
所有 ProTable 页面统一：
```tsx
options={{ reload: true, density: true, setting: true, fullScreen: false }}
```
所有 ProForm 使用 ProFormText/ProFormSelect 等子组件，不退回 Form.Item。
所有 ProDescriptions 详情页字段两列布局。
操作列 fixed: "right"，有序排列。
状态标签：启用 green，停用 default，异常 red。
