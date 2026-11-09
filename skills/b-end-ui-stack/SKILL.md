---
name: b-end-ui-stack
description: B端系统前端技术栈选型与迁移——React/Vue组件库组合、禁止Tailwind手搓、Ant Design迁移清单、Gemini坑点。
---

# B 端 UI 技术栈

## 初始化铁律

新 B 端项目第一时间问用户选 React 还是 Vue,按组合选组件库,**禁止 Tailwind 纯手搓**。

| 技术栈 | 组件库 | 适用场景 |
|------|------|------|
| React | Ant Design + ProComponents | B 端首选,ProTable/ProForm 开箱即用 |
| React | Shadcn/UI | AI 友好,源码拷贝理念 |
| React | Arco Design | 字节出品,紫色系设计感 |
| Vue | Vben Admin(Shadcn/UI 核心) | 可插拔 Ant Design Vue / Element Plus / Naive UI |
| Vue | Element Plus 原生 | 国内 Vue 生态最流行 |

## 复刻已有系统：原系统用什么组件库就用什么，绝不替换

**这是"有源码还样式对不上"的唯一根因。** 拿到源码复刻时，最容易做错的不是样式值，而是**把原系统的私有/特定组件库换成另一个通用库**——以为"都是移动端/都是后台，差不多"，实际 DOM 结构、默认尺寸、按钮皮肤、Tab ink 与滚动、搜索框形态全不一样，等于把原件拆成零件重新拼，再怎么调样式都对不上。

规则：

- 源码 `.vue` / `.tsx` 文件**原样搬**，组件名与全部属性照拄，不自创替代品。
- 私有组件库先验证能不能装（内部 registry / 私有源），能装就必须用真的。
- 唯一允许改的是**平台能力层**（原生桥、扫码、剪贴板、保存到相册）：换成浏览器 mock，因为环境没有那些 API。
- 数据层走本地 mock，接口函数保留源码入参出参结构。

**诊断顺序（别一上来调样式）**：① 浏览器数原组件节点，`document.querySelectorAll('[class*=fos],[class*=nx-]').length`——为 0 就是被替换了，问题不在样式；② 查组件库样式的注入方式（有的靠 babel import 按组件注入，不需要手动引 css）；③ 最后才验单位换算。

具体案例与私有组件库清单见 `references/私有组件库复刻.md`（vivo VOS `@vivo/vos-ui` 一套，可直接当模板对照）。

**源码能跑就先跑源码**：能装依赖、能起 dev server 的话，跑起来的真实渲染比"照代码搬"更准——可以直接对 computed style 和 DOM 取值，也可以用来判断原型差在哪。缺登录态也不影响看布局与控件形态，只是数据空态。

## 同构页面复刻到第 3 个起：先反抽 UI 规范 + 公共组件，再继续复刻

一个后台模块里连着复刻多个同构列表页/表单页时（订单、商品、赠品、活动…），从**第三个页面**开始成本就不再是「多写一页」，而是每页重写一遍筛选区、状态页签、表格、按钮，并且每轮给 agent 的指令都要把同一套形态再描述一遍。判据：同一批 `*-filter-*` / `*-table` / `*-btn` 类名在三个以上页面各写一遍，就该停下来抽了。

做法固定为「反抽、不新造」：

1. **先出 UI 规范文档，从现有 CSS 读实**：颜色、字号、间距、控件高度圆角、按钮形态（主/次/文字链）、表格表头与单元格内边距、空态、分页、表单标签与必填星号，每一条都标出处（文件或类名）。写不出出处的不写——凭印象编一份规范，后面每页都对不齐。产出放项目文档目录（如 `<项目>/03-产品设计/UI规范库/`），属产品/设计口径，不进 `src`。
2. **先建组件、不动旧页**：组件放 `src/components/<domain>/`，复用现有类名与 CSS，视觉零变化。旧页在新一轮触碰时再迁，不搞一次性全量重构——已验证过的页面被重构坏，返工比手工抽组件贵得多。
3. **组件边界按「一遍遍重写的东西」划**：筛选区（字段配置数组驱动）、状态页签、表格（列配置 + 空态 + 横向滚动）、状态圆点、表单字段（必填 + 字数统计）、弹窗外壳。弹窗先看有没有既有基础弹窗可包装，别另起一套遮罩与动画。
4. **两套类名前缀先收敛再抽**：老页面常用旧前缀（如 `xxx-shop__*`）、新页面用新前缀（`shop-*`），取值一致但类名不同。抽组件前先在规范里定「新代码一律用哪个」，否则抽出来的组件和旧页混着用，反而多一层。
5. **验收看「新页面还写不写样式」**：新页面复刻只允许「引用组件 + 填字段」，出现新写的 `filter` / `table` / `btn` 类名即视为没抽到位。

