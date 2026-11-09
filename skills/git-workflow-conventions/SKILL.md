---
name: git-workflow-conventions
description: 用户多仓库统一 git 工作流铁律：main 开发、master 收口。所有项目（forge-erp/wms/crm、copy-wms、lophy-jarvis-voice、/opt 本地基线）一律在 main 分支开发提交，push 走 main，master 永远是最后合并的收口分支，严禁直接 push master。给 Agent 的 git 指令必须写"main 先提交 push → 合并 master"。违反会造成分叉灾难，修复是灾难级。
trigger:
  - 任何 git 操作（提交/推送/合并/回退）
  - 给 Cursor/Codex 写含 git 步骤的指令
  - 用户提到分支、push、合并、回滚
---

# Git 工作流铁律（用户定稿，2026-08-07）

## 核心规则（所有项目通用）

0. **先 pull 再 push（铁律 0812 用户强调——比 main/master 更基础）**——任何仓库、任何操作（改文件/commit/push/部署前）一律**先 `git pull origin main` 拿对方最新改动**，基于最新版修改，再 commit + push。用户原话："不要写完就 Push，养成先 Pull 的习惯，刻在脑子里"、"之前让你做项目也是要求这个原则的，以后所以涉及到 git 都是先 pull"。用户本人 Mac 端也是这个习惯（Obsidian Git 每次 sync 先拉）——两边都先 pull 就基本不会冲突。**禁止写完就 push**（曾连踩 3 次 dashboard.md 冲突：我远程改 + 用户本地改 + 没先 pull）。本规则同时写入 notes-vault-ops（笔记库专用版）。即使用户只说了"提交一下"，still 先 pull 再看 diff——pull 已成肌肉记忆，不必等用户提醒（0824 用户主动说"不过你先 pull"验证了这点）。

0.6 **提交身份分离（0927 立，1022 修正）——VPS 上我的提交统一用 `jessica <jessica@users.noreply.github.com>`，用户 Mac 用 lophyJessica。**

- **全局与仓库级都要改成 jessica（1022 用户要求："git 不要拿我的 token，用你自己的"）**：`git config --global user.name jessica && git config --global user.email jessica@users.noreply.github.com`，再对需要提交的仓库 `git config --local user.name jessica && git config --local user.email jessica@users.noreply.github.com`。
**旧写法「全局保持 lophyJessica（用户的）、勿动」是错的，已废**——全局是用户身份时，VPS 上新 clone 的仓库会继承它，我的提交就全记在用户名下（实测就发生了，用户看到一团自己的名字来问）。
- **新机器 / 新 clone 后先核身份再干活**：`git config user.name` 与 `git config --global user.name` 各跑一次，是 lophyJessica 就改成 jessica；仓库多时批量核：`for d in /root/repos/*/; do cd "$d" && echo "$d $(git config user.name)"; done`（实测出现过一半 jessica、一半 lophyJessica 的混用）。
- **推送凭据是 SSH key，不是 token**：远端形如 `git@github.com:<owner>/<repo>.git`，走 `/root/.ssh/id_ed25519_forge`。**不要去找 `.git-credentials` 或用户的 token**——`ls -l ~/.git-credentials` 不存在、`git config --global credential.helper` 为空都是正常的，不要因此以为需要凭据。

0.5 **commit 前验证 diff 与真实代码对齐（0824）**——提交涉及路径/URL/接口的改动（如部署脚本探测地址）时，先 grep 后端真实定义确认对得上再 commit：FastAPI 路由 = `APIRouter(prefix="/api/auth")` + `@router.post("/login")` → 完整路径 `/api/auth/login`；探测语义：空 body POST 返回 422（参数校验）=可达、404=未通、405（GET 打到 POST 路由）=路由存在但方法不对。Containe commit message 只写"对齐后端实际路由"不够——先验证再提交，让 commit 里躺着的必然是正确路径。
1. **统一在 main 分支开发**——所有人生效（杰西卡/Cursor/Codex/反重力），严禁在 master 上直接开发/提交/push
2. **提交/推送都走 main**——commit 后**立即 push main**（不要 commit 了不 push，会造成本地与远程分叉）
3. **master 永远是最后合并的收口分支**——只有阶段性完成后才允许合并 main → master
4. **严禁直接 push master**——任何"push 到 master"的指令都是错的
5. **push 权限归用户**——用户说"我来 push"是在防 AI 搞错分支；默认本地 commit 即可，用户明确让 push 才 push
6. **指令/中间产物先讨论再 push（0826 用户纠正）**——写指令文件、改文件、生成文档后**不要立刻 commit+push**（哪怕本地 VPS 仓库也要等）。先给用户看内容讨论，等用户说"可以 push/可以了"再推。用户原话："你不要push 那么快，等我们全部讨论完，你问我是否可以后，再 push"。需求常在中途澄清（本会话审核下线指令两轮反转：先"全部取消"→ 澄清"人工新建免审、导入/AI 保留审核"），边写边推会造成无效提交和误导 Codex 的过期指令。**指令文件写好后明确说"未 push，等你确认"，用户确认才走 git add/commit/push**。

