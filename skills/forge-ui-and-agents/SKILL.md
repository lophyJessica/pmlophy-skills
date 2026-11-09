---
name: forge-ui-and-agents
description: Forge 项目 UI 框架决策门、Gemini 反重力指令红线、交叉走查、VPS SSH push 等实战经验。
category: software-development
---

# Forge UI & Agent 协作实战

## 1. UI 框架决策门

**新 B 端项目/模块初始化前必须先问用户:**

```
React 还是 Vue?
  ├── React → Ant Design + ProComponents / Shadcn/UI / Arco Design
  └── Vue → Vben Admin(切 Element Plus 适配器) / Element Plus 原生
```

**禁止 Tailwind 纯手搓组件。**

当前 forge 三件套 UI(2026-07-30):\n| 项目 | 技术栈 | 设计风格 | 进度 |\n|------|------|------|:---:|\n| forge-erp | React + Ant Design + ProComponents | 稳重企业级 | 54 页全量迁移完成 |\n| forge-wms | React + Ant Design（0814 已从 Vue3+ElementPlus 迁移，与 ERP 一致——实现问题） | 稳重企业级 | 已完成 |\n| forge-crm | React + Shadcn/UI（0814 反重力全量重构完成——18 页） | 现代极简 | 已完成 |\n\n### Shadcn/UI 全量重构（CRM 实战 0814）\n\n**在现有项目上直接重构，不复制备份项目**（用户铁律：复制=集成层要重做）。git commit 就是备份——重构前先让用户 commit 打基线，可回滚。\n\n反重力 Shadcn/UI 重构指令要点：\n1. **保留集成层铁律**：`src/api/erpSync.ts`（CRM→ERP 客户同步）、`src/db.ts`（Dexie）、路由结构、业务逻辑——只重构 UI 组件层。红线写死"绝不碰 erpSync.ts / db.ts / Dexie schema / 路由 / 业务逻辑"。\n2. **初始化**：`npx shadcn@latest init` + `npx shadcn@latest add button card table dialog form tabs select input badge alert dropdown-menu label separator skeleton`\n3. 逐模块重构（页面清单给全）→ `npm run build` 通过 → 部署。\n4. **验证风格真的生效**：browser_vision 看截图确认（大圆角/中性色/低饱和蓝=Shadcn；饱和色彩/硬阴影=旧 Tailwind 残留）。\n5. **Shadcn 与 Tailwind 兼容**（Shadcn 基于 Tailwind，不冲突——现有样式可复用）。

**重构后功能回归检查（0814 实踩）**：全量重构 UI 层最容易丢"非页面"功能——annotation-kit 静态文件保留但页面里的 `data-anno` 锚点属性被删（runtime 用 querySelector 找不到目标 → 原型标注按钮在但点击"没效果"）。给重构指令加一条红线："保留所有 data-* 锚点属性、annotation-kit 加载代码、集成功能"；验收清单加一条："重构后逐项点既有功能按钮（原型标注/标注清单/导出等）确认没丢"。\n\n### 品牌统一清理（0814 强盛科技→Forge 实战）\n\n品牌口径切换时，**残留不止前端**——三处都要清：\n1. 前端代码（页面文案 + db.ts 演示数据）——`grep -rn "旧品牌" src/` 逐个清\n2. **PRD 文档**（业务背景/示例数据/用例里的旧名）——`grep -rn "旧品牌" --include="*.md" .` 全仓搜（往往比前端还多）\n3. **AGENTS.md 品牌口径段**——不更新的话下次 agent 又按旧口径生成（0805 就发现"回头统一修"，拖到 0814 才清）\n4. **清完验证**：`grep -rn "旧品牌" --include="*.tsx" --include="*.ts" --include="*.md" . | grep -v node_modules | grep -v ".git/" | wc -l` 应为 0\n5. **git 协作节奏（用户 0814 定）**：用户先 commit → 我 pull → 我改 → 我 push → 用户 pull。**我改之前先 pull，push 前用户已确认**（先 pull 再 push 铁律）。

### Ant Design 迁移分步策略

全栈迁移不能梭哈——分三层:

```
第1层: 基础资料(4模块) → 验证 ProTable/ProForm 可用
第2层: 采购管理(17页面) → 验证复杂业务表单
第3层: 销售+库存+往来+零售(33页面) → 全量
```

