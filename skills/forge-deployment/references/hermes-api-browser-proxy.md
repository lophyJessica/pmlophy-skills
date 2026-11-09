# Hermes API Server — Browser Web Frontend Proxy Pattern

## The Problem

Connecting a browser-based web frontend (Jarvis, custom dashboard, etc.) to Hermes API Server requires navigating three layers of interference:

1. **Chrome security policy**: blocks `Authorization` header on HTTP requests to non-localhost IPs
2. **Cloudflare CDN/WAF**: blocks `Authorization` header on proxied domains
3. **Hermes endpoint auth inconsistency**: `/v1/models` needs `API_SERVER_KEY` header, `/v1/chat/completions` accepts `Authorization: Bearer`

## The Solution

Three components working together:

### 1. Nginx `map` for header conversion (in `http` block via `conf.d/`)

```nginx
map $http_x_hermes_key $bearer_token_for_api_key {
    ""      $http_authorization;
    default $http_x_hermes_key;
}
```

Uses the custom header `X-Hermes-Key` from the client, converts it to `API_SERVER_KEY` for the Hermes backend. Avoids `Authorization` entirely on the browser side.

### 2. Nginx reverse proxy location

```nginx
location /api-server/ {
    proxy_pass http://127.0.0.1:8642/;
    proxy_http_version 1.1;
    proxy_set_header Authorization "Bearer $http_x_hermes_key";
    proxy_set_header API_SERVER_KEY $bearer_token_for_api_key;
    proxy_set_header Host $host;
    proxy_read_timeout 120s;
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "X-Hermes-Key, Content-Type" always;
    if ($request_method = OPTIONS) { return 204; }
}
```

### 3. Browser-side fetch

```ts
fetch(`${apiUrl}/v1/chat/completions`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Hermes-Key': apiKey,  // NOT Authorization
  },
  body: JSON.stringify({ model: 'hermes-agent', messages, stream: true }),
})
```

## Debugging Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| 403 through Cloudflare domain | CF WAF blocks Authorization header | Use `X-Hermes-Key` custom header instead |
| 403 through direct IP + HTTP (Chrome) | Chrome blocks Authorization on HTTP to non-localhost | Use `X-Hermes-Key` custom header |
| 403 from Chrome, Remote Address shows `127.0.0.1:7897` | Local proxy (Clash/V2Ray) intercepting | Add bypass rule for VPS IP/domain |
| OPTIONS preflight 204 but GET/POST 403 | Nginx not forwarding Authorization | Add `proxy_set_header Authorization $http_authorization;` |
| `/v1/models` returns 401 with Authorization Bearer | Hermes needs `API_SERVER_KEY` header for models endpoint | Add `proxy_set_header API_SERVER_KEY $bearer_token_for_api_key;` |
| Connection works from curl but not browser | Missing CORS headers | Add `Access-Control-Allow-*` headers |
| `.env.local` changes not picked up | Vite caches env vars | Stop dev server, `rm -rf node_modules/.vite`, restart |
