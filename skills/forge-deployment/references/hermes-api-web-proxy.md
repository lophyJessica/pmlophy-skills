# Hermes API Server — nginx 反向代理 + CORS（独立 Web 控制台接入）

当 React/Vite 前端（如 Jarvis）运行在 Mac 浏览器，需要跨域访问 VPS 上的 Hermes API Server 时，以下模式绕过 Cloudflare CDN 和 CORS 限制。

---

## 适用场景

- 前端运行于 `http://localhost:XXXX`
- Hermes API Server 监听 VPS `0.0.0.0:8642`
- 前端通过 JS `fetch()` 调用 API
- 浏览器执行 CORS 预检 (OPTIONS)

## 认证要求

Hermes API Server 要求每请求携带 `Authorization: Bearer <API_SERVER_KEY>`。此外，`/v1/models` 健康检查接口不接受 `Authorization: Bearer`，必须额外设置 `API_SERVER_KEY` 头为裸 token 值。nginx 需要同时处理两种认证。

Key 在 VPS `.env` 中以 `API_SERVER_KEY=...` 格式存储。

## 方案：独立端口 nginx 监听，绕过 Cloudflare

Cloudflare 代理（橙色云朵）会拦截 `Authorization` 头和某些 POST 请求返回 403。解决方案是在 nginx 新增一个独立 `listen` 端口，不走 Cloudflare CDN。

### 1. nginx `map` 指令（放在 `conf.d/` 中以进入 `http` 块）

`map` 必须在 `http` 块中，不能在 `server` 块。在 `if` 中修改 `proxy_set_header` 是 nginx 常见反模式。

```nginx
# /etc/nginx/conf.d/jarvis-map.conf

# 从 Authorization: Bearer <token> 提取裸 token
map $http_authorization $bearer_token {
    "~^Bearer (.+)$" $1;
    default "";
}

# API_SERVER_KEY：同时从 X-Hermes-Key 或 Bearer token 提供
map $http_x_hermes_key $api_server_key {
    ""      $bearer_token;
    default $http_x_hermes_key;
}

# Authorization 头：若客户端发的是 X-Hermes-Key，则构造完整 Bearer 头
map $http_x_hermes_key $auth_header {
    ""      $http_authorization;
    default "Bearer $http_x_hermes_key";
}
```

### 2. 独立 server 块（放在 `sites-enabled/` 中）

```nginx
server {
    listen 8643;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8642/;
        proxy_http_version 1.1;

        # 核心：两个认证头（都要设）
        proxy_set_header Authorization $auth_header;
        proxy_set_header API_SERVER_KEY $api_server_key;

        proxy_set_header Host $host;
        proxy_read_timeout 120s;

        # CORS
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;

        if ($request_method = OPTIONS) {
            return 204;
        }
    }
}
```

### 3. 前端 `.env.local`

```
VITE_HERMES_API_URL=http://<VPS_IP>:8643
VITE_HERMES_API_KEY=<API_SERVER_KEY>
```

### 4. 前端 `hermes.ts` 请求头

```ts
function requestHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${apiKey}`,
  }
}
```

先通过 `/v1/models` 做连通检查，再通过 `/v1/chat/completions` 发送消息。两者请求头格式相同。

---

## 验证

```bash
# 健康检查
curl -s 'http://<VPS_IP>:8643/v1/models' \
  -H 'Authorization: Bearer <key>' -w '\nHTTP:%{http_code}'

# 对话
curl -s -X POST 'http://<VPS_IP>:8643/v1/chat/completions' \
  -H 'Authorization: Bearer <key>' \
  -H 'Content-Type: application/json' \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"test"}],"max_tokens":5}' \
  -w '\nHTTP:%{http_code}'
```

两条都必须返回 `HTTP:200`。

---

## 关键坑

| 问题 | 根因 | 修复 |
|------|------|------|
| 浏览器 403 但 VPS 内 curl 正常 | Cloudflare WAF 拦截 Authorization 头 | 独立端口监听，不走 Cloudflare |
| API 200 但前端始终显示"离线" | `/v1/models` 需要 `API_SERVER_KEY` 头接收裸 token，不接受 `Authorization: Bearer` 格式 | map 同时设置 `Authorization` 和 `API_SERVER_KEY` 两个头；从 `Authorization: Bearer` 中提取裸 token 注入 `API_SERVER_KEY` |
| nginx 转发后 401 | nginx 默认不转发 `Authorization` 头 | 必须显式 `proxy_set_header Authorization $http_authorization` |
| Vite 读不到 `.env.local` | Vite dev server 启动后改环境变量不会自动刷新 | 停止 → 删除 `node_modules/.vite` 缓存 → 重新 `npm run dev` |
| `map` 语法错误 或 `if` 导致行为异常 | `map` 只能在 `http` 块中，`if` 在 `location` 中不可靠 | `map` 放入 `/etc/nginx/conf.d/` |
| VPS IP 变化后仍 403 | `.env.local` 中是旧 IP | 每次会话前确认 `curl -s ifconfig.me` |
| 部署后 nginx 403/500 | 目录从 `mktemp -d` 继承 `700` 权限 | `find /var/www/... -type d -exec chmod 755 {} +` |

## CORS 预检已验证

```bash
curl -sv -X OPTIONS 'http://<VPS_IP>:8643/v1/chat/completions' \
  -H 'Origin: http://127.0.0.1:5188' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: authorization,content-type' 2>&1 \
  | grep -E 'HTTP|Access-Control|204'
```

应返回 `HTTP/1.1 204 No Content` 且包含正确的 CORS 响应头。