每层: 改完 → build → 部署 → 用户验证 → 下一层。

**pitfall:** Gemini/反重力不擅长 ProForm 子组件(ProFormText/ProFormSelect),退而求其次用 antd 原生 `Form.Item + Input` 即可。

### Cursor 一招制胜——ProForm 盲区终极解法(2026-07-30)

反重力对 ProFormText 5 轮指令零产出,始终产出 `Form.Item + Input + Modal`。换 Cursor 用同一段代码模板指令——一次性完成:

- 三个表单页(ProductForm/SupplierForm/WarehouseForm)
- ProFormGroup + PageContainer + 路由注册
- 完美对齐 ERP 仓库档案表单风格

**结论:** ProForm 子组件任务直接用 Cursor,不浪费反重力轮次。反重力适合 ProLayout 骨架+批量机械替换。代码模板见 `references/proform-page-template.tsx`。

| 任务类型 | 用谁 | 为什么 |
|------|------|------|
| ProForm 子组件(Text/Select/Digit) | Cursor | 反重力硬盲区,永远产出 Form.Item+Input |
| 独立路由表单页(不用Modal) | Cursor | 反重力永远产出 Modal.open() |
| ProLayout 骨架搭建 | 反重力 | 参照 ERP 可复现成功 |
| 批量组件替换(50+页) | 反重力 | 机械劳动,符合它的能力 |

## 2. 反重力/Gemini 指令红线

Gemini 常见毛病: 乱做主张、擅自加戏。

| 你让做 | Gemini 实际做 |
|------|------|
| 删一行跳转 | 重写整个路由层 |
| 改一个文件 | 新建 3 个重复组件 |
| 清路由树 | 从 3 套变成 5 套(叠罗汉) |

**所有 Gemini 指令必须加这条红线:**

```
红线禁止: 只删不增、不改不重构。不新建任何文件/组件/路由树。不重写现有逻辑。
```

**Gemini 适合:** 快速原型、全栈梭哈(一次给完整 PRD → 一次出全套代码)、Ant Design 组件填充。
**Gemini 不适合:** 精确 bug fix、路由修改、代码清理、删除重复代码。

## 3. 工具分工(2026-08-09 定稿: 文本型→Agent / 前端→IDE)

**用户 0809 定稿的分工原则**（写进记忆，未写进 AGENTS.md——用户明确说避免僵化）:

| 产物类型 | 用谁 | 为什么 |
|------|------|------|
| **文本型产物**(项目结构地基/context/PRD套件/流程/字段清单/功能清单/用例数据推演) | **Agent(Codex/Sol)** | 目标明确+文件操作+批处理——Agent 闭环执行最合适 |
| **前端开发**(页面/组件/交互/代码审查) | **IDE(Cursor/反重力)** | 可视化+可控制+要迭代——看 Diff/改样式/接受拒绝 |
| **突发情况**(Codex 没额度) | Cursor 可顶 Agent 的活 | Cursor 内置 Agent 模式/Composer——文本任务也能胜任 |

**本质**: 分工是"倾向"不是"铁律"——工具灵活，人按场景调（用户判断层）。常规: 文本→Codex、代码→Cursor+反重力；突发: 互换没问题。

**历史分工表**(2026-07-30,细节仍有效):

| 任务类型 | 用谁 | 备注 |
|------|------|------|
| **确认项目状态(技术栈/组件库)** | **杰西卡+VPS** | **动手前必须。自己查zip不猜不问** |
| PRD 套件生成 | Workbuddy + Kimi K3 / 反重力 | |
| 全栈梭哈(一次出) | 反重力(Gemini) | 需 ProLayout 骨架 |
| ProForm 子组件(Text/Select/Digit) | **Cursor** | 反重力硬盲区,5轮零进展 |
| 独立路由表单页(不用Modal) | **Cursor** | 反重力永远 Modal.open() |
| 精确 bug fix | Cursor Agent | |
| 代码审计(@codebase) | Cursor Agent 模式,只读 | |
| PRD 走查 | Codex / DS V4 Pro | |
| VPS 部署+运维 | 杰西卡(Hermes) | |
| memory 清理分析 | delegate_task 子Agent | 94%→74% |

