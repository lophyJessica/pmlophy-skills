# CLIProxyAPI 搬到 VPS：完整命令

适用：本机出口 IP 被上游风控（429 RESOURCE_EXHAUSTED）、或希望服务常驻不随终端退出。目标是客户端只连一个域名，出口固定成 VPS 的干净 IP。

下文的 `8317`、`/cpa/`、`pmlophy-cpa-2026` 都是示例值，按实际替换。

## 1 下载（先确认架构）

```bash
uname -m      # x86_64 → linux_amd64 ；aarch64 → linux_aarch64
curl -s https://api.github.com/repos/router-for-me/CLIProxyAPI/releases/latest \
  | grep browser_download_url | grep linux
```

拿到真实文件名再下（不要拼 `releases/latest/download/xxx.zip`，那个路径常年 404 只回 9 字节）：

```bash
mkdir -p /root/cliproxyapi && cd /root/cliproxyapi
curl -sL -o cp.tar.gz https://github.com/router-for-me/CLIProxyAPI/releases/download/<ver>/CLIProxyAPI_<ver>_linux_amd64.tar.gz
tar xzf cp.tar.gz && rm -f cp.tar.gz && ls -lh
```

## 2 生成 config.yaml

不要手打 YAML（空格会被粘贴吃掉），直接用 python 生成：

```bash
cd /root/cliproxyapi && python3 -c "
cfg = '''config-version: 8
server:
  host: \"127.0.0.1\"
  port: 8317
management:
  allow-remote: false
  secret-key: \"cpa-admin-vps\"
access:
  api-keys:
    - \"pmlophy-cpa-2026\"
observability:
  logs:
    debug: false
    request-log: false
'''
open('config.yaml','w').write(cfg)
print('written')
" && cat config.yaml
```

- `host` 收窄到 `127.0.0.1`：不直接对外暴露，统一走 nginx。
- `management.secret-key` 留空 = 管理页面整体 404。
- `api-keys` 别用 `sk-` 前缀（聊天里会被打码），也别留模板值。

## 3 搬账号凭证

账号 json 在**客户端**的 `~/.cli-proxy-api/` 下，整批传过去：

```bash
scp -P <ssh端口> -i ~/.ssh/<key> ~/.cli-proxy-api/antigravity-*.json root@<vps-ip>:/root/.cli-proxy-api/
```

落地后服务有 file watcher，几秒内自动加载，**不用重启**。确认：

```bash
ls -1 /root/.cli-proxy-api/*.json | wc -l
curl -s http://127.0.0.1:8317/v1/models -H "Authorization: Bearer <key>" | head -c 600
```

模型列表有内容就说明账号认到了。

## 4 systemd 托管

```bash
cat > /etc/systemd/system/cliproxyapi.service <<'UNITEOF'
[Unit]
Description=CLIProxyAPI gateway
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/cliproxyapi
ExecStart=/root/cliproxyapi/cli-proxy-api
Restart=always
RestartSec=5
StandardOutput=append:/root/cliproxyapi/service.log
StandardError=append:/root/cliproxyapi/service.log
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
UNITEOF
systemctl daemon-reload && systemctl enable --now cliproxyapi
systemctl is-active cliproxyapi && ss -tlnp | grep 8317
```

注意：`pkill -f cli-proxy-api` 在同一个 shell 里运行时可能把执行命令的进程本身也匹配掉（表现为命令被 SIGTERM 截断、unit 文件没写成）。写完 unit 再单独启一次，别把 pkill 和 systemctl 串在同一条里。

## 5 nginx 子路径反代

先备份，再插入（配置里往 `location ...` 块之间加，别用 sed 改大段）：

```nginx
    location /cpa/ {
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "content-type, authorization, x-api-key, anthropic-version, anthropic-beta" always;
        if ($request_method = OPTIONS) { return 204; }
        client_max_body_size 100m;
        proxy_pass http://127.0.0.1:8317/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Origin "";
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
    }
```

三个要点：`proxy_pass` 末尾的 `/` 用来剥掉 `/cpa` 前缀；`proxy_buffering off` 保证 SSE 流式实时吐出；`Access-Control-Allow-Headers` 必须含 `anthropic-version`、`anthropic-beta`、`x-api-key`，否则浏览器系客户端预检就挂。

```bash
nginx -t && systemctl restart nginx
```

patch 类工具不得直接写 `/etc/nginx/...`（会被拒），用 `python3` 读改写或 `cat >` 落块文件再插入。

## 6 验证序列（按顺序跑，每步一个判据）

```bash
echo -n '内网: '; curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1/cpa/v1/models -H "Host: <域名>" -H "Authorization: Bearer <key>"
echo -n '跳过证书: '; curl -sk -o /dev/null -w "%{http_code}\n" https://127.0.0.1/cpa/v1/models -H "Host: <域名>" -H "Authorization: Bearer <key>"
echo -n '公网: '; curl -s -o /dev/null -w "%{http_code}\n" https://<域名>/cpa/v1/models -H "Authorization: Bearer <key>" --max-time 20
echo -n '真实对话: '; curl -s -o /dev/null -w "%{http_code}\n" -X POST https://<域名>/cpa/v1/messages \
  -H "Authorization: Bearer <key>" -H "content-type: application/json" -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-sonnet-5-5-high","max_tokens":50,"messages":[{"role":"user","content":"hi"}]}' --max-time 40
```

纯 http 返回 301 是正常的（跳 https），继续跑 https 那几步。四项都 200 才算完。

## 7 客户端收尾

配置管理器（CC Switch / Cockpit）里改两处：

- 地址：`https://<域名>/cpa`（**不带 `/v1`**，客户端自己拼）
- Key：与 `access.api-keys` 一致

模型名照旧。本机那份反代可以停掉，但先别卸，留着当对照组。

## 排错速查

| 现象 | 先查 |
|---|---|
| 公网 200 但客户端仍 429 | 客户端是不是还在连本机地址 |
| 内网 http 301 | 正常，是 http→https 跳转 |
| `nginx -t` 通过但 404 | 没 restart；或 `proxy_pass` 少了末尾 `/` |
| 流式返回一卡一卡 | 少了 `proxy_buffering off` |
| 服务重启后没了 | 没 `systemctl enable` |
| 模型列表空 | 账号 json 没传到 `~/.cli-proxy-api/` |
