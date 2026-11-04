---
name: agent-skills-library
language: zh
description: 维护用户agent技能库(pmlophy-skills聚合+软链5agent)。加/迁移/软链skill时用。
---

# Agent 技能库维护（pmlophy-skills + 软链）

用户维护一套**跨 agent 的技能库**：GitHub 聚合仓库 `lophyJessica/pmlophy-skills` 是技能的权威源，`~/.agents/skills` 是 Mac 上的单一真源（一个软链指向每份技能真正所在处），再软链进各 agent 的 skills 目录供其读取。用户要"把这 skill 放进 pmlophy-skills / 我的 GitHub / 软链 / 同步给娜美(agent)"时使用。

## 结构
- **聚合仓库**：`pmlophy-skills`，技能在 `skills/<skill-name>/` 下（含 `SKILL.md` + 可选 `references/` `scripts/` `templates/` `agents/openai.yaml`），根 `README.md` 列每个 skill 的说明。
- **单一真源（Mac）**：`~/.agents/skills/` —— 每个技能一个软链，指向技能真正所在（如 `~/个人文件/pmlophy-skills/skills/<name>` 或某个项目仓库的 `skills/`）。
- **5 个 agent 镜像（Mac）**：`~/.cursor/skills` · `~/.codex/skills` · `~/.claude/skills` · `~/.gemini/config/skills`（反重力）· `~/.workbuddy/skills`；可选 TRAE `~/.trae-cn/skills`、ZCode `~/.zcode/skills`（不支持的 agent 用复制）。改一处源，所有 agent 同步（软链）。

## 加一个新 skill（流程）
1. 来源：自建，或采纳上游仓库（如维他命 `TopVitamin/agent-skills`）。
2. **上游采纳模式（两版本）**：把上游 skill 完整拷进 `skills/<name>/` 保留为**原版**（上游忠实，供日后 diff）；若本用户环境需要适配（采集车头/路径/场景），另立 `<name>-office` 等适配版（如 `old-system-ui-clone` 原版 + `old-system-ui-clone-office` 办公版，办公版采集走 Cursor 内置浏览器）。日常用适配版，原版留作上游参照。**保留全部 references/scripts/templates**，别只拷 SKILL.md。
3. 更新 `README.md`：为每个版本加一段说明（用途/采集入口/版本差异）。
4. `git add -A && commit && push` 到 pmlophy-skills main。
5. 用户在 Mac `~/个人文件/pmlophy-skills` 跑 `git pull`，然后软链进 `~/.agents/skills/<name>` + 各 agent 镜像（命令见下）。

## 软链命令模板（Mac zsh，无 `#` 注释）
```bash
cd ~/个人文件/pmlophy-skills
git pull origin main

mkdir -p ~/.agents/skills
ln -sfn ~/个人文件/pmlophy-skills/skills/<name> ~/.agents/skills/<name>

mkdir -p ~/.cursor/skills
ln -sfn ~/.agents/skills/<name> ~/.cursor/skills/<name>

mkdir -p ~/.codex/skills
ln -sfn ~/.agents/skills/<name> ~/.codex/skills/<name>

mkdir -p ~/.claude/skills
ln -sfn ~/.agents/skills/<name> ~/.claude/skills/<name>

mkdir -p ~/.gemini/config/skills
ln -sfn ~/.agents/skills/<name> ~/.gemini/config/skills/<name>

mkdir -p ~/.workbuddy/skills
ln -sfn ~/.agents/skills/<name> ~/.workbuddy/skills/<name>
```
验证：一条 `ls -la` 把各镜像一起列出来，每行应显示 `-> ~/.agents/skills/<name>`。

### 判断「齐不齐」与批量补齐（不要数个数）

**镜像目录的数量和仓库数量本来就不会相等，不能拿 `ls | wc -l` 当判据**：镜像里可能有仓库没有的第三方 skill（ego-browser 这类由应用自己装的实体目录），所以数字大不代表齐，数字小也不说明缺哪一个。实际排查里连错两次：先把 19 个当齐了（实际缺 6 个），补齐后又变成 26 个（多于仓库）。

