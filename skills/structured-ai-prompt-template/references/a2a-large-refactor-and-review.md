# A2A 大改与复核 Playbook

用户（刘龙飞）的工作拓扑：**Mac = 权威编辑端**（Codex/反重力 在 Mac 上改代码/文档，有 GitHub 推送权限）；**VPS = 只读复核镜像**（Hermes 在这里出五段式指令 + `git pull` 复核）。GitHub 是中转。

## 1. 写「会改文件」的指令前，先量爆炸半径

绝不凭标题估规模。动手前用 search_files 数清楚：

```
# 数某类改动占多少处、分布在几个文件（output_mode=count）
search_files(pattern=..., path=prd-docs, output_mode="count")
```

判据：
- 小改（≤ 十几处 / 几个文件）→ 直接出会改文件的五段式指令。
- **大改（几十文件 / 上百处）→ 先出「只读影响面报告」指令**（见 §2），审完再分批。

实战教训：本会话「货位命名统一」看着是一个文件，一扫才知代码早就 camelCase、只有文档滞后；而「全项目 SKU + camelCase 统一(C)」一扫是 **939 处 snake_case / 55 文件 + 195 处 SKU / 44 文件**——是前面 ①~⑤ 返修（18 文件/179 行）的 10 倍。若当时盲甩一条 mutating 指令，55 文件 diff 无法审、Agent 极易改塌场景数据。

## 2. 报告先行（Report-First）指令骨架

大改 / 涉及主数据重定基 / 有系统性分歧时，第一条指令**零改动**，只产出可审批的映射表：

```
Request:
扫描 <范围> 下所有 .md，列出每一处 <目标模式> 的引用，产出报告：
【文件+行 | 现值 | 建议映射 | 前端代码/SSOT 里的对应(查证) | 一致/存疑】。

Output format:
按模块分节，每节一张映射表 + 计数；末尾单列「存疑/待人工指定」清单。

红线禁止:
- 【本条只出报告，一个字都不许改】不动任何 .md、不动任何代码。
- 不臆造对齐关系，查不到标「待确认」。

Checkpoint:
报告一次产出，等我审批映射后再另行下达执行指令。
```

审完报告 → **按模块拆执行指令**，一次并行封顶 2-3（文件隔离铁律），基础数据/入库/出库/库存/盘点/调拨/报损逐块推进。这是跨多次会话的规范化工程，别想一晚啃完。

## 3. 指令锚定 SSOT / 金标准范本

不要在提示词里「凭空定标准」，先在仓库里找到已经是目标态的参照物，指令里当**只读范本**指过去：
- 同族里已改好的字段清单（本会话：库区字段清单已 camelCase → 货位照抄）。
- SSOT 文档（商品档案字段清单声明「Demo 用 `SKU001` 口径」）。
- **前端 seed / 代码真实字段名**（`front-prototype/src/db/index.ts` 用 `productCode` + `SKU001~007`）——这才是「前端页面↔文档对齐」的事实源。
教训：出库链 `SKU-A100` 与库存 `SKU10086` **两套 mock 都跑偏**，正主是商品档案/seed 的 `SKU001~007`。锚定 SSOT 后 Agent 出错率骤降，用户也认这套（"锚点摸好了"）。

## 4. 反重力跑非前端任务时的红线加固

Codex 挂了可让反重力(Gemini)顶文档/审计——五段式工具无关。但反重力惯性是「生成前端 + 跑得快」，红线段必须替换加固：

```
红线禁止:
- 【本次是纯文档审计，不是做页面】不许生成/改动任何前端页面或代码：
  front-prototype/ 下的 .tsx/.ts/db/api 一行都不许碰，只读改 prd-docs/ 下的 .md。
- 【别一把梭】必须先出差异报告，系统性问题只报告不改；拿不准的标「待确认」。
- 路径一律用项目内相对路径。
```

## 5. 复核 IDE Agent 的产出（A2A 的另一半）

用户铁律：**"别犯傻，先检查，再 pull。"** Agent 在 Mac 改完 push 后，VPS 侧标准动作：

```bash
cd <repo>
git fetch origin <branch>                                  # 只读，不动工作区
git merge-base --is-ancestor HEAD origin/<branch> && echo FF安全 || echo 已分叉别盲pull
git log HEAD..origin/<branch> --oneline                     # 远程多了哪些提交
git diff --stat HEAD origin/<branch>                        # 将改哪些文件
git diff --name-only HEAD origin/<branch> | grep -vE '\.md"?$'   # 红线:有没有动.md以外
# 干净FF + 只动该动的文件类型 → 落地
git merge --ff-only origin/<branch>
```
- 落地后再 read_file 抽验关键行（转义生效？表格不断？命名对了？），**别只信 Agent 自报**。

## 6. VPS git 是只读镜像（推送走 Mac）

- VPS **没配也不该配** GitHub 推送凭据（无 gh / credential.helper / token / SSH key）。在 VPS `git commit`+`git push` 会失败：`could not read Username for 'https://github.com'`。
- 若已在 VPS 误提交本地 commit：`git reset --hard origin/main` 丢弃它，保持镜像与远程齐平——**一个未推的本地 commit 会让 VPS 分叉，破坏下次 pull**。
- 需要落到 GitHub 的编辑，**改走 Mac 的 IDE Agent**（给反重力/Codex 一段话术让它改+commit+push），Hermes 再 pull 复核。

## 7. 小坑：git 引号中文文件名

git 对非 ASCII（中文）文件名会做八进制转义并**用双引号包起来**，行尾变成 `...清单.md"`。所以红线核验 `grep -vE '\.md$'` 会**误报**中文 .md 为「非 .md」。改用 `grep -vE '\.md"?$'` 或先剥引号再判。