**Claude 已弃用（2026-08-24 用户定）：** "后面我不打算用 claude 了，太慢了"——Sonnet 5/Opus 5 不再作为主力工具；曾用 Claude Code（桌面 App Code 标签）完成 forge-scrm 二期开发（85 API/17 表/28 路由，一次成型但耗时明显）。后续小修回 Cursor/Codex，部署维护杰西卡指挥。若未来再启用 Claude Code，入口选择查证结论（官方 docs code.claude.com）：**桌面 App 三标签 = Chat（对话）/ Cowork（长时程 agentic 工作、Dispatch）/ Code（软件开发——读 CLAUDE.md、改文件、跑命令）**，开发任务用 Code 标签；CLI 版无 work/code 之分，模式是 permission modes（Shift+Tab 循环：default/acceptEdits/plan/bypassPermissions/auto），大活走 plan→acceptEdits 两步。**CLAUDE.md 只做入口索引指向 AGENTS.md（用户已落地）**：Claude 只读 CLAUDE.md 不读 AGENTS.md，所以 CLAUDE.md 必须写"所有规则去读 AGENTS.md"，保持单一事实源；AGENTS.md 过长时 Claude 只记住开头，开发指令里要显式点名关键规则（R 编号/状态机）不要依赖它自己翻。


**Existing-project batch migration executor ranking (validated in forge-erp):** Workbuddy is preferred for broad, constraint-heavy UI migrations. It successfully read the baseline and existing samples first, preserved pre-existing uncommitted annotation changes, identified missing fields instead of inventing data, migrated 9 business modules and 4 master-data modules, preserved Dexie/API/business logic and `data-anno` anchors, built successfully, packaged a root-level ZIP, uploaded through the project delivery pipeline, and produced a self-check report. For similar tasks, prefer Workbuddy over Antigravity. Use Cursor for visual refinement, precise UI fixes, and cross-audit; use Codex for read-only diagnosis, high-quality engineering analysis, and structured implementation. Reserve Antigravity for rapid prototypes or narrowly bounded mechanical styling changes.

**Delivery principle:** The agent must be judged by the whole Harness loop, not model identity alone: baseline inspection → bounded edits → preservation checks → build → root-level unique ZIP → upload → self-check report → human-gated deployment. A fast ordinary model that completes this loop is preferable to a slower stronger model that requires repeated steering or leaves handoff work to the user.


生成后不要让同一个 AI 自查:
- 反重力出代码 → Cursor Agent @codebase 审计(只读)
- 反重力出 PRD → 换 Codex/DS V4 Pro 走查

**实战案例:** 反重力梭哈 54 页 antd 迁移后,Cursor @codebase 审计发现:
- P0: 供应商编码 SUP001 vs VEND001 三处不一致(报价系统全挂)
- P0: 主数据双份定义(MOCK_* vs baseDataApi,商品 SP-007 缺失)
- P1: ProtectedRoute 无角色守卫(供应商可访问所有 ERP 页面)
- P1: 合同/通知用 localStorage 而非 Dexie(数据分裂)
- 反重力生成的 SKU001 在源码中实际不存在(全是 SP-001)——审计消除了命名漂移恐慌

**结论:** 交叉走查不是锦上添花——是质量门禁。梭哈必审计。

## 5. VPS SSH Git Push

```bash
ssh-keygen -t ed25519 -C "forge-erp-vps" -f ~/.ssh/id_ed25519_forge -N ""
# 公钥加到 GitHub Settings → SSH Keys
git config core.sshCommand "ssh -i ~/.ssh/id_ed25519_forge -o IdentitiesOnly=yes"
git remote set-url origin git@github.com:lophyJessica/forge-erp.git
```

铁律: push 前必须用户同意,commit 备注必须详细。

## 6. Nginx SPA 子路径部署

React(BrowserRouter basename):
1. nginx: `alias /path/to/dist/; try_files $uri $uri/ /子路径/index.html;`
2. `index.html` 资源用相对路径 `assets/xxx.js`(不是 `/子路径/assets/`)
3. `index.html` 加 `<base href="/子路径/">`
4. `App.tsx`: `<BrowserRouter basename="/子路径">`

Vue(Vite + createWebHistory):
1. `vite.config.ts`: `base: '/子路径/'`
2. `router/index.ts`: `history: createWebHistory('/子路径')`
3. nginx 同 React 配置

