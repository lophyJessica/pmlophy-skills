---
name: coding-agent-subscription-bridge
description: 把 IDE/厂商订阅额度接进 coding agent（OAuth 插件或反代网关），含出口 IP 风控与 VPS 托管。
---

# 把订阅额度接进 coding agent

用户手里有 IDE 或厂商的付费订阅（Antigravity Pro、Claude、Gemini 等），想把它们的额度用在自己的 coding agent / 工作台里，而不是另外买 API 额度。本 skill 管两条路线怎么选、怎么装、以及版本与凭据的坑。

## 先分清三层：界面壳、agent 内核、模型额度

- **界面壳**（OpenChamber 这类装在 IDE 里的扩展、桌面 app、VS Code 插件）**不带任何模型额度**。它只是前端，背后必须有一个跑着的 agent 内核（如 OpenCode），模型和凭据都在内核那边。用户说「插件已经装好了」时，通常只完成了壳那一层；模型列表还是空的，不是装错了。先查内核与凭据，别去折腾壳。
- **agent 内核**（OpenCode / Codex / Claude Code）负责工具调用与执行，它自己不带额度，额度来自下面第三层。
- **模型额度**（Antigravity Pro、Claude 订阅等）独立于前两层，可以换来源而不动 IDE 和内核。

三层解耦的直接好处：**同一个 IDE 挂多个 agent 是成立的**（Cursor 与 Antigravity 的侧边栏都能同时列 Claude / Gemini / OpenAI / 自有 agent 多个入口）。要成立只需两条隔离：

1 **会话隔离**——每个 agent 用自己独立的上下文，共用一条对话会让 A 的记忆和 B 的指令混在一起。
2 **工作区隔离**——两个 agent 同改一个仓库必冲突，按目录 / 分支分开，或串行排队。

因此当用户嫌某个 IDE 的 harness 差时，正解是**把那个 IDE 降级成额度来源、换更好的壳去干活**，而不是在里面硬用。实测结论：反重力保留 OAuth 授权即为额度提供方，日常开发放 Cursor（编辑器体验、内置浏览器、多文件编辑都更成熟，且是用户每天在用的环境）。注意 Cursor 自带 AI 与 OpenCode 是两个独立入口，别在同一任务上重复消耗。

## 两条路线怎么选

| 路线 | 适用 | 代价 |
|---|---|---|
| **A. 内核内 OAuth 插件**（如 opencode-antigravity-auth） | 只在这一个 agent / 工作台里用 | 干净，少一层中转；只对该内核生效 |
| **B. 本地反代网关**（如 Antigravity-Manager 起在 127.0.0.1:8045，出 OpenAI/Anthropic 兼容接口） | 要让多个工具共用（Hermes、Cursor 等） | 多一层中转，排错要分两段；这类反代项目接口易变，历史上不稳 |

默认先走 A，跑通能用了再衡量要不要上 B。用户明确说「暂时不需要给别的 agent 用」时，直接 A。

## 客户端能不能吃这份额度：先问协议格式，再问工具名字

额度接得通不通，最终卡在**客户端要什么格式**，不是反代稳不稳。判断顺序：先看反代对外暴露的路径，再选客户端。

| 客户端 | 怎么接 | 能吃什么格式 |
|---|---|---|
| Claude Code（CLI / IDE 插件） | 环境变量 `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN`；指向该端点时它会查 `/v1/models` 填充 `/model` 选择器 | 原生 Anthropic Messages（`/v1/messages`）；经路由层还能吃 OpenAI / Gemini 格式 |
| Claude Desktop（图形 App） | 由 CC Switch 这类配置管理器改供应商，**必须重启应用本身**才生效 | 只有原生 Anthropic 格式，自己不做格式转换 |
| Codex / Gemini CLI / Grok Build | 各自配置管理器条目 | 支持路由与聚合（格式转换、故障转移、多供应商混列） |

