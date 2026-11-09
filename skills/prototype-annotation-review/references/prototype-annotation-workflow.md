# 原型标注工作流：从理念到 MVP 到治根（2026-08-08 forge-crm 线索列表页全记录）

## 背景与理念
- 用户理念：模仿 Axure 传统"左原型右标注"（页面 + 右侧交互/规则/字段说明），PRD 不赘述文字版交互规则
- 用 AI 实现自动化标注：旧时代高效方案 × 新时代 AI = 效率复利
- 来源：维他命课程 09（迭代场景的版本管理与原型标注），配套 Skill `vitamin-prototype-annotation`（zip 下载）
- 用户原话："老师给的不是终极答案，我们实践完善它"——治根原则

## 三层分工（用户定，铁律）
- **执行者**: Codex/Cursor——项目内 `prototype-annotation/` 目录（SKILL.md + scripts + assets），实际跑标注
- **检阅者**: 杰西卡 + 罗宾——Hermes skill `prototype-annotation-review`（审质量），公司禁用飞书时罗宾可独立承担
- **验收者**: 用户——最终拍板

## 部署到项目的步骤
1. 解压 Skill zip → 放项目根（**不要放 .cursor/——被 .gitignore 忽略推不上 GitHub**）
2. git mv 改名（vitamin-prototype-annotation → prototype-annotation）+ SKILL.md 内部 name 同步
3. 提交 push main → 用户 Mac pull → Codex 执行
4. 产物自动流转：Codex build+zip（**解压即根**：`cd front-prototype/dist && zip -rq ../../forge-crm.zip .`）→ rsync 到 incoming → 报告 POST → 杰西卡读报告检阅 → 部署（deploy-all.sh --deploy forge-crm）→ 用户验收

## 治根历程（每轮实践发现 → 补进 Skill → push → 重跑）
| 轮次 | 发现的问题 | 治根内容 |
|---|---|---|
| MVP | 标注生成（初始） | 初始化工作流：读PRD→提取规则→映射data-anno→写标注md→compile→runtime注入 |
| 治根1 | 标注面向开发（英文枚举/路由路径） | Annotation Language Standard：面包屑路径、中文状态名、业务语言、英文枚举仅括号附注 |
| 治根2 | 面板缺 type 分类 | Annotation Classification & Panel UI Standard：5 类 type（page/interaction/rule/field/pending）+ 面板 UI 要素 |
| 治根3 | 点击按钮直接弹说明，不知对应哪个区域 | Interaction Flow：按钮→显示序号徽章→点徽章才看内容；initialMode=preview |
| 治根4 | 内容长段落平铺 | Content Structure Standard：分组标题+分项列表（- 项名：描述） |
| 治根5 | 渲染样式平铺 | 项名加粗/分组标题加粗/展开收起(N项)/来源灰色框/白底圆角卡片 |
| 治根6 | 内容缺交互/规则/字段细分，只有3大块太粗 | Detail Tab Standard：每块 6 tab（全部/页面内容/交互说明/业务规则/字段说明/待确认），空 tab 也展示（拓展预留口）；粒度按功能点拆细（3块→9块：页面/状态页签/筛选查询/新建导入/批量作废/表格字段/AI评分/行操作/权限） |
| 治根7 | 入口遮挡页面控件（右上角固定挡住批量导入/新建线索） | Entry floating & draggable：标注清单+原型标注悬浮 fixed 定位 + 鼠标拖移 + sessionStorage 记忆位置 |

## 9 块标注结构（治根6 后，forge-crm 线索列表页）
| ID | 区域 | type | data-anno |
|---|---|---|---|
| 1 | 线索列表页面 | page | leads-page-header |
| 2 | 状态页签与线索池视图 | interaction | leads-status-tabs |
| 3 | 线索筛选与查询栏 | field | leads-filter-bar |
| 4 | 新建与批量导入工具 | interaction | leads-create-tools |
| 5 | 批量作废工具 | interaction | leads-batch-tools |
| 6 | 线索表格字段与分页 | field | leads-table-fields |
| 7 | AI评分与分流规则 | rule | leads-ai-score |
| 8 | 线索行操作与状态流转 | interaction | leads-row-operations |
| 9 | 权限与异常边界 | rule | leads-permissions |

## 浏览器实测技法（2026-08-08，部署一致性排查的最终武器）
用户报"线上没看到入口/元素"时，**先用 browser_navigate 打开线上 URL + browser_snapshot/browser_vision 确认元素实际存在与否及位置**，再下结论：
- 实测案例：用户无痕打开 forge-crm 说"没看到入口"→ browser 实测"标注清单/原型标注"按钮在右上角正常显示、无遮挡——是用户截图视角/旧缓存问题，**不是部署失败也不是 Codex 布局 bug**
- 避免让 Codex 空跑一轮"修一个不存在的问题"（浪费一轮迭代 + 用户时间）
- 线上文件才是真相：VPS `/root/repos/` 仓库可能没同步 Codex 的 Mac 改动（只上传 zip 不 push），排查以 `/var/www/pmlophy.com/project/<项目>/` 线上文件为准

## 关键文件位置（forge-crm）
- 执行侧 Skill: `/root/repos/forge-crm/prototype-annotation/`
- 标注源: `prd-docs/线索管理/annotations/`（annotation.config.json + pages/leads-list.md + coverage.md）
- 编译产物: `front-prototype/public/annotation-kit/annotation.bundle.json`
- 运行时: `front-prototype/public/annotation-kit/runtime.js + runtime.css`
- 页面锚点: LeadsList.tsx 三个 data-anno（leads-status-tabs / leads-filter-bar / leads-table-operations）

## 标注过程暴露"原型 vs PRD 不一致"（附加价值）
Codex 对照 PRD 映射页面时如实记录差异（报告"遗留风险"）：
- 原型多了状态（我的线索含 DRAFT vs Demo 定义）
- 原型没执行 PRD 规则（7天防撞墙保护/超时回收不完整）
- 原型没实现 Demo 能力（多值搜索/导出/批量分配）
- 校验不严（放弃原因最少15字）
处理：用户拍板（本次"当时先调了原型、PRD没同步"→ 改 PRD 对齐原型）

## 部署一致性排查（线上 vs 本地自检截图不一致时）
1. 查部署日志 `grep '\[部署\]' /var/log/jarvis-deploy.log | tail`——确认最新 zip 部署成功
2. 线上 runtime 含新逻辑特征字符串（`grep -c '已显示标注区域序号' runtime.js`）
3. zip 里 JS 名 vs 线上 index.html 引用（相同=新部署）
4. Cloudflare cf-cache-status（EXPIRED=实时；浏览器本地缓存→强刷）
5. **JS 名不变不代表没更新**——runtime.js 是 public/ 静态文件，不进 JS hash；改的是 runtime 而非业务代码时 index-*.js 名可能不变，但 runtime.js 内容变了