**pitfall:** build 缓存污染——源码改了但 bundle 还是旧的。清缓存重 build:
```bash
rm -rf dist node_modules/.vite && npm run build
```

**pitfall:** 反重力多次修改后 bundle 出现重复路由树——源码 clean 但 build 产物叠加。根因是 Vite chunking + 未删旧产物。`rm -rf dist` 必须彻底。

**pitfall(WMS 陷阱):** Vben Admin 5.x 没有独立脚手架(`@vbenjs/create-app` 不存在于 npm)。它的安装方式是从 GitHub clone monorepo。且项目路径不能含中文/空格(Turborepo 会崩溃)。当前 WMS 方案: Vue 3 + Element Plus 裸写 + 反重力优化主题(不寄望 Vben Admin)。

**pitfall(猜测组件库——2026-07-30 WMS灾难):** 给 Agent 写组件替换指令前,**必须先确认**目标项目实际用什么组件库。不要猜、不要靠记忆。方法:让用户发 package.json 或 dist,用 `strings` 搜 JS 文件中的组件库名(`ant-design|element-plus|arco|naive|tailwind|vue`)。今天 WMS:猜了三次(ElementPlus→Indigo→Arco),全猜错。**不确认状态不给指令。**

**pitfall(技术栈确认——2026-07-30):** 用户说"换成和 ERP 一样的"时,ERP 是 **React** + Ant Design,不是 Vue + Ant Design。必须查 package.json 确认是 React 还是 Vue,不能自动脑补成 Vue。

## 7. PM 角色边界(铁律)

用户是 PM,不是开发者。以下操作绝对禁止要求用户执行:
- go to definition / 搜索文件 / 查看源码
- 手动改代码行 / 删注释 / 调配置
- grep -rn 项目目录
- "你打开 XXX.tsx 看看第几行"(这是最严重的失职)

**正确做法:** 诊断在 VPS 侧完成 → 给反重力/Cursor 发精确指令 → 它们改代码。
优先排查顺序: 浏览器缓存(IndexedDB/localStorage) → VPS 构建产物(Nginx 加载了哪个 JS) → 最后才怀疑源码。

**教训(2026-07-30):** 用户说了三次"ERP本地正常VPS异常",我反复让他看Mac代码——问题最终确认是VPS有11个重复JS文件,Nginx加载了错误的那一个。应该在VPS侧完成所有排查,不给用户下"打开文件看看"的指令。

### 谋定而后动:不猜状态(2026-07-30 3次违规 → 追加到20+次累计)

今天在 WMS 任务中猜了三次,全猜错:
1. 猜 WMS 用 Element Plus → 实际是 Arco Design
2. 猜 WMS 是 Vue 项目 → 实际是 React(和ERP同技术栈)
3. 猜 VPS 上的 WMS 就是 Mac 上的版本 → 完全不同
4. 用户说"就是ElementPlus换AntDesign"时我没验证,直接出指令 → 猜错了

**铁律升级: 不确定当前状态时,不用问用户'package.json是什么'——直接自己确认。**
- 用户发 zip → VPS 上 `strings assets/*.js | grep -oP 'antd|arco|element-plus|react-dom|vue' | sort -u` 一键确认
- 不问用户,不猜,不自以为知道——自己查 zip。

**铁律:不确定当前状态时,让用户发 dist/package.json,自己在 VPS 用 `strings` 查,绝不猜。**
确认组件库: `strings dist/assets/*.js | grep -oP 'ant-design|element-plus|arco|tailwind|vue' | sort -u`
确认技术栈: 看 package.json 的 dependencies

### 事实类信息绝不靠猜/默认(2026-08-09 用户两次抓到,升级为铁律)

用户问"我怎么才能给你纠正纠正"——光记"不靠猜"没用,必须行为改变:
- **场景**: 用户设备配置(核数/内存/电池)、系统状态、账号情况等**具体事实**——禁止按"官方标准配置/常理"默认推断
- **正例**(用户示范): 用户自己跑 `sysctl hw.physicalcpu` + `system_profiler SPDisplaysDataType | grep Cores` 实证
- **反例**(我犯的): 问 M3 Air 核数时默认"官方标准 8 核"——虽然猜对了(确实是 8核CPU/10核GPU),但**方式错**: 该先问或让用户查,不默认。猜错一次=浪费用户一轮纠正,用户会失去信任
- **规则**:
  1. 能自验的自验(自己跑命令/API/文件——如 VPS 上 strings 查组件库)
  2. 不能自验的(用户设备/账号)→ 明说"我不确定,你查一下/告诉我",不编数字
  3. 把"我猜是X"换成"这个需确认"——尤其当"猜错成本高"(价格/配置/时间)
