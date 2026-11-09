---
name: be-ui-framework-selection
description: B端系统UI框架选型——新项目启动时第一时间问用户选组件库组合，禁止Tailwind纯手搓。
---

# B端系统 UI 框架选型

> 2026-07-29 定稿：基于 forge 三件套实战 + copy-wms Arco Design 验证 + Vben Admin/Element Plus 调研。

## 触发条件

用户说"做新项目"或"开始新模块前端开发"→第一时间问：**React 还是 Vue？然后推荐组件库。**

## 铁律

**禁止 Tailwind 纯手搓 UI。** 反重力用 antd/Arco/Shadcn 画原型比手写 Tailwind 快 10 倍且好看。已有一个教训：forge-erp 全部 Tailwind 手写,UI 不精致。

**禁止让用户(PM)去搜代码/改文件。** 用户是产品经理不是开发者。排查问题只看自己 VPS 侧,出指令让 AI Agent 改。绝不说"你打开文件看看第几行"。

**改现有项目前必须先确认当前技术栈。** 不给反重力发任何指令,直到确认项目实际用的什么组件库(看 package.json,不靠猜)。2026-07-30 翻车: 猜 WMS 用 Element Plus,实际是 Arco Design——导致多轮无效修改。

## React 项目选型

| 框架 | 场景 | 说明 |
|------|------|------|
| **Ant Design + ProComponents** (首选) | 企业级 B 端 | ProTable/ProForm/Descriptions 开箱即用 |
| **Arco Design** (字节) | 设计感优先 | 紫色主题,Figma 风格 |
| **Shadcn/UI** | AI 驱动快速原型 | 源码拷贝,AI 友好 |

## Vue 项目选型

| 框架 | 场景 | 说明 |
|------|------|------|
| **Vben Admin** (首选) | 标准方案 | Shadcn/UI 核心,可插拔 Ant Design Vue/Element Plus/Naive UI |
| **Element Plus** | 轻量快速 | Vue 生态最流行 |
| **Ant Design Vue** | React 迁移 | API 对齐 React 版 |

## Ant Design 迁移关键坑

### ProForm 能力必须按 Agent 区分

反重力(Gemini/DeepSeek)多次无法稳定生成 ProFormText/ProFormSelect 等 ProForm 子组件，容易退回 antd 原生 Form.Item；给反重力的任务应提供完整 TSX 模板，或明确允许使用原生 Form.Item。

Codex/Cursor 不适用这条限制：目标明确要求 ProComponents 时，应直接使用 ProForm、ProFormText、ProFormSelect、ProFormDigit、ProForm.Group，并通过源码检查和 build 验证，不能因为反重力的能力上限主动降级。

**反重力无法完成 ProForm 时的退路:**
```tsx
<Form layout="vertical" onFinish={handleSave}>
  <Row gutter={16}>
    <Col span={12}>
      <Form.Item name="code" label="编码" rules={[{required:true}]}>
        <Input disabled={isEdit} />
      </Form.Item>
    </Col>
  </Row>
</Form>
```

### 表单居中
反重力会给表单外层加 max-w 容器→删除即可。antd Form 默认全宽。

### 列表页
ProTable 替代手写 DataTable+搜索栏+分页,反重力支持良好。

### 分步迁移

采用“样板对象 → 完整模块 → 全量页面”的三级阶段门：

1. 先选一个中等复杂度对象做样板，跑通 ProTable、ProForm、ProDescriptions、状态动作和数据层。
2. 样板验收后，先完成同一模块的所有对象；例如基础资料必须完整覆盖仓库、库区、货位、供应商、商品的列表/新增/编辑/详情/启停，不能样板做完就跳去库存等其他业务域。
3. 用户在本地浏览器集中截图验收完整模块，把视觉与交互问题合并为一轮返修。
4. 完整模块验收通过后，再把它作为唯一标准，让长目标 Agent 全量迁移其余页面。
5. 最后统一全局布局、公共组件、构建和 Cursor 交叉审计。