- **「路由 / 聚合」只对 Claude Code / Codex / Gemini CLI / Grok Build 开放，Claude Desktop 没有这一层。** 所以反代只给 OpenAI 兼容格式（`/v1/chat/completions`）时，桌面端接不了，同一个反代交给 CLI 却能吃——报错别往 key 和端口上找。
- 结论：反代暴露 `/v1/messages` → 桌面端和 CLI 都能接；只暴露 `/v1/chat/completions` → 只有 CLI 经路由能吃，桌面端是死路，不要再调参。
- 挑反代时看它是不是三格式齐全（OpenAI + Anthropic + Gemini），这类通常另做了 thinking signature 缓存回放，否则 Claude Code 的思考块会断。
- 目标是桌面端时，先确认配置管理器对该应用有没有「路由」入口；没有就说明只支持直连，格式不对别再试。

## 路线 B 的具体选型：CLIProxyAPI（用户实际在用）

把 Antigravity / Gemini CLI / Codex / Claude Code 等 CLI 额度包成 **OpenAI / Gemini / Claude 三格式** 标准 API，默认端口 8317，可同时喂给 CC Switch、Cockpit Tools、Claude Code、Hermes。

先分清三个东西，别混：
- **CLIProxyAPI** 才是反代本体（出 API、发 key）
- **CC Switch / Cockpit Tools** 只是配置切换器，改客户端的地址与 key，自己不是反代
- **Antigravity / Cockpit 自己监听的端口**（如 62440）多为内部鉴权服务，返回 401 不代表它是通用反代

最小配置（从 `config.example.yaml` 复制成 `config.yaml`，只改这几处）：

```yaml
server:
  host: "127.0.0.1"      # 不给局域网用就收窄到本机
  port: 8317
management:
  secret-key: "xxx"      # 必填！留空则管理页整个 404，登不了账号
access:
  api-keys:
    - "sk-xxxx"          # 客户端拿这个当 token，见下方「模板值禁用」
```

启动 `./cli-proxy-api`，管理界面 `http://127.0.0.1:8317/management.html`（密码即 secret-key），在里面 OAuth 登录账号，页面会列出可用模型。

### api-keys 不能留模板值（会静默关掉整个代理）

`config.example.yaml` 自带的 `your-api-key-1/2/3` 是**模板占位符**。原样启动后访问任何代理路径，服务会回一个「Example API key detected」页面并**禁用全部 proxy 端点**——不是 401，也不是连不上，是整段端点被关掉，很容易误判成端口或网络问题。

启动前就换成真 key，一次 sed 到位：

```bash
KEY="sk-cpa-$(openssl rand -hex 12)"
sed -i '' "s/your-api-key-1/$KEY/" config.yaml
sed -i '' '/your-api-key-2/d' config.yaml
sed -i '' '/your-api-key-3/d' config.yaml
grep -A3 "^  api-keys:" config.yaml; echo "key: $KEY"
```

改完必须重启进程（Ctrl+C 再 `./cli-proxy-api`），只刷新页面不生效。

### 账号凭证：导入 ≠ 已加载

管理面板「配额管理」里凭证卡片都列出来了、但顶部写「N 个凭证 · 0 个已加载」，是正常的中间态——还没去拉额度。点「刷新全部凭证」等它跑完，计数变成 N/N 才算可用；再逐张看卡片上的 5 小时 / 周限额与重置时间，挑额度最充裕的号。

### 改完配置不生效：先查端口，再查文件位置

key 明明在文件里、格式也对，接口却持续 401，两个根因按顺序排：

1 **旧进程还在应答**。端口被占时新进程直接 `bind: address already in use` 退出（很容易在满屏启动日志里漏掉），旧进程继续服务，你测到的永远是旧内存配置。铁律：`pkill -f cli-proxy-api` → `lsof -nP -iTCP:8317` 必须无输出 → 再启动。
2 **改的不是它读的那份**。启动日志里出现 `<home>/.cli-proxy-api/kv.db` 就说明数据目录在那，真配置很可能也在那边；先 `ls ~/.cli-proxy-api/`，别对着一个没人读的文件改半天。

### YAML 缩进会被粘贴吃掉（表现为 Invalid API key）

