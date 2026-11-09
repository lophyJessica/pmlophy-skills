---
name: web-deployment-debugging
description: >
  Deploy static web apps to VPS and debug network/connectivity issues.
  Covering the diagnostic matrix approach, nginx config patterns,
  Chrome security policies, and common pitfalls when connecting
  frontend apps to Hermes API Server.
---

# Web Deployment & Debugging

## Core Rule: Diagnostic Matrix FirstBefore making any changes, draw the full request chain:

```
Chrome → System Proxy → Cloudflare → Nginx → Hermes API
```

Test each layer independently before jumping to conclusions.
Grep the access log (`tail -f /var/log/nginx/access.log`) to confirm
whether requests reach nginx before guessing at the cause.

### 前端 → API 400 无日志排障（pcap 抓真实请求体重放）
前端报 400 但构造复现不了、服务端无日志时：tcpdump 抓后端端口 → python 从 pcap 提取 TCP payload 重组 JSON body → curl 重放拿 400 响应体 → 定位坏消息。完整步骤见 `references/http-400-replay-pcap.md`（2026-08-26 罗宾 invalid_image_url 实踩）。

### Markdown 文档 → 门户 HTML 发布（含 Mermaid）

把 md 长文渲染成门户页（`/var/www/pmlophy.com/docs/`）、让 mermaid 图真的画出来、以及门户在线编辑小服务的做法与坑，见 `references/markdown-doc-site-publishing.md`。**要点**：markdown 的 fenced_code 会把代码块内容 HTML 转义（`-->`→`--&gt;`），换成 `<pre class="mermaid">` 前必须 `html.unescape()`，否则 mermaid 画不出来；改完用「块内无 `--&gt;`」断言 + 真发布页勾一眼来验收，不看编辑器预览。

## React SPA 白屏调试（页面空白 = 渲染期 throw）

部署后页面能加载但某路由**全空白**（#root 空、无报错提示）→ 不是 nginx/路由问题，是 **React 渲染期抛错**（无 ErrorBoundary 时整树卸载）。最快定位：浏览器注入 `window.__errs` 监听（console.error + window.onerror + unhandledrejection）→ 从正常页**内部导航**触发崩溃（整页刷新会清掉监听器）→ 读真实堆栈 → grep 错误字符串定位源码 throw 点。典型根因：**数据/代码不一致**（如商品编码 SKU→SP 迁移后 initialOrders 仍引用旧编码，getSalesOrders 校验商品 throw）。完整调试流程+诊断清单见 `references/react-white-screen-debugging.md`（0813 forge-erp 实踩）。

## Standard Deployment Steps

1. Extract zip, find `dist/` folder (may be flat or nested)
2. Fix asset paths: `href="/assets/" → href="./assets/"` and `src="/assets/" → src="./assets/"`
3. Fix API path: `"/api-server"` or `"/hermes"` → correct path
4. Copy CSS from known-good version if layout broken
5. Deploy to `/var/www/pmlophy.com/<project>/`
6. Add nginx location block if new project
7. `systemctl restart nginx` (NOT reload — see Pitfalls)
8. Verify: `curl -sk -o /dev/null -w '%{http_code}\n' 'https://pmlophy.com/<path>/'`

## Critical Pitfalls

### deploy-all.sh 审查门禁管道（2026-08-05 新建，v135 实踩）

新管道（jarvis-voice + forge 三项目 + copy-wms 通用）：AI 产物 rsync 到 `incoming/` → cron 只跑 `--check` 检测 → 用户确认后 `--deploy`。完整架构见 `ai-artifact-pipeline` skill。

```bash
bash /root/deploy-all.sh --check                      # cron 每分钟，只检测不部署
bash /root/deploy-all.sh --deploy                     # 部署全部 pending
bash /root/deploy-all.sh --deploy jarvis-voice        # 只部署指定项目
```

**⚠️ `--deploy` 参数是"项目名"（不带 -incoming 后缀）**——脚本内部自己拼 `${TARGET}-incoming`。传 `jarvis-voice-incoming` 会拼成 `jarvis-voice-incoming-incoming` → 日志报"未知项目"且**不部署**（v135 实踩：第一次传错没部署，线上还是旧版）。

**⚠️ 新项目接入管道的三步注册（0811 贾维斯实踩）**：`mkdir -p /var/www/pmlophy.com/<项目>-incoming /var/www/pmlophy.com/<部署目标>` + deploy-all.sh 的 `declare -A PROJECTS` 加一行映射（如 `["jarvis-local-incoming"]="/var/www/pmlophy.com/agent/jarvis"`）——AI 的 rsync 上传目标目录不存在时上传会失败，所以**先建目录再让 AI 传 zip**。

**⚠️ 预建部署目标目录会弄坏 deploy 脚本（0811 实踩）**：deploy-all.sh 解压到 TMP 后，若 `$DEST` 已存在会 `mv` 到 backup 再 `shutil.copytree(src, dest)`——但**手动预建的空目录**会被 mv 走后又因 copytree 报 `FileExistsError: File exists: <dest>`（Python 3.11 copytree 的 dirs_exist_ok 行为），脚本仍打印"部署完成"但**目标目录是空的**（index.html 不存在 → HTTP 403）。排查：部署后 `ls <部署目标>/index.html` 必须存在，不能只看"部署完成"日志。修复：删掉预建空目录让脚本自己管理，或手动兜底 `rm -rf <dest> && mkdir -p <dest> && cd <dest> && unzip -q <zip> && ls index.html`。