- 同源教训: Holographic 用法靠猜(SQL直插=僵尸记忆) → 读官方源码实证才找到正确用法(见 holographic-memory-usage skill)

## 8. 反重力与 ProLayout —— 成功/失败的边界(2026-07-30)

反重力在 forge-erp 成功、forge-wms 反复失败——根因不是 AI 能力,是骨架:

| | forge-erp(成功) | forge-wms(4轮失败) |
|------|:---:|:---:|
| 布局骨架 | **ProLayout**(开箱即用) | 手搓 layout |
| 表格组件 | ProTable | 手写 DataTable |
| 表单组件 | antd Form | 手写 Form |
| 迁移方式 | 小模块先行→梭哈 | 每次从零裸写 |
| 结果 | 54页全量 antd 化 | 回滚,还是原始版好 |

**结论:** 反重力在给定 **ProLayout + ProTable + ProForm** 骨架时,只管填充业务字段——成功率高。裸写 UI 时视觉审美差。
**WMS 重建方案:** 从 ERP 复制 package.json + vite.config + tsconfig,用 ProLayout 做壳,反重力只填页面内容。

### ProForm 子组件盲区与代码模板方案(2026-07-30 4轮验证)

反重力对 ProForm 子组件(ProFormText/ProFormSelect/ProFormDigit)存在硬盲区:
- 5轮指令要求 `ProFormText name="code"`，产物永远是 `Form.Item name="code"><Input />`
- 4轮指令要求"独立路由页面+ProForm"代替 Modal，产物永远是 `Modal.open({content: Form})`
- 根因:反重力不知道 ProFormText 的 import 路径和 JSX 语法,只会用通用 Form.Item + Input

**解法:直接贴代码模板。** 下面是已验证可用的 ProForm 独立路由表单页模板(见 `references/proform-page-template.tsx`):

```tsx
import { ProForm, ProFormText, ProFormSelect, ProFormDigit } from '@ant-design/pro-components'
import { useNavigate, useParams } from 'react-router-dom'

export default function ProductForm() {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEdit = !!id

  return (
    <ProForm onFinish={async (values) => { navigate('/base') }}>
      <ProForm.Group>
        <ProFormText name="code" label="商品编码" rules={[{required:true}]} disabled={isEdit} width="md" />
        <ProFormText name="name" label="商品名称" rules={[{required:true}]} width="md" />
      </ProForm.Group>
      <ProForm.Group>
        <ProFormSelect name="category" label="分类" width="md" options={[...]} />
        <ProFormText name="unit" label="单位" width="md" />
      </ProForm.Group>
      <ProForm.Group>
        <ProFormDigit name="price" label="参考单价" min={0} width="md" />
        <ProFormText name="spec" label="规格型号" width="md" />
      </ProForm.Group>
    </ProForm>
  )
}
```

**规则:** 反重力不会写 ProForm 子组件时,**不描述"怎么做"**,直接贴代码模板让它复制改字段名。

### grep -c 误判构建产物(2026-07-30)

`strings dist/assets/*.js | grep -c 'darkAlgorithm'` 会把 Ant Design 库内部的 darkAlgorithm 引用也数进去(4处全是 antd 自身代码),误报为"用户未修复"。
- 检查用户代码: `grep -rn 'darkAlgorithm' src/`
- 检查 ProForm 子组件: `grep -rn 'ProFormText' src/pages/`
- **不检查 dist/ 构建产物的字符串匹配结果**

## 9. 记忆清理模式(2026-07-30)

MEMORY.md 膨胀到 94%/80条时,用 delegate_task 分析:
- 子Agent读全部条目 → 输出: 删除N条(理由) + 合并N组(N→1) + 保留N条
- 主会话只看分析报告,不加载170行原文
- 用户审核后,分批执行 memory remove/replace → 效果:94%→74%

**规则:** memory 修改操作单批别超过 6 条(一条不匹配全失败)。超过分多批。