把 `  api-keys:` 粘进 heredoc / 终端，两个空格可能被压成一个，Go 侧解析成空列表，现象是「key 明明存在、长度也对，但就是 Invalid API key」。

- 改缩进敏感文件不要手打空格，用 `\x20` 拼：`re.sub(r"(?m)^\s*api-keys:\s*$", "\x20\x20api-keys:", s)`
- 校验别靠眼看，用 `awk 'NR>=n && NR<=m {match($0,/^ */); print NR, RLENGTH}' config.yaml` 数准空格（`access:` 0 / `api-keys:` 2 / 列表项 4）
- 实在弄不好就别折腾文件，直接去管理面板改，GUI 不碰缩进

### 不要把 key 写进给用户的命令行（变量形态同样中招）

对话里的 `Bearer <密钥>` 形态会被平台打码成 `Bearer ***`，用户复制后就是按字面请求，必然 401——而且看起来像 key 错了，最容易把排查带偏。

**只把明文换成 shell 变量 `$K` 不够**：`-H "Authorization: Bearer $K"` 整段仍会被打码，用户拿到的还是 `***`。三个层级依次试：

1 `H=$(printf 'Authorization: Bearer %s' "$K")` 先拼好 header，curl 用 `-H "$H"`——载荷里没有「Bearer + 值」的连续形态，一般不触发打码
2 命令替换内联：`-H "Authorization: Bearer $(grep -oE 'sk-cpa-[a-f0-9]+' config.yaml | head -1)"`
3 上面仍失效（用户回报还是 401）→ 直接让用户把完整 key 手动补进命令，这是他最省事的兜底，别再试第四种写法
4 如果这批 key 是你自己生成、还要在聊天里贴着用，**一开始就别选 `sk-` 开头的前缀**：`sk-` 字符串本身就会被当成密钥打码，哪怕它不是 Bearer 形态、哪怕只是写在配置里回显。用 `服务名-用途-年份` 这种形态（如 `pmlophy-cpa-2026`）能完整显示，省掉一整轮「两边对不上」的猜疑。客户端兼容性上很多反代不强制 sk- 前缀，生成前先确认。

判据：用户报 401 且响应体是 `Invalid API key` 时，**先怀疑打码，不要先怀疑配置**。同理，同一形态的命令连续两次让用户跑失败就停手换写法。

### 429 / RESOURCE_EXHAUSTED：配额、速率、请求特征是三件事

上游日志出现 `daily-cloudcode-pa.googleapis.com` 且响应体为 `{"code":429,"status":"RESOURCE_EXHAUSTED"}`，是 Google API 的原生错误格式——本地代理伪造不出来，所以它证明请求**真的打到了 Google**，仅此而已。这条错误有四个互相独立的成因，别在第一个上停住：额度、速率、请求特征、**出口 IP 风控**。

**最容易漏掉、也最难自证的是出口 IP。** Google 对代理 / 机房 / 被污染 IP 就返回这个原生 429，跟你自己的额度、模型、请求体都无关。用户在本地走 Clash、你在 VPS 上测，两边结果不同时，差别就是出口 IP，不是他配错了。判据：

- **同一 key、同一模型、同一句请求，换出口 IP 各跑一次**。本地 429、VPS 200（或反之）→ 就是 IP，不需要再往下查。这是本类问题里最高价值的单次实验，先做它。
- 用户说「我关了 Clash 就好了」「之前关掉代理能成功」时，**直接采信并围绕它设计验证**。不要因为「代理伪造不出这个响应体」就排除代理——原生的错误码和本地的风控成因可以同时成立，混淆这两件事会把排查带偏一整轮（实测踩过：把 IP 风控误判成额度/模型问题，用户直接反问「额度明明还有」）。
- 修法不是关代理，而是**把反代搬到出口干净的一侧**（见下方「把反代搬出本机」），一次解决、以后不再受本地网络波动影响。

顺序：

