# Nginx → Hermes API Proxy：生产配置

## 最终验证通过的模式

### 同域独立端口（绕过 Cloudflare + CORS + 证书）

当 Jarvis 需从浏览器访问 Hermes API，且 Mac 代理、Cloudflare WAF、
HSTS 同时阻碍所有其他路径时，这是唯一经过端到端验证的方案。

```nginx
server {
    listen 8080;
    server_name _;

    location /hermes/ {
        proxy_pass http://127.0.0.1:8642/;
        proxy_http_version 1.1;
        proxy_set_header Authorization "Bearer <API_SERVER_KEY>";
        proxy_set_header API_SERVER_KEY <API_SERVER_KEY>;
        proxy_set_header Origin "";       # 致命：Hermes API 拒绝含 Origin 的请求
        proxy_set_header Host $host;
        proxy_read_timeout 120s;
    }

    location / {
        root /var/www/pmlophy.com/jarvis;
        try_files $uri $uri/ /index.html;
    }
}
```

### Cloudflare 域名路径（代理开启可用）

```nginx
location /hermes/ {
    proxy_pass http://127.0.0.1:8642/;
    proxy_http_version 1.1;
    proxy_set_header Authorization "Bearer <API_SERVER_KEY>";
    proxy_set_header API_SERVER_KEY <API_SERVER_KEY>;
    proxy_set_header Origin "";           # 同样致命
    proxy_set_header Host $host;
    proxy_read_timeout 120s;
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "x-hermes-key, content-type" always;
    if ($request_method = OPTIONS) { return 204; }
}
```

## 三条硬性要求

1. `proxy_set_header Origin ""` — Chrome 发 POST 必带 Origin 头，Hermes API 收到就 403。剥离它。
2. `Authorization: *** API_SERVER_KEY: <key>` **同时注入** — /v1/models 只认 API_SERVER_KEY，/v1/chat 只认 Authorization，两者不通用。
3. `systemctl restart nginx` **不是** `reload` — 多次 reload 后 worker 可能持有旧配置缓存，硬编码 key 不生效。

## 已验证的故障排除序列

逐层从终端 curl 排除，每轮只改一个变量：

1. `curl http://127.0.0.1:8642/v1/models -H 'Authorization: ***'`（上游健康）
2. `curl http://127.0.0.1:8080/hermes/v1/models`（nginx 本地）
3. `curl http://192.220.14.245:8080/hermes/v1/models`（外部可达）
4. 浏览器开发者工具 → Remote Address 检查（代理劫持 → 127.0.0.1:7897）
5. `curl` 加 `-H 'Origin: ...'`（触发 Origin 拒绝）
6. 浏览器无痕窗口 + 系统代理关闭（排除 Chrome 扩展干扰）

## Chrome 特定兼容

- `crypto.randomUUID()` 需要安全上下文（HTTPS）；HTTP 下注入 polyfill
- 部署新 JS 后 `Cmd+Shift+R` 无效 → 重命名文件 + 更新 index.html
- `/v1/models` 返回 200 但 `/v1/chat` 403 → Origin 头未剥离
