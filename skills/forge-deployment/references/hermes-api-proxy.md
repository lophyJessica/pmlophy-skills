# Hermes API Proxy for Browser Apps (Jarvis pattern)

When a browser app (local dev or deployed) needs to talk to Hermes API Server,
four layers must align: CORS, auth header format, browser security policy, and
proxy/firewall routing.

## Architecture

```
Browser (localhost:5188)
  → nginx proxy (VPS :8643 or pmlophy.com/api-server/)
    → Hermes API Server (VPS :8642)
```

## Nginx Config (Direct Port, bypassing Cloudflare)

```nginx
server {
    listen 8643;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8642/;
        proxy_http_version 1.1;
        proxy_set_header Authorization "Bearer $http_x_hermes_key";
        proxy_set_header API_SERVER_KEY $http_x_hermes_key;
        proxy_set_header Host $host;
        proxy_read_timeout 120s;
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "x-hermes-key, content-type" always;
        if ($request_method = OPTIONS) { return 204; }
    }
}
```

Key points:
- `$http_x_hermes_key` extracts the `x-hermes-key` header (nginx lowercases + underscores)
- `Authorization` header value = "Bearer $http_x_hermes_key"
- `API_SERVER_KEY` = raw key value (needed by /v1/models health check)
- CORS Allowed headers must include BOTH `x-hermes-key` AND `content-type`
- `proxy_pass` must end with `/` when using `location / { ... }` with no path suffix

## Why X-Hermes-Key Instead of Authorization

Chrome blocks `Authorization` header on HTTP requests to non-localhost IPs.
Using a custom header (`X-Hermes-Key`) and converting it at nginx avoids this.

Two other options that also worked:
1. HTTPS via `pmlophy.com/api-server/` path (but Cloudflare may WAF-block it)
2. Direct HTTP with `Authorization` — works from curl/terminal, fails in browsers

## Hermes API Auth Quirks

- `/v1/chat/completions` accepts `Authorization: ***`
- `/v1/models` health check requires `API_SERVER_KEY` header (NOT Authorization Bearer)
- Both must be set by nginx for the browser app's `checkHermesConnection()` to pass

## Debugging Flow

1. **curl from VPS localhost** — verify API works at all
2. **curl from VPS to public IP** — verify nginx proxy works
3. **browser F12 → Network** — check if request reaches nginx (access log), check CORS preflight
4. **Chrome Console fetch() test** — isolate browser security from app code
5. **Check Remote Address in Network tab** — 127.0.0.1:7897 = proxy interception

## Common Failure Modes

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| CORS error: header not in Allow-Headers | nginx CORS config missing custom header | Add to Access-Control-Allow-Headers |
| 403 with 0 bytes from browser | Chrome stripped Authorization on HTTP | Switch to X-Hermes-Key custom header |
| 403 via public IP, 200 via localhost | nginx not reloaded after config change | `systemctl reload nginx` |
| Request hits 127.0.0.1:7897 (not VPS) | Mac proxy (Clash) intercepting | Bypass rule or use HTTPS path |
| /v1/models 403 but /v1/chat/completions 200 | Missing API_SERVER_KEY header | Add proxy_set_header API_SERVER_KEY |
