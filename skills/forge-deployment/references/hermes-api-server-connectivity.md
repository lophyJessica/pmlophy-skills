# Hermes API Server：Web 应用连接手册

## 架构

```
浏览器 (http://127.0.0.1:5188)
  → https://pmlophy.com/api-server/v1/...
  → nginx (SSL + CORS + 头转换)
  → http://127.0.0.1:8642 (Hermes API Server)
```

## 关键陷阱

### 1. /v1/models 和 /v1/chat/completions 鉴权不同

| 端点 | 期望的鉴权头 | 说明 |
|---|---|---|
| /v1/chat/completions | `Authorization: ***` | Bearer token 格式 |
| /v1/models | `API_SERVER_KEY: <key>` | 直接传 key，不用 Bearer 前缀 |

如果前端用 `/v1/models` 做健康检查（`checkHermesConnection()`），nginx 必须同时注入两种头。

### 2. Chrome 阻止 HTTP 的 Authorization 头

Chrome 安全策略禁止向非 localhost 的 HTTP 目标发送 `Authorization` 头。
请求表面返回 403，实际是浏览器在发送前就剥离了该头。

**症状**：curl 正常，浏览器 403。

**解法 A**：使用自定义头（如 `X-Hermes-Key`），Chrome 不拦截自定义头。
**解法 B**：使用 HTTPS 代理路径。

### 2b. CORS 预检白名单必须包含自定义头

浏览器在发送带自定义头的跨域请求前会先发 OPTIONS 预检。
nginx 的 `Access-Control-Allow-Headers` 必须列出该自定义头，否则预检失败，
实际请求被浏览器阻止（`net::ERR_FAILED`），而不是真正的 HTTP 403。

**症状**：Console 显示
`Access to fetch at '...' has been blocked by CORS policy: Request header field x-hermes-key is not allowed by Access-Control-Allow-Headers in preflight response.`

**修复**：`add_header Access-Control-Allow-Headers "... , x-hermes-key" always;`

无论独立端口还是域名路径，CORS 白名单都要包含实际使用的自定义头名。
nginx 会把客户端发来的头名原样传下去；`$http_` 前缀变量则始终使用
**全小写 + 下划线**（`$http_x_hermes_key`），两者不冲突。

### 3. Mac 本地代理拦截

用户 Mac 运行 Clash/V2Ray（127.0.0.1:7897），HTTP 请求会被代理接管。
直接 IP + HTTP 连接可能被代理拒绝，返回 403。

**解法**：使用 `https://pmlophy.com/api-server/`，经 Cloudflare + nginx SSL 代理，
不会被本地代理拦截。

### 4. VPS IP 是动态的

本会话中 IP 从 192.220.33.25 变为 192.220.14.245。
不要在任何 `.env.local` 中硬编码 IP；优先使用域名路径。

## nginx 配置

### 独立端口（绕过 Cloudflare，仅限内部使用）

```nginx
# /etc/nginx/conf.d/jarvis-map.conf（http 块内）
map $http_authorization $bearer_token {
    "~^Bearer (.+)$" $1;
    default "";
}
map $http_x_hermes_key $api_server_key {
    ""      $bearer_token;
    default $http_x_hermes_key;
}
map $http_x_hermes_key $auth_header {
    ""      $http_authorization;
    default "Bearer $http_x_hermes_key";
}

# /etc/nginx/sites-enabled/jarvis-api
server {
    listen 8643;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8642/;
        proxy_http_version 1.1;
        proxy_set_header Authorization $auth_header;
        proxy_set_header API_SERVER_KEY $api_server_key;
        proxy_set_header Host $host;
        proxy_read_timeout 120s;
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
        if ($request_method = OPTIONS) { return 204; }
    }
}
```

### 域名路径（通过 Cloudflare + HTTPS）

```nginx
# /etc/nginx/sites-enabled/pmlophy.com 内
location /api-server/ {
    proxy_pass http://127.0.0.1:8642/;
    proxy_set_header Authorization $auth_header;
    proxy_set_header API_SERVER_KEY $api_server_key;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 120s;
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "X-Hermes-Key, Content-Type" always;
    if ($request_method = OPTIONS) { return 204; }
}
```

注意：Cloudflare WAF 会拦截带 `Authorization` 头的请求，走域名路径时前端必须使用 `X-Hermes-Key` 自定义头。

## 前端 .env.local

```
# 方案 A：HTTPS 域名（推荐，绕过本地代理 + Chrome 安全策略）
VITE_HERMES_API_URL=https://pmlophy.com/api-server

# 方案 B：直接 HTTP（仅当 VPS IP 正确且代理已绕过时）
# VITE_HERMES_API_URL=http://192.220.14.245:8643
```