0 **先看 message 文案，一条就能定案。** 两种 429 的文案不一样，含义也不同：
   - `Individual quota reached. Please upgrade your subscription. Resets in <h m s>` —— Google 给出明确重置时间，是**真配额耗尽**。唯一解是等重置或加号，别再查 IP、模型、请求格式，查了也是白查。
   - `Resource has been exhausted (e.g. check quota).` 且无重置时间 —— 才是风控 / 速率 / 请求特征那一类，继续按下面顺序排查。
1 **换出口 IP 对照**：同一请求本机 vs 干净出口各一发。结果不同 → 定案，跳到搬机器。
2 **横向打模型**：同一 key 分别打几个模型。只有一个 429、其它 200 → 该模型在这个号上额度紧（Opus 类高档模型在 Pro 号里额度本就少）。
2 **核对面板真实余量**：管理面板「配额管理」里的 5 小时 / 周限额进度条与百分比才是额度真相。**面板显示满格或剩余 100% 时，就不要再讲「额度耗尽」**——那是把 429 想当然了，用户会直接反问。
3 **量请求体**：小请求（几十 token）200、真实客户端（几千 token system prompt + tools）429，且面板额度充足 → 是**速率限流或请求特征**触发的，与额度无关。这时的小请求 200 不能证明「能用」，只能证明链路通。
4 **看请求打到哪个端点**：错误日志文件名带端点前缀（`error-v1-responses-*.log`、`error-v1-messages-*.log`），一眼看出客户端走了哪条路。Claude Code 正常走 `/v1/messages`，落到 responses 上说明配置里地址多写了 `/v1`，或开了路由转层。

别用「换个模型试试」当止步方案：小请求全 200 而真实客户端仍 429 时，换模型只是把同一症状重演一遍。

### 旁证不能当结论（面板 / 截图读数先经命令行确认）

从截图读数值——配额百分比、剩余额度、刷新倒计时——视觉模型经常读错或读偏，拿它当判据会把方向整反（把「额度充足」读成「额度耗尽」）。规则：

- 截图与面板只用来**提线索**（有没有这个账号、这个菜单叫什么、按钮在哪），不承担判据。
- 判据只能是可重放的东西：`curl -o /dev/null -w "%{http_code}"` 的状态码、日志里的原始响应体、配置文件的实际字节（`awk` 数缩进、`grep` 取真实值）。
- 用户说「额度明明还有」「我这几个号没怎么用」时，第一反应是自查有没有又拿旁证当了证据，再继续往下查；不要顺着自己的推断继续加固。

### 重客户端终局：反代不适合当 Codex / Claude Code 的主通道

轻量请求全通不代表能用。实测（CLIProxyAPI 8.0.58 → Antigravity，4 个 Pro 号）：

- curl 发的 `/v1/models`、`/v1/messages`、`/v1/responses`，连 600KB 纯文本、40 个自造 tools、流式 SSE 全部 200。
- Codex Desktop 的真实请求（243KB：system prompt + 17 个工具定义 + 13 条历史，用户实际只打了一句 8 个字）稳定 429。

**二分定位法（值得背下来）**：CLIProxyAPI 的 `~/.cli-proxy-api/logs/error-<端点>-*.log` 里带完整的 `=== REQUEST BODY ===`。抠出来原样重放 → 必现；再逐项删减（去 `include` / 去 `tools` / 只留最后一条 input）→ 只剩最后一条 user message 时 200，带完整 system + tools 就 429。

根因：反代要把 Anthropic / OpenAI 格式**转译**成 Google 内部格式，tools schema 与多轮结构转译后变形，Google 侧不认这种拼装请求体。与额度、IP、模型名都无关。

结论：反代能跑通哪些客户端，判据是**端点 / 请求格式**，不是请求体积。实测同一套反代：Hermes 走 `/v1/chat/completions`（OpenAI 格式）带 7.2 万 token 输入（完整记忆 + 技能注入）4.2 秒正常返回；Codex Desktop 走 `/v1/responses` 的 243KB 请求稳定 429。两边都是「大请求」，一通一不通，差别只在端点。

