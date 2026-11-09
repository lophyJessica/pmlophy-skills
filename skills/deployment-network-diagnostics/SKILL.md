---
name: deployment-network-diagnostics
description: Diagnose connectivity issues between web frontends and VPS APIs — nginx/Cloudflare/Chrome/path pitfalls and the mandatory diagnostic-matrix-first approach.
---

# Network Diagnostic Matrix

When a web frontend can't reach the API, draw the full chain first:

```
Browser → System Proxy → Cloudflare → nginx → API Server
```

Eliminate each layer with one test before changing any config:

| Layer | Test |
|-------|------|
| API | `curl http://127.0.0.1:PORT/endpoint` from VPS |
| nginx | curl through public IP:PORT |
| Cloudflare | curl through domain vs IP (diff = Cloudflare issue) |
| Proxy | Chrome DevTools Network → `Remote Address` → `127.0.0.1` = proxy |
| Browser | Clear cache + incognito window |
| 客户端设备 VPN/代理 | 设备级 VPN/代理开启时，到 Cloudflare 的连接可能被代理重置（见下方 0806 实锤） |

**Rule:** Never modify nginx config >3 times without checking the proxy and browser layers first.

## 客户端持续 ERR_CONNECTION_CLOSED 但服务端全绿 → 先查设备 VPN/代理（2026-08-06 实锤）

现象：用户手机**多个入口全挂**（APK + 系统浏览器 + Chrome 都 `ERR_CONNECTION_CLOSED`，关掉重开重试多次仍一样），但同一时刻 VPS 源站 200（`curl -k -H "Host: pmlophy.com" https://127.0.0.1/`）且公网连测 5 次全 200。服务端完全正常，问题在手机端。

排查顺序（这次 20 分钟内锁定）：
1. **服务端自证**：本机带 Host curl（`curl -s -o /dev/null -w "%{http_code}" -H "Host: pmlophy.com" https://127.0.0.1/jarvis-voice/`）+ 公网循环连测 5 次 → 全绿 = 排除 VPS/nginx/Cloudflare
2. **区分范围**：换一个客户端测（Mac 浏览器）——Mac 通 + 手机挂 = 手机独有问题
3. **切网络**：WiFi ↔ 流量切换（排除运营商/路由器）
4. **查设备 VPN/代理**：根因是手机开着 VPN/代理 → 代理节点到 Cloudflare 的连接被重置（数据中心 IP 被 CF 拒/TLS 指纹问题）→ 关闭 VPN 即恢复。**VPN 代理会拦代理网络自己**，这是最隐蔽的一层——诊断矩阵里"System Proxy"层不只是桌面浏览器代理，还包括手机设备级 VPN。

## "之前能用现在不能用" — 先查官方文档参数，再怀疑基础设施（用户两次批评"武断太多"后的铁律）

当服务突然连不上（WebSocket/API 握手失败），**不要先怀疑代理/Tailscale/地域限制**——那是 0803 绕了 2 小时的方向（实际根因是百度 WS 漏了 `?sn=` 参数）。顺序：

1. **先查官方文档的连接地址/参数示例**——很多 API 要求 URL 带必填参数（百度实时语音识别 `wss://vop.baidu.com/realtime_asr?sn=<随机串>`，不带 sn 返回 HTTP 200 空响应而非 101 升级，所有库/所有网络环境表现一致）
2. **两边同时"坏"= 请求本身缺东西**：Mac（国内）和 VPS（海外）同时连不上，恰恰排除地域限制假说，指向协议/参数缺失
3. **用 curl 看响应头特征**：`HTTP/2 200 + content-length:0`（缺 sn 的特征）vs 真实拒绝（403/451）
4. 换库测试（aiohttp/websockets/websocket-client 都试）——**如果所有库同一错误码，是请求/服务端问题，不是库问题**；只有单库出错才是库兼容问题
5. 最后才检查代理/DNS/Tailscale/路由（`ip route` 看默认路由、`resolvectl status` 看 DNS 接管）

**红线（用户原话）**：不要武断下结论、不要每轮让用户"再说一次/再测一下"当测试员——先自证（合成请求跑通链路）再请用户验证，调试日志打全让用户说一次就拿全证据链。

## nginx Pitfalls

1. `systemctl reload` → does NOT clear worker caches. Use `restart` for config changes.
2. `Authorization` header → nginx drops it by default. Must `proxy_set_header Authorization $http_authorization;`
3. `map` directive → must be in `http{}` block (in `conf.d/`), NOT inside `server{}`
4. Hermes needs BOTH `Authorization: Bearer <key>` and `API_SERVER_KEY <key>` set on proxy
5. **CORS preflight 三种症状别混淆**（2026-08-04 APK 跨域实锤）：
   - `OPTIONS → 401` = auth_request 拦截预检（预检不带 Authorization）→ 该 location 加 `if ($request_method = OPTIONS) { return 204; }` 放行预检
   - `OPTIONS → 204 但日志里没有后续 GET` = 预检通过了但浏览器判定 CORS 头缺项拦截真实请求 → `Access-Control-Allow-Headers` 缺 `authorization`（前端带 Bearer token 时必查此项）
   - `OPTIONS → 204 + GET 正常` = CORS 没问题，查后端
   诊断法：`curl -i -X OPTIONS <url> -H "Origin: https://localhost" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: authorization"` 看响应头；**每个带 auth 的 location 逐个 grep Allow-Headers 是否含 authorization，不能只修一个**

