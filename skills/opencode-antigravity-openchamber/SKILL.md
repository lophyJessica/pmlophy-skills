---
name: opencode-antigravity-openchamber
description: Use when 接反重力额度进 OpenCode/OpenChamber 或插件不加载。
---

# OpenCode + 反重力额度 + OpenChamber

## 三个东西别混

| 名字 | 是什么 | 不带什么 |
|---|---|---|
| OpenChamber | OpenCode 的图形界面（桌面版 / VS Code 扩展 / 网页 PWA）。反重力里装的是 VS Code 扩展（FedaykinDev.openchamber，官方仓库 openchamber/openchamber，MIT） | 不带模型、不带账号 |
| OpenCode | 真正的 agent 内核，模型与凭据都在它这里 | 不自带任何模型 |
| opencode-antigravity-auth | OpenCode 插件，用 Google 账号 OAuth 登录反重力，把反重力额度变成 OpenCode 模型 | 版本敏感，不是开箱即用 |

用户常以为「反重力里插件装好了」= 通了。不是——扩展只是界面，必须本地有 opencode 且登录过，否则打开是空的。

## 版本矩阵（最容易踩死的地方）

- 插件 **2.x（2.0.0 / 2.1.x）对标 OpenCode 2.x**，README 明写 `Requires OpenCode 2.1.2+`。
- 插件 **1.6.x 及更早** 面向 OpenCode 1.x。npm 上 1.6.0（2026-02）之后直接跳到 2.0.0（2026-10）。
- 官方说 OpenCode 1.18.29+ 仍支持，但那是「兼容通道」：实测 **OAuth 能登、模型注册不生效**——`opencode models` 无 antigravity、日志里连插件记录都没有。
- **`opencode auth list` 为空不能单独当故障证据**：插件是直接读 `~/.config/opencode/antigravity-accounts.json` 的，不走 OpenCode 的 auth 体系。实测在完全正常的状态下（内核 2.2.5 + 插件 2.1.2，`opencode models` 能列出全部 antigravity 模型）它照样回 `No authenticated integrations`。判定顺序永远是先看 `opencode models` 里有没有 antigravity 那一批，有就说明凭据通着，不要因此去重新授权（重复登录 Google OAuth 有风控风险）。
- 结论：**内核 1.x 配 2.x 或 1.6 插件都调不出模型**，别在旧内核上耗，直接升 2.x。

## 安装顺序（照做，别跳）

1. **装 bun**。OpenCode 用 bun 下载/运行插件，没有它插件会被静默跳过（`bun not found` 是根因线索）。`brew install oven-sh/bun/bun`，装完重开终端。
2. **装 OpenCode**。V2 用 `brew install opencode`；V1 是 `brew install anomalyco/tap/opencode`。装 V2 前先 `brew uninstall anomalyco/tap/opencode`。
3. **`opencode --version`** 确认 2.x 才配插件 2.1.x。
4. **写配置** `~/.config/opencode/opencode.json`：2.x 用复数键 `"plugins": ["opencode-antigravity-auth@2.1.2"]`；1.x 用单数 `"plugin"`。`opencode.json` 与 `opencode.jsonc` 并存会打架，只留一个，另一个改名 `.bak`。
5. **最后才授权一次**（见下节）。

## 授权：用户明确要求不反复做

用户原话：「不要搞老是重复授权，会被风控的，尽可能排除好了后，再授权 Google」。Google OAuth 反复登录会触发风控、有封号风险。所以：

- 先把内核版本、插件版本、bun、配置全部弄对，**验证到只剩授权这一步**再动手登。
- 凭据文件 `~/.config/opencode/antigravity-accounts.json`（结构：version / accounts / activeIndex / activeIndexByFamily）。**升级内核前先备份** `cp` 到 `~/antigravity-accounts.backup.json`，升级后插件往往直接读旧文件，一次不用重登。
- 登录是 `opencode auth login google`（不是搜 `anti`），下一级选 **Google OAuth (Antigravity)**；Project ID 留空回车。
- 加第二个号必须在**无痕窗口**开 OAuth URL，否则 Google 复用会话，同一个号被加两遍。
- 自动回调等不到时，把地址栏整条 `http://localhost:51121/oauth-callback?code=...` 粘回终端；只粘 `code=` 后那段也行。
- `Add another account? (y/n)` 加到想要的号一定答 **n**。