## 10. Figma MCP —— 设计稿直驱代码(2026-07-30 新工具)

反重力视觉审美的根本解决方案:不再让 AI "猜"设计,而是从 Figma 直接读设计数据。

```
旧流程: PM画Figma → 截图 → AI看图猜 → 代码跑偏
新流程: PM画Figma → AI读取节点/颜色/间距/文本 → 精准生成代码
```

**接入方式(反重力已配置):**
```json
{
  "mcpServers": {
    "figma-custom": {
      "command": "npx",
      "args": ["-y", "figma-developer-mcp", "--figma-api-key=xxx", "--stdio"]
    }
  }
}
```

**可用工具:** `get_figma_data`(读设计数据) / `download_figma_images`(导出图层)

**工作流:** Figma 画页面 → 反重力 `get_figma_data` 读取 → 生成 React + Ant Design 代码(颜色/间距/字号按设计稿)

## Agent Selection Reference

For the validated tool ranking and harness-first selection criteria, see `references/agent-selection-and-harness-fit.md`. Use it when choosing between Workbuddy, Codex, Cursor, and Antigravity for an existing-project task.

## 11. Hermes 内存清理 —— 先翻上限再腾空间(2026-07-30)

**教训:** MEMORY.md 94%膨胀时,手动删30条用了1小时。一条命令即可:
```bash
hermes config set memory.memory_char_limit 20000  # 10,000→20,000
```
**规则:** 内存满了先 `memory.memory_char_limit`,别手动腾空间。delegate_task 分析+批量 operation 清理是辅助手段。

## 12. 二期开发实战坑（2026-08-26 forge-scrm 全流程沉淀）

- **前后端 API 路径契约必须全系统统一**：前端 axios baseURL=`/api` + 调用 `/benchmark-accounts` → 实际请求 `/api/benchmark-accounts`；一期后端 router prefix=`/api`（正常），二期新模块 prefix=`/api/v1` → 前端全 404 "Not Found"（页面能开、接口全挂）。**新模块路由 prefix 必须对齐系统已有约定（/api），禁止引入 /v1 分层**；审查时把"前端调用路径（baseURL+路径）"与"后端 router prefix 拼接结果"核对，不能只看接口在源码存在。
- **Alembic 数据迁移依赖应用启动时创建的数据（如 admin 用户）会在全新环境静默跳过**：seed 迁移读 user 表（created_by 外键），迁移先于应用启动 seed admin 执行 → user 空 → 迁移 `return` 跳过 → 部署后数据表空但 `alembic current` 是 head（自检报告预警"全新数据库无用户会跳过"应验）。修复：手动补插（项目自身 `settings.database_url` + SQLAlchemy，取首个用户 id，幂等检查）；治本：应用启动钩子空表自动 seed（必须在 admin 创建之后）。**验收部署必须查数据表实际行数，不能只看 alembic 版本**。
- **Codex 自报"已部署"可能不完整**：声称部署成功但只同步了后端——前端 dist 是旧 bundle（mtime 上午）、alembic 停旧版本、seed 没跑。**验收部署核对三样：①前端 dist bundle 时间戳 + grep 新代码特征字符串 ②`alembic current` 到最新 ③后端关键路由存在**。Agent 自报不可信，走 deploy.sh 全通道（build→rsync dist→rsync 后端→migrate→restart→HTTPS verify）最可靠。
- **前端调不存在的 API → 404 弹错但兜底"碰巧能用"最迷惑**：loadReport 先调 `/research-tasks/{id}/report`（后端没这接口）→ 404 → axios 拦截器弹 "Not Found" toast → catch 兜底 `/research-reports/{id}` 成功——**碰巧 report.id==task.id 才 work，id 错位即白屏**。审查逐条核对前端 fetch 路径 vs 后端路由表；"页面有数据但弹 Not Found"优先怀疑前端调了不存在的接口，不是后端坏了。
- **删字段必须同步清理 import**：MaterialForm 删"有效期"字段后残留 `DatePicker`/`dayjs` import → tsc 构建失败 TS6133（declared but never read）→ 部署通道 [1/6] 卡死。**改动后本地先 `npm run build`（tsc -b 抓未使用 import）再提交，别让部署通道来抓错**。
- **antd Select 选中态显示三层取舍（生成页模板库下拉实战）**：①`optionLabelProp="shortLabel"` 只显示短名（如"选题生成"四个字）用户嫌太狠；②label 全量无 optionLabelProp → 选中后长文本撑宽控件，用户嫌"占满全屏"；③**正解 = label 全量 + `labelRender` 包 span（maxWidth:100% + overflow:hidden + textOverflow:ellipsis + whiteSpace:nowrap）→ 选中态正常省略号截断**；同时 `optionRender` 下拉项 `whiteSpace:'normal'` 完整多行 + Tooltip 悬浮全文。**"正常截断"= 控件宽度内 ellipsis，不是短名也不是全文**；两页同构（选题/脚本生成页）必须同步改，否则用户看到"风格不同步"。
- **内置模板下拉"暂无数据"≠ bug**：生成页模板下拉显示数据库模板；内置模板（代码常量）不落库不进下拉——空下拉 = 用内置，属设计行为。用户看不懂时解释"下拉是自定义备胎，空着用默认"，或干脆做"内置/自定义"单选交互（用户最终拍板全模板化：seed 进表 + 删除保护每 task_type 至少一条 + 自定义一键存模板）。

