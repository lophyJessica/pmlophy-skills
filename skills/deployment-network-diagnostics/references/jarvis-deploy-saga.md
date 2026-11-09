# Jarvis Deployment Debug Log

Real-world example of why diagnostic matrix matters — 7 hours saved to 15 minutes.

## Timeline of Wrong Turns

| Round | What we tried | Time wasted | Root cause |
|-------|--------------|-------------|------------|
| 1-3 | Changed nginx CORS headers | 30min | Was Chrome HTTP Authorization blocking, not CORS |
| 4-5 | Switched between IP/Cloudflare paths | 20min | Didn't check proxy layer |
| 6-7 | Added nginx map directives | 15min | Map in wrong block (server not http) |
| 8-9 | Self-signed cert on api subdomain | 20min | HSTS inherited from root domain |
| 10 | `systemctl reload nginx` | 15min | Worker cached old config |
| **Final** | Origin header stripping | **2min** | **Single targeted fix** |

## What Actually Worked

```
nginx config:
  proxy_set_header Origin "";
  proxy_set_header Authorization "Bearer <key>";
  proxy_set_header API_SERVER_KEY <key>;
  proxy_set_header Authorization $http_authorization;
  proxy_pass_request_headers on;

Vite deploy:
  sed -i 's|href="/assets/|href="./assets/|g' index.html
  sed -i 's|"/api-server"|"/p/jarvis"|g' assets/*.js
  mv assets/index-xxx.js assets/index-vN.js  # version bust
```

## Hermes API Peculiarities

- `/v1/models` health check requires `API_SERVER_KEY` header
- `/v1/chat/completions` requires `Authorization: Bearer <key>`
- BOTH must be forwarded through nginx proxy
- Requests with `Origin` header → 403 with 0 bytes
- Profile-based routing: `/p/<profile>/v1/chat/completions`

## Key Takeaway

Draw the 5-layer chain FIRST. Test each layer in ONE command.
If curl works but browser doesn't → browser or proxy issue. Move up the chain.
Never touch nginx config until you've ruled out proxy and browser.
