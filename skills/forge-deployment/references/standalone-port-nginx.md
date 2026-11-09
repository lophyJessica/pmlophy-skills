# Standalone HTTP Port Deployment (Bypass Cloudflare/CORS/Cert)

When a Web frontend (SPA) deployed behind Cloudflare HTTPS cannot call the same-domain Hermes API proxy due to Cloudflare WAF blocking POST requests, a standalone nginx port serves as a clean bypass.

## Pattern

Serve frontend + API proxy on a single non-Cloudflare HTTP port with same-origin routing:

```nginx
server {
    listen 8080;
    server_name _;

    location /hermes/ {
        proxy_pass http://127.0.0.1:8642/;
        proxy_http_version 1.1;
        proxy_set_header Authorization "Bearer $http_x_hermes_key";
        proxy_set_header API_SERVER_KEY $http_x_hermes_key;
        proxy_set_header Host $host;
        proxy_read_timeout 120s;
    }

    location / {
        root /var/www/pmlophy.com/jarvis;
        try_files $uri $uri/ /index.html;
    }
}
```

Key properties:
- Same origin (port 8080) for frontend and API → no CORS, no mixed content
- No Cloudflare proxy → WAF cannot intercept
- No SSL cert needed → no HSTS/compatibility issues
- `$http_x_hermes_key` maps directly from client's `X-Hermes-Key` header
- Both `Authorization: Bearer` and `API_SERVER_KEY` headers forwarded to Hermes API

## When to Use

- Cloudflare WAF blocks API POST requests (browser fingerprinting triggers 403)
- HSTS + self-signed cert makes subdomain HTTPS impossible
- Mac local proxy (Clash/V2Ray) interferes with direct IP connections
- Chrome blocks `Authorization` header on HTTP cross-origin requests

## JS Version Busting (Cache Bypass)

Chrome aggressively caches SPA JS bundles even with `Cmd+Shift+R`. When the JS content changes (e.g. API URL updated), rename the file:

```bash
mv assets/index-xxx.js assets/index-v2.js
sed -i 's|index-xxx.js|index-v2.js|' index.html
```

This forces fresh download. Increment version on each deploy that changes the JS bundle.

## crypto.randomUUID() Polyfill (HTTP Non-Secure Context)

`crypto.randomUUID()` is only available in secure contexts (HTTPS or localhost). On standalone HTTP ports, it throws `TypeError: crypto.randomUUID is not a function`. Inject a polyfill at the top of the JS bundle:

```bash
POLYFILL='if(!crypto.randomUUID){crypto.randomUUID=function(){return"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,function(e){var t=16*Math.random()|0;return("x"===e?t:3&t|8).toString(16)})}};'
echo "$POLYFILL$(cat assets/index.js)" > /tmp/patched.js
mv /tmp/patched.js assets/index.js
```

## Nginx Restart vs Reload (Hard-Coded Key Caching)

When nginx proxies with hard-coded `proxy_set_header` values (e.g., API keys), `systemctl reload nginx` may NOT apply the new config — worker processes retain cached configuration. This causes symptoms like:

- curl from VPS localhost → 200
- curl from VPS public IP → 403
- Browser from Mac → 403

Use `sudo systemctl restart nginx` instead of `reload` after changing ANY `proxy_set_header` with hard-coded values. This fully kills and restarts all workers with the fresh config.

## Chrome Compatibility Checklist for Standalone HTTP Port

1. `proxy_set_header Origin ""` — Hermes API rejects POSTs with Origin header
2. `Authorization` + `API_SERVER_KEY` both injected — models vs chat use different auth
3. `crypto.randomUUID()` polyfill — unavailable on HTTP non-secure context
4. JS version busting (rename + update HTML) — Cmd+Shift+R doesn't bypass JS cache
5. `systemctl restart nginx` — reload may cache old proxy_set_header values

Cloudflare may allow `curl` API POST requests but block identical requests from Chrome. This is browser-fingerprint-based WAF, not header-related. Confirmed symptoms:

- `curl -X POST ... 200` from VPS through Cloudflare
- Chrome `POST ... 403` from Mac through same Cloudflare path
- Both requests appear in nginx access log (Cloudflare proxies both)
- Different Cloudflare edge IPs may produce different results

The standalone port pattern above bypasses this entirely.