7. **push 之后自己核实落地，再告知用户；用户说拉不到时先自证、别先甩锅**——说"已 push"之前自证远端确有该 commit：`git ls-remote origin main`（远端 hash 是否等于本地 HEAD）+ `git show --stat <sha>`（该提交改了哪些文件）。用户说"我拉不到"时的顺序：**先自证远端 → 再帮用户查其本地**（未 fetch / 分叉 / 不同的 clone）。**禁止先断言"文件在，是你仓库的问题"**——用户不接受，而且十有八九是我自己的核验方法错了（见下表中文文件名一行）。

## 提交备注写法（用户定，1021 强化）

- **备注要短：一行主题 + 最多两三行要点，不是交付报告。** 用户看到多段落 / 分节 / 带项目符号的长备注会直接反问「提交备注这么长？？」——commit message 是给以后 review git log 用的，不是给本次交付做说明。要解释的写进聊天或文档，不塞进 commit。
- **一个提交只放一种性质的东西**：取证产物（截图/DOM/证据档）、代码改动、文档修订分开提。混在一个提交里必然导致备注与内容不符——实测出现过备注写「只读取证，未改代码」而提交里带着一批前端代码改动，git 历史直接失真，事后没人说得清哪次改了什么。
- **备注是我凭已知产出拟的，不代表它覆盖了实际改动——用户 push 完必须核 diff。** 用户在他自己机器上连跑了几条 agent 指令后来要备注，我能看到的只有交接与报告里的产出，实际改动常多出一倍。流程固定：先给一版短备注并声明「push 完我核 diff，漏了补一条」→ 用户 push → `git pull --rebase` → `git show --stat --name-status <sha>` 逐项过 → 分三类回报：
  - 备注没覆盖但无害的（新增模块、样式、mock、文档套件）→ 给一条补充备注让他补提，不阻塞；
  - **删文件 / 口径反转 / 数字对不上** → 单独拎出来问「是不是有意」，别混进补充备注带过（删了一整份报告、把已定口径改反，都是用户必须知情的事）；
  - 报告自述的数字（如「TSV 扩到 N 行」）一律用 `wc -l` 实测，对不上就报实测值，不引用报告的说法。
