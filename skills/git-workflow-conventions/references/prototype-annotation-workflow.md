# 原型标注工作流（2026-08-07 forge-crm 试点）

用户产品理念：模仿 Axure 时代"左原型右标注"的高效评审模式，用 AI 实现自动化标注——页面区域挂业务规则标注（交互/规则/字段），评审时一眼对照，PRD 不用赘述文字版交互说明。

## 三层分工（用户定稿）

- **执行者**：Codex/Cursor（项目内跑标注工作流）
- **检阅者**：杰西卡 + 罗宾（审标注质量，不出手改项目代码）
- **验收者/使用者**：用户（最终拍板）

## Skill 安装位置（实战确认）

- Skill 包放**项目根目录**（如 `forge-crm/vitamin-prototype-annotation/`），**不是 .cursor/rules/**：
  `.cursor` 被项目 .gitignore 忽略，git add 报 "The following paths are ignored"，push 不上去。
- 装好后走 git 工作流：VPS 仓库 commit + `git push origin main` → 用户 Mac `git pull origin main` → 用户发执行指令给 Cursor/Codex。
- Skill 包本身放哪都行（Agent 读 SKILL.md 即知用法）；关键是**生成物的位置**要规范。

## 课件标准目录结构（Skill 生成物位置）

```
prd-docs/<模块>/                        ← 标注跟 PRD 走
├── 主PRD.md / 字段清单.md / Demo_列表页.md
└── annotations/
    ├── annotation.config.json          ← 标注块↔页面区域↔PRD来源
    └── pages/<module>.md               ← 标注内容（一个文件可放多个页面区域）
<prototype>/public/annotation-kit/
    └── annotation.bundle.json          ← 编译产物，原型页面实际读取
```

标注文件跟 PRD 旁边；编译产物在原型工程 public/annotation-kit/。运行时只读（无编辑/保存/写回）。

## 给 Cursor/Codex 的执行指令模板（初始化）

```plaintext
Context:
项目：forge-crm（Mac 本机 /Users/liulongfei/个人文件/forge-crm/）
任务：用 vitamin-prototype-annotation Skill 对【线索列表页】做原型标注初始化
Skill: 项目根 /vitamin-prototype-annotation/（已 pull）
目标: 线索列表页加"左原型右标注"（标注跟随 PRD 目录，编译产物在原型工程）

Request:
1. 读 Skill: vitamin-prototype-annotation/SKILL.md（Workflow A 初始化）
2. 读线索 PRD: prd-docs/线索管理/线索主PRD.md + 字段清单 + Demo_列表页.md
3. 读页面: front-prototype/src/pages/LeadsList.tsx
4. 按课件标准结构产出:
   - 标注目录: prd-docs/线索管理/annotations/
     ├── annotation.config.json（scope=leads，映射页面区域/选择器/PRD来源）
     └── pages/leads-list.md（标注内容，含"来源"行）
   - 编译产物: front-prototype/public/annotation-kit/annotation.bundle.json
   - 运行时: 注入 runtime（最小 hook + data-anno 锚点）
5. 步骤: 提取列表页业务规则（状态Tab/筛选/操作列/字段规则/状态流转/异常）→ 忠于 PRD
   → 建 DOM 目标清单（稳定选择器，优先 data-anno）→ 按 UI 模块聚合标注
   → 写标注 Markdown（含来源行）→ config → compile_annotations.py 编译 → bundle
   → 注入 runtime → 浏览器验证（徽章+弹窗）→ 截图
红线: 不污染 PRD/业务代码（只加 data-anno + runtime hook）；不 commit/push/部署；标注忠于 PRD，来源不明标"待确认"
Checkpoint: 浏览器截图（徽章+弹窗）；标注文件/配置/bundle 路径清单；汇报标注了哪些区域、哪些来源待确认
```

## 检阅要点（reviewer 版，杰西卡/罗宾用）

1. **忠于 PRD**：标注内容来自 PRD（不是 AI 脑补）；每块有"来源"行；来源不明标"待确认"
2. **不污染**：PRD 未被改写；业务代码只加 data-anno/runtime hook；标注独立存放
3. **覆盖完整**：状态Tab/筛选/操作列等区域都有标注；用 coverage.md 查未覆盖
4. **增量更新**：只动受影响块；旧标注不乱删；id 规则（模块内 1/2/3，补充 A1/A2，嵌套 1a/1b）
5. **运行时合规**：只读；徽章不改变布局；选择器稳定（data-anno > testid > 语义选择器 > class）

## 部署坑（2026-08-08 试点实测，deploy 后 404 回滚）

- **zip 必须"解压即根"**：Codex 打包若保留 `front-prototype/dist/` 前缀 → 部署到 `project/forge-crm/` 后入口在嵌套路径 → 验证 404 → 自动回滚。正确：cd 进 `front-prototype/dist` 内部打包（zip 第一层直接是 index.html/assets）。检阅时先 `unzip -l` 看结构，发现嵌套路径要在部署前重打（或手动解压取 dist 内容部署）。
- **管道命令必须逐字写进指令**（v135 教训重演）：只写"按管道上传"不够——Codex 跑完标注不会主动 rsync/curl。指令末尾必须给完整命令（rm+zip / rsync / curl 报告上传）。检测"改好了但没收到产物"→ 先查 VPS incoming/ 和 ai-reports/ 是否为空，缺就给补传指令。
- **forge-crm 部署路径与其他项目不同**：incoming=`/var/www/pmlophy.com/forge-crm-incoming/`，目标=`/var/www/pmlophy.com/project/forge-crm`（注意 project/ 子目录，jarvis-voice 是根目录下）。
- **标注的增值 = 暴露"原型 vs PRD 不一致"**：Codex 跑标注时会发现原型实现和 Demo PRD 的差异（状态定义/回收规则/字段能力缺失）——这些是**待确认项**不是 bug。检阅时整理成清单给用户拍板（原型改对齐 PRD / PRD 改对齐原型 / 逐个确认）。本次试点报告出 5 个待确认项（DRAFT 状态定义、撤销放弃保护、FOLLOWING 回收、搜索/导出能力缺失、放弃原因校验）。

## 来源

- 维他命课程 09《项目资料的版本管理与原型标注》（/root/notes/vitamin-course/09...md）
- vitamin-prototype-annotation Skill zip（课程配套，含 SKILL.md/scripts/assets/references/tests）
