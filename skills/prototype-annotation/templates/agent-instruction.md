# Context
使用 `skills/prototype-annotation` 标准为本 PRD 套件建立或更新原型标注。只改标注源与编译产物，不改业务页面逻辑。

参数（仅填以下三项）：
- **项目根路径**：`{{项目根路径}}`
- **PRD 套件目录**：`{{PRD 套件目录}}`
- **本 PRD 涉及页面清单**：`{{本 PRD 涉及页面清单}}`（路由或页面名列表，供校验第 10 条）

契约全文见同 skill 下 `STANDARD.md`；标注块样例见 `templates/block-sample.md`。

# Request
按顺序执行五步，每步未达验收不得进入下一步。

**步骤 1 — 块清单（须人工拍板）**  
盘点本 PRD 在「涉及页面清单」内应有哪些标注块（按功能点，见 STANDARD §3）。输出表格：页面/路由、`screenState`、块名称、锚点意图。  
**验收**：清单已交人确认；**禁止**未确认直接写 md/config。

**步骤 2 — 编写 config 与 md**  
按 `templates/block-sample.md` 六页签形态编写；`sourceRefs` 覆盖需求点；宿主页 `screenState` 为 `host`，弹窗等写独立 `screenState`。  
**验收**：块数与确认清单一致；无展示用「来源」行写入 md。

**步骤 3 — 编译与校验（全绿）**  
```bash
python3 <PMLOPHY_SKILLS_PATH>/skills/prototype-annotation/scripts/compile_annotations.py "{{PRD 套件目录}}/annotations/annotation.workspace.json"
python3 <PMLOPHY_SKILLS_PATH>/skills/prototype-annotation/scripts/check_annotation_assets.py {{项目根路径}}/原型 public/annotation-kit 路径 --src {{项目根路径}}/原型 src --routes {{项目根路径}}/原型路由文件 --config "{{PRD 套件目录}}/annotations/annotation.config.json" --prd-pages "{{本 PRD 涉及页面清单}}"
```  
**验收**：两条命令均成功，十条判据无报错。

**步骤 4 — 构建**  
在原型工程目录执行 `npm run build`。  
**验收**：构建成功。

**步骤 5 — 人工验收后部署**  
浏览器验证角标、六页签、弹窗打开时仅显示对应 `screenState` 组角标。  
**验收**：人确认通过后，才允许部署；并递增 `index.html` 中 annotation-kit 的 `?v=`。

# Output format
每步汇报：做了什么、验收判据是否满足、命令原始输出（步骤 3–4）。

# 红线禁止
- 不修改业务源码与 PRD 正文（标注源除外）。
- 不跨 PRD 合并标注；不把历史 PRD 标注留在 bundle。
- 校验失败不得放宽判据或跳过 `--src` / `--routes` / `--config` / `--prd-pages`。
- 未做人审不得部署。

# Checkpoint
步骤 1 清单确认前停止；步骤 5 人审前停止。