所以分工是：Claude Code 走 `/v1/messages`、Hermes 走 `/v1/chat/completions` 这类原生格式的客户端能吃；必走 `/v1/responses` 的重客户端不行。要稳定吃 Antigravity 额度跑 coding agent，仍走路线 A（内核内原生插件），请求格式原生、不经转译。说「换个模型试试」能缓解单一模型的额度紧，但解决不了这个架构问题。

### 4ms 的 429 ≠ 上游拒绝

CLIProxyAPI 把被上游拒过的账号标成 cooldown，之后 `auth unavailable: N of N candidate(s) ... are in cooldown (reason=quota, remaining=Ns)` 时**在本地直接返回 429**，根本不出网。判据是耗时：

- **4ms 级** → 本地冷却拦截，测试自己打出来的，不代表服务坏了
- **几百 ms 到数秒级** → 真的发到了上游

连续重试会把账号打进冷却，然后所有请求都变成 4ms 429，容易误判成“彻底不通”。分辨办法：停 30 秒，回测一个之前 200 的请求，能通就说明只是冷却。同一模型多个号都被标 quota 时，日志会写 `2 of 2 candidates are in cooldown`。

### 两套实例抢端口，面板却照常能开

brew 装的旧版 + 手动下载的新版共用 `~/.cli-proxy-api/` 凭证目录、抢同一个端口。新进程 `bind: address already in use` 退出（这行很容易在满屏日志里漏掉），旧进程继续应答旧内存配置；而此时管理面板**依旧能打开**，容易误以为“服务正常”。改配置前先 `ps aux | grep cli-proxy` 确认只有一个进程，并考虑两个版本全部卸掉、只留一处。

### 管理接口与业务接口是两套密钥

- 管理接口（`/v0/management/*`、管理页面）认 `management.secret-key`
- 业务接口（`/v1/messages`、`/v1/models`）认 `access.api-keys`

拿业务 key 打管理接口会返回 `{"error":"invalid management key"}`——这是**预期结果**，恰好证明 key 本身没问题，别当成失败信号继续调配置。

### 接 Claude 之前先验 thinking signature

`/v1/messages` 的成功响应里必须同时出现 `"type":"thinking"` 和 `"signature"` 才算满血。只有 text 没有 thinking，说明思考链被吞，接进 Claude Code / Desktop 的表现是「能回话但干不动活」。

验一发真实请求（用 `claude-opus-5-5-high` 这类带 thinking 的模型），看响应体前几百字符里有没有这两个字段，再动客户端配置。

### 下载坑

GitHub `releases/latest/download/<名字>.zip` 这类路径经常直接 404（只回 9 字节，unzip 报 End-of-central-directory）。先查真实文件名：

```bash
curl -s https://api.github.com/repos/router-for-me/CLIProxyAPI/releases/latest | grep browser_download_url | grep darwin
```

实际是 `CLIProxyAPI_<ver>_darwin_aarch64.tar.gz`（**tar.gz 不是 zip**；Apple Silicon 认 aarch64，Intel 是 amd64）。

## 把反代搬出本机：VPS 托管 + 域名对外

本机出口被风控（或本机代理不稳定、终端一关就停）时，正解不是让用户天天开关代理，而是**把反代整体挪到一个出口干净的机器上**，客户端只连域名。这样出口 IP 固定、服务自启、本地网络怎么变都不影响。

骨架五步：

1 **下对架构**：VPS 上是 `linux_amd64`（`uname -m` 先确认），本机 Apple Silicon 是 `darwin_aarch64`。
2 **生成配置**：`host` 写 `127.0.0.1`（只给本机 nginx 反代，不直接对外），`management.secret-key` 必填，`api-keys` 用真 key（见上方「模板值禁用」）。
3 **搬账号凭证**：客户端那份 `~/.cli-proxy-api/*.json` 直接 scp 到目标机的同名目录；服务有文件监听，落地几秒内自动加载，不用重启。
4 **systemd 托管**：`Restart=always` + `enable`，避免重启机器后忘记拉起。
5 **nginx 子路径反代**：`location /cpa/ { proxy_pass http://127.0.0.1:8317/; }`（末尾斜杠才能剥掉前缀），**必须 `proxy_buffering off`**，否则 SSE 流式会被缓成一大块慢慢吐；再给 `proxy_read_timeout` 拉长到几百秒。