唯一判据是算差集，输出为空才叫齐：

```bash
comm -23 <(ls -1 ~/个人文件/pmlophy-skills/skills | sort) <(ls -1 ~/.codex/skills | sort)
```

缺什么不要逐个 `ln`，一条幂等循环补齐（已存在的不动，可重复跑）：

```bash
for s in ~/个人文件/pmlophy-skills/skills/*/; do n=$(basename "$s"); if [ ! -e ~/.codex/skills/"$n" ]; then ln -sfn "${s%/}" ~/.codex/skills/"$n"; echo "已补 $n"; fi; done
```

把 `~/.codex/skills` 换成 `~/.cursor/skills`、`~/.claude/skills`、`~/.gemini/config/skills`、`~/.workbuddy/skills` 各跑一次才算五个镜像都齐。**只给一个 agent 补过链，不代表其他 agent 读得到**——某 agent 报「找不到某 skill」时，先想那个镜像缺链，再怀疑 skill 不在库里。

⚠️ **指令里「先读某 skill」是软要求，读不到不会报错，也不会提醒你**。凡是不读就做错的硬约束（唯一数据真源、不许新增没定稿的元素、契约由后端定），必须同时写进指令正文——本会话里 Codex 缺了 vivo-project 那条链，但指令自身写死了两条硬约束，产出依然没跑偏。skill 是加分项，不是唯一约束载体。

**指令里给 agent 的 skill 路径必须写中枢，不写真源库。** Windows 上写 `C:\Users\<用户名>\.agents\skills\<skill>\SKILL.md`；写 `E:\projects\github\pmlophy-skills\skills\...` 等于绕开 Junction 机制——真源一挪位置或改名，所有指令里的路径一起失效，而且 agent 读到的是仓库副本而不是登记过的那份。同样禁写项目内的 skill 副本路径（`<项目>\.agents\skills`），那是造成同一 skill 出现两份的来源。

**同时加一句「读失败就停」**：指令里写明「上述路径任一读取失败即停下，说明哪条失败、实际看到什么，不许自行改用别的路径或跳过继续」。否则 agent 遇到断链会默默去别处找一份旧副本，交上来的是旧口径产物，而回报里一切正常。

## 同步给娜美（officeVPS 的 Hermes agent，非常规软链）
娜美是办公室 VPS 上的完整 Hermes，**不套 Mac 的软链机制**——她的 skill 安装目录是 `/opt/data/skills/`（不是 `~/.hermes/skills/`），skill_view 扫描的是前者。给她装 skill 的流程：
1. 先把 skill 提交进 pmlophy-skills main（同「加一个新skill」流程）。
2. 娜美侧执行：`git clone https://github.com/lophyJessica/pmlophy-skills.git || (cd pmlophy-skills && git pull)` → `cp -r pmlophy-skills/skills/<name> /opt/data/skills/<name>` → `chmod +x .../scripts/*.py` → 清仓库。仓库是公开的，git 拉取无需凭据。
3. **装完必须新开会话或重启 gateway 才刷新 skill 注册**——文件就位不等于 skill_view 能加载；文件结构/语法都对了但 skill_view 识别不到，先重启刷新再排查。
4. 验收三连：`skill_view(name)` 返回 readiness_status=available；scripts/ 三个 .py 齐全；`ast.parse` 语法通过。

> 娜美的安装目录是 `/opt/data/skills/` 这条是持久事实——每次给她发 skill 都按这个路径写，别照搬 ~/.hermes/skills/。

## Windows（公司机）与 Mac 的机制差异

### 同步判定流程（每次 pull 后按这个走，禁止凭感觉）

**第一问永远是平台**：Mac 和 Windows 是两套机制，命令不能互换。给用户命令前先确认他在哪台机器（个人机 Mac / 公司机 Windows），给错一路白跑。