## 反代路线（另一条，非必须）

Antigravity-Manager（lbjlaq，Tauri）在 `127.0.0.1:8045` 暴露 OpenAI / Anthropic 兼容接口，多账号轮询。OpenCode 里把 provider 的 `baseURL` 指过去。

选型：只在 OpenCode/OpenChamber 用 → 插件路线（少一层好排查）；要让 Hermes / Cursor 也吃这份额度 → 反代路线。用户对反代有负面印象（clipro 不稳定）。

排查点：`lsof -i :8045` 看进程；`curl -s http://127.0.0.1:8045/v1/models -H "Authorization: Bearer ***"` 返 `Proxy service is currently disabled` = 应用里的开关没打开，不是挂了。

## 诊断命令（按序，别乱试）

```
bun -v
which opencode; opencode --version
ls ~/.cache/opencode/packages/
opencode auth list
opencode models | grep -iE "antigravity|google"
grep -iE "antigravity|plugin|provider" ~/.local/share/opencode/log/opencode.log | tail -25
```

判读：包在缓存里 ≠ 插件被加载。日志里一条插件记录都没有 = 内核没执行它，此时调配置无用，只能换内核代际。

反过来，**`ls ~/.cache/opencode/packages/` 为空也不代表插件没装**——2.x 把插件装到 `~/.cache/opencode/npm/<包名>@<版本>/<哈希>/node_modules/...`，日志里 `msg="loading plugin" id=opencode-antigravity-auth@2.1.2 entrypoint=file://...` 那行才是真凭据。别拿空目录下「插件没装」的结论。

## 模型怎么选：只认 `antigravity-` 前缀（2026-11-04 实测）

`opencode models` 会把两类 Google 模型混在同一个 `google/` 命名空间下报出来，用户看到一长串分不清哪个能用：

- **`google/antigravity-*`** = 走反重力 OAuth，用账号自己的 Pro 额度，**只有这批能跑**。
- **`google/gemini-*`、`google/gemma-*`、`google/deep-research-*`** = 直连 Google API，要自备 `GOOGLE_GENERATIVE_AI_API_KEY`。选这批发消息会报 `AI.Error: Method doesn't allow unregistered callers (callers without established identity). Please use API Key or other form of API consumer identity to call this API.`——**这不是插件坏了、也不是凭据掉了**，是选错档。判据就一句：报错里出现 `unregistered callers` 或 `Please use API Key`，先去查当前会话选的模型有没有 antigravity 前缀。

antigravity 前缀那一批的实际构成（2026-11 两个 Pro 号）：claude-opus-5-5 / claude-sonnet-5-5 各 high·medium·low 三档，gemini-3.8-flash 三档，gemini-4-argon 三档，gemini-3.5-flash-lite，gpt-oss-120b-medium。

分派建议：批量扫描/静态提取用 `antigravity-gemini-3.8-flash-high`（长上下文、省额度）；要动推理的口径判断用 `antigravity-claude-opus-5-5-high`；旗舰长文用 `antigravity-gemini-4-argon-high`。

另有两条日志会陪着一起出现，都不是账号问题：`/api/provider` 返 503、`Failed to fetch models.dev` 超时 10s，是面板拉 provider 与模型库元数据失败，重开 opencode 进程即可。

## 结果形态

登录成功后模型名为 `google/antigravity-claude-...`、`google/antigravity-gemini-...`。登录前 `opencode models` 只有 opencode 免费模型是正常的——反重力模型登录后才从账号里拉出来。新模型能否出现取决于插件是否跟上新 ID，跟不上就在配置里手写模型定义。
