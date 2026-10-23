---
name: prototype-annotation-workflow
description: 原型标注工作流——用 AI 给已有前端原型生成"左原型右标注"（模仿 Axure 传统，AI 自动化）。三层分工：Codex/Cursor 执行（读 PRD 生成标注）、杰西卡/罗宾检阅（审质量）、用户验收。覆盖标注语言规范（产品视角）、治根原则（实践补 Skill 不靠指令）、产物部署坑点。当要给 forge 系/任意已有前端页面加业务规则标注、或检阅标注产物时使用。
---

# 原型标注工作流（AI 自动化版）

## 触发场景
已有前端原型（React/Vue/静态 HTML）+ 业务 PRD → 给页面加"左原型右标注"（页面区域挂业务规则，评审/研发不用翻长 PRD）。方法论源头：维他命课程 09《项目资料的版本管理与原型标注》+ 配套 Skill `vitamin-prototype-annotation`（老师提供，起点非终点）。

## Standalone public Skill 的使用边界（2026-08-21）

公开仓库 `prototype-annotation-skill` 只提供通用能力层：SKILL.md、runtime、schema、编译/安装脚本、参考资料与测试；它**不是下载后即可运行的独立标注产品**。

使用者必须自行准备并适配：
- 已有的 React/Vue/静态 HTML 原型与其目录/构建框架；
- PRD、字段清单、业务规则、Demo 规格等业务地基；
- 可被 runtime 命中的 `data-anno`、`data-testid`、`id`、`aria-label` 或稳定语义选择器；
- 项目自己的 `public/`、HTML 入口、构建命令和部署方式。

正确交付口径：
```text
使用者已有项目 + 业务地基
→ 下载 Skill
→ 初始化 runtime/配置
→ 按项目结构适配安装路径
→ 生成标注并编译 bundle
→ 在自己的原型中浏览器验收
```

没有项目框架和业务地基时，使用者只能阅读方法论、参考 runtime/脚本和自行搭建适配层，不能期待直接得到 Forge 项目中的完整标注效果。公开 Skill 不包含任何 Forge CRM/WMS/ERP 源码、PRD、业务数据、凭据或 VPS 配置。

README 和对外介绍必须明确这条边界，避免把“公开可下载”误解为“开箱即用”。

## 接活前依赖盘点（2026-09-10 娜美实证——缺 PRD 套件只能靠猜）

**做原型标注前，先盘点依赖、校验现状；缺地基先汇报，不许用猜测硬做。**

**原型标注的依赖清单**：
1. **PRD 套件（核心依赖，缺了根本做不了）**——主 PRD（业务背景/功能范围/单据定位/状态机）+ Demo PRD（页面规格：字段怎么展示/输入/校验/反馈）+ 业务规则（状态/动作/异常边界）+ 流程文件（涉及上下游时）
2. **字段清单 TSV**（字段事实源——只是补充，不是全部）
3. **前端原型页面 + 可挂载锚点**（`data-anno` / 稳定选择器）
4. **标注规范**（annotation-scope 边界判断 + 编写规范 + SKILL）

**实锤案例（0910）**：用户拿 forge-crm 做升级试点（项目本身有完整 PRD 套件），但只把**前端代码**给了娜美——娜美**不检查输入**，拿着前端代码就"研究升级原型标注"，缺 PRD 地基只能反复猜着修，**浪费 2-3 天怎么做都不对**；一查才发现她那边只有前端空架子、**没有 PRD 套件**。

**关键**：只给前端代码 ≠ 能标注——标注的来源是 PRD（见下节"标注来源澄清"），没有 PRD 套件就只有字段清单可抱、只能猜业务规则。**接活三问**：①依赖哪些输入？②我手上有哪些？③缺哪些（缺的立刻汇报）？这条是"谋定而后动"在标注工作的落地（详见 `ai-apprentice-training` 常见坑）。

## 交付前必查：bundle 是否真的编译进去了
- 运行时读的是编译产物 `public/annotation-kit/annotation.bundle.json`，**不是** config。改了 config/md 必须重跑：`python3 /root/repos/prototype-annotation-skill/scripts/compile_annotations.py <config> --output <bundle>`。
- 多份 config 分叉（PRD 侧 `annotations/` 与部署侧 `public/annotation-kit/`）会让新页标注根本没进 bundle；现象=某些页面点开无标注。修法：合并成单一 config（每条必须有 `markdownFile`+`blockId`），重编一次，并核对 bundle 条目数与覆盖页面清单。
- 编译报 `unmapped source requirement` = 有 sourceRequirement 没被任何标注的 sourceRefs 引用 → 补 sourceRefs 或删过期需求条目。
- 每条标注 `target.selector` 里的 `data-anno` 值必须能在 `src/` grep 到；弹窗类标注的锚点要挂在弹窗内元素上。交付前核：bundle 锚点集合 − src 里 data-anno 集合 = 缺失清单。

## 标注语言规范（产品视角，最重要）
标注给【业务方/评审】看，不是给开发看——必须业务语言：
- 页面标识 → 面包屑路径（"线索管理/线索列表"），不用 URL/路由（/leads）
- 状态/枚举 → 中文业务名为主（待分配/跟进中/已转客户/已作废），英文枚举（PENDING_ASSIGN）仅括号附注供开发对照
- Tab/筛选 → 中文名称（全部/待分配/我的线索/公海）
- 规则 → 业务语言（"分配后48小时未首次跟进自动回收，回退待分配"），不用代码逻辑
- 字段 → 中文标签（线索名称），不用字段名（leadName）
- 英文枚举/技术路径为主描述 = 不合格，返工

## 治根原则（用户定调，2026-08-08）
- **实践发现问题 → 补进 Skill 本身，不靠临时指令修正**。用户原话："我们不仅是在实践，也是在完善这个 skill，而不是靠指令修正，要治根，老师给的不是终极答案"
- 老师/外部 Skill 是起点不是终极答案——每次实践缺口回写
- **执行侧 + 检阅侧同步补**：Codex 读的执行侧 Skill（项目里 `vitamin-prototype-annotation/SKILL.md`，英文文档→规范条目用英文写如 Annotation Language Standard 章节）和检阅侧 Skill（中文）都要加同一条规范，两侧一致才治本
- 案例：首版标注用英文枚举/路由路径 → 验收发现 → 补"标注语言规范"到两侧 Skill → 重跑，不再靠指令每次叮嘱

## 执行侧 Skill 管理
- **命名分工（2026-08-08 定稿）**：执行侧（项目里）= `prototype-annotation`（从 vitamin-prototype-annotation 改名，目录 + SKILL.md 内部 name 保持一致）；检阅侧（Hermes）= `prototype-annotation-review`（用户纠正过：先改成 prototype-annotation 又改回 review——检阅侧保持 review 名，只有执行侧项目文件夹改短名）
- 位置：项目根 `prototype-annotation/`（**不能放 .cursor/rules/——被项目 .gitignore 忽略，git 推不上去**）
- Skill 改动走 git：commit + push main → 用户 Mac pull → 才生效（用户 Mac 是主开发库）
- 结构：SKILL.md + agents/ + assets/annotation-kit/（runtime.js/css + config/workspace schema）+ scripts/（compile_annotations.py / install_annotation_kit.py）+ references/ + tests/

## 产物部署坑点（zip 解压即根）
- 标注产物走 ai-artifact-pipeline：build → zip → rsync 到 incoming → deploy-all.sh 部署
- **zip 必须"解压即根"**：`cd front-prototype/dist && zip -rq ../../forge-crm.zip .`，**不能带 `front-prototype/dist/` 前缀**——否则 deploy-all.sh 解压后入口在嵌套目录，验证 curl 404 → 自动回滚（2026-08-08 forge-crm 实锤，需手动解压修复）
- **deploy-all.sh 验证 URL 用 /project/ 前缀**（2026-08-08 已修）：forge 系部署在 `/var/www/pmlophy.com/project/<项目>`，验证 URL 是 `https://pmlophy.com/project/<项目>/`——写成 `https://pmlophy.com/<项目>/` 会 404 回滚；回滚逻辑也已加固（无备份时不删 dest）
- 指令里显式要求"zip 解压即根，unzip -l 第一层是 index.html"
- 部署由用户确认后执行（审查门禁）；cron 提醒到会话 ≠ 自动执行（需对话激活，半自动是设计使然）
- 管道命令（rsync/curl）必须逐字写进给 Codex 的指令——Codex 不主动执行外部操作

## 给执行者的指令骨架（Codex/Cursor）
```
Context: 项目/任务/Skill 位置（vitamin-prototype-annotation/）
Request:
1. 读 Skill 的 Workflow A（初始化）或 B（增量更新）
2. 读 PRD（主PRD/字段清单/Demo页）+ 页面代码
3. 按语言规范生成标注（annotations/ 目录跟 PRD 走，如 prd-docs/线索管理/annotations/）
4. 编译: compile_annotations.py → annotation.bundle.json（原型 public/annotation-kit/）
5. build + 打包（zip 解压即根）+ rsync + 报告 curl（逐字命令）
红线: 不污染 PRD/业务代码（只加 data-anno + runtime hook）；不 commit/push
Checkpoint: 浏览器截图（徽章+弹窗）；标注区域清单；来源待确认项
```

**长分步命令式提示词可能被 OpenAI reasoning 护栏拦截**（`Invalid prompt ... usage policy ... advice-on-prompting`），走 OpenAI 系中转/reasoning 端点时更易触发。绕法：把完整指令写进仓库里的 `.md` 文件（按项目提示词合集编号续号），喂 agent 一行"读取文件 X 并完整执行、按汇报要求贴 diff 和真实输出"——提示词正文不再含分步命令，护栏不触发；顺带让指令进版本、可追溯。

## 检阅清单（审什么）
1. 语言规范（第 0 条，最重要）——英文枚举/技术路径为主 = 返工
2. 忠于 PRD——标注内容来自 PRD 非脑补；**来源行的存在是检阅侧核对覆盖用的（作者级溯源），不是评审人要看的**——评审看到的标注内容里不渲染来源（见"标注内容展示格式"）；来源不明在检阅侧标"待确认"核对
3. 无污染——PRD 未改、业务代码只加 data-anno/runtime hook
4. 覆盖完整——涉及区域都有标注；coverage.md 查未覆盖
5. 增量更新正确——只动受影响块；id 规则（1/2/3、A1/A2、1a/1b）
6. 运行时合规——只读、徽章不改变布局、选择器稳定
7. **交互流（2026-08-08 新增）**——按钮点击后先显示序号徽章层，点徽章才弹内容；initialMode=preview（初始无徽章）；再次点击清理干净。**若"按钮直接弹说明、无区域对应"= 不合格**（用户实测踩坑）

## 检阅者当 QA：浏览器实测验收（用户认可，2026-08-09）
用户：\"看来后面还能让你出测试用例了\"——检阅者可用浏览器工具做**功能层实测验收**（点击流/滚动/tab 状态保持/拖拽/导出），用户只拍板最终体验。
- **实测法**：browser_navigate 打开线上 → 真实点击入口 → 验证徽章/tab/滚动状态 → 截图/Console 断言。例：选 tab 后 `window.scrollBy` 多次，断言 tab 不跳回"全部"
- **区分"真 bug" vs "滚动容器交互"**：标注面板的列表区是**独立滚动容器**（外层页面滚动不动它）——用户说"显示不全"时先确认是否需在列表区内滚动，再宣布 bug（2026-08-09 曾误报"显示数≠渲染数"为 bug、补了规范后又 git revert 撤回）
- **用户偏好：不建专门 QA skill**（\"不要，浪费 token，每次都要调用这个 skill\"）——QA 用浏览器工具临时做，随用随有，不固化成 skill

## 标注即审计（增值模式，2026-08-08 实锤）
标注过程 = 把 PRD 规则逐条映射到页面区域 → **天然暴露"原型 vs PRD 不一致"**（原型实现了的 vs PRD/Demo 写的对不上）：
- Codex 在标注时会发现这些差异，**如实记入报告的"遗留风险"**（本次 forge-crm 发现 5 处：我的线索含草稿 vs Demo 定义、作废后立即撤销 vs 7天防撞墙、超时回收只覆盖已分配、原型缺多值搜索/导出等能力、放弃弹窗仅非空校验）
- **检阅时把这些不一致单独拎出来，交用户拍板**（不是标注问题——标注忠于 PRD 是对的；是原型和 PRD 谁对谁错）：
  - A 全改 PRD 对齐原型（本次用户选这个——先调了原型、PRD 没同步）
  - B 逐个看（有的原型对、有的原型欠实现）
  - C 先记着（演示项目不急）
