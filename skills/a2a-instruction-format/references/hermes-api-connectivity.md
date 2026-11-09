# Hermes API Server 连通性排查

## 核心架构
Hermes 内置 API Server 监听 8642 端口（HTTP），提供 OpenAI 兼容的 /v1/chat/completions 接口。
前端（如 Jarvis Web 控制台）通过 HTTP 直连或 nginx 反向代理访问。

## 连通性排查清单（阶梯式，按序执行）

### 1. VPS IP 验证
VPS IP 可能因 DHCP 或重启发生变化，连接失败时第一步检查：
```bash
curl -s ifconfig.me
```
对比 `.env.local` 中的 VITE_HERMES_API_URL 是否正确。

### 2. VPS 内 API 自检
排除上游故障，确认 Hermes API Server 本身可用：
```bash
curl -s -X POST 'http://127.0.0.1:8642/v1/chat/completions' \
  -H 'Authorization: Bearer <key>' \
  -H 'Content-Type: application/json' \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"回：OK"}],"max_tokens":5}'
```
预期：HTTP 200 + JSON 响应。若这一步失败，问题在 Hermes 进程或 API key。

### 3. nginx 代理自检
从 VPS localhost 测试代理端口（如 8643），确认 proxy_pass 和 header 转发正确。
```bash
curl -s 'http://127.0.0.1:8643/v1/chat/completions' -H 'Authorization: Bearer <key>' ...
```

### 4. CORS 预检
```bash
curl -sv -X OPTIONS 'http://<IP>:8643/v1/chat/completions' \
  -H 'Origin: http://127.0.0.1:5188' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: authorization,content-type'
```
必须返回 HTTP 204，且 Access-Control-Allow-Headers 包含所有自定义请求头。缺少则浏览器会报 CORS 拦截。

### 5. nginx 不转发 Authorization 头（高频坑）
nginx 默认丢弃 Authorization 头。必须在 location 中显式设置：
```nginx
proxy_set_header Authorization $http_authorization;
```
缺少这行会导致 API 返回 401 "Invalid gateway API key"。

### 6. Cloudflare WAF 拦截 Authorization 头
通过 Cloudflare 代理的域名（如 pmlophy.com/api-server/）会拦截 Authorization 请求头返回 403。
绕过方式：(a) 用 X-Hermes-Key 等自定义头 + nginx 将自定义头转换为 Authorization，(b) 开独立端口绕过 Cloudflare CDN。

### 7. Chrome 禁止 HTTP Authorization 头到非 localhost IP
浏览器直接剥离该头，CORS 预检通过但实际请求缺鉴权 → 403（body 0 字节）。
绕过方式：(a) 用自定义头 X-Hermes-Key 代替 Authorization，(b) 部署到 VPS 上使用 HTTPS 同域访问。

### 8. Mac 本地代理（Clash/Surge）拦截直连 IP 请求
Chrome DevTools Network 中 Remote Address 显示 `127.0.0.1:7897` → 请求被代理截获。
临时关代理或加直连规则（如 `DOMAIN,*.pmlophy.com,DIRECT`）后重试。
注意：加规则后必须点代理客户端的"重新加载"才能生效。

### 9. nginx 自定义头转发
当使用 X-Hermes-Key 等自定义头时，nginx 需同时做两件事：
```nginx
# 将自定义头转换为 Hermes API 需要的 Authorization 和 API_SERVER_KEY
proxy_set_header Authorization "Bearer $http_x_hermes_key";
proxy_set_header API_SERVER_KEY $http_x_hermes_key;
```
注意 `/v1/models` 和 `/v1/chat/completions` 鉴权格式不同——前者只认 API_SERVER_KEY，后者认 Authorization Bearer。

### 10. 3 轮以上仍不通 → 部署到 VPS 同域（终极大招）
将前端 dist 部署到 VPS 上，通过 HTTPS + 同域 `/api-server` 路径调用。
清除 CORS、Chrome HTTP 策略和代理三重阻碍。部署检查：
- dist 中 index.html 资源路径改为相对路径（`./assets/`），否则子目录部署 404
- nginx 添加 location 块（如 `/jarvis/`）
- Vite 构建时 API URL 设为同域相对路径（如 `/api-server`）

## 验证命令
```bash
curl -s -X POST 'http://127.0.0.1:8643/v1/chat/completions' \
  -H 'Authorization: Bearer <key>' \
  -H 'Content-Type: application/json' \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"回：OK"}],"max_tokens":5}'
```
预期：HTTP 200 + JSON 响应。