- **并行任务各自提交**：多条指令并行时按目录分别 `git add <目录>` 提交；别在 Source Control 面板一键全提（会把对方半成品一起带上）。
- **同一工作区还有别的 agent 在跑时，提交方式要换档（用户会直接说"这个不行，需要 add 下"）**：平时的默认习惯是用户自己在 Cursor/Antigravity 面板提交、我们只给备注文本——**但工作区里有第二个执行方（反重力/Cursor/Codex）同时改文件时，这个默认失效**。此时交付物必须是**可直接粘贴的完整命令块**：`git status --porcelain` 先看范围 → `git add -- "<路径1>" "<路径2>"`（精确路径，按目录/文件收窄）→ `git status --short` 复核暂存清单只有本次该提交的文件 → 再 `git commit -m "<备注>"` → `git push origin main`。**绝不能只给一句 commit，或让它走面板一键全提**——那会把对方半成品一起带上。路径拿不准时先让用户把 `git status --porcelain` 的输出贴回来再定 add 范围，不要猜路径硬给命令。
- **工作区干净 ≠ 改动已入库**：`dist/`、`build/` 这类构建产物常被 .gitignore 忽略，改动只落在产物目录时 `git status` 永远是干净的。核"这批改有没有进 git"要去看**被跟踪的源路径**（如原型标注的源是 `public/annotation-kit/`，`dist/annotation-kit/` 只是 build 结果），而不是看工作区是否干净，更不要在干净的树上断言"已经提交过了"。
- **两批活已经混在同一工作区，事后按路径拆 commit**：`git add` 不是“保存改动”，是“把某个路径挑进暂存区”——只要两批动的文件不在同一路径，就能拆：`git add "skills/*/SKILL.md"` 提第一批 → commit → `git add <第二批目录>` → commit。用户问“这怎么做到的/分不出来了”时，答的是这条机制，不是让他手动挑块。**只有同一文件里既有 A 任务的改动又有 B 任务的改动时**才分不开，那时才用 `git add -p` 按块挑。**分批命令里的排除清单必须覆盖第二批改过的每一个目录，而不是你以为的那几个**——实测给用户的分批命令只排除了 `masterData`、`mock`、守卫脚本、`package.json`，漏了 `pages/`，于是第二批的页面改动全被卷进「只改样式」那一笔，两笔提交语义都不纯，事后想单独回滚任何一批都拆不开。判据换掉「暂存区里不该出现 X」这种列举式检查，改成：**`git status --short` 的每一行都要能说出「这属于哪一批」**，说不出来的就是清单漏了。拿不准两批到底各含哪些文件时，不要硬拆成两笔——先让用户把 `git status --short` 全量输出贴回来，或干脆一笔提交并在备注里说明含哪两块。拆完再看 `git show --stat` 两笔各改了哪些文件，确认没有串。
- **按「轮次」拆不开时退化为按「文件」拆**：用户说「我做了两轮改动，想分两笔提交」时不一定要按轮次——两轮常落在**同一批文件**里（第二轮是把第一轮的实现改回来），此时按轮次拆根本不可能。可行解法是按文件拆（一个文件一笔、各自一句短备注），并在回复里说清「按轮次拆不了，按文件拆」而不是硬凑两笔同名改动的提交。**别把「两轮」写进备注**（「第二轮修正…」对以后 review 它的人毫无意义），只写这笔记改了什么。

## 给用户 push 命令块：顺序是「commit → pull --rebase → push」

用户说「我要 push」时要给**可直接粘贴的完整命令块**，且顺序不能颠倒（凭直觉很容易排成「先 pull 再提交」，所以**写之前照本节顺序核一遍，不凭记忆**）：

1. `git status --short` 先看范围；
2. 分笔 `git add <精确路径>` + `git commit -m "<短备注>"`（一笔一种性质）；
3. **最后才** `git pull --rebase`；
4. `git push origin main`。

**为什么不能先 pull**：工作区有未提交改动时 `git pull --rebase` 直接报 `error: cannot pull with rebase: You have unstaged changes` 并中止，整段命令链断在第一步。用户不会自己把顺序倒过来，他看到报错就贴回来问，白花一轮。

用户已经撞上这个报错时，给两条路而不是只给一条：改动要留（绝大多数）→ `git add -A && git commit -m "<短备注>"` 再 `git pull --rebase`；改动只是临时试验不想入库 → `git stash -u`（`-u` 把未跟踪的新文件也存进去，不加则新文件仍挡着）→ `git pull --rebase` → `git stash pop`。另提一句：本地没有任何改动时 `git pull` 就是快进，效果与 `--rebase` 相同——`--rebase` 只在「本地有未推送提交」时才有实际意义，别把它说成无条件必须。

**公司机 Windows 上执行**：路径用 `E:\<repo>`，命令照 PowerShell 写（`git` 子命令与 Mac 一致，不需要 bash 特有语法）；**在 CMD 里提交中文备注前先跑 `chcp 65001`**，否则 `git commit -m "<中文>"` 按本地代码页写入，`git log` 里是乱码（IDE 面板提交不受影响，只有命令行需要这一步）；`git status --short` 里中文文件名显示为 `\344\272\247...` 这类八进制转义是 git 默认行为，不是乱码也不是仓库坏了，不要试图解码，也不要据此判断文件缺失——要看真实文件名用 `git -c core.quotepath=false status --short`。

## 分支一致性

- 目标状态：`origin/main` 与 `origin/master` 指向同一 commit（main 领先，master 快进跟随）
- 合并永远应该是 **fast-forward**（快进）——如果出现 merge commit/冲突，说明流程已经被破坏
- 检查一致性：`git rev-parse origin/main origin/master`（两 hash 相同 = 一致）

## 合并特性/测试分支进主线（两级 fast-forward，2026-09 实测）
阶段性完成要收口时，按铁律走两级，**不一步跳 master**：`特性分支（如 0913test）→ main（开发收口）→ 验收后 main → master（发布收口）`。