## hermes.ts 请求头

```ts
// 走域名路径：使用 X-Hermes-Key（Cloudflare 不拦截自定义头）
headers: { 'Content-Type': 'application/json', 'X-Hermes-Key': apiKey }

// 走直连端口：可使用 Authorization（Chrome 会拦截，仅 curl/内部可用）
// headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` }
```

### 5. nginx 不默认转发 Authorization 头

`proxy_set_header Authorization $http_authorization;` 必须显式设置。nginx 不会自动转发 `Authorization` 头，缺失则上行请求永久 401。

### 6. Chrome JS 缓存阻止 API 路径更新

如果修改了已编译 JS 中的 API 路径（例如 `/api-server` → `/hermes`），Chrome 会缓存旧 JS，导致浏览器仍向后端访问已经废弃的旧路径。

**症状**：nginx 日志中请求仍命中旧路径，与已更新的 JS 不一致；ctrl+shift+R 可能无效。

**修复**：重命名 JS 文件（如 `index.js` → `index-v2.js`）并同步更新 `index.html`，强制浏览器下载新文件。

### 7. Cloudflare WAF 按路径拦截 POST

Cloudflare WAF 可能针对特定 URL 路径拦截 POST 请求，即使 nginx 的配置相同、请求头相同。本会话中 `/api-server/` 的 POST 持续返回 403（0 字节），而新路径 `/hermes/` 在完全相同的 nginx 代理配置下直接返回 200。如果请求已达到 nginx（access.log 可见）但仍然被拒绝，可尝试更换 API 路径名称。

### 8. map 变量可被直接引用替代

`map` 变量在通过 Cloudflare 代理时可能出现无法可靠解析的问题。当 `$http_x_hermes_key` 在 nginx 请求中完全可用时，直接以内联方式使用该变量比通过多层 map 重写更可靠：

```nginx
# Simpler, more reliable than map:
proxy_set_header Authorization "Bearer $http_x_hermes_key";
proxy_set_header API_SERVER_KEY $http_x_hermes_key;
```

1. `curl http://127.0.0.1:8642/v1/models -H 'Authorization: ***→ 200？`
2. `curl http://192.220.14.245:8643/v1/models -H 'Authorization: ***→ 200？`
3. 浏览器 Network 标签 → 请求的 Remote Address 是否被代理（127.0.0.1:7897）？
4. 浏览器请求头中 Authorization 是否存在？
5. `tail -5 /var/log/nginx/access.log` → 请求到达 nginx 了吗？

### 9. crypto.randomUUID 仅安全上下文可用

`crypto.randomUUID()` 仅在 HTTPS 或 localhost 下可用。部署到 HTTP 非 localhost IP 时，
浏览器抛出 `TypeError: crypto.randomUUID is not a function`，导致前端完全无法启动。

**修复**：构建后往 JS bundle 头部注入 polyfill：

```js
if(!crypto.randomUUID){crypto.randomUUID=function(){return"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,function(e){var t=16*Math.random()|0;return("x"===e?t:3&t|8).toString(16)})}}
```

### 10. 独立 HTTP 端口完全绕过 Cloudflare（最终可用方案）

当 Cloudflare WAF 拦截浏览器 POST、子域名遇到 HSTS 证书冲突、域名路径更换后仍被拦，
将前端和 API 部署在同一个 nginx server block 的非标准 HTTP 端口上，同域无 CORS：

```nginx
server {
    listen 8080;
    server_name _;
    location /hermes/ {
        proxy_pass http://127.0.0.1:8642/;
        proxy_http_version 1.1;
        proxy_set_header Authorization "Bearer <key>";
        proxy_set_header API_SERVER_KEY <key>;
        proxy_set_header Host $host;
        proxy_read_timeout 120s;
    }
    location / {
        root /var/www/pmlophy.com/jarvis;
        try_files $uri $uri/ /index.html;
    }
}
```

### 11. Mac 系统代理绕过：优先系统设置而非代理客户端

即使用户关闭了代理客户端（Clash/V2Ray），Mac 系统设置中的代理可能仍然启用。
仅关闭客户端图标或修改客户端规则是不够的。

**两步确认**：
1. 系统设置 → 网络 → Wi-Fi → 详细信息 → 代理 → 所有协议全部取消勾选
2. 或在"绕过代理设置的主机与域"输入框中追加 VPS IP：`,192.220.14.245`

浏览器 F12 → Network → 403 请求的 Remote Address 若显示 127.0.0.1:7897，
说明代理仍在劫持 Chrome。以上两步必须都完成。