- 拍板后走 git：改 PRD 对齐原型 → commit + push main（Codex 执行，标注重新编译）

## 标注 UI 目标样式（2026-08-08 已实现 + 交互流修正）
对标别人实现的完整标注面板样式（只有截图、无源码——别人也是基于维他命 Skill 自己调出来的）：
- 页面顶部"原型标注"按钮（白色，文档图标）→ 点击开/关标注模式
- 浮层面板：标题"原型标注" + 条目总数徽章 + 关闭 X + 副标题"点击条目定位页面中的对应区域"
- 页签：全部/页面/交互/规则/字段/待确认（当前 tab 品牌绿高亮）→ 标注块带 type 元数据（page/interaction/rule/field/pending，存 config + Markdown 块标记）
- 条目卡片：序号徽章（绿圆数字）+ 标题 + 类型标签（交互/规则/字段）+ 摘要 + "展开详细说明（N 项）"收起/展开
- 点击条目 → 定位/高亮页面对应区域（data-anno 锚点）
- 样式：白底卡片 + 阴影 + 圆角 + 品牌绿
- 已实现：面板+页签+type 分类+卡片+定位（Codex 完成）；compile_annotations.py 无需改（保留 type）

### 交互流铁律（2026-08-08 用户实测踩坑后治根）
**按钮 → 序号徽章层 → 点徽章才看内容**，三步骤缺一不可：
1. 页面有"原型标注"按钮
2. 点击按钮 → **页面显示各标注区域的序号徽章**（绿圆数字浮在 data-anno 区域上）——用户先看到"标注对应哪个区域"
3. 点击徽章 → 才弹出该区域标注内容（不渲染来源行）+ 高亮区域
- **CRITICAL：点击按钮绝不允许直接弹标注内容**——必须先显示序号层。用户踩坑原话："点击原型标注，直接显示一个原型说明，我都不知道是哪一个区域的原型说明"——首版实现就是按钮直接弹说明，用户不知道对应哪个区域，判定不合格
- `initialMode` 必须 `preview`（页面初始无徽章、无内容；按钮点击才显示徽章）
- 再次点击按钮 → 清理徽章/弹窗/面板，回干净页面
- 已补进执行侧 Skill（prototype-annotation/SKILL.md "Interaction flow" 章节 + CRITICAL 说明，e139c15）——治根，不靠指令每次叮嘱
- 参考截图：见会话图片（在途采购页标注面板，img 缓存）；细节见 `references/annotation-ui-style-target.md`

## 标注内容展示格式（2026-08-08 已治根，含渲染样式）
标注内容**不能长段落平铺**（业务定义/显示样式一大段文字），要**结构化分组 + 分项列表**（对标参考效果）：
- 顶层：需求描述标题（如【状态页签】）。**块首的 `> 来源：xxx.md#章节` 溯源行整体替换为 `> {该区域的功能描述}`**——不是保留溯源供检阅侧、也不是裁剪去重到一条，而是整行换成面向评审/业务方的一句话"这个区域是干嘛的"（用户定："来源就不要说明了，那是给自己看的""不要提来源，来源于别人看不懂""改成> 对商机列表进行筛选的功能"。例：「商机查询筛选」→ `> 对商机列表进行筛选的功能`）。评审点开角标看到的是"这是什么功能/怎么操作"，不是文档章节映射。溯源核对走 config 的 `sourceRefs` + coverage.md（独立于 md 的来源行）。字段表格下方的裸 `来源：{字段清单}.tsv` 行同样删。
- **删除/替换 来源 行不影响 compile**：`compile_annotations.py` 不读 md 的 `> 来源`/`来源：` 行——它们是静态 markdown 内容，直接编译进 bundle；REQ 覆盖校验看 config 的 `sourceRefs`↔`sourceRequirements`，与 来源 行无关。所以批量把 来源 行改成功能描述后照常 compile 即可（不报 unmapped、不丢块数）。改完 `python3 -c` 读 bundle 确认各块首行已是功能描述、且无 `> 来源` 残留。
- 分组小标题（如"页签通用行为"、"状态说明"）
- 分项列表：每项"名称: 描述"（如"全部: 默认选中，显示全部单据"、"数量徽标: 显示对应状态单据数，随状态变化/删除同步更新"）
- 长文本在条目卡片里"展开详细说明（N 项）"收起/展开
- **已治根**（本轮完成）：补"Annotation Content Structure Standard"进执行侧 Skill（ef87832）+ Codex 重写 3 块内容为分组+分项（共 40 项）+ **渲染样式升级**（分组标题加粗/项名加粗+描述常规/来源灰色框/白底圆角卡片/展开收起按钮，Codex 已实现）——检阅时核对：内容分组结构化（不是大段文字）、渲染层级对齐参考
- **粒度拆细**：标注块按【功能点】拆分（参考 8-10 块：状态页签/筛选查询栏/表格/批量工具/行操作/新建线索/AI评分/权限），**不是按页面大区聚合**（曾只 3 大块太粗、每块只写定义缺交互/规则/字段细节）；每块一个 data-anno 锚点（缺锚点补，只加锚点不改业务）

## 标注详情 6-tab 规范（2026-08-08 治根）
每个标注块的内容必须按 **6 个 tab** 组织（不是单一平铺正文）：
```
全部（各 tab 合并视图，默认） / 页面内容 / 交互说明 / 业务规则 / 字段说明 / 待确认
```
- **空 tab 也展示**（如"待确认 0 项"）——作为拓展预留口，不隐藏
- 每个 tab 内继续用"分组标题 + `- 项名：描述`"分项格式（见"标注内容展示格式"）
- 交互说明覆盖点击/状态流转；业务规则覆盖校验/权限/异常；字段说明覆盖字段级规则——都从 PRD 提取，不脑补
- 已补进执行侧 Skill（Annotation Detail Tab Standard，41fcbae）
- **tab 标签写死在 runtime.js、内容按 `###` 标题约定解析**；空 tab 展示"0 项"可反推缺口，但前提是 `###` 标题齐全——审计/补全方法见 `references/annotation-tab-and-heading-architecture.md`

## 面板 tab 状态持久化（2026-08-09 治根——滚动重渲染丢 tab）
用户实踩：点"标注清单"→ 选条目"页面内容"tab → 鼠标滚动页面 → tab 跳回"全部"。
- **根因模式**：滚动触发 `scheduleMeasure`（scroll 监听捕获阶段）→ 面板 `renderAnnotationPanel` 用 `innerHTML` 重建卡片 → 详情 tab 节点被销毁 → 从新 DOM 读不到原 tab → 回退默认 `all`。
- **正确模式**：UI 状态存**重渲染之外**的持久 store（`VPA_STATE.detailTabByCard: Map`，按 `data-annotation-key` 作 key）；切换时保存，重建时恢复——"DOM 只负责呈现，状态不放在 DOM 里"：
  ```js
  const cardKey = container.closest('[data-annotation-key]')?.dataset.annotationKey;
  const savedTab = cardKey ? VPA_STATE.detailTabByCard.get(cardKey) : null;
  const requestedTab = savedTab || container.dataset.detailTab || initialTab;
  if (cardKey) VPA_STATE.detailTabByCard.set(cardKey, currentTab);
  ```
- 验证：选一个详情 tab（如页面内容）→ 滚动页面 → tab 应保持，不跳回"全部"（浏览器实测：scrollBy 多次后仍保持）
- **通用教训**：凡是"滚动/刷新触发的 DOM 重建"组件（tab/折叠/勾选/筛选），状态必须外置持久化（VPA_STATE 等），DOM 默认值不是状态源
- 已补进执行侧 Skill（Panel Tab State Persistence Standard，a66c616）

## 滚动事件不得重建滚动容器（2026-08-09 治根——滚动条死）
紧接 tab 跳回 bug 之后用户又踩：标注面板的外层列表/内层详情 tab 滚动条**无法滚动**（scrollTop/scrollLeft 每次回 0）。
- **根因模式**：可滚动容器自身触发 scroll → `scheduleMeasure()` → `renderAnnotationPanel()` **重建了滚动容器** → 新节点 scrollTop/scrollLeft 归零 → 滚动条"死了"。与 tab 跳回同源（滚动→重渲染链），但这是"容器被重建"（结构问题），不是"状态丢失"。
- **正确模式（Codex 终解，比"重建+恢复状态"更优）**：滚动事件里**只更新需要跟随业务页面移动的定位元素**（`measureBadges()`），**绝不重建面板**；面板重建只由明确动作触发（tab 切换/展开收起/数据刷新）：
  ```js
  window.requestAnimationFrame(() => {
    VPA_STATE.measureScheduled = false;
    measureBadges();
    // 滚动期间绝不调用 renderAnnotationPanel()
  });
  ```
- **金律**：滚动事件只更新定位；结构更新（重建）由显式动作驱动，绝不由容器自身的滚动事件触发。从根上避免重建，优于"重建+恢复状态"。
- 验证：面板列表 scrollTop 能从 0 正常变化并保持；内层 tab 横向 scrollLeft 正常；滚动后 tab 仍保持选中
- 已补进执行侧 Skill（Scroll Event Must Not Rebuild Scrollable Containers，d79f0ff）

## 标注块粒度（2026-08-08 治根：3 块 → 9 块）
- 按**功能点**拆块（不是按页面大区聚合）——参考效果 9 条 vs 首版 3 大块，评审逐点看
- forge-crm 线索列表页 9 块示例：页面/page、状态页签/interaction、筛选查询/field、新建导入/interaction、批量作废/interaction、表格字段/field、AI评分/rule、行操作/interaction、权限异常/rule
- 每块一个 data-anno 锚点（缺锚点就补，只加锚点不改业务）

### 颗粒度分层模型：global / page-global / element（维他命 QS-JXC 实证 2026-09）
标注块按**三层 type**划分，页面级规则**绝不能当普通 element 块挂具体区域锚点**：
- `global`：跨页共享（模块范围/单据定位/共享状态机），不挂锚点，`target={'type':'global'}`。
- `page-global`：该页通用规则（权限/边界、页面级业务规则），`target=None` **不挂锚点**——挂了锚点徽章就会贴到随便一个元素上，规则"错挂区域"（埋先例：forge-crm 把「权限与异常边界」anchor 到筛选栏内的 `leads-permissions`，徽章 9 贴错；页面级规则应提为 page-global）。
- `element`：具体 UI 区域块（筛选区/表格/表单区），挂 data-anno。
- **颗粒度本身是偏好不是对错**：维他命按 UI 区域粗分（列表页 4 块 = module-scope + list-page-rules + 筛选区域 + 列表与行操作；新/编辑页 3 块；详情 4 块）；我们按功能点细拆（线索列表 9 块）。两种均合法——但无论粗细，**页面级规则必须提为 page-global（不挂锚点）**，区域块才挂 element 锚点。改粒度前先向用户确认偏好（细=评审逐点看 / 粗=简单）。
- **字段/动作一律用 markdown 表格呈现**（维他命参考：行操作矩阵、条件动作、二次确认、字段全表格），字段用四列 `字段|展示/输入类型|业务说明|约束与备注`；不要用段落文字（用户实测对照参考效果判定不合格）。