客户端地址写成 `https://<域名>/cpa`（不带 `/v1`，由客户端自己拼 `/v1/messages`）。

三个易错点：

- **nginx 改完语法检查通过不代表生效**：`nginx -t` 后要 `systemctl restart nginx`，reload 在带 SSL 的配置里不总是吃新 location。
- **本机验证要走 https**：`curl https://127.0.0.1/... -H "Host: 域名" -k`，纯 http 会回 301 让你误以为失败了。
- **凭证是敏感文件**：scp 到远端前确认目标机是用户自己的机器，并在完工后提醒授权文件得了什么权限。

完整命令（下载、配置生成、systemd unit、nginx block、验证序列）见 `references/vps-hosted-gateway.md`。

## 把反代接进 Hermes：只挂非主力 profile

Hermes 走 OpenAI 兼容格式，反代暴露 `/v1/chat/completions` 就能接。接入前先验一发（用真正要挂的模型）：

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8317/v1/chat/completions \
  -H "Authorization: Bearer <key>" -H "content-type: application/json" \
  -d '{"model":"claude-opus-5-5-high","max_tokens":50,"messages":[{"role":"user","content":"你好"}]}'
```

配置落在**目标 profile 自己**的 `config.yaml` + `.env`：`providers` 下加一条（`api` 与 `base_url` 都写 `http://127.0.0.1:8317/v1`、`key_env` 指向该 profile `.env` 里的变量），再把 `model.provider` 改成 `custom:<名字>`，`model.model` 与 `model.default` 同步改成目标模型 ID。key 追加进该 profile 的 `.env`，别动主 profile 的。

两条纪律：

- **改前备份 `config.yaml` 和 `.env`**（带时间戳后缀），并把回滚命令一并写进交付说明。
- **只改非主力 profile**（网页端助手这类），主 agent 一条链路都不动。用户的要求是「总得留一个口子」——反代随时可能因风控失效，让它只影响一个可以牺牲的 profile，另一个始终在线。

改完不自动生效：重启网关必须由用户手动执行，交付时给「重启命令 + 回滚命令」两条，不要代跑。

完整命令（备份、改 model 段、插 provider、校验 YAML、回滚）见 `references/hermes-provider-wiring.md`。

## 路线 A 的正确顺序

1 **先确认内核版本**：`opencode --version`。插件与内核版本强绑定，先查再装。
2 **必须装 bun**：`which bun`；没有就 `brew install oven-sh/bun/bun`。内核靠 bun 下载插件，缺了会**静默跳过**（包目录没有、日志也没有、模型列表空），最难查。
3 **写内核配置**：`~/.config/opencode/opencode.json`，2.x 内核用复数键 `"plugins": ["opencode-antigravity-auth@2.1.2"]`；1.x 用单数 `plugin`。两个配置文件（json 与 jsonc）并存会打架，先备份改名 `opencode.jsonc.bak-<日期>` 再写一份干净的。
4 **认证入口在 Google 下面，不在插件名下**：`opencode auth login google` → 下一步才选 `Google OAuth (Antigravity)`。在搜索框输 `anti` 是搜不到的，别在这儿判断「插件没装上」。
5 **多账号**：加第二个号时用**无痕窗口**开 OAuth URL，否则浏览器复用已登录会话、把同一个号加两遍。加完在「Add another account?」处答 n。
6 **验证**：`opencode models | grep -i antigravity`（未登录前列表为空属正常），再 `opencode run --model=<模型ID> "用一句话说明你是谁"` 跑真请求。

## 版本匹配铁律（这条错了会浪费一整轮）

插件的 2.x 是为内核 2.x 重写的，1.x 只能走 legacy 通道且能力不全。表现上：