配套：规范里单独留一节「待收口清单」，把这次不做但已知的差异（分页形态、状态色未取证、旧前缀）写进去，避免每轮复刻都有人顺手改一下，越改越散。

## 移动端 H5 原型的视口（桌面浏览器里看真机效果）

原型要在桌面浏览器里模拟手机，四个条件缺一不可：

- **容器 `max-width: 375px` 居中 + 两侧淡灰底**；
- **容器上有 `container-type: inline-size`**；
- **PostCSS 用 `cqw` 不用 `vw`**（`viewportUnit` 和 `fontViewportUnit` 都改）；
- **所有路由都包在同一个容器里**——常见错误是只包了首页那层，其他模块是独立路由直接挂在 router-view 下，结果首页好好的、其他页面全宽铺开。

只用 `vw` 时换算基准是桌面窗口宽度，元素整体放大；只限 `max-width` 却没设 `container-type` 时 `cqw` 退回按视口算，同样失效。验证一行：`getComputedStyle(document.querySelector('.mobile-viewport')).containerType` 返回 `inline-size` 才算生效。

`position: fixed` 的顶栏/底栏/浮层在容器内会相对浏览器窗口定位、横跨整屏——给容器加 `transform: translateZ(0)` 建立新的包含块才能圈进 375px。

## 三项目矩阵（2026-08-14 用户定稿——forge 系当前技术栈）

- **forge-erp** = React + Ant Design + ProComponents（企业稳重）
- **forge-wms** = 原定 Vue3+ElementPlus → **已迁 React + AntDesign（与 ERP 一致）**（实现问题驱动——WMS 和 ERP 共用组件体系更省力）
- **forge-crm** = **React + Shadcn/UI（现代极简）——0814 反重力全量重构完成**（18 页，从纯 Tailwind 手搓重构；保留 erpSync.ts 集成层 + Dexie + 路由，只换 UI 组件层）
- **forge-scrm（0826）** = React 18 + antd 5 **裸拼（无 ProComponents）**——页面各写各的（操作栏/表格/表单风格不统一，观感"像手搓的"）。重构方向：ProComponents（ProLayout/ProTable/ProForm）统一骨架；**用户 UI 参照目标 = copy-wms 的紫色 Tailwind 设计（主色 #7c3aed / violet-600）**——antd ConfigProvider colorPrimary 配 #7c3aed 对齐。copy-wms 在用户 Mac = `~/个人文件/copy-wms`。
- 表单必须用 ProForm 子组件（ProFormText/Select/Digit），不用原生 Form.Item（ERP/WMS 用 antd 时）

## 全量重构前端的原则（0813-0814 CRM 重构决策）

**重构 ≠ 复制项目**：用户明确不要复制一份再改（像 copy-wms 那样）——现有项目里有珍贵集成资产（如 CRM 的 `src/api/erpSync.ts`——CRM→ERP 客户自动同步、Dexie 对齐 ERP schema、转客户→ERP 客户列表已打通），复制一份这些集成要重做、风险大。**正确姿势：直接重构现有仓库（git commit 就是备份——重构前打基线可回滚，不需要物理复制）**。

**重构指令必须划清保留区 vs 重构区**：
- 保留：`src/api/`（含 erpSync.ts 等集成）、`src/db.ts`/Dexie schema、路由结构、页面清单、业务逻辑（状态机/动作按钮驱动）
- 重构：UI 组件层（Tailwind 手搓 → 目标组件库 Button/Card/Table/Dialog/Form/Tabs/Select 等）
- 给 agent 的指令里逐条列保留文件（erpSync.ts 绝对不能动/删/重写），否则反重力/Cursor 重构时会顺手"优化"掉集成逻辑
- **重构后必须回归验证非业务属性（0814 实测）**：重构会丢掉页面组件里的 `data-anno` 标注锚点（9 个全丢→标注 runtime 按钮在但点不动）——给重构指令加"保留 data-anno 锚点"红线 + 验收清单含标注功能回归。详见 prototype-annotation-workflow skill「重构后标注功能失效」节。

Shadcn/UI 落地命令（CRM 用）：
```bash
npx shadcn@latest init   # 选默认配置（Tailwind 兼容）
npx shadcn@latest add button card table dialog form tabs select input badge alert dropdown-menu label separator skeleton
```

## Ant Design 迁移清单

从 Tailwind 手写 → 组件库的标准化做法:

