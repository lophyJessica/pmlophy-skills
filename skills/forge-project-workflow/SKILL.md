---
name: forge-project-workflow
description: Forge 项目从0到1的标准工作流——搭框架→PRD→用例推演→前端→审计。CRM/WMS/ERP项目均适用。
---

# Forge 项目标准工作流

> CRM 实战验证的 9 步法,适用所有 Forge 新项目。

## 核心铁律

1. **用例数据推演是前端编码前的强制关卡。推演不过关,不写前端。**
2. **命令官模式：只给 A2A 指令,不自己动手改文件/部署/编译。** 用户不说"你改/你部署",绝不碰文件。前端/UI/视觉类任务只写指令给 Gemini/反重力,不做执行者。
3. **单线程对话：一个任务完成→确认→下一个。** 不并行追问,不猜测进度,不等"跑完了吧"。

## PRD 质量标准（v2.0 — 对齐 ERP 采购订单）

> CRM 实战教训：v1.0 PRD 主PRD 仅 191 行，"根本上不了评审台"。
> v2.0 标准来自 forge-erp/prd-docs/采购管理/采购订单/ 的 PRD 套件（主PRD 344行）。

| 文档 | v2.0 最低行数 | 必须包含 |
|------|:---:|------|
| 主PRD | **≥300行** | §1-11全章节：业务痛点5条+In/Out含原因+链路图+场景S01-SXX编号+状态流转表含前置/后置/失败处理+规则R01-RXX编号+AI失败处理+操作权限矩阵+边界异常+验收V01-VXX含输入条件 |
| Demo_列表页 | **≥180行** | Tab含计数/查询区每控件规格/表格列含宽度+固定/行内操作按状态动态/二次确认弹窗文案/Mock含状态分布/反馈文案 |
| Demo_新增编辑页 | **≥190行** | 每字段控件类型+placeholder+字符限制+联动规则/编辑模式差异/字段联动规则/交互规范(保存/提交/返回) |
| Demo_详情页 | **≥170行** | 状态区Badge+时间线/KV只读卡片/关联单据/底部操作矩阵/交互规范含弹窗文案 |
| 字段清单 | — | SSOT唯一权威源,下游严禁重复定义枚举值 |

模板文件：`templates/CRM业务对象PRD模板.md`

| 步骤 | 产出物 | 验证方式 |
|:---:|------|---------|
| 1 | **搭框架** — 项目目录+git init | `forge-{name}/` |
| 2 | **AGENTS.md** — 品牌口径/技术栈/系统边界/铁律 | 审阅对齐 WMS/ERP |
| 3 | **context/** — 01~07:背景/系统/功能清单/流程/命名/评分/通用规范 | 对齐已有项目结构 |
| 4 | **templates/** — PRD模板/字段清单模板/用例推演模板 | 复用 WMS/ERP 模板 |
| 5 | **主模块 PRD** — 主PRD + 字段清单(SSOT) + **状态机** | 状态机闭环?所有分支有入口? |
| 6 | **用例数据推演** — 带具体数值跑状态机全分支(happy path+驳回+异常+超时),推演通过才下一步 | 每个案例有结论 ✅/❌ |
| 7 | **Demo PRD** — 列表页/新增编辑页/详情页(字段引用SSOT,不重复定义) | 字段与清单一致 |
| 8 | **前端搭建** — 骨架→模块页面→交互,对齐 Demo PRD | 并行只改源码不build |
| 9 | **全局审计** — 交叉审计 PRD vs 前端 vs context/07 | P0/P1/P2→修正→**一次build**→dist→部署 |

## 踩过的坑

- 跳过步骤6直接写前端 = 死结靠代码发现,成本翻倍(CRM 教训)
- Demo PRD 漏了 = 前端字段与 SSOT 不一致,返工
- 并行编译互相覆盖 → 只改源码不 build,最后手动一次 build
- 部署后 docs/flow/ 被 dist 覆盖 → 部署完从源仓库恢复手动文件
- VPS 无 GitHub token → 只 commit 不 push,发 md 文件给用户 push
- **子路径部署路由调试** → `<base>` 与 HashRouter 冲突/Puppeteer 浏览器实测/按钮导航相对路径。详见 `references/deployment-pitfalls.md`
- 自己动手改 UI/HTML 而非给指令 → 跟用户 Gemini 并行改同一文件,效率归零。视觉类任务只写指令,不执行
- 发文件前不 pull 检查 → 重复发用户已 push 的内容,造成混乱
- SSOT 混淆 → CRM 客户档案 SSOT 在 ERP,不是 CRM。跨系统字段必须先定 SSOT 归属,再写 PRD
- 三系统数据串联 → 同域名 Dexie 共享方案见 `references/三系统Dexie串联方案.md`
- **Dexie 跨系统共享 (2026-07-19 纠错)**: 两种方案均可行:① `new Dexie('DB名').open()` 不定义 schema,Dexie 自动使用已存在的 schema(最简单); ② 定义与源系统**完全一致**的 `version(1).stores({...})`,包含所有12张表,不能只写4张(2026-07-19验证通过)。关键: schema 必须精确匹配,不可定义子集。验证: Chrome DevTools→Application→IndexedDB→找到 DB→对比两个系统的数据是否一致。readTable 缓存陷阱: ERP 的 readTable 先从 tableCache 取数据,Dexie 水合用 void(不等待),外部写入永久不可见→改为 useLiveQuery 直读 Dexie。**DB 名必须从源码确认(读 constructor super()),不可猜测。**\n- **跨系统 Bug 调试策略**: 当多轮修复无效时,给 Codex 全量诊断指令——让它同时读两边完整源码,输出诊断+修复。不要自己逐轮猜,Codex 能一次定位根因(DB名错误/schema不匹配等)。
- **Checkpoint 格式**: 部署类任务必须写 `dist→你发我→我在VPS部署→你开浏览器验证`,不写"部署→验证"
- **部署覆盖原有项目 (2026-07-19)**: 用户发参考 WMS dist,未确认路径直接解压到 forge-wms 目录 → 原 forge-wms 被覆盖。铁律:部署前必须确认路径(第三方项目→独立路径如 /project/reference-xxx/,不可覆盖 forge- 系列)。
- **Codex @chrome 前端复刻**: Codex 内置 `@chrome` 可操控浏览器直接复刻目标页面→React代码,比 Gemini 截图→描述→改歪快 10 倍。见 `gemini-frontend-rebuild/references/codex-chrome-browser-clone.md`。