### 批量字段说明→四列表格（脚本转换，真做过的坑）
把全项目已有标注的"字段说明"从段落一次性转表格时，脚本按这几条做才不出劣质产物：
- **只转干净的 `- 字段名：描述` 对**（字段名短、后跟 `：`）。枚举/短语行——一串字段名无冒号、或一个长描述——**保持要点不塞表格**；无差别转成表行 = 垃圾行（`| 关键词、合同编号… | - | - | - |`）。转换脚本判据：`^\s*-\s+([^：:，,、。．]{1,20})[：:]\s*(.+)$`。
- **模块感知 TSV**：只把来源模块自己的字段清单 TSV 填进该模块的标注；绝不把线索 TSV 套到客户/商机等其它模块字段上（字段名撞名但语义/类型不同）。**无 TSV 模块的类型/约束列填 `-`**——这空列正是"反推补齐点"的信号（哪列空=该模块待补字段清单 TSV）。
- **跳过已是表格的段**：已转成 `| ` 表格的块（另一 agent 转好的）不重复转换，直接保留——脚本遇到 `^\s*\|` 行就 flush 跳过。
- **编译输出路径**：`compile_annotations.py <workspace>` 默认 output 可能指向框架改造前的旧 `front-prototype/public/annotation-kit/`（workspace 配置残留旧路径），编译会写偏到未跟踪目录；务必显式 `--output "<live>/public/annotation-kit/annotation.bundle.json"`，再 `check_annotation_assets.py` 对 live 路径实跑。误写出的旧目录产物 rm 掉、别提交。
- **改完任何模块的标注 md 后，必须用全项目 workspace 重编译 bundle，绝不用单模块 config**：`compile_annotations.py <单模块>/annotation.config.json` 会生成只含该模块角标的残缺 bundle（如线索 26 条，全项目 138 条中只剩 26）——若提交/部署，会覆盖掉其他模块（商机/客户/合同/拜访/业绩）的标注，静默丢数据。正确入口是聚合全部模块的 `annotation.workspace.json`。**编译成功 ≠ 产物对**——重编译后必须读 bundle 核对（`python3 -c` 列 page 分布 + 总角标数应=各模块之和；如 138），确认其他模块页面还在，再 commit/部署。单模块 config 只用于 `--check` 校验单页结构，不用于生成合入全项目的 bundle。
- **部署 zip 会原样打包本地 public/annotation-kit/bundle.json——改标注 md 不自动重编译，必须先重编译 workspace 并 commit 后才让用户/agent build 打包，否则 zip 里是旧 bundle**。
- **验收"部署成功"要看部署出的 bundle，不看部署日志的 HTTP 200 也不看仓库 public/ 版本**：解压 incoming 里实际部署的 zip 读内层 bundle（`unzip -p ... annotation-kit/annotation.bundle.json | python3 -c '...'`），核对该块首行已含功能描述 / 无 `> 来源`，再读 `/var/www/pmlophy.com/project/<项目>/annotation-kit/annotation.bundle.json`（绕过 CF 直接读部署目录）。"部署成功 HTTP 200"只证明 zip 解压到位，不证明新标注上线——若用户/agent 本地 build 时 bundle 没重新编译，zip 会是旧版，线上自然看不到改动。
- **并行 agent 改同一分支同一批文件时**：与另一个 agent 的 commit 分叉（都改了 annotation.md + bundle），不要手工 rebase 解冲突；`git reset --hard origin/<branch>` 落到对方版本，再重跑你的确定性脚本（脚本会跳过已转换/已是表格的）——得到干净叠加，Cheap 且不丢内容。

### 颗粒度按页面类型：表单页区域级，列表页功能点（2026-09-13 用户纠正）
**表单页（新增/编辑）的"基本信息"必须整块一个标注**（区域级，不逐字段拆）；**列表页才按功能点细化**。用户实测判池：新增/编辑页上"一个基本信息，不该每个字段分一个"——第一普遍把来源/公司/联系人/手机号/邮箱/行业/地区/备注各挂一个徽章，全挤在"基本信息"卡片里，还重复标注条件规则（手机号/邮箱"选填其一"在两行各标一次）。正确做法：基本信息一张卡片一个 `element` 锚点（如 `<Card data-anno="xxx-form-basic">`），字段说明合并成一个表格并去重（条件的共享约束如"至少填一个"整块级标一次）；页面头/校验/保存/提交仍各自成块。这 5 个表单页（线索/商机/合同/拜访/业绩）同病——列为 agent 移交模式（以改好的 LeadForm 为参照，见下）。

### 改标注块结构必须同步 config（合并字段级→区域级时）
把表单页字段级块合并成区域级块时，改 markdown 只是第一步，**还须同步 annotation.config.json，否则 compile 失败且不写新 bundle（旧 bundle 残留带旧块）**：
- config 的 `annotations` 条目要跟着改为新块（id/type/page/markdownFile/target 与新 markdown 的 `anno:start` 一致）；config 用路由格式做 page（如 `#/leads/new`），不是中文面包屑。
- **每个 `sourceRequirements` 必须被某个 annotation 的 `sourceRefs` 数组覆盖**——漏会报 `unmapped source requirement`，compile 直接失败、`annotation.bundle.json` 不更新（check 还用旧 bundle 所以"通过"，容易误判）。新增/合并块后逐个核对 REQ 覆盖：块 1(页面头)↔PAGE/MODE，块 2(基本信息)↔FIELDS/DEDUP，块 3(校验)↔VALIDATION，块 4(保存草稿)↔DRAFT，块 5(提交)↔SUBMIT/AI。
- 之后重编译（带 `--output`）+ `check_annotation_assets.py`，并 `python3 -c` 读 bundle 验证该页块数=新结构块数（不信 check 的 green）。
- **手工改前端锚点时不要顺手改 JSX 结构**：移除字段级 `data-anno` 只在标签上加区域锚点；曾误插一行多余 `<Label>`/多余 className 改了布局——只动属性，不动结构。

## 对标参考效果：同一交互入口比 + 默认展开 + 来源归一（2026-09 用户纠正）

用别人/维他命标注做对标时，**必须按同一交互入口比，别跨入口比**：我们点角标默认就展示该区域内容（还带虚线框标出该区域范围），跟它的「标注清单/抽屉展开」不是一回事——别因为参考图"展开得很全"就误判我们的模式差，更别把"点角标"的交互流改成"点入口直接摊开全部"。参考截图往往混杂多种入口，先分清它在比哪一个（交互流铁律：按钮→序号徽章层→点徽章才弹内容）。

**用户定稿的三件精修（forge-crm 验证，改完回写两侧 skill）**：
1. **展开/收起的当前定稿：标注清单默认收起、点角标弹窗默认展开（两机制分开定）**：
  - **「标注清单」面板卡片默认收起**（2026-09-27 用户改回："标注清单默认收起，不展示全部"）——每条缩成一行（编号+标题+类型标签+摘要），不默认摊开全部详情；点"展开详细说明"才展开。
  - **点页面角标弹出的 popup 默认展开**（2026-09-26 用户定，仍有效）——点徽章直接看该块全部 tab 内容。
  - **实现（已验证）：`VPA_STATE.expandedCards`（Set）语义 = "展开的卡片集合"，初始空 = 面板卡片默认收起；只在用户手动点"展开"时才 `add(key)`**。改四处：①渲染判断 `const expanded = VPA_STATE.expandedCards.has(key)`（默认 false=收起）②填充详情时 `if (!card || !VPA_STATE.expandedCards.has(key)) return;`（未展开不填详情）③toggle 的 add/delete 保持原样（点展开 add、再点 delete）④第 30 行注释改为"展开的卡片集合(默认全收起)"。**toggle 不需要改**——`has?delete:add` 正是"点收起移集、点展开加集"。改完**同步两份 runtime.js**（public/annotation-kit + prototype-annotation/assets/annotation-kit），否则下次 build 用旧模板覆盖默认收起。
  - **⚠️ 两个独立的展开机制，别只改一个（2026-09-26 实锤）**：标注有**两条展开路径**——①「标注清单」面板的**卡片**（`vpa-card`，由 `VPA_STATE.expandedCards` 控制）②点页面**徽章/角标弹出的 popup 内容**（`vpa-popup`，由 `setPopupContent` 内的 `syncDetails(wasOpen)` 控制）。用户对"默认展开/收起"的诉求会落在这一条或另一条——**先分清楚用户说的针对哪个入口**（页面角标 vs 标注清单卡片）再改对那个机制，别默认只改一处。
  - **历史上这条被改过三次，方向会来回**——先读清用户当次诉求（"标注清单卡片"默认收起 / "点角标"默认展开 / 全部默认收起），再定 expandedCards 语义方向，别照 skill 里某个日期版本就断言"该默认展开"。判据：用户说"标注清单/清单"→面板卡片；说"点角标/徽章/弹窗"→popup。
2. **字段说明一律表格**：凡有"控件/数据来源/展示格式/约束"映射的，用表格列（字段｜展示或输入类型｜业务说明｜约束与备注；模块字段区按 TSV 13列），socketW心情不用段落描述。skill 规范里已有此条但执行未到位——派活时明说，验收时逐块查字段 tab 是否有表。
3. **来源行 → 换成功能描述（2026 定稿，取代早前"简洁归一"）**：标注块首的 `> 来源：{文件}.md#章节` 溯源行**整体替换为 `> {该区域的功能描述}`**（如 `> 对商机列表进行筛选的功能`）——不是保留溯源、也不是裁剪去重到一条。评审/用户看不懂文档章节引用（"来源是给做标注的人看的，评审人和用户看了只会困惑哪来的""不要提来源，来源于别人看不懂""应该改成对这个功能/模块的描述"）。溯源核对走 config 的 `sourceRefs` + coverage.md，不靠 md 的来源行。字段表格下方裸 来源 行同样删。
  - **描述必须从该块正文/该功能所属 PRD 内容提炼，绝不凭空手写新内容（2026-09-26 用户纠正）**：功能描述是"这块区域是干嘛的"的精简概括，不是 AI 自由发挥。批量写描述时**逐块依据**该块的 页面内容/交互说明/业务规则 提炼一句话（例：「线索筛选与查询栏」正文里有"关键词支持逗号或换行分隔匹配公司/联系人/手机号/编号"→描述写"支持按关键词、来源、行业、评分等条件组合筛选"），禁止编造原正文没有的能力。若某块正文不足以概括出描述（无实质内容），宁可不加描述行也不要臆造——否则产生"非来自权威文件"的格式正确但内容可疑的标注（用户原话："描述没问题了，但现在关键是这个描述的来源要怎么解决，现在是你批量手刷的数据，不是来源于某个权威文件"）。
  - **描述自动提取的具体规则（2026-09-26 实现，取代手写）**：描述 = 该块 `### 页面内容` 小节内的**首个 `- 要点句`**（无 `-` 要点则取首个 `####` 小标题，再无则退回块内首个 `-` 行；页面能宽限到仍取到真实原句）。这样描述 100% 是该块标注正文的原句（正文来自 PRD），零手写、可追溯、可随正文变化自动 follow。实现是脚本逐块提取后**无条件覆盖**每块的 `> 描述` 行（脚本即 `scripts/extract_desc.py`，可复用）——**不要"只在值不同时才替换"**（那样会同一文件里部分块是自动提取、部分块仍是手写残留，成品描述风格不一致）；统一后核验每块 `>` 行数 = 总块数、且无 `> 来源` 残留。
  - **早前"来源简洁、全站归一"（统一成 `来源：{模块} {文件}.md#{章节}`）是被取代的旧方向**——那仍是"保留来源只改格式"，用户更进一步：来源行根本不进标注，换成功能描述。见"标注内容展示格式"节。
  - **裁剪陷阱（不要做的）**：当"来源太多有重复"时，不是裁到留一个主来源——那仍是留溯源行，评审照样看不懂。正确做法是整行换成功能描述。

**节奏**：先改 forge-crm 真标注验证效果与坑位（哪个字段要转表/哪个要塞垃圾），验证通过再回写执行侧+检阅侧 skill——**skill 从实践提炼，不先凭空改规范再套**。

## 标注块 ID 每页独立计数（2026-08-19 硬得利——flag 序号跨页累加）
**症状**：从线索列表页（徽章 1-9）切到新建页 → 徽章直接从 10 开始（10-18），详情页 19-28。大模块多页面会累加到 100+，序号不像"每页的定位"，Review 找块混乱。
- **根因**：runtime 徽章数字 = `annotation.id`（runtime.js `badge.textContent = annotation.id`）。compile 时 config 里的 id 原样进 bundle——若三页面 id 被【全局连续】编成 1-9 / 10-18 / 19-28 → 跨页累加。
- **正确模式**：每个【页面】的标注块 id **独立从 1 连续编号**（list=1-9, create=1-9, detail=1-10）。同一数字在不同页可重复——徽章按页面 scope 渲染（`routeMatcher` 限当前页），不冲突。
- **诊断（不猜）**：查 `annotation.bundle.json` 按 page 分组看 id。各页 id 前缀连续（1..N, N+1..M, ...）= 全局累加错误；每页都 1..N = 正确。
- **治根已补**：执行侧 `prototype-annotation/SKILL.md`（Annotation ID Numbering Standard）+ 检阅侧 `prototype-annotation-review`（"id 独立计数"检阅点）。检阅时核对：切到不同页面徽章都应各自从 1 起。

## 标注入口状态：两个入口按钮"激活态"必须对称（2026-08-19 治根）

**症状**：页面顶部有两个标注入口按钮——「原型标注」和「标注清单」。点「标注清单」面板打开了，但按钮本身不显示"被选中/高亮"样式；而「原型标注」按钮打开时却有 is-active 高亮。用户实测报：点【标注清单】后按钮没显示被选中样式。