- 列表页 → `ProTable`(自带搜索/分页/工具栏)
- 表单页 → `antd Form + Form.Item + Row/Col` 两列布局
- 详情页 → `Descriptions + Table`
- 弹窗 → `Modal.confirm`
- 状态标签 → `Tag`
- 表单全宽,不加 `max-w-*` 居中容器

### antd Select 收起态展示坑（0826 用户纠正）

**`optionLabelProp="shortLabel"`（收起态显示自定义短字段）会被用户嫌弃\"选完就变成四个字了\"**——长文本选项（如提示词模板，几百字）收起态只显示短名（如\"选题生成\"），用户要求\"正常截断就行了\"。**正确做法：options label 直接用完整内容（`${task_type}：${content}`），不设 optionLabelProp——antd 自动单行 ellipsis（省略号）截断；下拉展开用 `optionRender` 渲染多行完整内容（`whiteSpace:'normal'`）+ Tooltip 悬浮全文**。教训：长文本选项的收起态，用户要的是\"截断预览\"不是\"极端缩减\"；下拉展开和悬浮才是看全文的地方。

## 全局 UI 统一调整模板（用户吐槽\"UI 丑\"时用）

B 端项目被吐槽\"UI 丑/像手搓的\"时，给 Cursor（Grok 快模型）+ 用户选定的参照设计出一份**全局 UI 统一指令**：主题色对齐参照目标 + 操作栏规范 + 状态 Tag 统一色板 + 列表页/表单/弹窗骨架统一。完整可复制指令见 `templates/global-ui-unify.md`。要点：
- **先问用户参照目标**（如 copy-wms 紫色风）再写指令，参照路径写死（`~/个人文件/copy-wms`），别写\"或 forge-wms\"候选让 AI 自己猜。
- 分批跑：先主题（确认全站变色）→ 再操作栏/表格/表单分页跑，每批 build 验证；快模型（Grok 4.6）一次别碰太多页面。
- 状态 Tag 色板必须全局一致（启用绿/停用红/待审核橙/草稿 default/部分成功 gold），不允许每页自定义颜色。

## Gemini (反重力) 已知坑

1. **ProForm 子组件不来**: ProFormText/ProFormSelect/ProFormDigit 多次未生成。改用 antd 原生 `Form.Item + Input/Select`。
2. **梭哈产生重复路由树**: 全量迁移后 bundle 出现 3-12 套重复路由树,检查: `strings assets/*.js | grep -c "project/forge-erp"`。
3. **乱加角色重定向**: Gemini 在路由保护组件中加 SUPPLIER→supplier-quotations 跳转。排查: 先检查 localStorage `auth_role`,再 grep 源码确认。
4. **ProTable valueType:'select' 编码列陷阱**: 编码列配置 `valueType:'select'` + `fieldProps:{options:[{label:'[SP-002] 晨光...',value:'SP-002'}]}` 时,ProTable 用 label 替代 cell value。**只改 render 无法修复**——必须删除 `valueType` 和 `fieldProps`,然后用 `render:(_,r)=>r.productCode`。排查: `strings assets/*.js | grep -oP 'productCode.{0,50}valueType.{0,50}'`。
5. **新建项目不自查**: Gemini 现在会先做可行性评审(NPM包是否存在、路径兼容性、重构成本),不再埋头改。引导它先分析再动手。

## 前端白屏排查（点击某页面空白 = React 渲染崩，0813 ERP 实测）

**症状**：页面能登录、主工作台正常，点某个菜单（如销售订单）→ 全白，console 有 JS 异常但 message 为空（React 渲染错误不吐 message）。

**根因模式（先想这几种）**：
1. **渲染期同步调用抛错**：组件顶层直接调 API（如 `const customers = salesApi.getCustomers()`），内部 `throw new Error(...)` → React 渲染崩 → 白屏（无 error boundary 时整树卸载，`#root` 空）。
2. **数据/代码不一致（编码迁移未同步）**：商品编码体系从 SKU-xxx 迁到 SP-xxx，但 `initialOrders()`/种子数据仍引用旧编码 SKU001 → `getSalesOrders` 读订单时校验商品存在 → throw → 白屏。**编码迁移后必须全局搜旧编码引用（含初始数据/种子/mock），不能只改商品表**。
3. Dexie 表不存在/schema 不匹配（较少见——readTable 有缓存兜底通常不崩渲染）。

