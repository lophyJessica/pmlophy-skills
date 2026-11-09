# n8n 社区版自托管部署（forge-scrm 2026-08-24 实测通过）

自托管 n8n Community Edition = 免费、开源、无执行次数限制（要 SSO/多环境/审计才需付费 Business $800/月——单人使用用不上）。4C8G VPS 随手跑。

## 安装（npm 全局，免 Docker）

```bash
# 环境：Node 20+ 已有即可（vue 系装 node20 用 nodesource）
npm install -g n8n          # 耗时 3-6 分钟，用后台跑，别前台干等
n8n --version               # 2.8.4 本次实测
```

## systemd 守护（含子路径环境变量）

```bash
cat > /etc/systemd/system/n8n.service <<UNITEOF
[Unit]
Description=n8n workflow automation
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
Environment=N8N_USER_FOLDER=/root/.n8n
Environment=N8N_HOST=127.0.0.1
Environment=N8N_PORT=5678
Environment=N8N_PATH=/n8n/
ExecStart=/usr/bin/n8n        # $(which n8n) 展开成实际路径
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNITEOF
systemctl daemon-reload && systemctl enable n8n --now
```

**N8N_PATH 生效要求**：改 systemd unit 里的 Environment 后必须 `systemctl daemon-reload` + **restart**（不是 reload）——环境变量是进程启动时读取的。

## nginx 子路径反代（scrm.pmlophy.com/n8n/）

```nginx
location /n8n/ {
    proxy_pass http://127.0.0.1:5678;          # ⚠️ 不带尾斜杠！带 / 会把 /n8n/ 前缀吞掉 → 404
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;    # WebSocket（编辑器实时）
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 300s;
}
```

**proxy_pass 尾斜杠坑（实测打脸）**：
- `location /n8n/ { proxy_pass http://127.0.0.1:5678/; }` → nginx 会把请求路径中 `/n8n/` 部分替换为 `/`，实际请求变成 `http://127.0.0.1:5678/` → 但 n8n 已配置 N8N_PATH=/n8n/ 只认 `/n8n/*` → **404**
- 正确：`proxy_pass http://127.0.0.1:5678;`（不带尾斜杠）→ 路径原样透传 `/n8n/xxx` → 200

**N8N_PATH 设置后的直接访问行为**：`http://127.0.0.1:5678/` 变 404（根路径不再有效），编辑器真实地址是 `http://127.0.0.1:5678/n8n`（日志会打 `Editor is now accessible via: http://127.0.0.1:5678/n8n`）。`/n8n` 无尾斜杠 → 301 → `/n8n/` → 200，正常。

## 验证

```bash
systemctl is-active n8n nginx
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5678/n8n/   # 200
curl -s -o /dev/null -w '%{http_code}' -L http://<域>/n8n/           # 外网 200
curl -s -L http://<域>/n8n/ | grep -oE '<title>[^<]*</title>'        # n8n.io - Workflow Automation
```

## 首次使用 + 后续要点

1. **首次打开创建 owner 账号**（邮箱+密码）——这是 n8n 实例的超级管理员，记住即可
2. **⚠️ HTTP 访问白屏错（2026-08-24 实测）：`Your n8n server is configured to use a secure cookie, however you are either visiting this via an insecure URL, or using Safari.`** —— n8n 默认要求 secure cookie（仅 HTTPS 传输），纯 HTTP 部署（POC 期无 SSL）时浏览器拒收 cookie → 初始化页直接白屏报错。**修法**：systemd unit 加 `Environment=N8N_SECURE_COOKIE=false` → `daemon-reload` + restart。**上 HTTPS 后必须改回 true**（POC 期临时手段，记入迁移文档）。排查顺序：先看报错文案是不是 secure cookie（不是资源 404），再改环境变量。
3. Python 任务节点：日志常见的 `Failed to start Python task runner... virtual environment is missing` 是**非致命**警告（内部调试模式才需要），JS 节点照常用；生产 Python 节点要配 external mode task runner
4. 与业务系统同机共存的架构原则（forge 系列定）：**自动化平台只通过 HTTP API 调业务后端（如 forge-scrm 的 /api/*），禁止直写 MySQL**——n8n 里用 HTTP Request 节点打业务 API，喂数据也用 API 落库
5. 配置可代码化：工作流可用 JSON 导出/导入（git 版本管理），不用手动拖节点——这是自托管相比 Make 的核心优势（Make 手动配置是用户弃用它的原因）
6. **闭环验证路径（n8n → 业务系统 → MySQL）**：三步走——① HTTP Request GET 业务后端 /api/health（连通性）→ ② POST 登录接口拿 token（认证）→ ③ 带 token POST 业务接口建数据，去 MySQL 查落库。n8n HTTP Request 节点用 127.0.0.1 直连同机后端最快（n8n 与业务系统同机时）。

## ⚠️ 子路径双重路径 bug（2026-08-24 实测，未完全解决）

N8N_PATH=/n8n/ + nginx 无尾斜杠透传后：**页面和静态资源正常（/n8n/static/... 200），但 API 端点双重路径**：

```text
POST /n8n/rest/login → "Cannot POST /n8n"（n8n 收到 /n8n/rest/login 后又按 N8N_PATH 加一层 → /n8n/n8n/rest/login）
```

这是 n8n 已知问题（GitHub issue #16983：N8N_PATH + 反代场景内部链接/API 重复 /n8n/ 前缀）。资源前缀 vs API 路径两头矛盾，改了这头坏那头：

- 保留 N8N_PATH + 无尾斜杠透传 → 静态资源带前缀 ✅，但 API 双重路径 ❌
- 去掉 N8N_PATH + nginx 剥前缀 → API 正常但 HTML 资源丢前缀（/static/ 打到业务站点）❌
- N8N_EDITOR_BASE_URL 只影响登录后页面，不管 HTML 静态资源前缀

**结论/正解：n8n 走反代子路径是坑，直接给独立子域名**（n8n.pmlophy.com → A 记录 → nginx 独立 server 块反代 5678 根路径，无 N8N_PATH、无前缀剥离，什么都不设）。子域名不算繁琐（DNS 加一条记录），配置反而更简单，彻底避开双重路径。二期接入时用子域名方案，不要复用 /n8n/ 子路径。

## 选型结论（2026-08-24 定稿）

- 弃用 Make（手动配置麻烦、读不了 DS 分享链接、数据在第三方）
- 定稿 n8n 社区版自托管（免费、数据自持、配置可代码化、与业务系统同机）
- 一期不接（一期无自动采集），二期自动采集/定时任务时启用