**根因（代码实证，不猜）**：runtime 注入两个入口按钮，但选中态逻辑只处理了其中一个——
- 「原型标注」按钮 = `.vpa-entry` → 打开时有 is-active（runtime.js 约 1220 行 toggle + CSS `.vpa-entry.is-active`）
- 「标注清单」按钮 = panelToggle → 打开面板只加 `is-visible`，按钮自身【没有任何 is-active class + 无对应选中态 CSS】
- 图上红色虚线框是浏览器 devtools 的选中框，不是按钮自身的宿主选中态——按钮实际没高亮。

**修复模式（治根）**：给「标注清单」按钮（panelToggle）也加选中态——打开面板时加 is-active class、关闭时移除；CSS 补选中样式并对齐 `.vpa-entry.is-active` 视觉。状态开关必须"打开↔关闭"对称。

**修正判别（2026-08-19 二轮实锤）——"两个入口不对称"还有第二层根因：JS 已修但 CSS 漏配**：修完"两个入口对称"后用户仍报"点了没选中效果"，且是线上实测。逐层查（代码实证）：①本地/线上 runtime.js 里 panelToggle 的 classList.toggle('is-active', isPanelOpen) 已在（JS 对了）②但 runtime.css 没有 .vpa-panel-toggle.is-active 样式定义（只有 .vpa-entry.is-active 在 560 行）→ JS 加了 class、CSS 无视觉 → 白加还是看不到选中。排查必须 JS + CSS 双查：JS toggle 是否存在 ≠ 修好，还要 CSS 对每个入口按钮的 .is-active 都定义视觉。两个入口（或任意多入口）要"状态 class + 对应 CSS"成对，缺一味就是半修。

**通用教训**：凡是一个功能有【多个对称入口】（多按钮/多 tab/多开关），它们的"激活态"管理必须**对称实现**——一个入口有 is-active + 对应 CSS、另一个没有 = 必然出现"面板开了但按钮不高亮"的怪象。修复时逐入口检查【状态 class + 对应 CSS 是否成对】，不能只修主入口，也不能只改 JS 不补 CSS。

## runtime.js/css 多副本同步（2026-08-19 实锤——"本地能 VPS 不能/反之"假象的起因）
**症状**：改标注 runtime（如修入口按钮选中态）后，出现"本地有效 VPS 无效"或相反——用户实测判定方向都反了。根因常是**多份 runtime.js/css 不同步**，先确认本地线上是不是同一版，再怀疑环境/缓存。
- forge-crm 有**两份** runtime：`front-prototype/public/annotation-kit/runtime.js`（build/部署用）+ `prototype-annotation/assets/annotation-kit/runtime.js`（skill 附带模板）。改动 runtime 时两份必须同步，否则下次 build 用旧版覆盖。**规范做法：以 `prototype-annotation/assets/annotation-kit/` 下的 runtime.js/css 为唯一权威源，改完跑 `install_annotation_kit.py <项目>/public --public-path annotation-kit` 把它刷进 public**——不要直接改 public 下的 runtime 就当完事，因为 `install_annotation_kit.py`（模板→public）或 fetch/reinstall 会在后面覆盖它，你手改 public 的版本会被冲掉。反过来若某次直接在 public 改了，也应把改动 cp 回 assets 模板，否则下次 install 又覆盖回旧版。改动后核对两份字节一致（`wc -c`）再 commit；只 commit 一份而另一份不同步，下次 build/deploy 就会用旧 runtime 覆盖，线上看不到新行为。
- **排查步骤**：① stat -c%s 对比本地/线上 runtime.js 字节数（不一致 = 版本不同）②两份本地副本 diff（不一致 = 某份旧）③线上 curl 拉回对比关键特征字符串（grep -c 'toggle(.is-active., isPanelOpen)' 线上 vs 本地）。
- **教训**：别先怀疑 CF 缓存/环境——先查"本地代码和线上代码是不是同一版"。本地旧/线上新 或 反之，都会制造"环境差异"假象，导致误判 bug 在哪。

## 本地校验 vs 部署：分两条指令（2026-08-19 用户定的节奏）
给 Codex 派"全局大活"前，用户要求**先本地校验关键修复，再铺全局**——不要一步到位带部署：
- **第 1 条指令（修复类/被修改的点）**：给 Codex 做本地修复，**不带部署通道**（用户本地先跑通/浏览器验收）
- **第 2 条指令（全局/铺量类）**：用户校验通过后再发，**这条才带完整部署通道**（build → zip 解压即根 → rsync → 报告 curl）
- 原因：全局铺量（如给 20+ 页铺标注）读入大量 PRD/页面，一次带部署风险大且不好本地回滚；先修好"关键痛点"让用户确认代码方向和体验，再放全局任务。用户原话："先修复bug的指令给我，然后我本地校验后，再给我全局指令，然后用部署通道，所以第一个修复指令不需要用部署通道"

## 标注入口悬浮规范（2026-08-08）
- 入口按钮（"标注清单"+"原型标注"）必须**悬浮 fixed 定位**，不占页面布局流、不遮挡页面控件
- 支持**鼠标拖移**（拖动改变位置，位置存 sessionStorage 刷新保持）
- ⚠️ **drag/click 冲突坑（2026-08-08 实锤，Codex 修 4 轮才到终解）**：悬浮容器拖拽实现与子按钮点击天然冲突。症状：入口按钮能显示（悬浮可拖），但点击「原型标注/标注清单」完全无反应——F12 无任何事件触发、无报错，本地 vite 和 VPS 都复现。
  - **F12 手动绑定诊断法（定位「点击无反应」的标准手法）**：Console 执行 `document.querySelector('.vpa-entry').addEventListener('click', () => console.log('手动点击成功'))` 再点按钮——**无输出 = 事件根本没到达按钮（被上层拦截）**，不是 runtime 绑定问题；有输出 = 是 runtime 自己的 addEventListener 问题。
  - **真根因是 setPointerCapture**：浮动容器对 pointerdown 用 setPointerCapture → 点击子按钮后的 click 目标被父容器接管，子按钮永远收不到点击。前几轮只修了 click 捕获拦截（容器捕获阶段拦 click / suppressClick 残留），都治标——**第一轮修完点击好了但拖拽没了，第二轮移 setPointerCapture 点击好但拖拽被取消**。
  - **终解**：移除 pointer capture，改用 window 级 move/up 监听追踪拖拽；未移动时保留原生 click，移动超阈值才更新位置并抑制误触 click（区分点击/拖拽靠移动阈值，不靠事件捕获）。
  - **验证清单**：点击出徽章/toast、点击开面板、拖拽位置变化、拖完再点仍正常——四者都要验（Codex 报告称「验证正常」也要自己实测，曾连续 3 次部署踩同一坑）。
  - **部署后必须实测两个按钮点击**（不能只看自检报告说通过）
- **回归教训（2026-08-08 实锤）**：Codex 每轮"加新功能"（如悬浮可拖）都可能破坏既有功能（点击）——本轮连续 3 次部署"入口/点击"问题都源自此。部署前让 Codex 自检**核心交互回归**（入口点击/开关/面板/徽章），不能只验收新功能本身。给 Codex 的指令加一行："验证既有功能未被新改动破坏（重点：入口点击、徽章开关）"

## 待确认 = 评审问题记录系统（2026-08-09 用户纠正，重要）
**待确认 tab 不是从 PRD 提取的**——是**评审人工输入的问题追踪器**。评审时看到问题 → 手动录入待确认 → 变成可解决的待办项。用户原话："待确认不是文档中有缺失……这个功能应该延展为可输入框，在评审的时候，方便记录评审会遇到的问题，所以他的来源是手动输入。"

### 数据模型（每条 issue）
```
id: 稳定 id（标注块 key + 时间戳）
blockKey: 所属标注块（如 leads-status-tabs）
description: 问题描述（评审输入）
status: open / resolved（勾选框）
resolution: 解决方法（解决时填写，并展示——不只是打勾）
```

### 需求（已实现，Codex + 部署 v=10/v=11）
- **每块**：每个标注块的待确认 tab 有输入框 + 添加按钮（问题归属该块）
- **全局**：面板顶部待确认 tab 汇总所有块问题（按块分组，筛选 全部/未解决/已解决）
- **持久化**：localStorage（key 如 `forge-crm-leads-pending-issues`，数组）——刷新不丢
- **解决流程**：勾选 open/resolved + 解决方法输入框（解决时写方法，展示解决方案，不是只打勾）
- **导出**：按钮导出 PRD 待办 Markdown 块（复制剪贴板 + 下载 .md）：
  ```md
  ## 待办项
  - [ ] 问题描述（来源：标注块X / 页面区域）
    - 解决方法：（待补充）
  - [x] 已解决问题（来源：标注块Y）
    - 解决方法：已解决方式描述
  ```
- **导出细化（2026-08-09 v=12 验收）**：①单块导出——每个标注块的待确认 tab 详情内也有\"导出待办\"按钮，只导该块，**同样带 序号 X（标题）+ 待办清单**；②全局导出——按标注块分组，每组前缀 `### 序号 X（块标题）`（评审可追溯每个待办属于哪个区域）。单块/全局共用同一分组 writer（传参控制范围，格式不分叉）
- **显示数 = 渲染数**：全局待确认页签计数必须等于实际渲染卡片数——若计数与渲染不一致（数据在导出里有、显示少）先查分组渲染循环是否丢组；但**先排除\"滚动容器交互\"**：列表区是独立滚动容器，外层页面滚动不动它——用户可能没在列表区内滚动误以为显示不全（2026-08-09 实锤为误判，不是 bug；曾据此补了\"显示数=渲染数\"规范，后 git revert 撤回）
- **PRD 同步边界**：浏览器沙盒无法直接写 PRD 文件 → 导出块 → 用户/Codex 合并进 PRD；Markdown 待办格式（- [ ]/- [x] + 解决方法）使状态可回读（双向通过块格式实现）
- **状态模式**：问题数据放 runtime 外部 `VPA_STATE.pendingIssues` + localStorage，DOM 只呈现（同 tab 持久化金律）
- **滚动性**：每块问题列表 + 全局问题列表必须可滚动（`overflow-y:auto` + max-height，不依赖面板自身滚动，不在自身滚动事件中重建）——2026-08-09 踩坑：列表超高被截断

## 治根流程：Codex 修复 + 反馈修法 → 再补 Skill（不猜，2026-08-09 用户定）
用户发现"直接让 Codex 修更快，但 Skill 补的可能不准"——**治根必须基于真实修法，不靠猜**：
- **给 Codex 的修复指令末尾加"汇报要求"**：详细说明 ①根因（为什么）②改动（哪个文件/函数）③修复模式（关键代码/思路）④一句话总结（以后做这类功能的正确模式）
- Codex 报告里的"修复方案"章节 → 据此补 Skill（执行侧 + 检阅侧）——准确治根
- 若 Codex 的修法和预判一致 → Skill 已够；有新发现 → 再补
- 用户理念：老师/现成 Skill 是起点不是终极答案，实践完善它（不靠指令临时修正）
- **补错规范要撤回**：若后续发现某条规范基于误判（如\"显示数=渲染数\"其实是滚动容器交互、不是 bug），用 `git revert <commit>`（保留历史、生成 Revert commit）再 push——比 reset 安全（用户定 git 铁律：main 开发、master 收口、严禁直接 push master）

## PRD 补全工作流（标注当体检报告，2026-08-09 定方向）
标注内容的信息源是 PRD——**PRD 不全/不细，标注就不准**（标注只能标\"有的\"，缺的标\"待确认\"）。用户定：下一阶段回到**补全主PRD + DemoPRD + 字段清单**（含页面展示内容/字段规则/交互方式/业务逻辑），让标注更准确。

