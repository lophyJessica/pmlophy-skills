# Jarvis / Hermes API 部署故障排查

## 诊断矩阵（先画图再试错）

当浏览器无法访问 VPS API 时，按五层逐层排除，不要揪着一层反复改：

```
Chrome → 系统代理 → Cloudflare → nginx → Hermes API
```

每层用一个最小可复现命令验证，通了下移，不通就停。

## 常见根因与修复

### 1. Hermes API 拒绝 Origin 头
- 症状：curl 200，Chrome POST 403
- 根因：Hermes API 的 `/v1/chat/completions` 拒绝任何 Origin 头
- 修复：nginx `proxy_set_header Origin "";`
- 参考：`/hermes/` 路径配置

### 2. Hermes API /v1/models 鉴权差异
- 症状：`/v1/models` 返回 401/403，但 `/v1/chat/completions` 正常
- 根因：models 端点只认 `API_SERVER_KEY` 头，不认 `Authorization: Bearer`
- 修复：nginx 同时设置两个头

### 3. Cloudflare WAF 拦截浏览器 POST
- 症状：curl 200，Chrome POST 403，日志中请求未到达 nginx
- 根因：Cloudflare 检测浏览器指纹拦截 POST
- 修复：使用独立子域名（灰云 DNS only）或独立端口绕过

### 4. Chrome HTTP Authorization 限制
- 症状：Chrome 发送的请求没有 Authorization 头
- 根因：Chrome 禁止在 HTTP 连接中发送 Authorization 头到非 localhost
- 修复：HTTPS 域名 或 自定义头（X-Hermes-Key）替代

### 5. crypto.randomUUID() 不可用
- 症状：HTTP 页面 JS 报 `crypto.randomUUID is not a function`
- 根因：Web Crypto API 只在安全上下文（HTTPS）下可用
- 修复：HTTP 部署时注入 polyfill

### 6. nginx reload 未生效
- 症状：修改 nginx 配置后行为不变
- 修复：`sudo systemctl restart nginx`（非 reload）

### 7. 代理绕过 IP 直连
- 症状：Remote Address 显示 127.0.0.1:7897
- 修复：系统代理设置中配置 IP 绕过规则

## 持久化会话

Hermes API 的 `/v1/chat/completions` 通过 `system_prompt + first_user_message` 哈希派生会话 ID。
- 每轮请求需发送完整历史（含 system 消息和首条 user 消息）
- `session_key` 字段不被 OpenAI-compatible 端点识别
- 验证：连续两轮 curl，第二轮能引用第一轮内容