1. **Mac** —— 不用跑任何脚本。`git pull` 完即生效，只需**新开一个 agent 会话**（老会话里还是旧内容）。
2. **Windows** —— 先看这次 pull 进来的提交里有没有 **skill 目录的增删改名**，看提交不看感觉：`git log --name-status -6`
   - 全是 `M skills/xxx/SKILL.md` / `M skills/xxx/scripts/...`（只改内容）→ **什么都不用跑**，Junction 是目录链接，内容改动直接生效。
   - 出现 `A skills/<新名>/SKILL.md`（新增）→ 缺一两个就单条 `mklink /J` 补；缺一大片才跑 `sync-skills-windows.bat`。
   - 出现 `D skills/<旧名>/...`（删除或改名）→ 先 `rmdir` 掉对应旧 Junction，再补新的。
3. **跑 bat 前必须先知会用户它有副作用**：它是「拆链重建 + 生成 `.backup-<随机数>` 残留」，不是幂等操作；跑完要给出清理命令。

铁律一句话：**skill 指错 = 全盘白做**。链指错、或读到旧副本时，agent 照常回报「完成」，产物却是旧口径，事后极难发现。所以每次给 agent 指令前，先确认这个 skill 在**对应平台的中枢**里真实存在，再写路径。

**Mac：软链，pull 完即生效，什么都不用跑。**软链指向仓库目录本身，改了内容链接不变。pull 后只需**新开一个 agent 会话**（Cursor 老会话里读到的还是旧内容）。

**Windows：逐 skill Junction，pull 后不必无脑跑脚本——先判 skill 目录有没有增删改名。** Junction 是目录链接，仓库里 `SKILL.md` / `scripts/` / `references/` 的**内容**改动会直接生效，`git pull` 完就完事；只有「新增 / 删除 / 改名 skill 目录」时才需要重跑 `sync-skills-windows.bat` 补齐中枢与各镜像。判据不看感觉，看仓库提交：`git log --name-status -6` 全是 `M skills/xxx/SKILL.md` 就说明只改了内容，不用跑；出现 `A skills/<新名>/SKILL.md` 或 `D ...` 才跑（再往回翻，取最近一次新增目录的日期作为「上次该跑 bat」的时间线）。