### 核心机制：标注是编译产物，不是实时获取
- 链路：PRD → 执行 Agent 读 PRD 写标注 Markdown（annotations/pages/*.md）→ `compile_annotations.py` 编译 → `annotation.bundle.json` → 前端 runtime 读取展示
- **PRD 改了 ≠ 标注自动变**——每次 PRD 变更都要执行 Agent 重跑一轮\"标注同步\"（读新 PRD → 更新标注 → 重编译 → 部署）
- 用户明确**不自动化**这个同步（2026-08-09：\"暂时不用，得需要的时候，现在用不上，浪费 token\"）——需要时手动让 Codex 跑，不建触发/监控机制

### 批量铺标注执行策略：按模块分批（2026-08-19 用户定）
用户明确拒绝一条大指令铺满全部页面（如 22 页一条塞给 Codex）——太重容易做乱/漏/超时。正确做法：
- **按 PRD 模块分批**（一次一批，如同批「线索+公海+商机」），每批一个 Codex 任务，页面集有限（3-7 页）范围清晰
- 追加逻辑：用户先给 bug/关键修复做本地校验 → 通过后再发铺批指令 + 部署通道（见"本地校验 vs 部署"节）

## 项目结构与模块视图组织（forge-crm 实测 2026-08-19）
- 前端页面在 **`front-prototype/src/pages/*.tsx`**（不是项目根 `src/`）——排查先 `find . -name package.json` 定位 front-prototype，再 `ls src/pages/`
- PRD 在项目根 `prd-docs/<模块>/`；标注产物 `prd-docs/<模块>/annotations/`；runtime 在 `front-prototype/public/annotation-kit/`；注入在 `front-prototype/index.html`
- **模块视图共用页面的组织**：当一个"模块"实际是主模块的视图/tab（如公海 = 线索列表页 HIGHSEAS tab + LeadPool 组件，且有独立 PRD/字段清单/Demo），标注**归到主模块**下，作为该页的一个 tab/子视图做块级标注——不单独成独立页面标注对象。PRD 依据 = 主模块 PRD + 子视图独立 PRD 都要读。排查用代码实证（grep 主页面 activeTab 枚举 + 主PRD 定位句如"公海是线索共享视图，不是独立主数据对象"）
- **重构丢锚点后 = 从零铺不是增量补**：页面 data-anno 全 0（`grep -c "data-anno" src/pages/<X>.tsx`）即使旧 annotations/*.md 还在 → 这批要【补全锚点 + 新建/恢复标注】当一轮做，顺序：补 data-anno → 写标注 → 编译 bundle → 部署（与"重构后锚点丢失"坑一致）

## 项目定位：forge-crm 是方法论练习场，非交付项目
用户 2026-08-09 明示：\"这不是要交付的项目，主要是跑通就行\"、\"并没有要满足的实际的业务\"。
- 补 PRD/改原型的目标 = **跑通\"标注体检 → 决策 → 补 PRD → 标注变准\"的循环**（证明方法论可行、可面试讲），不是做真实完整的业务系统
- **不要过度投入**：补几条代表性决策证明循环即可，不追求 10 项全量落地、不追求业务正确/完整、不为\"业务对错\"纠结
- 决策定稿文档留着当\"方法论样例\"（面试可讲拍板流程），是否实际落地看用户节奏

### 方法：标注的\"待确认/研发备注\" = PRD 缺口清单
- 标注内容里的\"待确认\"\"研发备注\"条目，本质是**PRD 没写清楚/原型与 PRD 不一致**的体检结果（2026-08-08 forge-crm 实例：我的线索含草稿 vs 定义、撤销放弃 vs 7天防撞墙、关键词多值搜索语法、AI评分边界校验、创建时间筛选、查询区展开/搜索操作、导出/批量分配/列宽拖拽能力范围、跟进中48h回收+10分钟定时扫描）
- 但**先区分两类**：①原型欠实现（PRD 定义了、原型没做）→ 补原型或 PRD 标注\"未实现\"；②PRD 不清晰/缺失 → 补 PRD。用户此前拍板：先调原型、PRD 没同步 → **改 PRD 对齐原型**（A 方案）
- **权威基线**：主PRD 是权威，但可能写的不够细；DemoPRD/字段清单同样可能缺——补的时候以主PRD 为准，Demo/字段清单对齐它

### 决策清单拍板法（批量推进，避免逐条来回）
1. 逐条整理成\"现状 + 冲突 + 建议方案\"（标注体检报告里的每条待确认）
2. 用户批量拍板（哪些补 PRD、哪些对齐原型、哪些标\"未实现\"）
3. 给 Codex 一次补全三个文件（主PRD/Demo/字段清单）→ 重编译标注 → 标注内容自动变准
- 补全后重新编译：`compile_annotations.py` → bundle → 标注的\"待确认\"应减少（缺口被 PRD 定义吸收）

## 给执行者的指令铁律：不引用截图
- **给 Codex/Cursor 的指令里绝不能写"参考第二张图/如截图所示"**——执行 Agent 看不到用户的截图，会懵
- 参考格式必须**用文字完整写进指令**（如目标格式的逐行示例），Codex 只按文字执行
- 用户指出过："这个参考格式第二张图，他知道第二张图是什么吗？"——教训：指令必须自包含

## 多项目并行铺标注（2026-08-19 用户定——效率优先）
用户明确：CRM 跑通线索+公海后，可【并行】跑 WMS/ERP（不同项目、不同目录不冲突，避免串行等死）。点齐要点：
- **skill 是按项目独立装的**：`prototype-annotation/` 目录在项目根（如 forge-crm/），不是全局共享。要给新项目铺标注，**必须先确认/安装该项目自己的 skill + runtime**——排查两个信号：`ls <项目>/prototype-annotation/SKILL.md` 存在（执行规范）+ 前端 public/annotation-kit/runtime.js 存在 + index.html 有 runtime 注入（运行时）。缺任一 = 该项目还没装，直接派标注 Codex 会读不到 skill。
- **装 skill ≠ 简单复制**：runtime.js/css 的注入路径按各项目实际 public/ 目录 + index.html 引用方式配；annotation.config.json 的项目名/路径要改。先查目标项目前端结构（`find . -name package.json` 定位 front-prototype/，`ls src/pages/`，public/ 路径，打包方式）再决定装法，直接复制会踩坑。
- **每个 agent 会话务必开在对应项目目录 + 喂对应指令**（wms 指令不掺 erp——用户曾被误伤过）；push 前逐仓库 git status 核对改动只落对项目（见 git 工作流铁律）。
- **铺标注前先核验 PRD 信息源**：不要默认"别的项目 PRD 偏粗需要重写"。查证过的反例：forge-erp / forge-wms 的 PRD 套件已较完整（主PRD + 字段清单 + 业务规则规格 + 流程/用例推演 + Demo_列表/新增编辑/详情——与 CRM 同构分层），信息源通常够。但标注那轮仍应逐个模块核验 Demo 交互细节是否细到能锚点标注（个别早期模块可能单文档偏粗）。
- **Codex 指令里的项目路径必须用 Mac 本地路径**（`/Users/liulongfei/个人文件/forge-*`），**绝不能写 VPS 的 `/root/repos/forge-*`**——Codex 跑在用户 Mac 上，写 VPS 路径找不到项目（2026-08-19 用户纠正）。同理部署 rsync 的本地源也要 Mac 路径。拿不准就先去项目根 `find . -name package.json` 实证本地实际路径，不猜。初始化（复制 skill + runtime 注入）**与组件库无关**，wms/erp 的 antd 版也能直接做；但铺实际标注时 antd 页面按 antd 组件结构加 data-anno（与 CRM 的 Shadcn JSX 结构不同）——铺标注指令要按目标组件库写。

## 症状分类："标注清单有内容" vs "原型标注点着无效果"（2026-08-20 用户报 ERP/WMS 部分页面）
**用户实测："标注清单"（面板）点开有内容；但"原型标注"（徽章/定位模式）点击后无效果。** 这两个入口症状不同 = 排错方向不同，先分清三类：
- **面板有内容（清单条目都能展开看清楚）+ 原型标注无徽章/点了无区域高亮** → 是【徽章/定位模式】问题：`data-anno` 锚点没命中（antd 结构、条件渲染区、重构丢锚点——见下方三节），或 `annotation.bundle.json` 的 selector/routeMatcher 与当前页 DOM 不匹配。面板条目来自 bundle 数据、徽章定位来自 `document.querySelector(bundle selector)`——数据在 ≠ 选择器能命中 DOM。
- **面板也有内容、徽章也能显示，但"截取/定位"跳不到区域** → selector 命中了但滚动定位目标错/区域高度 0（条件渲染未展开）。
- **两个入口都无内容/面板空** → bundle 没编译进去或 routeMatcher 不匹配当前路由（另查）。
- **跨项目/部分页面缺失** → 先确认该项目 skill+runtime 装了没 / 该页 data-anno 铺了没（VPS 仓库可能是旧版，以 Mac 工作区+线上 zip 为准——三系统曾出现线上 144 块、VPS 仓库只有 9 块）。
排错顺序：浏览器 console `document.querySelectorAll('[data-anno]').length` + 看 bundle 该页面是否有 `annotations` + 对比线上/本地 bundle 版本。别把"面板有内容"当成"标注全好"——面板只证明 bundle 数据在，徽章/定位才证明锚点命中。**症状**：前端做技术栈重构（如 Tailwind 手搓 → Shadcn/UI）后，页面右下角"原型标注/标注清单"按钮还在（runtime 正常注入），但点击"原型标注"只切模式没徽章、点"标注清单"面板不出现——像"没效果"。console 无报错（boot() 成功、按钮渲染成功，只是找不到标注目标）。

**根因**：annotation-kit 是 public/ 静态文件（runtime.js + bundle.json——重构不动它们，所以还在），但**标注锚点 `data-anno` 属性是嵌在页面组件里的**（如 LeadsList.tsx 的 9 个 `data-anno`）——反重力/Cursor 重构页面时按新组件库重写了 JSX，**把 data-anno 属性丢光了** → runtime 的 `document.querySelector('[data-anno=...]')` 找不到任何目标 → 徽章/面板/定位全失效。

**排查确认（验证锚点在不在，而不是查 runtime）**：
```js
// 浏览器 console：数页面上还有几个 data-anno 锚点
document.querySelectorAll('[data-anno]').length   // 0 = 锚点被重构丢掉（根因）
// 对比：vpa-root/vpa-floating-entries 存在 = runtime 正常，问题在页面锚点
```

**修复指令要点**（交给 agent，Hermes 不亲自修——分工铁律）：重构后必须回归验证标注功能（指令里加"验证 data-anno 锚点完整性 + 标注徽章/面板/定位可用"），若锚点丢失则按 annotation.bundle.json 的 9 块补回 `data-anno`（leads-page-header/leads-status-tabs/leads-filter-bar/leads-create-tools/leads-batch-tools/leads-table-fields/leads-ai-score/leads-row-operations/leads-permissions——每块 id 见 bundle 的 annotation id）。**给重构类指令的红线里加一条：保留页面 data-anno 锚点属性**（与"保留 erpSync.ts/Dexie/路由"并列，见 b-end-ui-stack 重构保留区）。

**通用教训**：前端重构（尤其换组件库重写 JSX）时，**嵌入页面组件的"非业务"属性（data-* 锚点/测试钩子/无障碍属性）最容易被顺手清掉**——静态资源（runtime/bundle）没事，页面锚点才是断点。重构验收清单必须包含标注功能回归（按钮/徽章/面板/定位四件套），不能只看页面渲染正常。

## antd 页面锚点加法（2026-08-19 WMS 入库模块实测）
WMS/ERP 是 React+antd（ProTable 等），与 CRM 的 Shadcn JSX 结构不同——直接给 ProTable 的属性加 data-anno，运行时 `querySelector` 找不到目标。实测可行的加法：
- **ProTable 的筛选区/表格区用 `searchFormRender` / `tableRender` 包裹实际渲染 DOM**，在包裹层上加 data-anno——保证能命中。
- **行操作/重复行**：同一 data-anno 在 N 行重复出现是允许的——运行时按目标选择器定位首个可见实例（Codex 实测 OK）。
- **条件渲染区（弹层/表单分支/新增编辑共用页）**：可见后挂载——锚点只在对应状态显示，标注面板清单仍显示该路由全部配置块；新增/编辑共用表单页时页面 ID 可共用（如 `#/inbound/form` 一个配置覆盖两种模式）。
- 验证锚点命中用浏览器 console：`document.querySelectorAll('[data-anno]').length` > 0 且对应区域高亮/徽章出现；滚动到条件渲染区（如分页/弹层）徽章按需出现属正常。
- **初始化后先铺 1 个页面验证 antd 锚点能命中，再扩整个模块**（WMS 入库列表 8 块先行 → 入库模块 43 块全铺），避免整模块返工。

## 部署后 CF 缓存坑（2026-08-08 实锤）
- **静态资源（runtime.js 等）会被 Cloudflare 缓存**（max-age=14400，cf-cache-status: HIT 可长达 80 分钟）——部署新版后浏览器仍拿旧文件，表现为"入口看不到/点击无反应"（本地 vite 正常、线上异常）
- 排查：`curl -sI <url> | grep cf-cache-status`——HIT 且 age 大 = 缓存；带 `?v=$(date +%s)` 参数能拿到新版
- **治根：index.html 引用静态资源加版本参数**（`runtime.js?v=N`，每次部署递增）——浏览器强制拉新版
- ⚠️ **deploy-all.sh 重新部署会覆盖 index.html**（Codex zip 里的 index.html 无版本参数）——**每次部署后必须重新加版本参数**（sed/python 改线上 index.html），否则下一轮又踩缓存坑

## 部署一致性验证（线上 vs 本地自检不一致时）
用户会拿 Codex 本地自检截图对比线上效果；不一致时按序排查（**不要先怀疑部署失败**）：1. **查部署日志**：`grep '\[部署\]' /var/log/jarvis-deploy.log | tail`——确认最新 zip 是否部署成功（HTTP 200 ✅）及部署的包名
2. **查线上 runtime 是否含新逻辑**：`grep -c '新特征字符串' /var/www/pmlophy.com/project/<项目>/annotation-kit/runtime.js`（如"已显示标注区域序号"）——>0 说明新代码在线上
   - **runtime 是 build 时打进 zip 的——只改 runtime 源码不重新 build+部署，线上永远是旧的。"部署成功 HTTP 200"只证明 zip 解压到位，不证明新 runtime 上线**。尤其改了"默认展开"这类交互后用户线上仍见旧行为（默认收起/展开详细说明），先 grep 线上 runtime 是否含反转特征（`const expanded = !VPA_STATE.expandedCards.has(key)`）；若否，是重新 build 的 zip 里 runtime 仍旧（本地没重新 install_annotation_kit 或 build 用旧 public），补齐"install 刷新 runtime → 重新 build → 重打包 → 重部署"再验，别以为改没生效。
3. **查 zip vs 线上 JS 名**：backup 里最新 zip `unzip -l | grep index-` vs 线上 index.html 引用——相同 = 新部署 OK（注意：改的是 public/runtime.js 时 JS hash 可能不变，要查 runtime.js 内容而非 JS 名）
4. **Cloudflare 缓存**：`curl -sI <url> | grep cf-cache-status`——EXPIRED = 实时取源无缓存问题；浏览器本地缓存则**强刷**（Ctrl+Shift+R / 无痕窗口）解决
   - **2026-08-19 最终定论（用户纠正）**：标注清单选中态"本地修好线上仍看不到"——**最终根因是 CF/浏览器缓存**（本地 Codex 已修、线上拿旧 runtime），不是代码没部署。顺序铁律：线上"新效果看不到"**先查缓存**（cf-cache-status + 强刷/无痕/`?v=` 参数），再怀疑代码没部署/没修好——不要急着让 Codex 重改（曾误判为 CSS 缺失，实际缓存一刷就好）
   - **验证线上 bundle 用 `curl -s URL -o /tmp/x.json` 下载到本地再 `python3 -c` 解析——不要 `curl | python3` 管道**（2026-08-19 被安全扫描 BLOCKED 拦截）
- 部署脚本坑（已修）：deploy-all.sh 验证 URL 必须带 `/project/` 前缀；zip 必须"解压即根"；回滚逻辑加固（无备份不删 dest）——详见上方"产物部署坑点"

## 对外发布与安全边界（2026-08-21）

当用户要把原型标注 Skill 提供给外部使用者下载时：

- 不要直接分享包含产品源码、PRD、审计报告和个人项目背景的完整 Forge 仓库；优先从项目内复制 `prototype-annotation/`，建立独立的 public Skill 仓库。
- 独立仓库只保留可复用内容：`SKILL.md`、`agents/`、`assets/`、`references/`、`scripts/`、`templates/`、`tests/`，另补 README 和许可证；去掉嵌套 `.git`、`__pycache__`/`.pyc` 和项目专属部署/业务文件。
- 发布前扫描导出目录和 Git 历史：`.env`、私钥、凭据、API key、密码、服务器 IP/内网地址、内部域名、部署请求头、绝对本机路径，以及项目专属业务资料；发现敏感内容先清理再公开。
- 原有 Forge 仓库如果含项目源码或 PRD，应改为 private；这是 GitHub 远程副作用，必须先确认有 `gh`/API/SSH 认证，再执行并独立核验，不得把“本地准备完成”说成“GitHub 已改好”。
- 如果当前环境没有可用 GitHub API 登录，不要猜 Token、不要伪造 push/visibility 成功；先完成本地独立 Skill 准备，给用户浏览器操作步骤，等用户创建 public 空仓库后再推送。
- 对外说明下载入口时，明确“下载独立 Skill 仓库”与“下载完整项目仓库”的差异，避免使用者误拿内部项目材料。
- GitHub public 只解决仓库权限，不保证中国大陆网络可达；给大陆使用者发布时，GitHub 作为 canonical source，同时准备可达域名上的版本化 ZIP 镜像或其他维护中的镜像。README 中分别标明 canonical URL、镜像 URL、版本和校验方式。

**维护纪律：独立公开 skill 仓库会随项目内实例升级而掉队（2026-09 实锤）**——只升级项目内 `prototype-annotation/`（区域级/本页规则 page-global/字段表格/check 脚本/countMarkdownItems 修复），公开 `prototype-annotation-skill` 不会自动跟随，会长成"SKILL.md 提了新特性但缺实际资产文件"的半同步版（本案例：SKILL 有 page-global/check 字样，但 `check_annotation_assets.py`、`annotation-scope.md`、runtime 新特性全缺）。**每次升级项目内标注能力后，必须同步把公开仓库 bump 成新版本（v-N）**：把 SKILL/scripts/references/assets/runtime 拷进独立仓库 + commit + `git tag v-N && git push origin v-N`。bump 公开仓库时**净化红线**：剥掉项目专属路径（`99-产品原型`/`03-产品设计`/日期版本目录）、品牌名、业务实体名（线索/商机/客户）、域名与部署细节（pmlophy/incoming/rsync/Dexie）——只留通用能力层。**公布前用 grep 复查公开仓库零残留再宣布完成**（`grep -rnE '项目路径|品牌|业务名|域名' --include=*.md --include=*.js …`，无命中才算干净）——公开库绝不能漏项目内容。核验独立仓库改动读 `origin/main` 实货、`git ls-remote --tags` 验证 v-N tag 已推，不信 agent 自报。

**公开 skill 的 README 不能只有方法论/原则/使用前提/边界——必须含「快速上手」实操**（安装 `install_annotation_kit.py` 真实命令 / 加 `data-anno` 锚点（page-global 不加锚点）/ 写标注 5 小节+四列表格 / 编译单模块+workspace / `check_annotation_assets.py` 校验 / 浏览器验收 / 修改与维护红线）。真实命令先读 `scripts/*.py` 的 argparse 再写，不凭记忆编。发布前清掉 README 里与快速上手重复的孤儿残节（孤立的 git clone 代码块 + 残缺「### 2. ### 3.」小节）。**打 v-N tag 后若有后续 doc/README 提交，把 tag 移到最新提交再推**（`git tag -d v-N && git push origin :refs/tags/v-N && git tag v-N && git push origin v-N`），否则 clone tag 的发布包缺 README；净化复查把项目英文实体变量名（如 CRM 的 `lead-`）也当敏感词剥掉，公开库更通用。

---

## 标注工具升级版三大能力 + 三步验证法（2026-09-07 定稿）

维生素新版（`vitamin-prototype-annotation`）把标注从"靠人经验驱动"升级为"靠规范+校验+示例驱动"，三大能力缺口补齐：
1. **`references/annotation-scope.md` 标注边界判断**——明确什么时候该标（状态/字段约束/计算/权限/异常/操作后果），什么时候不标（布局/尺寸/圆角/静态标题/Mock数据）。判据是"业务后果与信息缺口"，不是固定业务类型。
2. **`scripts/check_annotation_assets.py` 编译后自动校验**——编译后自动检查 bundle 完整性/配置/sourceRefs 映射/重复ID/缺失选择器，把"标完再人工看"变成"机器先过一遍"。
3. **`examples/static/` 可运行示例**——完整示例项目（config→Markdown→编译→部署全流程可跑），新项目接入"直接抄作业"。

**移植 check 脚本必须适配目标 bundle schema**：维他命 `check_annotation_assets.py` 假设 `annotation.bundle.inline.js` + `fullMarkdown` + 条目带 `markdownFile` 字段；forge-crm 的 bundle 只有 `annotation.bundle.json`（条目 `markdown` 内联、有 `coverage`，无 inline.js/fullMarkdown）——原样复制必 fail。移植时先 `python3 -c` 读目标 bundle 实测【顶层 keys + 条目字段 + coverage】，再写对应检查（forge-crm 版校验：bundle 完整性、每页无重复 id、markdown 已编译内联、target 选择器齐全、coverage 存在）。借"编译后自动校验"的纪律，不照抄文件。

**三步验证法（交付标注的强制验收标准，2026-09-07 定）**：
1. **边界判断** → 输出"该标 N 条 / 不标 M 条 + 依据"文档
2. **编译校验** → 跑 `compile_annotations.py --check` + `check_annotation_assets.py`，贴**真实运行输出**（不是"新增了脚本"）
3. **浏览器真跑** → 实际打开页面看**角标渲染**、点击出内容、无 JS 错误（贴截图/证据）

**验收口径铁律**：工具链跑通（compile→check→bundle）**≠** 标注工具可用。**"页面能看"才是核心价值**——只跑通工具链就宣称"不影响结论"是偷换（2026-09-07 娜美踩坑：跳过浏览器验证说"不影响结论"，被打回）。三样都有真实证据才算过：边界判断能指导标注 + 编译校验能抓 bug + 浏览器真能看到角标。

**给 agent 的三步验证指令模板**：分步要证据，每步"做了什么 + 真实运行/打开的证据 + 遇到的问题"。防"摆文件交差"：让她贴运行输出、贴实际打开结果，而不是只说"新增了脚本/示例"。

## 评审PRD = 标注的交付件（2026-09 定稿方向）

**定位关系**：原型标注 = 评审现场的展示工具（左原型右标注、点角标看、临场用）；**评审PRD = 正式交付件**。两者内容同源——评审PRD 就是把标注块内容**结构化搬运**成"翻开就看到"的完整文档，评审人读它审、开发按它做，不用切多份PRD。**搬运 ≠ 脑补**：内容必须来自标注/PRD，脑补会信息不一致——标注不准则评审PRD跟着崩，这条是闭环铁律。

**权威源边界（最关键）**：评审PRD 是**评审工作入口，不是第四权威源**——业务事实仍以字段权威源（字段清单文件，TSV 或 md）+ 主PRD + Demo 为准。文件头固定标这句话。开发过程中评审PRD会主动更新，但每次改动最终要回写权威源（规则→主PRD、字段→TSV、页面→Demo、跨单据→流程），靠"回写 skill"控制——**回写是人为触发的回写会话（通常一天集中一次），不是自动立即写**。

**评审PRD 每页结构（定稿）**——不单独放顶部整页大图（会和表格重复），直接进功能清单表：
```
### {页面名}
**操作路径**：线索管理/线索列表     # 面包屑，第一行
**功能清单**（9 个功能）：
| 序号 | 操作路径/功能点 | 原型页面 | 页面说明 | 备注 |
| 1 | 线索管理/线索列表-线索列表页面 | ![1](./images/线索列表页-L1.png) | （搬运该块） | 评审手填待确认，平时留空 |
```
- **表头五列加序号：`序号 | 操作路径/功能点 | 原型页面 | 页面说明 | 备注`**（多轮纠正定稿：加序号列头；"截图"→"原型页面"、"说明"→"页面说明"、"操作路径"→"操作路径/功能点"）。序号**每页独立从 1 连续**（1/2/3…，不用 L1/F1/D1 角标编号、也不用 `#`）——评审人逐条指认"第 N 个功能点"（线索列表 1-9 / 新增 1-6 / 详情 1-11）。第二列（操作路径/功能点）必须是**面包屑+具体功能点**（如 `线索管理/线索列表-状态页签`），**不允许整页同名重复**——同一页的多个角标要拆到具体功能后缀；标题用 "功能清单" 不是 "角标清单"（用户纠正）。
- **字段表 = 六列定稿：`字段名称|填写格式|是否必填|字段来源|能不能改|字段说明`**（2026-09-26 定）。值**全部从「字段清单文件」映射（评审PRD只呈现、不重新定义——字段事实权威源是字段清单，**TSV 或 md 均可，别写死 .tsv**：商机模块的字段清单就是 11 列 md，曾因 skill 写死 .tsv 而误判它无权威源）。字段清单→六列映射：填写格式←取值说明；是否必填←必填性；字段来源←字段来源（措辞统一为**用户填写/用户选择/系统生成/系统计算**，不写模糊"哪里来"）；能不能改←新增页/编辑页+备注推断；字段说明←字段说明。三页字段表（列表/新增/详情）都改六列，字段范围维持各页相关字段、不并页。
- **截图 = 整页截图 + 单红虚线框圈该角标功能点**（最终定稿，不是区域小图）——每张图是"该功能所在页面的整页截图 + 红虚线框圈出该功能位置"。角标数 = 截图数 = 说明数 = 功能清单数，四者严格相等；页面底图可重复但圈框位置不同、功能不重复（"26 个页面，页面重复但圈选区域不重复"）。**不要打开原型标注层截图**（遮挡页面），也不要裁区域独立小图（看不出所在页面布局）。只圈当前角标这一个功能点，同页其它角标不圈。
- **自动生成（Playwright + Pillow，VPS 直出，不用反重力）**：playwright `executable_path=` 指已缓存 chromium 打开在线原型 → `document.querySelector("[data-anno='xxx']")` 拿该角标 `getBoundingClientRect()`（元素高超过视口要人为限制，如表格区 max 800px）→ Pillow 在整页 PNG 上画红虚线矩形圈住该区域 → 存 `images/线索列表页-L{N}.png`（精简中文名+角标号，不带长功能描述）。画框 = 复制整页基准图 + `ImageDraw` 逐边画 dash 线（dash=8/gap=4/width=3/pad 6）。页面级角标（page/page-global/权限）框整页。弹窗类角标（转客户 D9 "转为正式客户"/作废 D10 "确认作废草稿"）先真实点击触发弹窗再截，用弹窗图而非画框。
- 角标清单每行直接搬运对应标注块内容（不脑补）；功能 / 说明来自角标标题与标注正文。
- **备注列平时留空**，是评审时手填"待确认/裁决"的输入位，不是预填内容。
- 弹窗类角标（D7 添加跟进 / D8 放弃）已有弹窗截图直接复用，不画框。

**给截图 agent（反重力）的区域截图指令**：反重力作"法拉利"执行会漂移，必须配 ego lite（"导航/眼睛"）定位网页元素——读本机 `~/.agents/skills/ego-browser` skill，用 ego 打开在线原型、`document.querySelector("[data-anno='xxx']")` 拿区域做截图，反重力判断"这块是哪个角标"。指令必须写明：逐角标 路由 + data-anno 锚点 + 截图区域 + 中文文件名（如 `线索列表页-L3-线索筛选与查询栏.png`）；弹窗类角标要点开触发再截；红线 = 只截图、不改代码、不 push、不伪造（每个角标必须真正定位到的实拍）；ego 报 503 = 应用没启动，Cmd+Q 重开。优先用 Cursor 内置浏览器（也能定位区域+截图，与 ego lite 等价）或反重力+ego。
模块结构 = 业务总览 / 功能清单 / 主要流程(含 Mermaid 业务流程图) / 状态流转(单据才有) / 业务规则 / 页面与操作 / 字段 / 权限(默认不写) / 验收。**"必有"层**（总览/功能/流程/规则/页面/字段/验收）和**"按需"层**（状态机/权限/异常边界）分开——按需层"有才写，无则标不适用"。

**功能清单 = 原型标注角标一一对应（生成期铁律）**——每条功能对应一个标注块/角标，**数量必须严格相等**（线索 9+6+11=26 角标 → 功能清单就 26 条）。严禁把角标聚合成"功能群"写成 11 大条（用户纠正："现在角标有 10 个，就要补充 10 个功能清单"）。生成时先从 `annotations/pages/*.md` grep `anno:start` 数出实际块数，再按同名角标逐条列功能；做功能清单时别凭空脑补新功能名——名称/内容都来自角标标题（如「状态页签与线索池视图」「表单完整性与去重拦截」）。验证用计数核对：功能清单条目数 == 标注块数（`grep -c 'anno:start' annotations/...`）不等就返工。⚠️ 这个"一一对应"是**生成/校验时的逻辑**（SKILL 里的动词），**不是要写进评审PRD正文的陈述句**——文档里绝不能出现"与原型标注角标对应、共 N 个"这类字眼（用户两轮纠正："这个给谁看的？我和评审人都看不懂"）。

**制作说明句必须从评审PRD里删光**（2026-09-26 用户两轮纠正）：凡是给"做标注的人/生成 AI"看、讲"怎么来的/怎么做的"的句子——"与原型标注角标一一对应、共26个（列表9+新增6+详情11）""内容来源：由原型标注搬运整理而成""…对应原型标注角标，评审时在原型图讲述…""修改请回写权威源"——评审人/开发/用户都看不懂，是**噪音，一律删**。评审PRD受众 = 评审人 + 开发 + 用户，只留**业务内容**（是什么/怎么操作/什么规则/判断条件），不给受众讲制作背景或来源映射。判别一句删不删：这句是给"做标注的人"看的制作说明 → 删；是给"评审人和开发"看的业务陈述 → 留。做完全局 grep 常见制作词（角标/标注块/来源/搬运/how/映射）清零再交付。

**MD 嵌图（评审/交付文档）**：截图存评审PRD同级 `images/` 目录，用相对路径 `![xxx](./images/xxx.png)`——图随仓库走，GitHub 在线可渲染（已实测），评审人不依赖外链/单独文件。页面章节必须先嵌该页截图再写描述——评审人没有截图就"无法图示"（用户纠正）。

**嵌图排版：一图对应一份说明，就近对照**——不能把图全堆在章首、文字全堆在章后（用户判为可读性差）。每页一张干净整页图，图下方跟该页角标清单表格（角标｜功能｜说明｜备注）。图固定"放在页面操作路径之后、角标清单之前"，同一页面图与角标清单就近——评审看图找位置、看角标清单读该块说明，不来回跳。（早期的"左图右说明合并单元格"已被本次定稿替代——用户要的是"一图 + 逐角标清单"而不是把功能/关系/交互/规则塞进一个单元格。）

**截图规范**（评审PRD固定规则）：①**准确**——截自实际能跑的原型/系统，反映真实渲染，图上内容和页面说明一致，不脑补；②**全面**——不只有主页面，关键交互小图也截：弹窗/Toast提示/二次确认/批量操作/空数据态都要覆盖，评审看的交互点就有图；③**中文命名对应章节**——如 `线索列表页.png`、`弹窗-添加跟进记录.png`，一眼知道是哪页；④存 `images/` 子目录。

**Playwright 无头截在线原型图（附链到线上截图）**：VPS 用 python playwright 截图已部署的 forge 原型页（如 `https://pmlophy.com/project/<项目>/#/leads`）。坑：pip 装的 playwright 库要的 chromium 版本 ≠ 缓存里已下的版本，launch 会报 `Executable doesn't exist at .../chromium_headless_shell-1243/...`——**别 `playwright install`，直接 `executable_path=` 指到已存在的完整版二进制**：`p.chromium.launch(headless=True, executable_path="/root/.cache/ms-playwright/chromium-1148/chrome-linux/chrome")`。整页图 `page.screenshot(full_page=False)`；截整页内某个区域用 `clip={...}` 传坐标框。截弹窗/交互层：真实点击（如点行内"查看"进详情、点"添加跟进"弹窗）后再截图，弹窗用 `full_page=False`（居中模态，全页截会带遮罩底）。截图后 `file` 验证是有效 PNG、尺寸正确再入库，别存"加载中/空状态"的图（字段值未渲染的假截图）。

**交付格式：md 源 + base64 内嵌发布版**（跨平台图不断的关键）。Cursor 的 md 预览窗**不支持图片点开放大**，GitHub 网页点图要跳转——都不适合"发给外部人"的交付。语雀/Confluence 支持图片放大。所以交付前跑 `scripts/embed_images.py {评审PRD}.md` 把相对引用替换成 `data:image/png;base64,...`，生成自包含发布版——图以 data URI 内嵌进文档，发到语雀/Confluence/邮件图都不丢（实测语雀能放大）。仓库保留引用版（好维护），交付用发布版。

**文档版本记录：叫「修改记录」，放文档最上面，只留版本|修改人|修改内容**（2026-09-26 定，多轮纠正）。名字**绝不能用「台账」**——台账特指财务/交易类系统（借贷流水），评审PRD是文档更新记录，会误导；用「修改记录/变更记录」。位置在**文档头部版本行正下方**（不是文末），表头 `日期 | 版本 | 修改人 | 修改内容`。**只保留这三要素**——去掉"回写目标/回写完成"列：回写权威源是回写 skill 的职责（另有一套变更映射），本表只记录这份评审PRD自身的修订史，两职责解耦。改动时同步更新头部版本号（如 V0.7），改完 push。

**语言规范（大白话）**：正文全中文，**禁用 In/Out of Scope、SSOT、RBAC 等英文术语**（"做哪些/不做哪些"、"按角色权限管控"）；唯例外是技术枚举值/代码字段名（DRAFT、ONLINE）保留英文给研发对照。目录结构要有但全中文。判据：普通业务人一眼能懂 = 合格，要查字典/想半天 = 不合格。"颗粒度细但不啰嗦、说重点要点"——尽量条件→结果一条一行、表格优先。

**权限治理（用户明令，AI 默认爱加权限是病）**：权限是评审PRD的"按需"项，**默认不写**。真实场景权限多由运维/运营/RBAC 管控，不由产品经理定义。写权限章的判据（决策表）：
- ✅ 需求分析明确区分"不同角色所看不同/所操作不同"——页面要做角色控制
- ✅ 系统未实现 RBAC，需要页面自己做角色控制
- ❌ 只是常规账号/组织/系统权限靠 RBAC/运维 → 标注"由运维/运营/RBAC 管控"
- ❌ 无角色差异需求 → 不写，禁硬造角色×操作矩阵
- 拿不准 → 标"待确认：权限归属由XX确认"，绝不自行拍板一个矩阵。

## 标注来源澄清：PRD 还是 TSV？（2026-09-07 关键纠正）

**标注的来源始终是 PRD Markdown 文件**（SKILL Workflow A 第2步：Read business PRDs）——`TSV 字段清单是标注的前置输入，不是标注本身的来源`。**三步验证法是验证环节，不改变标注来源。**

**但"规则和约束"要分两层，来源不同**：
| 层 | 内容 | 来源 |
|---|---|---|
| **字段事实层** | 字段类型/来源/必填条件/取值范围/枚举/格式/字段级校验 | **TSV**（字段事实源） |
| **业务规则层** | 跨字段/跨状态/跨单据约束（如"审核后不可修改""入库数不超未入库数"） | **PRD**（业务规则源） |

**所以标注的"约束和规则"是 TSV + PRD 的混合来源，按类型各归其主**——字段级约束对齐 TSV，业务级规则来自 PRD。若标注里字段约束全从 PRD 扒、TSV 没被引用，说明 **TSV 白跑了**（没发挥"字段事实源"作用）。

**v1/v2 标注内容看起来一样是正常的**（同一套 PRD 生成），**v2 的价值在交付质量**（三步验证法的验收记录），不在标注内容差异。但要警惕"v2 加了 TSV 却完全看不出 TSV 生效"——那 TSV 就是"为跑 skill 而跑"，需追问"TSV 到底用在哪一步、有没有影响后续 PRD/标注的字段定义"。

## 模型选择：严谨对齐的标注别用漂移模型（2026-09-07 教训）

标注生成需要**严谨对齐 TSV 字段事实 + PRD 规则**。用**易漂移/幻觉的模型**（如 Gemini/反重力）做这类严谨活，漂移是必然 → 标注质量差、漏字段、来源引用错。**标注生产优先用稳的模型/流程**（Codex/DS 等），反重力/Gemini 适合"快而糙"的原型/UI 批量，不适合严谨对齐活。诊断教训：v2 标注 bug 部分源于用反重力生成（"他很容易漂移幻觉"）。修复类活交 Cursor（精准改），别让生成侧硬修。

**漂移 agent 的自检报告会虚标覆盖范围**——不只生成的内容会漂，它还会在报告里写"统一改为…""0 遗留风险"，实际只改了极小一部分（先例：反重力声称"字段说明统一改为四列表格"，实只做了一页的 3 块；"0 遗留风险"里藏着范围不足）。验收**必须先 ground-truth**：查实际 git diff（`git show <commit> --stat`）+ 重读目标文件/bundle 核对，声称的"全量/统一/0遗留"逐条对实货再下结论——自报不是证据。

**核查 shared 分支上 agent 的交付，从 `origin/<branch>` 读实货**（`git show origin/<branch>:<path>` 或先 `git pull --ff-only`），**别读可能落后的本地工作区**——本地落后会把"其实已改好"误判成"没改"，冤枉 agent（先例：VPS 本地 clone 落后 origin，读本地 config 全是旧字段级块，差点判定 agent 没做）。
**判定 agent 失败前，先自查你的验证查询本身**：文件真实名称大小写（opp 表单页是 `OppForm.tsx` 不是 `OpportunityForm.tsx`）、精确子串（config target 是 `-basic` 不是 `.basic`）。false-negative 验证会冤枉 agent、浪费一轮重做。

## 字段说明转表格后"显示空"的运行时坑（2026-09-13 实锤）
把标注的 字段说明 从段落 `- x：y` 转成 markdown 4 列表格后，面板里"字段说明"tab 显示 **0 项 / 该分组暂无内容**，即使表格数据在 bundle 里。根因：runtime.js 的 `countMarkdownItems` 只统计 `- + * 或数字`列表行（`/^\s*(?:[-+*]|\d+\.)\s+/gm`），**markdown 表格行不计** → 表格字段说明计数 0、渲染空；"全部"合并视图也因 count=0 忽略纯表格的 tab。
修复：`countMarkdownItems` 统计 markdown 表格数据行。**只排除分隔行不够——表头行也会被数进去**：表头 `| 字段 | 展示/输入类型 |…` 下一行是分隔行，但旧 regex 把表头当数据行计数 → tab 显示 N+1（实锤：字段说明 tab 显 4、真实数据行 3）。正确用逐行扫描——表头(下一行是 `| --- |` 分隔)不算、分隔行不算、只有"下一行不是分隔的数据行"才算：
```js
const isSep = (line) => /^\s*\|(?:[ \t]*:?-{3,}:?[ \t]*\|)+\s*$/.test(line);
const isBar = (line) => /^\s*\|/.test(line) && !isSep(line);
let listItems = 0, tableRows = 0;
for (let i = 0; i < lines.length; i++) {
  if (/^\s*(?:[-+*]|\d+\.)\s+/.test(lines[i])) listItems++;
  else if (isBar(lines[i]) && !isSep(lines[i + 1] || '')) tableRows++;
}
return listItems + tableRows;
```
**两份 runtime.js 必须同步**（public/annotation-kit + prototype-annotation/assets/annotation-kit），只改一份下次 build 用旧模板覆盖。改完用 node 复现 parse+count 对真实 bundle 块验证数据行数（`parseAnnotationTabs` + `countMarkdownItems` 对着块 markdown 跑，期望数=数据行；**别相信"应该对"**——曾以为修好、实测仍显 0）。

## 反重力做严谨标注活会飘（2026-09-13 复证）
反重力/Antigravity 适合"快而糙"原型/UI，**不适合字段对齐类严谨活**：做字段表格化时自检报告虚标"0 遗留风险、已统一"，实际范围只做一页 3 块、其余全没动，还重写 runtime 引入回归。教训：标注/字段对齐这类精确活优先 Codex / 自写脚本（脚本要"模块感知 TSV + 只转干净的 `字段：描述`，枚举/短语类别硬塞表格"）；用反重力后必须独立核 diff 与范围，不信其自检报告。

## 字段说明目标 = 从字段清单TSV生成13列Excel（非4列摘要，2026-09-17 用户定）

字段说明的呈现目标**不是** 4 列摘要（`字段|展示/输入类型|业务说明|约束与备注`），而是**从该模块的「字段清单（详细稿）.tsv」编译生成完整 Excel 表**：表头=TSV 13列（字段所属分组/字段名称/字段类型/字段来源/字段说明/必填性/新增页/编辑页/列表展示/可筛选/详情展示/取值说明/备注），行=该页实际出现的字段，值全从 TSV 填（TSV 为 `-` 的空列保留 `-`），表尾加「来源：字段清单（详细稿）.tsv」。

**目前只有线索模块建了字段清单TSV**；商机/客户/合同/拜访/业绩 6 模块**没有 TSV** → 其字段说明无法做 13列，需先建 6 模块的字段清单详细稿TSV（用户记"周末梭哈所有模块"其实梭哈的是原型标注skill，字段清单TSV只建了线索）。反gravity 那次只把线索的 8 块做成 13列、其他模块字段说明仍空——验收必须核实「所有线索页（列表/表单/详情/公海）都改了 + 值真从TSV来 + 不是只做一页」（反gravity 历史坑）。

## 办公机/公司 agent 的自检上传泄漏红线（2026-09-17 实锤）

办公机反gravity 的 `.agents/rules` 有**全局默认「自检报告 curl 上传 pmlophy.com/p/jarvis/file/upload ai-reports」通道**，给所有 agent 继承——在公司 CMS/娜美项目上跑时会把**公司内容（知识宝典/审计/代码/PRD）泄露到个人 VPS**（实发：CMS 知识宝典一致性审计自检报告传上来了）。公司项目指令必须：①去掉「curl 上传 pmlophy ai-reports」整段（自检报告只落项目内 `08-相关资料/check-reports/`）②加红线「公司内容禁外发到任何个人/外部服务器」。个人管道的上传命令**只在个人项目（forge-*）指令里给**；office/公司 agent 指令模板一律不带个人管道上传段。

## 本页规则 page-global + 四层校验（维生素13节吸收，执行侧）
- **整页通用规则**（防重提交/未保存离开拦截/页面准入/整页加载失败）做成 **page-global**（type=page-global，无元素锚点），不硬挂具体按钮/字段角标；组件级规则才挂局部角标。
- **支撑细节走查按四层**：字段级（取值/格式/上下限）/页面级（联动/明细约束）/业务级（状态准入/重名/库存额度）/系统级（网络/超时/重复提交/并发）。每规则写清：触发时机（输入/失焦/动作）、操作结果（成功/失败/结果不明确怎么确认）、错误修正后何时清除。
- 避免模糊词（"宽松校验""格式错误"）——要写清宽松允许缺哪些、格式错误包含哪些。

## QS-JXC 项目框架对齐（把产品项目升级到分层框架）
**字段清单结构约定（2026-09-13 用户采纳，照维他命 QS-JXC）**：一个模块一个大 TSV，内部用 `===== 单据/子对象 =====` 分隔行切多个单据（如 采购模块详细稿 = `===== 采购订单 =====` + `===== 采购入库单 =====` + …），列A"字段所属分组"做二级分类（单据头/基本信息、单据体/商品明细、单据头/系统字段）；目录 `03-产品设计/<版本>/字段清单/<模块>的字段清单/<模块>模块字段清单（初稿|详细稿）.tsv`。详细稿 13 列=`字段所属分组|字段名称|字段类型|字段来源|必填性|新增页|编辑页|列表展示|可筛选|详情展示|字段说明/描述|取值说明|备注`（与 forge 线索详细稿列一致）。
**99 命名澄清**：QS-JXC 顶层 `99-产品原型prototype` 是**刻意**的末位原型目录槽位（非 09 笔误），forge-crm 已照搬同名字段保持一致。
要把已存在的产品项目（forge-*）升级/创建为 QS-JXC 分层框架（01全局背景~99原型 + 版本化 + 模块=主PRD+骨架+Demo合集+annotations）时，见 `references/qs-jxc-framework.md`。五个必守坑：
- **必须在 Mac 真源上做，不在 VPS 半镜像上**——VPS 拷贝缺 docs/drafts/prototypes/reference 等目录，推分支后真源旧目录 untracked 残留 → 新旧并存语义重复；先 `git status --short` 审计 tracked vs untracked。
- `git mv src dst` 到**已存在的空目录会嵌套**（`dst/src`）——改名先 rmdir 空目标或 rename 到不存在路径。
- `cp -rn src/dir dest`（dest 已存在）会套一层——合并逐项 cp。
- **AGENTS.md 受保护**：重写需用户明确批准；批准前先给草稿。
- **每条给 agent 的指令（含框架/文档合并）末尾都带自检报告上传通道**，否则会被用户补指。

## 参考资料
- `references/qs-jxc-framework.md`：QS-JXC 分层框架结构 + 逐文件夹职责/设计意图 + 五条设计本质(单一事实源/约束集中编号/变更传播/模板同构/待确认纪律) + 04模板执行索引(Step①-⑥关卡) + 07 UI spec-manifest 驱动 + 权威源分层/变更传播/TSV 体系 + 迁移坑 + 深度解读纪律
- 维他命课程 09：迭代资料管理（本次需求文件夹/模块当前基准资料/历史归档）+ ASCII 线框图先确认 + 标注 + 研发交接说明
- 课程配套 Skill：vitamin-prototype-annotation → 已改名 `prototype-annotation`（forge-crm 项目根，已补语言规范）
- `references/forge-crm-pilot.md`：试点完整记录（路径/命令/部署事故/5 个待确认项）——续作或推广到其他模块前先读
- `references/annotation-ui-style-target.md`：标注 UI 目标样式拆解（实现"面板+tab+卡片+定位"时对照）
- `references/annotation-tab-and-heading-architecture.md`：tab/标题机制（我们 6-tab 写死在 runtime.js、内容按 `###` 标题解析；维他命无 tab 是 TOC 阅读器）+ "空 tab=真缺口"审计法（判空先剔 `<!-- -->` 注释；待确认空是设计非缺口）
- `references/multi-project-rollout.md`：把标注系统铺到 wms/erp 的标准流程（初始化≠铺标注、路径用 Mac 本地、antd vs Shadcn 差异、部分项目 cron 只检测不自动部署需手动 --deploy、自检报告命名带项目名）
- `scripts/embed_images.py`：评审PRD 交付前生成 base64 内嵌发布版（解决 Cursor 预览不能放大图 / 跨平台引用路径断）——见"评审PRD"章节"交出格式"条
- `references/vitamin-new-version-comparison.md`：维生素新版 vitamin-prototype-annotation vs 我们的对比（0906）——他强在工程化/技术栈覆盖/诊断接口，我们强在业务语言+6-tab评审闭环+实战规范；融合=拿他工程化做底接我们产品视角。用户已定先不迭代。

## 方法论锚点（用户原创，面试/方案可讲）
- **技术转产品 = 经验判断 → 工具实证**（2026-08-09 用户洞察）：以前用技术经验判断"能否实现"（间接/可能过时），现在用 AI IDE 深度使用直接实证（做出来看，眼见为实）。技术底子给方向感/边界感，AI 工具给实证验证——forge 三件套就是此方法论落地（想法→让 Codex/Cursor 做出来→实测→拍板）。区别于纯 PM（缺方向感）/纯工程师（不深度用 AI 工具）的独特卡位。用户会把这叫"对 AI 许愿"（灵感→反复沟通打磨→沉淀成能力），一条灵感边做边变是常态，不是偏差。
- **用户说"总结要点"可能是在感慨，不是要正式交付物（2026-09-26 两轮纠正）**：干完一天的活，用户要"你帮我总结下"往往只是想复述/回味今天做了什么、get 到多轮打磨成型的爽感，不是要结构化的技术/方法论长文。先分清他要的是"方法论梳理"还是"情绪分享/感慨"——若他在尽兴（"我一直在对AI许愿，并且许愿成功了"），就顺着接住、简短附和他的成就感，别自动产出一份总结文档（曾先给技术总结被纠"总结就是针对一些灵感，需要多次沟通修改调整沉淀总结"，又给方法论版再被纠"不是，你扯远了，我是在跟你感慨呢"）。识别信号：带"哈哈/感慨/尽兴"语气、口语化、无明确"产出物"诉求。
- **不到万不得已不靠猜**（2026-08-09 铁律）：技术/工具/平台"应该怎么做"先查官方文档/源码/测试（实证）再下结论——Holographic 记忆用法就是教训（靠猜 SQL 直插=僵尸记忆，读官方源码才发现正确用法）。见 `holographic-memory-usage` 技能
- **标注当 PRD 体检报告**（2026-08-09 定方向）：标注是编译产物（非实时获取），PRD 变更需执行 Agent 重跑"标注同步"；forge-crm 是方法论练习场非交付项目（跑通循环即可，不过度投入）