合并前先验证分支亲缘——**别被"不同 tip"吓出"分叉灾难"判断**：两个分支 tip 不同不一定分叉，可能一个是另一个的祖先（快进关系）：
- `git merge-base --is-ancestor origin/main origin/<feature>` 成立 → 特性分支从 main 拉出、main 未前进 → 特性→main 是干净 fast-forward。
- `git merge-base --is-ancestor origin/master origin/main` 成立 → main 已含 master → master 只是落后不是分叉 → main→master 是 fast-forward。
- 只有两个方向**都不是**祖先才真分叉，才需要 merge commit/冲突处理。

执行：`git checkout main && git merge --ff-only origin/<feature> && git push origin main` → `git checkout master && git merge --ff-only origin/main && git push origin master` → 三分支最终同一 hash。

**收口终点（合并后记得做，否则留脏分支）**：内容三线一致后，删特性分支 + 打 git 基线 tag：
```bash
git checkout main
git branch -D <feature>                                    # 删本地特性分支（已并入，安全）
git push origin --delete <feature>                         # 删远端特性分支
git tag -a v<里程碑>-<日期> -m "阶段性收口：<一句话>" && git push origin <tag>   # 里程碑打 tag 作 git 基线，改坏可秒回
```
`master` 从不单独写，靠 main 合并进来覆盖跟随（快进）；阶段点永远落在 main 的开发提交 + 里程碑 tag 上。

**框架迁移型收口的正常现象**：fast-forward merge 会显示删除旧扁平结构文件（旧目录被 git-mv 搬进新分层、在新分支里已是新文件名，如 `prd-docs→03-产品设计/...`、`templates→04`、`prototype-annotation→99`）——是迁移的正确结果不是丢文件，合并前告诉用户别慌。

## 给 Agent 的 git 指令模板（仅限跑在 VPS 侧、我能直接盯着的 agent）

**不适用于用户本机的 Cursor / 反重力**：那些提交一律由用户自己在编辑器界面点，我们只给 commit 备注文本。指令里出现 `git add / commit / push` 就是违规，哪怕项目 AGENTS.md 里没写这条限制——`git add -A` 会把工作区里别人未提交的改动卷进同一个提交，而 agent 只看得见自己改的那几个文件，它编的备注与提交内容必然对不上。

```plaintext
Request:
1. git checkout main && git pull origin main（确保 main 最新）
2. 在 main 分支提交（分 commit，备注详细，不一把梭）
3. git push origin main
4. 【铁律】master 最后合并:
   git checkout master
   git pull origin master
   git merge main
   git push origin master
   git checkout main（切回主分支）
红线: 不直接 push master；合并冲突停下报告
Checkpoint: git status 干净；origin/main 和 origin/master 指向同一最新；汇报 commit hash + 双分支推送结果
```

## 灾难案例（2026-08-07 血泪）

- 在 /opt 建 git 基线时用了默认分支名 **master**，而 Mac 仓库在 **main** → 两边分叉，永远汇合不了
- 本地 commit 了归档改动但**没 push**，Cursor 也 commit 了同样改动并 push → 同一改动两个 commit → pull 报 "Need to specify how to reconcile divergent branches" → 只能 `git reset --hard origin/main` 放弃本地
- Cursor 按错误指令**直接 push 了 master**（v156/v157）→ 违反铁律 → 要回退（master reset 回旧 commit + force push）
- 教训：**commit 后立即 push main**，所有指令写"main 先提交 → 合并 master"，就不会有分叉和回退

## 已知分支现状（2026-08-07 确认）

- forge-erp / forge-wms / forge-crm / copy-wms / lophy-jarvis-voice：VPS 仓库全部在 main
- /opt（VPS 代理脚本本地基线）：已从 master 改名到 main（`git branch -m master main`），无 remote，纯本地可回滚
- GitHub 默认分支 = main（master 是冗余收口分支，与 main 同步）

## 撤自己的改动不要整文件回退

`git checkout <旧提交> -- <文件>` 把该文件**整体**拉回那一刻的样子——包括别人后来在这个文件里做的修复。实测踩过：自己改的原型代码与本地 agent 的活撞车，为不冲突把几个文件回到旧提交，结果把同一批里刚修好的构建守卫修复一并抹掉，构建又挂，白跑一轮。

撤之前先看这个文件自那以后被谁动过：