**跑脚本前先知道它不幂等**：`sync-skills-windows.bat` 对每个 skill 是「先把现有 Junction `move` 成 `*.backup-<随机数>`，再 `mklink /J` 重建」，跑一次就在中枢和 Cursor / Codex / Antigravity 三个镜像里各留一堆备份目录，要人工清。另两个容易踩的点：`SRC` 有 fallback（`.agents\skills` 不存在则用 `skills\`，仓库根现在就是 `skills\`）；Antigravity 镜像目标是 `%USERPROFILE%\.antigravity\skills`，与反重力实际目录 `~/.gemini/config/skills` 不一致时整条 `[SKIP]`，只改脚本才算真镜像。

**自查是否缺链不用跑脚本**：`dir "%USERPROFILE%\.agents\skills" /b` 看有没有某个新 skill 名；有就什么都不用做。**缺的只是一两个 skill 时不要重跑 bat**——单条 `mklink /J "%USERPROFILE%\.agents\skills\<name>" "<仓库>\skills\<name>"` 补上就行，跑整个 bat 等于把 20 多条活链拆了重建、再产出一批新备份。只有缺一大片或确认全是死链才跑脚本。

清备份也别手动一个个删：`for /d %D in ("%USERPROFILE%\.agents\skills\*.backup-*") do @rmdir "%D"`（`rmdir` 对 Junction 只删链接不动目标，真源安全）。删前先把要删的范围复述给用户确认，并确认目录里有 `ego-browser` 这类第三方实体 skill 不在删除范围内。

下面三种异常才是必须重跑脚本的场景：
1. 部分目录还是拷贝副本（早期没建链，脚本会备份后改建 Junction）；
2. Junction 指向绝对路径，仓库改名/挪位置就断链，断了就退回读旧副本；
3. 仓库新增/删除 skill 时，中枢 `~\.agents\skills` 和各 agent 目录不会跟随，需重跑脚本补齐。

自查形态（PowerShell/cmd）：`dir "C:\Users\72231384\.agents\skills"`——`<JUNCTION>` 是链，`<DIR>` 是拷贝副本。

**别拿字节数判副本。** Junction 指向的是 Windows 检出，CRLF 会把每行多 1 字节，同一个文件会比 VPS 上多出「行数个字节」（实测 718 行的 SKILL.md 正好多 718 字节），看上去像两份不同版本，实际完全一致。判形态只认 `dir /al` 的 `<JUNCTION>` 标记；要验内容一致就比行数或 md5，**不要比字节数**。Windows 真源实际是 `E:\projects\pmlophy-skills\skills`（仓库根就叫 `skills`，既没有 `.agents` 层也没有 `github` 层），别照记忆里的旧路径写。

**排查提醒**：如果发现“改了 skill 但 agent 行为不变”，先判形态再看内容——读的是拷贝副本时，改仓库等于白改，两边已不是一个版本。

### 重新 clone 后的批量重建（Windows）

仓库换位置或重新 clone 后，旧 Junction 会全部指向已不存在的路径，表现为**所有 agent 都读不到 skill**（`Test-Path ...\<skill>\SKILL.md` 返回 False）。先勘察再重建，不要直接跑旧脚本：

1. **先确认仓库里 skill 到底在哪个子目录**。别假设 `.agents/skills`——同一个仓库在不同时期可能是 `skills/` 或 `.agents/skills/`，猜错的结果是“从空目录建了一堆空链接”。命令：`Get-ChildItem <仓库根> -Force | Select Mode,Name`。
2. **看现有链接指向哪里**再决定重建：`Get-ChildItem <目录> -Directory | Where LinkType | Select -First 3 Name,Target`。指向已删路径 = 全断，直接清空重建。
3. **清空时要区分链接与实体**，不能一律 `-Recurse`：链接只删链接本身（`Remove-Item $p -Force`），实体才递归删（`-Recurse`）；对 Junction 用 `-Recurse` 有跟删目标内容的风险。
4. **必须加 `-Confirm:$false`**：`Remove-Item -Recurse` 不加这个会**逐个目录弹确认**，五十个 skill 就要按五十次 Y，人在旁边等到崩。
5. 重建：逐个 `New-Item -ItemType Junction -Path <镜像>\<name> -Target <真源>\<name>`，建完逐个镜像报「共 N 链接 M」，M 必须等于 N。
6. **改完先验能不能真读到，不只数个数**：`Test-Path <镜像>\<任一skill>\SKILL.md` 必须 True。

### 重建会顺手删掉第三方 agent 自装的 skill

`ego-browser` 这类 skill **不在 pmlophy-skills 仓库里**，是第三方应用（ego lite）安装时自动写进 `.agents\skills` 的。它的形态实测是 **Junction**（`dir /al` 显示 `<JUNCTION> ego-browser [\??\C:\Users\<用户>\.local\share\ego\ego-skills]`），不是实体副本——所以既不能被当作仓库副本删掉，重建时也要把它作为独立一条补回（target 指 ego 自己的目录，不是仓库）。清空重建 Junction 会把它一起清掉，现象是“agent 突然不会用浏览器了”“反重力没有 ego 技能了”。

- 重建**前**先记下各目录里不在仓库清单内的**实体目录**（那些就是第三方装的），重建后补回。
- 重建**后**验证几个已知会被用的第三方 skill 是否还在：`foreach ($n in 'ego-browser') { Test-Path "$env:USERPROFILE\.agents\skills\$n" }`。
- 补回的两种路：从还能读到的镜像目录 `Copy-Item -Recurse` 过去；或重跑第三方应用的 skill 安装入口。这类 skill 做成**实体目录**比 Junction 合适（它们的源本来就不在仓库里）。

**同一个 skill 在 agent 里出现两份（输入 `/xxx` 弹出两个一模一样）**：不是 agent 的 bug，是同一份 skill 被两处目录同时扫到。最常见是**项目目录里残留副本**（历史上把 skill 复制/软链进过项目，如 `E:\projects\cms-project\.agents\skills\`），与用户级 Junction 各算一份。自查：`dir /b "<项目>\.agents\skills"` 与 `dir /b "C:\Users\<user>\.cursor\skills"` 各列一遍，名字重复即坐实。修法=**只删项目内那份 skill 副本、保留 `.agents` 目录本身**，让 agent 只读用户级一份；删前把清单复述给用户确认。先查项目级、再怀疑用户级重复注册。

## 关键纪律
- **SKILL.md 的 `description` 写中文**：这个字段决定 skill 什么时候被触发，也是引用给人看的第一句。英文 description 在中文对话里常常不命中（用户用中文喊活，skill 不上），引用时也看不出用途。写法：首句是自包含的「当要……时用」+ 一句行为；**技术专名保留英文不译**（data-anno、routeMatcher、SKILL.md、React / Next.js 这类）。只改 description，正文照原语言不动——除非用户明确要求整篇中文化。
  批量盘：`grep -rn "^description:" skills/`，一眼看出哪些还是英文；改完再 grep 一遍确认清零。
  命中 `description: 问题描述（评审输入）` 这类正文里的同名字段是数据模型示例，不是 frontmatter，不要改。
- **给 Mac zsh 的命令块禁止含 `#`**（interactive_comments 默认关，`#` 会变参数；`&&` + 行尾注释最易 `parse error`）。注释放代码块外；命令用 `ln -sfn`/`mkdir -p` 保证幂等可重跑。详见 a2a-instruction-format 的 Format Rules。
- **Hermes 自己的技能（`~/.hermes/skills`）与 pmlophy-skills 是两套**：要在两侧都能用，就都建；同步改避免漂移。**操作后果：写进给用户 agent 的指令前，先核对该 skill 名在库的 `skills/` 下真实存在**（`ls <库>/skills` 或 `git ls-files 'skills/*/SKILL.md'`）。只存在 Hermes 侧的 skill（b-end-ui-stack、pre-task-checklist、prototype-fidelity-discipline 这类）在用户的 Cursor/Qoder 中枢里根本没有对应目录，指令点名它等于让 agent 去读不存在的路径——要么报错，要么自己另找一份旧副本，而回报里一切正常。要在指令里引用，必须先把它提交进 pmlophy-skills、让用户 pull 补齐 Junction 之后再写。
- **改完 Hermes 侧 skill 必须当场同步到库并 push，否则用户那边是旧版。**做法：`cp /root/.hermes/skills/<分类>/<name>/SKILL.md <库>/skills/<name>/SKILL.md` → commit → push，然后告诉用户提交号让他 pull。**同步前先 `diff` 两边 SKILL.md，不要把“我改过了”当“两边一致”**——实测过 VPS 侧已累积好几段新增内容从没推上去，而库里的看上去也像最新，不 diff 根本发现不了。
- **同步的不是只有 SKILL.md：`scripts/` 和 `references/` 必须一起同步。** 只推 SKILL.md 会让库里留下带病的脚本，而 agent 读库/软链自处跑的就是那份。实测库里 `embed_images.py` 与项目内同名脚本长期不一致（少拼了 `images` 路径前缀），每张图都判“缺失”被静默跳过却照常打印成功——生成出 0 张 base64、几十 KB 的“成品”。同步按文件逐个落到对应子目录：`cp <src>/SKILL.md <库>/skills/<n>/SKILL.md`、`cp <src>/scripts/<x>.py <库>/skills/<n>/scripts/`、`cp <src>/references/<x>.md <库>/skills/<n>/references/`。
- **别图省事把多个文件一次 `cp` 到 skill 根目录**：`cp a b c <库>/skills/<n>/` 会把脚本直接落在 skill 根，产生幽灵副本（既不在 `scripts/` 也不被引用）。commit 前跑 `git status -s`，逐个新增文件都得能归到 `SKILL.md` / `scripts/` / `references/` / `templates/` 四类之一，说不出的删掉。
- **VPS 侧库路径：`/root/repos/pmlophy-skills`（Mac 是 `~/个人文件/pmlophy-skills`）。** push 前先 `git pull --rebase`；改完要告知用户提交号，他在 Windows 上用 `sync-skills-windows.bat` 重建 Junction / 在 Mac 上直接 pull 生效。
- **给用户的验证命令，关键词要从文件实际内容里 grep 出来，不能凭记忆写。**凭印象拼的关键词（少一个字、多一个助词）会命中 0，而 0 命中看起来像“没同步”，于是白排查一轮。正确做法：先在词内文本上跑一遍取到真实字串，再把它写进给用户的命令；或者直接让用户验证一个必存在的短词（如列名、节标题），不验证自己新写的那句话。
- **skill 要接进指令入口才不是摆设**：五段式指令生成前先扫 skill 库匹配（见 a2a-instruction-format「Skill 路由：先扫后用」），命中就让 agent 先加载 skill。
- 新增 skill 后软链给 agent，用户才读得到；只 push pmlophy-skills 而 agent 没软链 = 白做。
- **时机要前置到「派活前」，不是「改完 skill 后」**（2026-11-04 用户定为铁律）：每次要派本地 agent（Cursor / Codex / 反重力 / Qoder）干活，发指令之前先过这三问——①这活要用的 skill 在库里有吗，没有就先补进库并 push；②各 agent 目录链过去了吗，跑一遍遍历看 `<base>/<skill>/SKILL.md` 在不在，不许凭印象；③两边是否已分叉，分叉就做定点 patch 而不是直接覆盖。缺一条，指令发出去 agent 也读不到该读的规矩。
- **判「链通没通」不能用 `Test-Path $link`，要用能不能读到里面的文件**（2026-11-04 实测踩坑）：Windows 的 junction 断链（目标路径已不存在）时，`Test-Path` 仍返回 True，于是「存在但读不到」的坏链被当成已建好、全量跳过、不修。正确判据是 `Test-Path (Join-Path $link "SKILL.md")`；判定为断链后先 `cmd /c rmdir "$link"` 只删链接（不要用 `Remove-Item -Recurse`，它会顺着链删掉目标内容），再 `New-Item -ItemType Junction` 重建。实测 antigravity 目录里 19 条老链全指向已不存在的路径，就是靠这个判据才揪出来的。
- **`skills/ai-coding` 是分类目录，根目录没有 SKILL.md**（下挂 grill-me / react-best-practices / simplify / taste-review / test-desktop-app 五个）。写遍历自检脚本时要按「目标目录下有没有 SKILL.md」过滤掉它，否则每次都会误报「缺 ai-coding」。期望值算法：真源目录数减去这类分类目录数（当前 24 减 1 等于 23）。
- **`sync-skills-windows.bat` 不是幂等操作**：它每次都把已存在的条目 move 成 `.backup-<随机数>` 再重建，反复跑会攒出一大堆残留（实测 cursor 20 个、codex 21 个、antigravity 42 个）。只在 skill 目录有增删改名时才值得跑整份；日常补一两个新 skill，用 mklink 逐条补、跑不通再修，比整份重建干净。
- **实测缺失的 agent 目录要如实报**：Mac 上 `~/.gemini/config/skills`、`~/.zcode/skills` 当前不存在，反重力与 ZCode 读不到任何 skill；建链脚本会按 `[ -d ]` 跳过它们，输出里少了哪几行要自己看出来并告诉用户，别把「6 个目录 OK」当成全都覆盖到了。
- **push 前先 `git pull --rebase`**：pmlophy-skills 常被多处更新（Mac 端、本机），直接 push 会被远程领先拒绝（rejected）。有未提交改动时先 commit/stash 再 rebase，rebase 类纯新增 skill 无冲突。