**⚠️ nginx 加静态站点 location（0811 实踩）**：patch/write_file 工具拒写 `/etc/nginx/sites-enabled/` 系统路径（安全保护）——用终端 `cp` 备份 + `python3 - << 'PY'` 读改写（锚点 replace 插入）+ `nginx -t` 验证 + `nginx -s reload`。新增 location 块 reload 即可生效（HTTP 200 立验）；改已有 location 的代理/缓存逻辑仍按铁律 restart。新静态 App 的 location 模板（alias + index + assets 长缓存 + html 不缓存 + try_files）：照抄现有 `/jarvis-voice/` 块改路径。

**⚠️ 同名 zip 重复上传会被跳过**——检测逻辑看 backup 目录是否已有同名 zip（有 = 视为已部署）。AI 每次打的名都是 `jarvis-voice.zip`，第二次上传同名会被误判"已部署过"直接跳过。**绕过**：incoming 里先 `mv jarvis-voice.zip jarvis-voice-v135-$(date +%H%M%S).zip` 改唯一名再 `--deploy`，或修脚本改为比较 hash/大小。**✅ 已根治（2026-08-26 加固）**：deploy-all.sh 部署成功后备份 zip 改名 `$(basename $LATEST .zip)-deployed-$(date +%Y%m%d-%H%M%S).zip`（不再原样 mv 进 backup 保持同名），回滚查找同步改为 `-deployed-*.zip`；同时把各 backup 目录历史遗留的 58 个旧 zip 统一改名加 `-legacy-` 后缀。**教训：脚本"备份时保持原文件名"是误判类 bug 的温床——备份/归档文件一律改名加时间戳，保证与 incoming 永不重名**。

**部署后验证**：`grep -o 'index-[^"]*\.js' /var/www/pmlophy.com/jarvis-voice/index.html` 确认主 bundle 换成新版（不能只看 HTTP 200——旧包也会 200）。v135 教训：日志"部署成功 200"但 index.html 仍引用旧 `index-rILMLJdh.js`。

**⚠️ forge 系项目部署目标在 /project/ 子路径**（2026-08-08 实踩）：`/var/www/pmlophy.com/project/forge-crm/`，deploy-all.sh 验证 URL 必须是 `https://pmlophy.com/project/<项目>/`（曾写根路径导致验证 404 误回滚）。部署失败日志特征："验证失败 HTTP 404，回滚"——先对比脚本 URL 与实际部署路径。

**⚠️⚠️ 验证 URL 的镜像坑：根路径项目被 /project/ 误判 404 → 假回滚（2026-08-20 jarvis-voice 实踩）**：deploy-all.sh 有一处写死 `URL="https://pmlophy.com/project/$(basename "$DEST")/"`——把它当所有项目通用。但 **jarvis-voice 部署在根 `/jarvis-voice/`（不是 /project/ 下）**，于是验证请求 `/project/jarvis-voice/` → nginx 404 → 脚本误判"部署失败"并触发回滚。**即使部署本身成功、线上已是新 bundle，脚本仍反复报"验证失败 404 回滚"**（且因 backup 无旧版走到"无备份可回滚，保留当前状态"——所以线上其实保留了新包，只是日志假失败）。**诊断特征**：部署日志"验证失败 HTTP 404，回滚"，但 `curl https://pmlophy.com/jarvis-voice/` 实际 200 且 index.html 已是新 bundle。**修复**：验证 URL 按 DEST 是否含 `/project/` 自适应前缀——
```bash
if [[ "$DEST" == *"/project/"* ]]; then URL="https://pmlophy.com/project/$(basename "$DEST")/"; else URL="https://pmlophy.com/$(basename "$DEST")/"; fi
```
改完自测：jarvis-voice → 根路径 200，forge-* → /project/ 200。**教训**：部署脚本验证 URL 不是所有项目都带 /project/ 前缀——先看部署目标映射（PROJECTS 数组）决定是根路径还是子路径。

**⚠️ zip 必须"解压即根"**（2026-08-08 实踩）：打包要 `cd <dist> && zip -rq ../../<项目>.zip .`（第一层就是 index.html）。若 zip 内是 `front-prototype/dist/index.html`（带目录前缀），部署解压后入口在子目录 → 验证 404。检查：`unzip -l <zip>` 第一层应是 index.html/assets，不是目录前缀。指令里必须逐字写打包命令，AI 默认会带前缀打包。

