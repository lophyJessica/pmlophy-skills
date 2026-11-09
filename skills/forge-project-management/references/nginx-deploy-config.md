# VPS 部署: Forge SPA nginx 配置

## 完整 nginx 配置
```nginx
server {
    listen 80;
    server_name pmlophy.com www.pmlophy.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name pmlophy.com www.pmlophy.com;
    ssl_certificate /etc/nginx/ssl/pmlophy.crt;
    ssl_certificate_key /etc/nginx/ssl/pmlophy.key;
    root /var/www/pmlophy.com;

    location /project/forge-erp/ {
        alias /var/www/pmlophy.com/project/forge-erp/;
        try_files $uri $uri/ /project/forge-erp/index.html;
    }

    location /project/forge-wms/ {
        alias /var/www/pmlophy.com/project/forge-wms/;
        try_files $uri $uri/ /project/forge-wms/index.html;
    }

    location / {
        try_files $uri $uri/ =404;
    }

    gzip on;
    gzip_types text/css application/javascript image/svg+xml;
}
```

## 排障记录

### 问题: WMS 白屏 (rewrite or internal redirection cycle)
**根因**: vite base 未改成 `/project/forge-wms/`,编译后的 index.html 仍引用 `/wms/assets/...`。同时根 location 的 try_files 回退到 `/index.html`(已删)造成循环重定向。

**修复**:
1. 改 vite base → 重新 build
2. nginx 根 location 改为 `try_files $uri $uri/ =404;`
3. 每个项目独立 `location` 块用 `alias` 不要共用 root

### 问题: Cloudflare 521
**根因**: Cloudflare SSL 模式设为 Full (Strict),但源站只有自签证书。
**修复**: 改为 Full 模式(接受自签)。

## Hysteria UDP 443 与 nginx TCP 443 共存
hysteria 监听 UDP 443,nginx 监听 TCP 443,不同协议不冲突,可以同时运行。