```bash
git log --oneline <旧提交>..HEAD -- <文件>
```

- 只有自己的提交 → 可以整文件回退。
- 有别人的提交 → 不能整文件退，按内容挑（`git diff <旧提交> -- <文件>` 逐处看过再手改），或只撤自己那几处 hunk。
- 回退完必须重跑一次构建/测试，确认没把别人的修复带走。

## 原型标注工作流（配套参考）

给项目安装可交付文件（如 vitamin-prototype-annotation Skill）的 git 流转、课件标准目录结构、执行指令模板、检阅要点、**部署坑（zip 解压即根 / 管道命令逐字 / forge-crm project/ 路径）**见 `references/prototype-annotation-workflow.md`。三层分工：执行者 Codex/Cursor、检阅者杰西卡/罗宾、验收者用户。


## VPS 多仓库 SSH 与远端追赶

当同一台 VPS 上维护多个 GitHub 仓库、且使用同一把 SSH key 时，可统一设置 Git 全局 SSH 命令，避免逐仓库配置：

```bash
git config --global core.sshCommand 'ssh -o IdentitiesOnly=yes -i /root/.ssh/id_ed25519_forge'
```

先用只读方式验证远端权限：

```bash
git ls-remote git@github.com:<owner>/<repo>.git HEAD
```

如果 `git push` 报 `fetch first`，不要 force-push。先 fetch 查看分叉，再把远端提交 rebase 到本地提交之前：

```bash
git fetch origin main
git pull --rebase --autostash origin main
git push origin main
```