## 语言与结构整理（全库中文化/去重的实做顺序）

要把整个技能库的表述统一成中文时，**先盘量再动手**，别凭感觉列清单：

```bash
cd <库>/skills
for f in $(find . -name SKILL.md | sort); do n=$(dirname $f); han=$(grep -oP '[\x{4e00}-\x{9fff}]' $f | wc -l); en=$(awk '/^```/{c=!c;next} !c' $f | grep -oE '[A-Za-z]{4,}' | wc -l); printf "%-40s 汉字%-6s 英文词%-6s\n" $n $han $en; done
```

按结果分三类，处理方式不同：①**纯英文**（汉字 <300、英文词 >200）→ 整篇翻译；②**中文为主但夹英文段落** → 只清理夹生段，不算翻译；③**已中文** → 不动。注意嵌套 skill 目录（如 `ai-coding/*` 下五个子 skill）也要盘进去，只扫顶层会漏。

顺序固定：**description → 纯英文正文 → 夹生英文段落**。description 最先，因为它决定触发（见下“关键纪律”），正文翻不翻都不影响调用。

铁律：
- **整篇翻译只做语言转换**：不改章节顺序、不合并小节、不删示例；frontmatter 全部字段（name/license/metadata/trigger）原样，第三方 skill 的来源归属（如 Vercel/MIT）尤其不能动。
- **翻译后行数基本不变是正常的**（逐句对位）；行数大幅增减就是删了或自行加了内容。验收用词频降幅 + 围栏代码块 md5（方法见 a2a-instruction-format「翻译/改写类交付的验收三件套」）。
- **中文为主但夹英文段落的文件**也值得清一遍：读者看到半句英文只能跳过去，等于那段话白写。

## 结构与去重：权威规则只在 SKILL.md 一份

同一套规则在 `SKILL.md` 和 `references/` 里各写一份，改一处漏另一处，两边就开始打架（实测：编号口径改了主文档，references 还是旧写法，执行方按旧的做等于修复被推翻）。做法：

- **权威规则上收到 SKILL.md**（标题 + 各细节都写完整）；`references/` 只留**展开型内容**：操作示例、md 模板、字段表格、各栈集成代码、决策树细节。
- references 里重复的规则正文**删掉、原位置留一行指针**（“规则见 SKILL.md §X.Y，本节只保留示例”）。
- **不能删成空壳**：全删成指针等于每次执行都要翻回主文档，示例/模板/代码块必须仍在。判断标准：改完打开这个 reference，是否还有只有它才有的东西。
- 重构/去重后**按已知坑关键词表逐条 grep 验收**（不是看结构和行数），最常丢的不是结构而是一条沉睡的经验（见 a2a-instruction-format「重构后的验收」）。

## 当前技能盘点（2026-10）

共 24 个 SKILL.md（顶层 19 + `ai-coding/` 下 5 个嵌套），**全部 description 已中文化，英文为主的正文与 references 已整篇翻译**。顶层含：a2a-instruction-format / de-ai-tone / old-system-ui-clone(原版) / old-system-ui-clone-office(办公版) / pm-* 五个 / prd-backfill / prd-doc-authoring / prd-requirement-review / prd-review-backfill / product-manager-workflows / prototype-annotation(及 -review / -workflow) / structured-ai-prompt-template / vivo-project；`ai-coding/` 下 grill-me / react-best-practices / simplify / taste-review / test-desktop-app。

pmlophy-skills 含：pm-research / pm-handoff / pm-to-spec / pm-prototype-decision / pm-discovery-dialogue（PM 流程）· ai-coding/{grill-me,taste-review,react-best-practices,simplify,test-desktop-app} · prototype-annotation(v2.1) · prd-backfill · prd-requirement-review · de-ai-tone · old-system-ui-clone(原版) + old-system-ui-clone-office(办公版) · **prd-doc-authoring**(评审PRD编写,截图+正文提取+base64发布) · **prd-review-backfill**(评审PRD变更回写权威源,diff找差异+以评审PRD为准+校验)。后者两件配套使用(一个写、一个回写),均已在娜美(/opt/data/skills/)+本地5 agent(软链)分发。