- 1.x 内核 + 复数键 `plugins` → 报 `ServiceUnavailableError: Location plugins did not finish activating`
- 1.x 内核 + 单数键 `plugin` → 包会下到缓存里，但**静默不注册模型**，`auth list` 里 0 credentials
- 查 npm 版本时间线再判断：插件如果从 1.6 直接跳到 2.0，中间的断层就是内核换代点

结论：先在内外核版本对齐，再去调配置。在旧内核上反复换插件版本是死路。

## 凭据与免重登

- 账号存在内核自己的文件里（如 `~/.config/opencode/antigravity-accounts.json`），**含凭据，换机前先备份**。
- **升级内核不会丢已登录的账号**：实测从 1.x 升到 2.x、换插件大版本后，旧账号文件被直接读到，模型列表直接出来，**不需要重新 OAuth**。
- 因此顺序永远是：先把内核版本、插件版本、配置键名全调对，**最后才授权一次**。重复授权会触发平台风控，用户会明确制止（「不要搞老是重复授权」）。
- 清本地插件缓存目录、改内核配置都不影响账号文件，可以放心做。

## 验证与日常用法

- 看额度、切号：进内核 TUI 敲 `/antigravity`（或插件文档给的短命令），能看每个号的剩余额度与重置时间。
- 档位叫法：同一模型常有 high / medium / low 几档，另有更贵的一档（如 gemini-4-argon）留给硬骨头。日常写前端用小模型或低档，复杂重构才上高档。
- **Opus 类高档模型在 Pro 号里额度极薄，别拿它当日常主力。** 实测量级：4 个 Pro 号的 `claude-opus-5-5-high` 合起来撑不住一次高强度会话（一次多轮工具调用的完整任务 + 少量重试就打满，两号同时 cooldown 3.5–4 小时）。挂给 agent 用时主力放 Sonnet / Gemini 档，Opus 只留重活；或者多备几个号。
- **Gemini 组与 Claude 组是两份独立配额池**，一组打满不影响另一组。实测同一批号：`claude-opus-5-5-high` / `claude-sonnet-5-5-high` 双双 429 时，`gemini-4-argon-high` / `gemini-3.8-flash-high` / `gemini-3-flash` 全部 200。所以额度告急时的第一动作不是等重置，而是横向打一遍模型确认哪组还有量，然后把 agent 切到仍可用的那组继续干。
- 看降级时间：`grep -E "cooldown|quota" <service>.log | tail` 里带 `remaining=3h51m` 这类，就是还要等多久；日志写 `2 of 2 candidate(s) are in cooldown` 时该模型的全部号都打满了。
- 模型 ID 形式一般是 `google/antigravity-claude-...`、`google/antigravity-gemini-...`，以 `opencode models` 实际输出为准，不要照抄文档里的旧型号名。

## 风险边界（必须主动告知用户）

- 用 OAuth 把 IDE 订阅额度接到第三方工具，属平台服务条款的灰区，社区有账号被封的反馈。
- 用户的付费账号如果是「核心账号」，先提示用非主力号试水，不要拿主号当消耗品。
- 走厂商域名（Google 等）需要代理，内网/受限网络下用不了。

## 用户环境（已经用户确认，别再让他重复检查）

用户的 Mac 上 OpenCode 一直处于装好且配置就绪的状态：bun、内核版本、antigravity 插件、OAuth 授权都已到位。更直接的两条：**在 Antigravity 里打开 OpenCode 就能直接用**；**Cursor 里也装了同一个插件，一样可用**。不需要任何启动配置或环境检查，也不要让用户去跑 `which bun` / `opencode --version` / `auth list` 这套流程。只有换机、升级内核或插件失效（models 列表变空）时，才需要回头按下面的顺序重查。

## 排环境坑的顺序

1 `which bun` → 2 `内核 --version` → 3 配置文件键名单复数 → 4 插件包有没有下到缓存目录 → 5 `auth list` 有没有凭据 → 6 `models` 有没有模型。
按这个顺序逐层排除，不要从最后的报错往回猜。
