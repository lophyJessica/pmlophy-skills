# Hermes API Server Origin Header Rejection

致命陷阱：Hermes API Server 拒绝任何带有 Origin 请求头的 POST 请求，返回 403 且响应体为 0 字节。

## 根因

Hermes API Server 对 Origin 头做严格校验。Chrome 在所有 POST 请求上自动附加 Origin 头（即使同源请求），curl 默认不发，因此 curl 测试总能通过但浏览器永远 403。

## 症状识别

- curl 从 VPS 发 POST → 200
- 浏览器发 POST → 403，响应体 0 字节
- GET /v1/models 正常
- curl 加上 -H 'Origin: ...' 后同样 403 → 确认

## 排查

```bash
# 1. 无 Origin 基线
curl -s -X POST 'http://127.0.0.1:8080/hermes/v1/chat/completions' \
  -H 'Content-Type: application/json' \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"1"}],"max_tokens":2}'

# 2. 带 Origin 复现
curl ... -H 'Origin: http://192.220.14.245:8080' → 403 即命中

# 3. 逐个排除浏览器专有头
for h in 'Origin: ...' 'Referer: ...' 'sec-fetch-site: ...' 'sec-fetch-mode: cors'; do
  curl ... -H "$h" ...
done
```

## 修复

nginx 中剥离 Origin 头：

```nginx
location /hermes/ {
    proxy_pass http://127.0.0.1:8642/;
    proxy_set_header Origin "";
}
```

不要在 Hermes API 侧修改——内置行为，只能在前置代理剥离。

## 区分其他似因

| 症状 | 根因 | 修复 |
|------|------|------|
| GET 200 POST 403 0 bytes | Origin 头 | nginx proxy_set_header Origin "" |
| GET 403 Remote 127.0.0.1:7897 | Mac 代理劫持 | 系统设置关代理 |
| OPTIONS 204 GET 403 | CORS 缺自定义头 | nginx allow-headers |
| HTTPS POST 403 | Cloudflare WAF | 独立 HTTP 端口 |
| crypto.randomUUID 报错 | HTTP 无 Web Crypto | JS polyfill |