**排查路径（浏览器实测，不靠猜）**：
- `browser_navigate` 打开 → 登录 → 点出问题的菜单；`browser_console` 无表达式抓 `js_errors`（message 常为空——不够用）
- **注入全局错误监听再内部导航**（React Router 内部跳转不刷新页面，监听器保留在 window 上）：
  ```js
  window.__errs = []; const oe = console.error;
  console.error = function(){ window.__errs.push({type:'console.error', args:Array.from(arguments).map(a=>a&&a.message?a.message:String(a)).join(' | ')}); oe.apply(console,arguments); };
  window.addEventListener('error', e=>window.__errs.push({type:'window.error', msg:e.message, stack:e.error?String(e.error.stack).substring(0,600):''}));
  ```
- 然后 `browser_click` 点菜单（内部导航）→ `browser_console` 读 `JSON.stringify(window.__errs)` → **拿到真实错误+堆栈**（如 "Uncaught Error: 商品 SKU001 不存在" + bundle 内函数链）
- 堆栈定位后到源码找对应函数（grep 错误文案如「商品」→ `createSalesOrderItem` 的 `getSalesProducts().find(...)` throw）
- 用 `browser_console` 表达式直查 IndexedDB 验证数据假设（如 `products` 表 codes 列表 vs 订单引用编码是否对得上）
- 修复后**必须浏览器实测复现路径**（登录→点菜单→页面有内容 + `document.querySelector('table')` 存在 + body 无错误文案），不能只看 HTTP 200。

## 品牌口径统一清理（0814 强盛科技→Forge 实战）

品牌口径切换（如"强盛科技"→"Forge"）时，残留往往比预想多，**三处都要清**：

1. **前端代码**：页面文案 + db.ts/种子数据里的品牌名。`grep -rn "旧品牌" src/` 逐个清（注意 sed 全局替换后还要再 grep 一遍确认 0 残留——常有一两处藏在放弃原因/占位符/邮箱里）。
2. **PRD 文档**：业务背景/示例数据/用例推演里的旧名（`grep -rn "旧品牌" --include="*.md" .`）——往往比前端还多（0814 前端 14 处，PRD 23 处）。
3. **AGENTS.md 品牌口径段**：不更新的话下次 agent 又按旧口径生成。**品牌口径变更要同步改 AGENTS.md**——只清代码不清规范，agent 会持续引入旧名（0814 教训：AGENTS.md 一直写"强盛科技=演示公司名并存"，拖到用户点名才改）。
4. **清完验证**：`grep -rn "旧品牌" --include="*.tsx" --include="*.ts" --include="*.md" . | grep -v node_modules | grep -v ".git/" | wc -l` 应为 0。

**git 协作节奏（用户 0814 定）**：用户先 commit（打基线）→ 我 pull → 我改 → 我 push → 用户 pull。我改之前先 pull、push 前用户已确认（先 pull 再 push 铁律）。

## 交叉验证审计

反重力(生成) + Cursor(审计)——同一个 AI 不会说自己错了,换另一个能发现前者漏掉的问题。
2026-07-30 实战: Cursor 审计发现 SUP001 vs VEND001、主数据双份、路由守卫缺失等 10+ 问题,5 次 commit 全量修复。

## PM 铁律: 不让用户改代码

用户是 PM(不是开发者),绝不要求用户"打开文件看看第几行""搜一下源码""改一下 render"。
诊断问题 → 给反重力/Cursor 精确指令 → 它们执行代码修改。
如果非技术 PM 遇到同样问题,上述操作等于 rm -f。

## VPS 部署诊断(本地好 VPS 不好)

优先顺序: 清浏览器缓存 → 清 IndexedDB → 检查 VPS JS 文件 → 查 nginx 缓存 → 最后才动代码。

**多 JS 文件病**: build 后 `ls assets/index-*.js | wc -l` > 2 → 路由树重复。排查:
```bash
# 找到不含 bug 的干净 JS
for f in assets/index-*.js; do
  hits=$(strings "$f" | grep -c 'productCode.*valueType.*select')
  [ "$hits" -eq 0 ] && echo "CLEAN: $(basename $f)"
done
# 切换 HTML 引用
sed -i 's|index-.*\.js|index-CLEAN.js|' index.html
```

**浏览器 IndexedDB 旧数据**: 清 IndexedDB 后刷新,应用 seed 代码重新灌入新格式数据。F12 → Application → IndexedDB → Delete database。

## 兜底策略

- 输出精确指令(附示例代码)
- build 后检查 bundle: 路由树数量 + 残留模式
- 部署后验证: curl HTTP status + strings 检查关键代码片段
- 重复问题优先清缓存: `rm -rf dist node_modules/.vite && npm run build`
- VPS 部署后本地好 VPS 不好 → 直接 strings+grep 查 VPS JS,不依赖截图
- 出问题先怀疑部署层(缓存/旧文件/IndexedDB),源码往往是干净的