这套流程适合“本地只提交了目标规则文件、工作区还有不应提交的未跟踪文件”的情况。提交时只 `git add` 目标文件；rebase 后再次检查 `git status --short --branch`，确认本地与 `origin/main` 对齐。
| 坑 | 症状 | 修复 |
|---|---|---|
| 在 master 上开发/提交 | 与 main 分叉，合并冲突爆炸 | 改到 main：`git branch -m master main`（本地）；远程需 reset + force push（用户确认） |
| commit 不 push | 本地领先远程，别人也 commit → 分叉 | commit 后立即 `git push origin main` |
| 给 Agent 指令写"push master" | Agent 直接推 master，违反铁律 | 指令模板永远带"main 先提交 push → 合并 master" |
| 拉取失败 "reconcile divergent branches" | 本地与远程分叉 | `git reset --hard origin/main`（本地无价值提交时）或 merge 后 push |
| 拉取失败 "Need to specify how to reconcile divergent branches"（0813） | 本地有未推送提交 + 远程有新提交——两边各自领先（不是文件冲突） | 先 `git fetch` + `git log --oneline HEAD..origin/main` 看分叉量 → 多数情况 `git pull --no-rebase` 自动合并（用户本地无价值改动时也可 reset）——先了解再动 |
| 用户 pull 失败 "Your local changes to the following files would be overwritten by merge"（0919） | 该文件在**用户本地**有未提交改动（常见：用户也在编辑同一笔记，或 Obsidian 常改的 workspace.json），git 保护不覆盖 → 把用户的拉取拦住了；**是我 push 到用户正在编辑/持有未提交改动的文件造成的** | 保留本地改动: `git add -A && git stash` → `git pull` → `git stash pop`（git 自动合并）；舍弃本地: `git checkout -- <file>` 若还有 index 残留则 `git reset --hard` → `git pull`。**铁律加码：改仓库文件前先 `git pull`，且不要 push 到用户已知正在本地编辑的文件；一旦推了而用户本地脏，主动把解围命令给用户** |
| 误判"master 与 main 一致" | 缓存旧 remote 引用 | 先 `git fetch origin` 再比较 hash |
| 项目内 .cursor/ 目录 add 失败 "paths are ignored" | 想把 Skill/规则文件装进项目（如 vitamin-prototype-annotation）放到 .cursor/rules/ 下，git add 被 .gitignore 拦（.cursor 通常被忽略） | **项目内可交付文件放项目根目录**（如 `forge-crm/vitamin-prototype-annotation/`），不要放 .cursor/（push 不上去）；只有本地生效的编辑器规则才放 .cursor。装好后走 git 流程：VPS commit+push main → 用户 Mac pull |
| `git rm --cached` 不带路径参数 | **整个 index 里所有 staged 文件被清空**（158 个文件全变 `D`，含刚 git mv 的）——`git rm --cached` 无 pathspec 时作用域是全部 index，不是"当前目录" | 抢救：`--cached` 只动 index 不动工作区 → `git reset HEAD` 恢复 index，再 `git add -A` 重收（git 自动识别 rename）。**铁律：任何 index 易变命令（`git rm --cached`/`git reset`/`git checkout`）必须带精确路径参数**，批量移动用 `git mv` 逐条或结尾统一 `git add -A` |
| 批量 git mv 重构后怕丢文件 | status 显示大量 D/新增，说不清有没有意外丢失 | **用 git tree 对比验证无损**：`git ls-tree -r --name-only HEAD~1 | wc -l` vs `HEAD` 版本数（差 = 有意删除数）；`comm -23 <(git ls-tree -r --name-only HEAD~1|sort) <(git ls-tree -r --name-only HEAD|sort)` 列消失清单，逐条核对均为有意删除（废弃目录/重复文件）才算完。别用 basename-grep 脚本比对（中文路径八进制转义会让 grep 报 Invalid back reference 全量误报） |
| 核验 push 是否落地时误判"远端没有这个文件" | 拿**中文/非 ASCII 文件名**去 `git ls-tree origin/main` 里 grep，或拼成 raw URL 去 curl——git 对非 ASCII 名做 octal 转义并加引号，匹配必然失败，于是误判"没推上"，把核验责任推给用户（用户会认为你没推） | 核验要**列全量再断言**：`git -c core.quotepath=false ls-tree --name-only -r origin/main \| grep -F '<文件名>'`（quotepath=false 让 git 直接输出 UTF-8 名），或更稳——`git show --stat <sha>` 看该提交改了哪些文件（提交里列了就是推上去了）。**结论必须建立在自己核实过的远端事实上** |
| 用户本地解完冲突自己 push 后，我只拉下来看 | 合并提交可能把**用户那侧的改动合丢**：他基于旧版改的文件，遇上我同一文件的新版重写，冲突解决后主线留的是我的版本，他自以为保住的改动其实不在线 | 核三步：① `git status -sb` 干净再 `git pull --ff-only`；② `git show --stat <用户那条 sha>` 看清他动了哪些文件；③ **对关键文件做跨版 diff**（`git diff <我上一个提交> HEAD -- <文件>`）——只有读 diff 才能判断「他以为保住的改动」是否真进了主线。发现被合掉就直说并问以哪版为准，不擅自按自己那版重做；说「你的改动没推」前必须先证明（静态 grep 不到通常是我搜错，见前条）。 |
| 用 `git add -A` 提交时带进无关文件 | 仓库里常常长期躺着**历史遗留的未跟踪文件**（旧报告、废弃草稿、别处拷来的 md）。图省事用 `-A`，它们会被一并收进本次提交 → 内容超出本次范围，要再补一个删除 commit，用户当场会问"这个不是我这次要提交的吧" | **日常提交一律用精确路径 `git add <目标目录/文件>`**，不要用 `-A`。只有刚做完 `git mv` 批量重构、需要 git 重新识别 rename 时才临时用一次 `-A`，且提交前先 `git status --short` 过一遍——**每一个 `??` 新增行都要能说出它为什么属于本次改动**，说不出的就不 add。发现已被误提交：`git rm` 掉再单独一个 commit 说明误提交原因，别 amend 已经 push 的提交 |
| 用户说"把内容删了"→把整个目录连壳删了 | 删完才被告知要留目录，原话「我让你删的是内容，不是文件夹啊」，判为"这个毛病得改" | **删除/批量改动前先复述"删什么、留什么"等确认，范围严格按字面，禁擅自扩大或缩小**。技术细节：git 不跟踪空目录，`git rm -r <dir>` 后 pull 下来目录照样消失——要保留目录壳必须给每个目录（含子目录）放 `.gitkeep` 占位 |
| 报"只有 N 个文件"明显偏小 | `ls <dir>/*.md | wc -l` 只扫顶层，把 48 个文件报成 19 个，4 个子目录全漏；删完 `git show --stat` 才对上真实数量 | 任何文件数/体积统计一律递归：`find <dir> -type f | wc -l`；删除前也用递归列清单给用户确认 |
| 删目录后文档里留下指向空气的引用 | README 目录树、“先读 xx/”的步骤仍指着已删目录 | 删目录前 `grep -rn "<目录名>" --include="*.md" .` 扫全部引用；**保留目录壳则目录树条目照留，删掉内容则引用它的步骤一并删**——两者不同步就是文档说谎 |
| `git pull --rebase` 报 `there is already a rebase-merge directory` | 上一次 rebase 被中断（冲突没继续、被 kill、或命令中途报错）留下了 `.git/rebase-merge` 状态目录，此后 pull/push 全被拦住 | **用 `git rebase --quit` 清状态，不要用 `--abort`。** `--abort` 会把 HEAD 回退到 ORIG_HEAD，把已完成的提交在工作区撤掉（远端虽在，本地退回旧状态，又得再拉一次）；`--quit` 只清中间状态、不动提交与工作区。清完 `git status` 应干净、`git log` 头几条与远端一致 |
| 公司机打开过的 Office/二进制文件被透明加密后提交进 git | `git status` 显示 pptx/xlsx 有改动、`git diff --cached --stat` 里字节数变了，但推上去的文件打不开。`file` 输出 `data`，文件头是 `%TSD-Header-###%` 而不是 `PK`——公司机的 DLP 透明加密软件在 Office 打开文件时就地加密，跟用户是否编辑无关 | **提交二进制文件前验证文件头**：`file <路径>` 应显示 `Microsoft PowerPoint 2007+` 一类；或 `head -c 8 <路径> \| xxd` 应是 `504b 0304`。发现被加密就从上一个好提交恢复（`git show <好提交>:<路径> > <路径>`）后重新提交，并把约定写进项目须知：**二进制文件只在个人 Mac 上编辑，不在公司机打开**——打开一次就已经加密了 |
| 构建产物被跟踪进 git → 每次 build 都脏、不断挡住 pull/push | `git status` 反复出现 `dist/index.html`、`dist/icons.svg` 一类修改；接着 `git pull --rebase` 报 `You have unstaged changes`、push 被拒 non-fast-forward，每次干活先清一遍才能动 | 根因：`dist` 目录虽在 `.gitignore` 里，但其中个别文件曾被强制加进去——**已跟踪的路径不再受 gitignore 约束**，每次构建都会改出差异。修法：`git rm -r --cached "<项目>/dist"` → commit → push（`--cached` 只移出索引，本地文件照留，构建后可重生）。执行前先确认部署链路不依赖 GitHub 上的 dist——若走“本地打包 zip 上传内网 VPS”或“VPS 自己 build 再 rsync”，dist 完全不该入库。| 工作区没改内容却显示一堆 modified，`git pull --rebase` 报 `You have unstaged changes` 卡住拉取 | 全是 CRLF/LF 假改动：仓库存 LF、Windows 工作区是 CRLF；`git diff --stat` **一行统计都没有**，只有 `CRLF will be replaced by LF` 警告 | 先用 `git -c core.quotepath=false diff --stat` 确认无实质差异，再 `git restore <路径>` 丢弃（内容不丢）；**不用 `git checkout .`（范围过大）、更不 `reset --hard`（真实改动一起丢）**。根治：仓库根加 `.gitattributes` 写 `* text=auto eol=lf` |
| 用 `git pull` 而非 `--rebase`，main 上留一串 merge commit | `git log` 出现 `Merge branch 'main' of github.com:...`，历史分叉、溯源困难 | 拉取一律 `git pull --rebase`；已产生的 merge 提交不必回退（内容没错），但当场把习惯纠正 |
| 同一工作区多个 agent 并行干活，开工前不 pull、提交时 `git add -A` | 两个会话把对方未提交的改动一起带进自己的 commit，历史失真 | 并行前先确认**文件清单不重叠**（这是不撞车的判据）；每个会话开工先 `git pull --rebase`，提交只 `git add` 自己改的那几个文件，禁 `-A` / `commit -a` |
| 重出的产物类文件（截图、生成的发布版）一提交就“全部改动”，看不出到底改了什么 | 顶栏时钟、生成时间戳这类实时渲染内容让整批产物的字节都不同，`git status` 会把 22 个文件全列成 modified，据此判断“影响面变大了”是错的 | **产物类文件不能用 git 变更数判断语义影响面**：影响面要看源改动落在哪些模块/页面，产物则当作“同一批整体重生、整体提交”处理。要证明“脚本产物 = 已提交产物”，在干净环境重跑一次生成脚本输出到 /tmp，再用 `cmp -s /tmp/x <仓库里的那份>` 比字节——一致才算验收通过，只报“脚本跑成功”不算 |