局部迁移期间，新旧页面并存是正常过渡状态：样板页可能已使用 `PageContainer + ProTable/ProForm/ProDescriptions`，其他模块仍是 Tailwind/手写表格。此时出现页面宽度、左对齐、筛选栅格不同，先判断是否属于“组件体系未迁移”而非单条 CSS 错误。

- 如果旧页面根容器明确有 `mx-auto`、`container`、`max-w-*`，可做局部布局修复。
- 如果组件本身没有这些限制，但仍呈现居中/收窄感，通常来自旧筛选栅格、固定列数和手写内容结构；不要用全局 CSS 强行抹平，应在该模块正式迁移时统一换成 `PageContainer + ProTable`。
- 截图只能证明视觉结果；构建产物/源码用于证明组件体系。两种证据要结合，不能因页面“像 AntD”就宣称已全量迁移。

### ProTable 标准工具栏不可误关

企业后台列表页使用 ProTable 时，默认保留三项标准能力：刷新、表格密度、列设置。推荐统一配置：

```tsx
<ProTable
  options={{ reload: true, density: true, setting: true, fullScreen: false }}
  toolBarRender={() => [<Button type="primary">新增</Button>]}
/>
```

常见误区：Agent 为了“简化页面”写入 `options={{ reload:false, density:false, setting:false }}` 和 `toolBarRender={false}`，结果虽然装了 ProTable，却缺少标准组件。除非产品明确要求，禁止关闭 `reload`、`density`、`setting`；业务新增/导出按钮应放在 `toolBarRender`，不能用 `toolBarRender={false}` 后另搭一套工具栏。

验收时不要只看组件库是否安装，要同时检查每个列表页的实际 ProTable props，并与标准样板对比。

### 本地截图验收闭环
前端 UI 迭代默认走短链路：Agent 修改本地源码 → 用户在 Mac 本地浏览器验收并截图 → Hermes 根据截图生成下一轮精确指令。样板阶段禁止每轮打包、上传 VPS 或远程部署验证；只有用户明确说“准备部署”后，才统一 build、审计、打包和部署。这样避免旧 dist、Vite 缓存、Nginx 残留文件干扰视觉判断。

### Build 缓存未清 → 旧代码残留
修改源码后 `npm run build` 出来的 dist 仍包含旧逻辑时,先清 Vite 缓存:
```bash
rm -rf dist node_modules/.vite && npm run build
```
原因: Vite 缓存了旧的模块图,源码改动未触发重新编译。反重力梭哈全量迁移后,源码已删的角色跳转逻辑可能在 bundle 中仍然存在。

### Dexie/IndexedDB 旧数据不刷新（高频坑）
Mock 数据首次加载通过 `bulkPut` 写入 Dexie。源码改了 mock 数据后,浏览器已有旧数据就不会重新灌入。

**修复:** F12 → Application → IndexedDB → `qs_inventory_db` → Delete database → 硬刷新。删除后数据自动回来= seed 逻辑重新灌入,说明不是数据问题而是渲染问题。

### ProTable valueType:'select' 渲染污染
ProTable 的 `valueType:'select'` 列会把 label(如`[SP-002] 晨光...`)赋给 cell value 传给 render 函数。编码列应删掉 valueType,直接用 `record.productCode`:

```tsx
{
  title: '商品编码',
  dataIndex: 'productCode',
  width: 110,
  render: (_, record) => <strong>{record.productCode}</strong>,
  // 不要 valueType: 'select'
}
```

### Nginx/VPS 旧 JS 残留(高频坑)

本地好 VPS 不好 → Vite 构建产物出现多个 index-*.js 文件(本应是 1 个):
```bash
ls /var/www/pmlophy.com/project/forge-erp/assets/index-*.js | wc -l
```
若 > 1 → 旧路由树残留(反重力梭哈时多次复制路由树)。
**修复**: 从所有 JS 文件中找出没有 bug 的那个(对比关键代码),然后改 index.html 指向它:
```bash
# 检查哪个 JS 文件没有 valueType:'select':
for f in assets/index-*.js; do
  echo "$(basename $f): $(strings $f | grep -c 'productCode.*valueType.*select')"
done
# 切换到 0 匹配的文件:
sed -i 's|index-旧文件名.js|index-干净文件.js|' index.html
```
Vite 单入口应只产 1 个 JS。若 > 1 → 源码层面删除重复路由树,不应靠切 HTML 修复。