### 审核规则定稿（三轮澄清教训——防再误判）

用户说"把审核功能下了/先隐藏" **≠ 全部取消审核**。三轮澄清后定稿（forge-scrm 权威口径）：
- **人工创建资料** → 免审核直接「已生效」（忽略 submit_for_review）
- **导入资料** → 保留「待审核」（来源不可控，人工审核后生效）
- **AI 产物**（AI 回写资料 / 生成选题 / 脚本 / 分析结果）→ 保留审核（R8：AI 产物与原始事实必须区分）
- 资料审核页/菜单/路由保留（审导入与 AI 回写产物）；脚本审核、分析审核不动

**两个坑**：①"只隐藏入口但不取消流程"= 死锁（保存后永远待审核、又无处审核）；②动手前先对齐用户是"隐藏入口"还是"流程取消"，且取消范围要**逐类确认**（人工/导入/AI 三类分开问），别一锅端理解成"全取消"。

## 14. 产品架构图/业务流程图三件套生成（2026-08-31 forge-scrm 实战）

**触发**：用户要\"把整个产品架构图画出来，参照 forge-wms docs/flow\"——给某 Forge 项目生成可视化架构文档套件。

**产出三件套**（放 `docs/` 下，对齐 WMS 结构）：
1. `docs/forge-产品架构图.md`——总览 Mermaid（系统关系）+ 模块全景表 + 核心作业链 + 外部系统关系 + 与同矩阵系统关系
2. `docs/flow/flowchart.md`——全系统产品结构 Mermaid flowchart（业务链 + 边界 + 主数据虚线）+ 结构解读表
3. `docs/flow/index.html`——深色 Mermaid 渲染页（mermaid@10 CDN + marked，带缩放控件），把 md 内容嵌入；多份 md 用 Promise.all 同页顺序加载 + 分隔线 + 统一错误提示（保留原访问路径，不搞页签）

**Codex 指令关键约束（缺一就产出跑偏）**：
- **信息源圈死**：主PRD + modules 各模块 PRD + `App.tsx` 路由 + `MainLayout.tsx` 菜单 + `context/` 状态机。**以代码为准**——要求输出\"PRD 与代码差异\"小节，防止文档吹了 PRD 里有但代码没有的功能。
- **路由核对硬要求**：文档里每个页面路径必须能在 App.tsx 找到对应 `<Route>`，报告里给 36/36 这种逐项对照表；没有路由的\"页面\"不许写进图（如自动采集详情只有展开行，就画展开行不造独立页）。
- **审核字样口径延续**：状态描述用 `displayStatus` 映射后的用户可见状态，不出现\"待审核/审核中\"（仅允许一次性历史说明）。
- **预留项诚实标注**：PRD 设计但未实现的（定时采集/微信推送/语义去重/官方平台适配/对象存储 vs 本地文件）必须标\"预留\"+原因，不吹成已上线。

