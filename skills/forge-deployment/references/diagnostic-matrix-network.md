# Network Diagnostic Matrix (API Connectivity)

When debugging "curl works but browser doesn't" or "API works locally but not from Web frontend",
draw a layer-by-layer diagnostic matrix BEFORE touching any config.

## Layer Stack (top to bottom)

```
Browser (DevTools, headers, console)
  → Local Proxy (Remote Address 127.0.0.1:7897)
    → Network (DNS, Cloudflare WAF, ISP)
      → Reverse Proxy (nginx, CORS, SSL)
        → Application (Hermes API, auth, Origin rejection)
```

Each layer must be individually confirmed working before moving to the next.

## Method: Single-Header Elimination

When `curl` from VPS works but browser doesn't, add browser-specific headers to curl one
at a time:

```bash
for h in 'Origin: http://...' 'Referer: http://.../' 'sec-fetch-site: same-origin' 'sec-fetch-mode: cors'; do
  code=$(curl -s -X POST URL -H "$h" -d '...' -w '%{http_code}' -o /dev/null)
  echo "$h → $code"
done
```

If ONE header triggers the failure, fix at the proxy layer. Example: `Origin` header triggers
403 on Hermes API → nginx `proxy_set_header Origin ""`.

## Red Flags & Root Causes

| Symptom | Layer to check | Likely fix |
|---------|---------------|------------|
| Remote Address = 127.0.0.1:7897 | Local proxy | Disable system proxy or add bypass |
| curl works, same config browser doesn't | Reverse proxy | `systemctl restart` nginx (not reload) |
| GET /v1/models 200, POST /v1/chat 403 | Application / Origin | Strip Origin in nginx |
| 403 with Content-Length 0 | Application | Origin header rejection |
| 401 "Invalid API_SERVER_KEY" | Reverse proxy | Check key format, nginx restart |
| crypto.randomUUID() TypeError | Browser | HTTP non-secure context; inject polyfill |
| HTTPS with self-signed cert + HSTS | Network / SSL | Chrome refuses connection; use HTTP or valid cert |
| Cloudflare WAF 403 (browser) but curl 200 | Network | WAF browser fingerprinting; use direct port |

## Order of Operations

1. Confirm API works from VPS localhost (`curl http://127.0.0.1:8642/...`)
2. Confirm API works from VPS public IP (`curl http://IP:8642/...`)
3. Confirm reverse proxy works from VPS (`curl http://IP:8080/hermes/...`)
4. Confirm from user machine via `curl` (terminal, not browser)
5. Open browser with DevTools Network tab → headers, Remote Address
6. If broken at layer 5, use single-header elimination on layer 3-4

**Never skip a layer.** Every skipped layer can hide the real root cause behind
a misleading symptom at a higher layer.