### 迁移后验证: Cursor 交叉审计（推荐）

> 详细工作流与实战案例见 `references/anti-gravity-cursor-cross-audit.md`。

反重力/Gemini 生成快但毛糙——迁移后必须用 Cursor Agent 做只读审计:

```
@codebase 审计以下5项，只读不改:
1. 商品编码/供应商编码/仓库编码是否一致(不同 mock 文件间)
2. 路由定义是否重复(搜索 "basename" 出现次数)
3. 角色跳转是否只在 Login.tsx 一处
4. 所有页面文件是否都在路由中注册
5. Mock 数据源是否唯一(主数据是否双份定义)
```

**真实案例**: 反重力梭哈全量 antd 迁移后,Cursor 审计发现 P0 问题: 供应商编码 SUP001 vs VEND001 三处不一致、主数据双份定义、无角色路由守卫。同一个 AI 不会说自己错了,换一个就能发现。

## Forge 迁移顺序（以源码实查为准）

forge-wms 已于 2026-07-31 完成全量 React + Ant Design + ProComponents 迁移并通过部署验证。当前三件套状态：

| 项目 | 技术栈 | 设计风格 | 状态 |
|------|--------|---------|:---:|
| **forge-erp** | React + Tailwind (手搓) | — | 待迁移（WMS 完成后启动） |
| **forge-wms** | React + Ant Design + ProComponents | 对齐 ERP 视觉规范 | 全量迁移完成 ✅ |
| **forge-crm** | React + Shadcn/UI | 现代极简 | 规划中 |

下一阶段：以 WMS 为已验证模板，全局迁移 forge-erp 到 Ant Design + ProComponents。

完整迁移方法见 `references/react-handbuilt-to-antd-migration.md`。

## 跨项目一致性铁律

Forge 系列目标技术栈可以统一，但必须区分“当前源码事实”和“目标状态”。每次迁移前都检查 `package.json`、锁文件与组件源码；只有确实声明并使用依赖，才能称为 Ant Design 项目。

## WMS 视觉升级失败复盘(2026-07-30)

**根因不是 Vue/React 选错，而是未先实查源码与依赖、连续更换方案、没有稳定样板。** 后续审计确认原始 forge-wms 实际已是 React + TypeScript + Tailwind/手写组件，而不是早先误判的 Vue 3。

失败链:
1. 未读应用 `package.json` 就凭印象判断技术栈。
2. 连续尝试 Element Plus、Indigo、Arco、Ant Design Vue、React + Ant Design，多次改变目标。
3. 页面、全局布局和技术栈同时变化，无法通过截图定位问题，最终回滚。

修正方法:
1. 先读 git、package.json、锁文件、路由、目标模块和数据层。
2. 把当前栈、目标栈、参照栈分开；视觉参照不等于技术依赖。
3. 选择一个业务边界明确的基础资料对象做样板，只迁模块页面，暂不动全局布局。
4. Mac 本地截图验收通过后再推广；一个项目完成后再迁第二个项目。

**未来铁律**:
- 新项目从成熟 admin 模板起步，不让 Agent 裸搭设计系统。
- 现有手搓 React 项目按 `references/react-handbuilt-to-antd-migration.md` 分阶段迁移。
- Codex 负责摸底与样板实现，Cursor 负责全量审计和复杂收尾；反重力只承担模式明确的机械修改。
- 小模块先行→本地截图验证→逐模块推广→全局布局→审计→部署。

## Vue 项目详细指南

### Vben Admin 概览
- Vue 3 + Vite + TS + Monorepo(Turborepo)，31.5k⭐
- Shadcn/UI 核心 + 可插拔 UI 适配器(Ant Design Vue/Element Plus/Naive UI)
- 内置: 动态菜单/角色权限/暗色模式/i18n/按钮级权限/Nitro Mock
- 一个项目切换 UI 库不改业务代码

### Element Plus
- 饿了么出品，Vue 生态最流行(24k⭐)
- 清新蓝白设计，中小公司首选
- Vben Admin 内置 Element Plus 适配器