## Chrome Quirks

- Blocks `Authorization` header on HTTP to non-localhost → use custom header or HTTPS
- `crypto.randomUUID()` → only available in secure contexts (HTTPS/localhost)
- Self-signed certs → HSTS policy includes subdomains, blocks them

## Cloudflare WAF

- Browser POST + `sec-fetch-*` headers → 403. curl same request → 200.
- Fix: strip `Origin` header in nginx: `proxy_set_header Origin "";`
- Alternative: DNS-only (gray cloud) subdomain bypasses CDN

## Deployment Checklist

1. Change HTML asset paths from absolute to relative — **BOTH `href=` and `src=`**: `sed -i 's|href="/assets/|href="./assets/|g; s|src="/assets/|src="./assets/|g' index.html`. Missing `href=` causes CSS 404 (file returns 162 bytes, all styles lost).
2. Fix API path in built JS with sed (`/api-server` or `/hermes` → `/p/jarvis`)
3. Copy stable CSS from working build if layout broke
4. Version-bust JS filename on each deploy to bypass browser cache
5. Verify with Chrome DevTools → Network → disable cache → check Remote Address

## Vite 子目录部署：JS 内部资源绝对路径坑（2026-08 两次实锤）

**现象**：Vite 打包的 JS 里若写死绝对根路径资源（`new Audio("/robin-thinking.mp3")`、常量 `BA="/robin-avatar.png"`），部署到子目录（如 `/jarvis-voice/`）后浏览器/APK 请求的是**站点根目录** → **404**，资源不显示（头像空白/提示音不响）。

**排查顺序（一次锁定）**：
1. grep 线上 bundle 找资源引用：`python3 -c "js=open('assets/index-*.js').read(); print(js[js.find('robin-avatar')-40:js.find('robin-avatar')+60])"` → 看是 `/xxx`（根）还是 `./xxx`（相对）
2. 对比两路径：`curl -s -o /dev/null -w "%{http_code}" https://pmlophy.com/robin-avatar.png`（JS 引用路径，期望 404）vs `.../jarvis-voice/robin-avatar.png`（实际位置，200）→ 实锤
3. **注意和 Cloudflare 缓存 404 叠加**：无参数 404 可能是"真 404"也可能是"CF 缓存了 404"——**带 `?v=$(date +%s)` 测源站真相**

**修复两条路**：
- **快**：把资源复制到站点根目录匹配 JS 引用（`cp jarvis-voice/robin-avatar.png /var/www/pmlophy.com/robin-avatar.png`）——但根目录文件会被下次部署覆盖，且是补丁不是根治
- **根治**：前端指令要求 JS 内资源用**相对路径**（不带前导斜杠）或 Vite `base` 配置，让子目录部署自然解析；**静态资源放 `app/public/` 打进 zip**（见下）

## Cloudflare 缓存 404（2026-08 两次实锤）

**现象**：源站有文件（`ls` 确认存在）但 `curl` 无参数访问 **404**，带参数 `?v=1` 却 **200**——Cloudflare 缓存了**过去的 404 响应**（文件曾缺失时被 CF 缓存，补上文件后 CF 仍回旧 404）。

**诊断铁律**：任何"源站有文件但线上 404"的怀疑，**先带时间戳参数测**（`curl "...?v=$(date +%s)"`）——200 = CF 缓存 404；仍 404 = 真路径问题。

**修复**：
1. Cloudflare 控制台 → Caching → Purge Everything（全站清，1 分钟，用户操作）
2. 或前端/资源改新文件名（version-bust，新 URL 天然无旧缓存）
3. 根治：给资源响应加 `Cache-Control: no-store`（jarvis-tts 曾因 Etag 无 Cache-Control 导致浏览器缓存旧音频，加 `no-store, no-cache, must-revalidate` 解决）

## 部署 zip 覆盖源站静态资源（2026-08-06 实锤）

**现象**：v156 部署后源站 `robin-avatar-sm.png` 文件消失（curl 带参数 200 但 `ls` 无文件）——`deploy-all.sh` 解压 zip **覆盖整个部署目录**，zip 里没有的旧静态文件被清掉，只剩 Cloudflare 缓存顶着，缓存一过期就 404。

**铁律**：
1. **前端 zip 打包必须包含静态资源**（`app/public/` 下的 png/mp3 等，`zip -rq` 全量打，不挑文件）——v157 把菲儿图打进 `public/` 后部署不再丢
2. 部署后**验证源站文件存在**（`ls -la` 部署目录的静态资源），不能只看"部署成功"日志或 curl 200（可能吃 CF 缓存）
3. 部署脚本（deploy-all.sh）若解压覆盖，考虑保护非 zip 管理的文件（或明确约定 zip 全量自包含）