**部署到线上（文档不是应用，别走 deploy.sh 的 dist rsync）**：
- 独立静态目录放到主站静态根（`/var/www/pmlophy.com/<子目录>/`），浏览器直接访问渲染页。
- **先确认主站域名托管在哪台机**——pmlophy.com 主站走 Cloudflare 回源到老 Lisa（192.220.14.245），而搬瓦工 nginx 只托管 scrm/n8n 子域。放错机器会\"源站直连 200、经 CF 404\"（CF 回源到的是另一台）。传之前用 `nginx -T | grep server_name` 确认哪个站点接 pmlophy.com 主域。
- 上传后经 CF 可能有几分钟边缘缓存，强刷一次。

**Mermaid 渲染验证**：Codex 报告若含\"Mermaid parse 通过 + 浏览器渲染 SVG 计数 + 缩放控件测试\"才可信；围栏必须成对（偶数）。



### UI 类任务省额度三原则（用户烧掉 Cursor 60% 额度后定）

**背景**：forge-scrm UI 对齐 copy-wms（紫色 Tailwind 手搓版）用了 6+ 轮迭代（布局对齐→侧栏→滚动条→全局主题→修复→返回按钮），每轮 build+部署+看效果再调，一天烧掉 Cursor 60% 额度。归因不是模型贵，是往返多。

```
① 参照一次给全：给 Cursor 的目标 UI（如 copy-wms）要【源码路径 + 关键样式截图 + 主色 hex】
   ——让它一次理解到位，不猜（猜=每轮部署验证往返）
② 试点先行：先 1 个模块确认风格满意 → 再铺全局。
   "试点小范围 → 再模块 → 全局梭哈"是既定节奏——全局梭哈的代价是多轮修补返工
   （用户曾因我违背此节奏给新模块开发指令而发火："你有毛病吧"）
③ 验收标准写死：颜色/间距/圆角/操作栏/状态 Tag 色板列清楚，减少"看着不对再调"
```

### antd 全站主题统一的可复用模式（forge-scrm 紫色主题实战）

一个 `theme.ts` + 两个全局封装即可全站统一，不用逐页改：

```ts
// theme.ts：ConfigProvider 主题 + 全局状态色板 + 分页默认
export const appTheme: ThemeConfig = {
  token: { colorPrimary: '#7c3aed', colorLink: PRIMARY_COLOR, borderRadius: 6 },
  components: { Menu: { darkItemSelectedBg: PRIMARY_COLOR }, Layout: { siderBg: '#141414' } },
}
// STATUS_TAG_COLOR 映射：启用/已通过/已生效/已完成→green；停用/已废弃/失败→red；
// 待审核/待筛选/执行中/检索中→orange；草稿/待执行/pending→default；部分成功→gold
export function statusTagColor(status?) { return STATUS_TAG_COLOR[status] ?? 'default' }
// TABLE_PAGINATION = { position: ['bottomRight'], showSizeChanger: false }
```

- `TableActions.tsx`：操作栏封装（≤2 个文字按钮并排 Space 8，>2 个收入 Dropdown「更多」）
- Switch 类启停开关放**状态列**（Tag+Switch 组合），不放操作列
- 菜单选中态用主色 `darkItemSelectedBg`，侧栏保持深色

### 验证线上 bundle 修复的两个坑（今日实踩）

- **React inline style 编译后是 JS 对象不是 CSS 字符串**：`style={{maxWidth:720}}` → bundle 里是 `maxWidth:720`（JS 属性名），grep `max-width:720px`（CSS 形式）= 0 **不等于没部署**。要 grep JS 形式 `maxWidth:720` 或业务特征字符串（如页面 title）。
- **rsync -a 保留源 mtime**：远端文件时间戳旧 ≠ 没部署——hash 相同内容相同（Mac build 产物未变）时远端 mtime 就是旧值。判断部署是否生效以**内容特征 grep** 为准，不看时间戳。

### 协作节奏（用户 0826 定，与 git 铁律并列）

- **写指令/改文件后不要立即 push**——先给用户看讨论，等用户说"可以 push/确认"再推（需求中途变化避免无效提交）。
- **用户说"下一个指令"要先确认轨道**：用户可能指当前任务的延续（如 UI 修改），不是开新模块开发。出指令前确认"继续当前轨道还是新任务"，避免答非所问（今日实踩：用户要 UI 下一指令，我给了数据报告新模块开发）。
- **交付后只给提交备注（commit body），不给标题**：用户用 Cursor/Antigravity 界面提交，标题自己定，备注粘贴到提交框备注区。