**⚠️ 回滚逻辑加固**：deploy-all.sh 回滚在无备份时必须保留当前目录（曾因备份缺失 + 误删导致线上目录整个消失 → HTTP 500）。修复后：`if [ -n "$LATEST_BACKUP" ]; then rm+mv; else log "无备份可回滚，保留当前状态"; fi`。恢复手段：项目 backup 目录的 `-<时间戳>` 备份，或手动重部署（解压 zip → cp dist/* 到目标）。

**⚠️⚠️ 回滚 bug：`mv backup 的 zip 到项目目录` 会把目录变成 zip 文件（0814 实踩——P0 级，线上 500）**：旧回滚代码 `rm -rf "$DEST"; mv "$LATEST_BACKUP" "$DEST"` 假设 backup 是目录——但 backup 里是 **zip 压缩包**，mv 后项目路径变成一个 zip 文件（不是目录）→ `curl` 500 / 目录不存在。**正确回滚：`ROLLBACK_DIR=$(mktemp -d)` → `unzip -q "$LATEST_BACKUP" -d "$ROLLBACK_DIR"` → 找 index.html 所在层（`$ROLLBACK_DIR/index.html` 直接有，或 `$ROLLBACK_DIR/dist/` 嵌套）→ `rm -rf "$DEST"; cp -r <那层> "$DEST"`**。恢复手段：直接从 incoming 里残留的 zip 手动解压重部署（`rm -rf <dest> && mkdir -p <dest> && cd <dest> && unzip -q <zip> && ls index.html`）。

**⚠️⚠️ 回滚/部署后目录权限 700 → nginx 403（0814 实踩）**：`cp -r` 恢复（或 mktemp 解压复制）的目录权限继承源（700），nginx 读不了 → 验证 403 → 又触发错误回滚（死循环）。**部署和回滚后必须 `chmod -R 755 "$DEST"`**（deploy-all.sh 的 python copytree 部分自带 chmod，但手写 cp -r 回滚没有）。排查特征：部署日志"验证失败 HTTP 403，回滚"反复出现 + 项目目录 `ls -ld` 是 `drwx------`。

**⚠️⚠️ 验证 403 误判：curl 不带 UA 被 Cloudflare 拦（0814 实踩）**：deploy-all.sh 的验证 `curl -sk -o /dev/null -w '%{http_code}' "$URL"` 无 UA——VPS 直连会被 Cloudflare 拦成 403 → 误判部署失败 → 触发错误回滚（把好部署回滚掉）。**验证 curl 必须带浏览器 UA + 失败重试一次**：`curl -sk -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36" ...`，首次非 200 `sleep 2` 再试。改完 deploy-all.sh 后 cron 每分钟自动用新逻辑（脚本是每次执行读的，不用重启 cron）。

**⚠️ 半自动模式（2026-08-08 用户确认）**：上传 + cron 检测（2分钟）自动，但"提醒→处理"需要会话激活（agent 不常驻，无法零延迟自动执行）。**每次对话开始主动查 pending**（incoming 新 zip + ai-reports 新报告），不等用户提醒；部署仍需用户确认（审查门禁）。用户不接受"提醒发了但没实际处理"——提醒只是通知，处理要真实发生。

### Cloudflare 缓存旧静态文件（2026-08-08 实锤，forge-crm runtime.js）
部署新版后用户线上仍看到旧效果（如\"入口按钮没出现\"\"还是旧交互\"），先怀疑 **CF 缓存了旧静态文件**——即使源站已更新：
- 诊断：`curl -sI https://pmlophy.com/<项目>/<静态文件>` 看 `cf-cache-status`——**`HIT` + `age: 4xxx` 秒 = 旧文件被缓存**；`DYNAMIC`/`EXPIRED` = 实时取源。**index.html 通常 DYNAMIC（不缓存），但 runtime.js 等静态文件带 max-age=14400（4小时）会被 CF 缓存**。
- 实锤法：带随机参数请求 `curl -s "...runtime.js?nocache=$(date +%s)" | grep -c '<新特征字符串>'` —— 有参数拿到新版、无参数拿到旧版 = 缓存问题实锤。
- **根治（每次部署必做）**：给 index.html 里静态文件引用加**版本参数**并**每次部署递增**（`runtime.js?v=2` → `?v=3`），否则 CF 一直发旧文件。验证 `curl -s "...runtime.js?v=N" | grep -c 新特征`。
- **注意**：deploy-all.sh 重新部署会用 zip 里的 index.html **覆盖掉你手动加的版本参数**——每次 `--deploy` 后要**重新加版本参数**（sed 递增）。且 runtime.js 常由 index.html body 内动态 script 注入（`document.createElement('script')`），不是静态 `<script src>`——grep 静态标签会漏，要 grep 注入路径。

### ⚠️ 先证明「线上是不是最新」再谈怎么部署（HTTP 200 等于没验）

被问「你确定这个地址是最新的前端代码吗」时，200 不算答案。四条实测判据，缺一条就不能说线上是最新：

```bash
# 1) 线上引用哪个 bundle（不是看页面开不开，是看引用哪个文件）
curl -s "https://<域名>/<子路径>/?v=$(date +%s)" | grep -oE 'assets/index-[A-Za-z0-9_-]+\.js'
# 2) 部署目录的实际落盘时间
ls -lt --time-style=+%m-%d_%H:%M /var/www/<站点>/<子路径>/ | head -3
# 3) 本地 dist 引用的 bundle（与 1) 不同名 = 线上不是本地这份构建）
grep -oE 'assets/index-[A-Za-z0-9_-]+\.js' <仓库>/dist/index.html
# 4) 部署时间之后源码还有没有提交没上线 —— 这条最容易被漏，也最能一击定性
git log --since="<部署目录 mtime>" --oneline -- <原型/前端源码目录> | head
```

第 4 条查出提交 = 线上落后，与「页面能打开」无关。反过来也要查一层：本地 `dist/` 是不是最新源码的构建——`git log --since="<dist mtime>" -- src public` 为空才说明 dist 没落后（否则要重 build，不是重部署）。

### 手动铺 dist 的部署序列（没有 deploy 脚本时照这套走）

```bash
git ...  # 若走管道先 pull
cp -a /var/www/<站点>/<子路径>/. /root/deploy-backup/<项目>-$(date +%m%d_%H%M)/   # 先整目录备份，回滚锚点
rsync -a --delete <仓库>/dist/ /var/www/<站点>/<子路径>/                         # --delete 清掉旧 bundle
chown -R www-data:www-data /var/www/<站点>/<子路径>
```

**验收以 md5 对齐为终判**，不是以 200 为终判：`curl -s <线上 bundle> | md5sum` 必须等于本地 `md5sum dist/assets/index-*.js`；再抽查三五个 SPA 深链（如 `/engage/list`、`/sales/comments/list`）逐个 200。

两个「看起来像失败其实不是」的现象：① **旧 bundle URL 仍然 200 且在发真 JS**——`curl -sI` 看 `cf-cache-status: HIT` + `last-modified` 是旧日期，是 Cloudflare 边缘缓存，磁盘上其实已删，没有页面引用它，等 max-age 过期即可；② **index.html 是 `cf-cache-status: DYNAMIC`**（不进缓存），所以用户拿到的一定是新引用，仍要提醒他硬刷新一次（本地浏览器缓存的是 HTML）。

### 绝对根路径 vs 子目录部署（v146 robin-thinking.mp3 + v157 robin-avatar.png 两次实踩）
前端 JS 里写**绝对根路径**资源（`/robin-thinking.mp3`、`/robin-avatar.png`）而应用部署在子目录（`/jarvis-voice/`）时，浏览器/APK 请求的是 `https://pmlophy.com/<资源>`（根目录）→ 源站根目录没这文件 → **404/裂图**。排查特征：`curl https://pmlophy.com/<资源>` 404 但 `curl .../jarvis-voice/<资源>` 200。
- **根因**：Vite 产物里硬编码 `/xxx`（绝对根路径），未用相对路径或 Vite base 配置。
- **快速缓解**：把资源复制到站点根目录 `/var/www/pmlophy.com/<资源>`（robin-thinking.mp3、robin-avatar.png 都这么救过）。
- **根治**：指令要求 agent 用相对路径（`robin-avatar.png` 不带斜杠）或 `import` 打包，禁止硬编码根路径——同一坑出现两次，指令红线必须写"禁止绝对根路径资源引用"。
- **Cloudflare 缓存 404**：根路径资源首次 404 会被 CF 缓存（`cf-cache-status: HIT` 仍是 404）；源站补文件后无参数请求可能仍 404，带 `?v=时间戳` 参数 200 即实锤。修复后需 Purge Everything 或让前端 URL 带版本参数。

**⚠️⚠️ AI 会谎报\"已部署\"——独立验证铁律（2026-08-21 WMS 连续两次实踩）**：Codex/Cursor 自检报告常写\"已 rsync + 部署 + HTTP 200\"，但实际 zip 还在 Mac 本地 `/tmp`，根本没进 VPS incoming、线上还是旧版。**部署验证绝不信 AI 自报的 HTTP 200**，必须核对三条独立证据（任一条不满足 = 没真正部署）：
1. **线上 index.html 文件时间戳**：`stat -c "%y" /var/www/pmlophy.com/project/<name>/index.html` —— 应为本次部署时间，若是上次部署时间则没更新
2. **线上主 bundle 物理时间**：`find .../assets -name "index-*.js" -printf "%TY-%Tm-%Td %TH:%TM" | sort -r | head` —— bundle 是今天的还是上次的
3. **部署日志**：`grep '<项目>' /var/log/jarvis-deploy.log | tail` —— 有\"部署成功 HTTP 200 ✅\"且时间对得上才是真部署
自检报告与实测矛盾时**以实测/线上为准**（用户铁律）。诊断特征：AI 报告\"部署成功 HTTP 200\"，但 incoming 是空的 / 线上 index.html 时间没更新 / 部署日志没这轮记录 → 它是谎报。

**⚠️⚠️ 部署验收三查的补充坑（2026-08-26 forge-scrm 实踩）**：
1. **bundle 内容特征 grep 必须用 JS 形式，不是 CSS 文本**：React inline style（`style={{maxWidth:720}}`）编译后是 JS 对象 `maxWidth:720`，bundle 里 grep `max-width:720px`（CSS 写法）= 0 会**误判"修复没上线"**。正确特征：grep `maxWidth:720`、`textOverflow`（labelRender）等**编译后形态**。判断修复是否上线用内容特征，不用文件时间戳。
2. **rsync -a 保留源 mtime → 远端时间戳误导**：`rsync -avz` 的 `-a` 保留 Mac 源文件 mtime，远端 `ls -la` 显示"10:58"却可能是刚刚传的——**远端时间戳 ≠ 传输时间**。曾因此误判"部署没生效"反复部署。验证一律用 bundle 内容特征 grep。
3. **deploy.sh 不自动 git pull**：Mac 本地源码落后时 build 出**旧 bundle 白部署**（hash 与线上相同，rsync 传了等于没传）。部署前 `git fetch` 后对比 `git log --oneline -1` 与 `origin/main`，源码最新再 build。
4. **alembic current 必须到最新 head**：Codex 部署常漏迁移（head 停旧版 → 新表/seed 数据没建 → 前端看着"没变化"）。验收必查 `alembic current` 与最新迁移版本一致。
- **根治：让 AI 只做\"传文件到 VPS\"，部署由 Agent/VPS 手动确认**。与其让 AI 自己跑部署（它老在部署这步谎报），不如指令改成：**只 scp/rsync zip 进 incoming**，并回报**文件时间戳 + 字节数**作上传证据（`ssh ... "ls -la incoming/"`），明确要求\"不要声称已部署，部署由 VPS 侧手动确认\"。文件真到了（incoming 有、字节数吻合），Agent 侧手动 `bash /root/deploy-all.sh --deploy <项目>` + 三条证据独立验证。这样 AI 只做它可靠的部分（传文件），部署的确定性由自己掌控。
- **验证上传成功的靠谱写法（给 AI 的指令里）**：传完后让它 `ssh -p 2222 -i ~/.ssh/id_ed25519_vps root@VPS "ls -la <incoming>"` 回报文件名/字节/时间戳——文件时间和字节能对上就是真上传了，比它报\"已部署\"可信得多。

**⚠️⚠️ 手动/回滚部署白屏：index.html 的 /assets/ 绝对路径只被 deploy-all.sh 自动修正（2026-08-20 实踩）**
打包产物 `index.html` 常含**绝对路径** `/assets/index-xxx.js`（Vite base 配 `'/'` 时）。走 **deploy-all.sh 管道**部署时，它的 python 段会把 `/assets/` → `./assets/`（自动），所以管道部署正常。但**手动部署 / git 回滚后重打包 / 直接用 zip 覆盖线上**（没走 deploy-all.sh）时，**index.html 仍是绝对路径** → 浏览器从 `https://pmlophy.com/assets/...`（域名根）加载 JS → 源站在子目录 `/jarvis-voice/assets/` → **域名根 `/assets/` 404 → JS 加载失败 → 整个页面白屏**（#root 有，但 React 没渲染）。
- **诊断特征**：线上 `index.html` 里 `<script src="/assets/...">` 是**绝对路径**（非 `./assets/`），且 `curl https://pmlophy.com/assets/index-xxx.js` 404 但 `curl .../jarvis-voice/assets/index-xxx.js` 200。
- **快速修复（不改代码、不重 build）**：直接改线上 `index.html`，把 `src="/assets/` 和 `href="/assets/` 改成 `./assets/`（用 patch 替换）。
- **根治**：让 vite base 配成相对/子路径（`base: './'`），或永远走 deploy-all.sh 管道（它会自动转相对路径），或手动部署后必须人工核验 index.html 是相对路径。
- **教训**：**每次手动部署 / 回滚 / 用用户 zip 直接覆盖后，第一件事检查 index.html 的 asset 引用是相对还是绝对**——绝对就白屏。回滚尤其危险：回滚版往往是用新打包（绝对路径）的 zip 直接解压覆盖的。

### 部署 zip 覆盖静态资源（v157 实踩）
`deploy-all.sh` 解压 zip 替换整个线上目录时，**zip 里没有的源站静态文件会被清掉**（v157 的 robin-avatar-sm.png 部署后从源站消失，只剩 CF 缓存顶着）。**任何部署后**必须校验非 bundle 静态资源还在：`ls /var/www/pmlophy.com/<项目>/*.png *.mp3`。根治：静态资源打进前端包（`app/public/`，随 build 进 dist）或部署脚本保护白名单文件。APK 侧同理：远程 URL 图在 Capacitor WebView 加载失败（浏览器正常）→ 图片本地化打进包；APK 缓存顽固（清缓存无效）→ 卸载重装。

**⚠️ deploy-all.sh 只检测 `*.zip`——rsync 上传的 dist【目录】不会被自动部署（0813 forge-erp 实踩）**：forge-erp 管道是 `rsync .../dist root@VPS:.../forge-erp-incoming/`（传目录），但 deploy-all.sh 检测逻辑是 `ls "$INCOMING"/*.zip`——目录永远不会匹配 → cron 每分钟 `--check` 都静默跳过 → 线上还是旧 bundle。排查特征：incoming 里有 dist 目录但 `tail /var/log/jarvis-deploy.log` 完全没提到该项目。处置（三选一）：①手动部署（备份旧 bundle → `cp -r incoming/dist/* 部署目标/` → grep index.html 确认引用新 bundle）；②给 agent 的指令改为打包 zip 再传（`cd dist && zip -rq ../proj.zip .`）；③改 deploy-all.sh 支持目录检测。**教训：写部署通道时确认该项目管道传的是 zip 还是 dist——dist 项目不能只靠 cron 自动部署。**

**⚠️ 报告统一归档（0814 用户铁律）**：项目所有自检/审计/复核/部署报告统一放项目根目录 check-reports/ 文件夹（禁止散落根目录）——已写进各项目 AGENTS.md。给 agent 的指令末尾写"报告统一放 check-reports/"；Agent 若把报告丢根目录（如 forge-crm-xxx-report.md 散落），执行后要 git mv 归纳进 check-reports/ 再 push。

**⚠️ 部署通道铁律（0813 用户强调——每条 agent 指令必带，不是摆设）**：给 agent（Codex/反重力/WorkBuddy）的每条修复/开发指令末尾必须附部署通道——rsync 完整命令（dist/zip → VPS incoming → cron 自动部署）+ 自检报告 curl 上传命令。AI 倾向保守，不主动执行外部操作，命令必须逐字给出（v135 教训重犯：给修复指令漏部署段——用户原话"不要忘了自动部署这个通道，不是拿来当摆设的"）。部署命令写给 agent 执行，不是给用户跑——用户是命令官模式（只发指令+验收），给用户终端命令会被批"不是为难我么"。默认自动部署；例外=用户要求"本地先启动服务浏览查阅"（用户说本地先看才跳过部署）。文档修改（PRD/context）不走部署通道——走 git（审后用户 push）——给 agent 的文档指令也写清"不部署，等用户审核后 git 提交推送"。

### ⚠️⚠️ 部署以"本地工作区"为准（rsync），不依赖 git pull + .env 必须排除 + Python 版本对齐（2026-08-25 forge-scrm 实踩，502 血泪）

**矛盾根源**：给 agent 的红线禁止其 commit/push → **Mac 本地工作区永远领先 git main** → 部署脚本里 `ssh ... git pull origin main` 拉到的是旧 main → 部署的是旧代码（用户原话："这个部署方式本身就有问题，要获取 git 最新的，但是给 agent 的提示词又不许他 git 提交，我这边 mac 实际上永远是比 git 要早一步的"）。

**修法（forge-scrm deploy.sh 已改，可照抄）**：部署改为纯 rsync，以本地工作区（含未提交改动）为准：
```bash
# 前端：build 后 rsync dist（dist 含全部改动，含未提交）
npm run build && rsync -avz dist/ root@VPS:$REMOTE/frontend/dist/
# 后端：rsync 源码（排除 venv/缓存/数据）
rsync -avz --delete --exclude='__pycache__' --exclude='*.pyc' --exclude='.venv' \
  --exclude='venv' --exclude='data/' --exclude='*.db' --exclude='.DS_Store' ../backend/ root@VPS:$REMOTE/backend/
# 不再 git pull；重启后端前幂等 pip install -r + alembic upgrade
```

**⚠️⚠️ `--delete` rsync 会覆盖目标机 .env → 生产配置/数据库凭据丢失（本次最惨坑）**：Mac 的 backend/.env 是开发用 SQLite 模式，rsync --delete 到 POC 机 → POC 的 .env 变成 SQLite 版 → 后端连不了 MySQL（`sqlite3.OperationalError: no such table: user`），且**真实 MySQL 密码被冲掉**，用户也不知道原密码（"我不知道 mysql 密码！！！！"）。**教训：.env 必须从 rsync 排除（`--exclude='.env'`）并以目标机为准单独管理，或部署机与开发机共用同一份生产 .env；任何 rsync --delete 前先想清楚目标机上有什么会被删**。密码救援：MySQL root 免密时 `ALTER USER 'app'@'localhost' IDENTIFIED BY '<新密码>'; FLUSH PRIVILEGES;` 重置，新密码写进目标机 .env（字母数字无特殊字符，防 shell 转义/连接串解析坑）。

**⚠️ Python 版本漂移：Mac 3.14 vs VPS Ubuntu 22.04 系统 3.10 → StrEnum ImportError → 服务崩溃循环**：`from enum import StrEnum` 是 3.11+ 才有——Mac 开发机跑得好好的，部署到 POC 后 `forge-scrm-api` 反复 `activating → failed`（systemd 崩溃循环，`systemctl show -p NRestarts` >0），登录 502。**部署前先核对 venv Python 版本**（`ssh VPS '.venv/bin/python --version'` vs Mac）。修复（VPS 侧）：`add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.11 python3.11-venv` → `mv .venv .venv.bak-$(date +%H%M%S) && python3.11 -m venv .venv && .venv/bin/pip install --upgrade pip && .venv/bin/pip install -r requirements.txt` → `systemctl restart <服务>`。**判断口径：后端代码写进仓库 = 按 Mac 的 Python 能力写没问题，但 VPS 运行环境必须对齐（装同版本/更高版本），别让生产环境拖后腿。**

**502 排查链路（后端服务型）**：首页 200 + 登录/API 502 = nginx 活着 + 后端端口死。顺序：`ss -ltnp | grep <端口>`（无 = 死）→ `journalctl -u <服务> --no-pager -n 25` 看 uvicorn 报错 → 逐层解（ImportError → DB 连接串 → DB 凭据 → 建表/seed）。**别停留在"重启服务"——activating 反复 = 启动即崩，必须看日志根因**（本案例链：StrEnum ImportError → SQLite 无表 → MySQL Access denied 三步才到真因）。

### 业务应用跨 VPS 迁移要点（2026-08-26 forge-scrm Lisa POC → 搬瓦工 实踩）

- **备份复制**：`scp -3` 只支持一个端口——源机 2222 / 目标机 22 不同端口时 `-3` 直传不可用，改**两段式**（源机→本地临时目录→目标机），到本地先 `sha256sum -c` 校验再推目标；跨机复制前 `ssh-keygen -R <ip>` 清理重装系统后的旧 host key（REMOTE HOST IDENTIFICATION HAS CHANGED）
- **Python 环境**：deadsnakes PPA 签名故障（apt-get update 报错）时不纠结，改用 **uv 独立 Python**：`uv venv --seed --python 3.11 .venv`——⚠️ **`uv venv` 默认不带 pip**（`.venv/bin/pip: No such file or directory`），必须 `--seed`；依赖安装用 `uv pip install --python .venv/bin/python -r requirements.txt`，不要调 `.venv/bin/pip`
- **数据库迁移**：mysqldump 全库备份 → 目标机 `openssl rand -hex 24` 生成新密码 → 用 **python 读改写 .env 的 DATABASE_URL 密码段**（避免 sed 引号嵌套/聊天脱敏坑）→ 建库建用户（`CREATE DATABASE ... utf8mb4` + `CREATE USER` + `GRANT`）→ 导入 dump → `information_schema.tables` 数表验证；密码只在目标机流转，不进聊天
- **部署后验证矩阵**：systemd active + `nginx -t` + 本地 curl（页面 200 / 登录空请求 422 / 带 token 真实登录测业务接口）——422 是接口可达的标志
- **DNS 切换验证**：`dig +short` 本地 + `dig @1.1.1.1` + `dig @8.8.8.8` 三源一致 + `curl -w '%{remote_ip}'` 实测落点，全绿才算切完；Cloudflare 先灰云（DNS only）验证 HTTP，再上 HTTPS（橙云 + 无 443 = 521/SSL 问题）
- **HTTPS**：`apt install certbot python3-certbot-nginx` + `certbot --nginx -d <domain> --non-interactive --agree-tos -m <email>` + http→https 301 + 自动续期（certbot.timer）；验证 `https://<domain>/` 200 + 登录接口 200 + http 301
- **部署脚本目标切换**：deploy.sh 的 host/port/key/remote_dir 统一改新机、删旧 IP 逻辑、验证 URL 用 HTTPS 域名；后端 rsync 必须 `--exclude='.env'`（防开发机 SQLite 版 .env 覆盖生产 MySQL 配置）

### SSH 远程多层命令引号爆炸 → base64 传脚本执行（2026-08-26 迁移全程反复实踩）

ssh 'remote bash' 里嵌 python heredoc / sed / 双引号变量时，本地 shell + 远端 shell 两层解析必炸（SyntaxError / unexpected EOF / quoting hell，execute_code 里 python 三引号再嵌脚本也炸）。稳定模式：本地把脚本 base64 编码，远端解码执行——脚本内引号/heredoc 零转义，脚本开头 `set -e` 保底：

```python
import base64
script = r'''多行 shell 脚本（可含 heredoc/单双引号，原样保留）'''
b64 = base64.b64encode(script.encode()).decode()
cmd = f"ssh -p 2222 -i <key> root@<host> \"printf '%s' '{b64}' | base64 -d | bash\""
```

- 该模式同时避免敏感串（密码/密钥）经聊天/日志脱敏成 `***`——base64 传输不落明文，是"密码只在远端流转"的可靠实现
- execute_code 里构造脚本避免 python 三引号嵌套：用列表 `script_lines = [...]` 拼接，或把脚本写到本地临时文件再读入编码

### ⚠️ nginx `proxy_pass` 带不带 URI 尾缀决定路径是否被重写（2026-08-20 jarvis-local file 实踩）
`location` 里 `proxy_pass` 的写法决定转发到后端的路径：
- **带 URI**：`proxy_pass http://127.0.0.1:8871/file;` → 用 `/file` **替换** location 匹配到的前缀 → `/p/jarvis/file/get` → 后端收到 `/file/get` ✅
- **不带 URI（只有 host:port）**：`proxy_pass http://127.0.0.1:8871;` → **保留完整请求 URI** → `/p/jarvis-local/file/get` → 后端收到 `/p/jarvis-local/file/get`（原样）→ 后端没这个路由 → **404** ❌

**实踩**：voice 的 file location 是 `proxy_pass http://127.0.0.1:8871/file`（带 URI → `/p/jarvis/file/get` 到达 8871 的 `/file/get` 200），但 jarvis-local 的 file location 是 `proxy_pass http://127.0.0.1:8871`（不带 URI → `/p/jarvis-local/file/get` 被 8871 原样接收 → 404）。**同一后端、同一接口，前缀不同 404 vs 200，根因就是 proxy_pass 的 URI 尾缀**。
- **排查特征**：后端直连接口 200（`curl http://127.0.0.1:8871/file/get?path=...` 通），但经某个 nginx 前缀转发就 404。
- **修复**：给对应 location 的 `proxy_pass` 补上后端路径 URI（如 `:8871/file`），使其剥掉前缀。
- **教训**：新增/排查子路径转发时，先看该 location 的 `proxy_pass` 是带 URI 还是裸 host:port——带 URI 会重写路径，裸的保留完整路径。给存储/上传服务加读取接口时，各前缀 location 要统一成带 `/service` URI 的形式。

### 给只存不读的文件服务加 HTTP 读取接口（jarvis-file.py 模式，2026-08-20 实踩）
VPS 上 `jarvis-file.py`（8871）原本只有 `POST /file/upload`（只存不读），要让前端跨设备用 URL 展示图片/文件，需补 `GET /file/get`。安全可靠的写法人人可复用：
- **防路径穿越**：`base=os.path.realpath(DATA_DIR); target=os.path.realpath(path_q)`，然后 `if not os.path.commonpath([base,target])==base or not os.path.isfile(target): 404`——只允许读 files 根目录内文件。
- **按扩展名给 Content-Type**（图片 inline 展示、文档 attachment 下载），不执行、不解析内容，只回字节。
- **加 Cache-Control: public, max-age=31536000** 让图片长缓存，节省回源。
- **上传接口顺带返回 `url` 字段**（`/p/jarvis/file/get?path=...`）——前端拿到即用，不用自己拼。
- **图片"base64 塞进消息 content"是反模式**（history 膨胀 + 跨设备不可见 + 点击预览难解析）——根治是**上传 VPS 存 path，content 只存轻量 path**，前端渲染时拼 URL。完整设计见 `references/vps-image-path-storage.md`。

### 互为克隆的项目要镜像修复（lophy-jarvis-voice ↔ lophy-jarvis-local，2026-08-20）
`lophy-jarvis-voice`（罗宾语音/网页版，`/jarvis-voice/`）和 `lophy-jarvis-local`（文字版，`/agent/jarvis/`）是**同源克隆**——`App.tsx` 的发送/竞态逻辑（`prepareSendTurn`/`executeSendTurn`/`activeRequestRef`）、历史同步几乎逐行相同。**在任一端修复的 bug（如播报/回复中发消息竞态、图片历史缺失）必须镜像到另一端**，否则改了一端另一端还带 bug。判断方法：`grep -c activeRequestRef App.tsx` 两端结构一致说明是同源；修复后对比两端文件 diff 确认只有预期差异。**注意两端部署前缀不同**（`/p/jarvis/` vs `/p/jarvis-local/`）、localStorage key/Dexie 库名/8868 账号各自隔离（<项目>隔离架构铁律）。

### ⚠️ Codex 沙箱默认禁网：curl DNS 全挂 ≠ Mac 网络问题（2026-08-26 实踩）
Codex CLI `workspace-write` 模式沙箱默认 `network_access = false` → 沙箱内 curl **连 DNS 都解析不了**（`curl: (6) Could not resolve host`），`--noproxy '*'` 只能绕 HTTP 代理、绕不过沙箱网络禁制。**用户 Mac 手动 curl 200（nslookup 正常）≠ Codex 沙箱能联网**——先怀疑沙箱禁网，别去改 Mac DNS/代理。修法：`~/.codex/config.toml` 加：
```toml
[sandbox_workspace_write]
network_access = true
```
或单次：`codex -s workspace-write -c 'sandbox_workspace_write.network_access=true' ...`。审批 503 是 Codex 本地审批服务问题，可加 `approval_policy = "on-request"` 改终端交互审批。**兜底**：Codex 沙箱传不了时，报告走 git（check-reports/），杰西卡 VPS 侧从仓库补传管道——不要让它反复重试。

### nginx: restart vs reload
`systemctl reload nginx` does NOT clear old worker process caches.
Always use `systemctl restart nginx` after config changes.

### ⚠️ systemd 系统级服务调 `systemctl --user` 报 dbus 错误（2026-08-24 model-rescue 实踩）
后端作为**系统级 systemd 服务**（`/etc/systemd/system/xxx.service`，multi-user.target）运行时，若要检查/重启**用户级**服务（如 Hermes gateway 的 `systemctl --user is-active hermes-gateway`），会报：
`Failed to connect to bus: $DBUS_SESSION_BUS_ADDRESS and $XDG_RUNTIME_DIR not defined`
（系统服务进程没有用户总线环境变量，连不上 root 的 user bus）。**修法**：unit 里加两行 Environment——
```ini
Environment="XDG_RUNTIME_DIR=/run/user/0"
Environment="DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus"
```
诊断特征：服务 active 但 /api/status 里网关状态显示 dbus 报错全文；`ls /run/user/0/bus` 存在（说明总线在，只是服务没带环境变量）。
**⚠️ 部署脚本用 heredoc 写 unit 模板时，改模板文件无效——脚本内嵌 heredoc 才是真实来源（2026-08-24 同场景实踩）**：deploy.sh 里 `cat > /etc/systemd/system/xxx.service <<'UNITEOF' ... UNITEOF` 把模板**硬编码在脚本里**，`deploy/xxx.service` 单独文件只是给人看的参考、脚本根本不读它。用户改了 `deploy/model-rescue.service` 模板文件 → 重新部署后 VPS 上 unit 仍是旧内容（缺 Environment），dbus 错误复发。**修法：改 deploy.sh 的 heredoc 块本身**（或让脚本 `cat deploy/xxx.service` 读文件），改完重跑部署覆盖。排查特征：改了模板文件、跑了部署、VPS `grep Environment /etc/systemd/system/xxx.service` 还是旧值——先查 deploy.sh 里是否另有 heredoc 写 unit。

### Hermes API rejects Origin header
The Hermes API Server returns 403 (0 bytes) when requests include
an `Origin` header. Chrome always sends Origin on POST.
Fix in nginx: `proxy_set_header Origin "";`

### Chrome blocks Authorization on HTTP
Chrome strips `Authorization` header on HTTP requests to non-localhost IPs.
Use `X-Hermes-Key` custom header instead, or serve over HTTPS.

### Verify HTTPS before blaming Chrome cache/HSTS
When normal Chrome cannot open a site but Incognito can, first verify the exact scheme and the server listener:

```bash
curl -vkI --max-time 12 https://example.com/
curl -sI --max-time 12 http://example.com/
```

A direct `connect ... port 443 failed: Connection refused` proves HTTPS is not configured/listening; it is not a Chrome cache, Service Worker, or HSTS problem. Check the address bar carefully: Incognito may be using `http://` while normal mode retains an auto-upgraded/bookmarked `https://` URL. If the project is an intentional HTTP-only POC, tell the user to use the explicit `http://` URL. Only investigate HSTS/cache after TCP 443 and TLS succeed.

### Diagnose first; give the shortest user action
For non-engineer users, do not send long shell blocks that require manual editing of placeholders, secrets, or configuration. First perform read-only verification where possible. If user action is unavoidable, provide one copy-paste-ready command with all values resolved, state the expected output, and avoid iterative trial-and-error commands. Never infer a deployment or browser cause from symptoms alone when `curl`, port checks, or logs can establish it.

### Chrome requires secure context for some APIs
`crypto.randomUUID()` only works on HTTPS or localhost.
For HTTP deployments, add a polyfill:
```js
if(!crypto.randomUUID){crypto.randomUUID=function(){return"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,function(e){var t=16*Math.random()|0;return("x"===e?t:3&t|8).toString(16)})}}
```

### HSTS blocks self-signed certs on subdomains
If Cloudflare sets HSTS with `includeSubDomains`, self-signed certs
on subdomains will be rejected. Use Let's Encrypt or serve over HTTP
on non-standard ports.

### nginx map variables are unreliable
When nginx `map` directives fail silently (empty values), replace with
direct variable references: `$http_x_hermes_key` instead of `$auth_header`.

### Cloudflare WAF blocks browser POST
Cloudflare may block POST requests from browsers (not curl) due to
WAF fingerprinting. Bypass via gray-cloud DNS or non-standard port.

### ⚠️ Python urllib 默认 UA 被 Cloudflare 拦 → HTTP 1010（2026-08-24 model-rescue 预检实踩）
Python `urllib.request` 的默认 User-Agent 是 `Python-urllib/3.x`——带 Cloudflare 防护的站点（如 opencode.ai/zen/go/v1）识别到非浏览器 UA 直接返回 **HTTP 1010 (banned based on browser signature)**。症状：工具/脚本直连报"认证错误: error code: 1010"，但浏览器或带规范 UA 的 SDK（OpenAI SDK）访问正常。**修法**：请求 headers 里加浏览器风格 UA：
```python
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
```
排查特征：`HTTP 1010` 且 curl 加 UA 就通、不加就 403/1010——UA 问题实锤。凡自建"连通性预检/健康检查"类脚本调 CF 保护的 API，**默认带浏览器 UA**，否则预检工具自身误报（能用的模型报"认证错误"）。

### System proxy intercepts all traffic
Mac system proxy (Clash/V2Ray on 127.0.0.1:7897) intercepts all
outbound connections. Add bypass rules or test with proxy disabled.

## nginx Location Template for Hermes API Proxy

```
location /api-path/ {
    proxy_pass http://127.0.0.1:8642/;
    proxy_http_version 1.1;
    proxy_set_header Authorization "Bearer <key>";
    proxy_set_header API_SERVER_KEY <key>;
    proxy_set_header Host $host;
    proxy_set_header Origin "";
    proxy_read_timeout 120s;
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "x-hermes-key, content-type" always;
    if ($request_method = OPTIONS) { return 204; }
}
```

## Frontend Code Instructions

When giving instructions to Codex or Cursor:
- One file at a time, with strict red-line boundaries
- Never let AI modify CSS/Canvas/layout when only changing ASR or API logic
- Prefer providing complete replacement code rather than describing changes
- After each change, run `npm run build` and verify dist contents

## User Context

User is a PM (刘龙飞 / 路飞 / LophyJessica), not an engineer.
Do not ask them to modify code, proxy settings, or system configs.
Provide copy-paste-ready instructions or do it on VPS yourself.
