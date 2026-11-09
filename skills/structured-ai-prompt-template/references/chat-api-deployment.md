# Hermes Chat API 部署指南

在作品站上部署 AI 聊天接口——让面试官直接在浏览器跟你的 AI Agent 对话。

## 架构

```
浏览器 GET  /chat  → 聊天 HTML 页面（纯静态）
浏览器 POST /api/chat → nginx 反向代理 → localhost:9120 Python 服务 → hermes chat CLI
```

## 三步部署

### 1. Python 桥接服务（/root/hermes-chat-api.py）

```python
#!/usr/bin/env python3
"""最小化的 HTTP→Hermes CLI 桥接"""
import subprocess, json, os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 9120

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<html>API doc page</html>")

    def do_POST(self):
        if self.path != "/chat": self.send_error(404); return
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        msg = body.get("message", "")
        r = subprocess.run(["hermes", "chat", "-q", msg, "-Q"],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "HOME": "/root"})
        reply = r.stdout.strip() or r.stderr.strip()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply}, ensure_ascii=False).encode())

HTTPServer(("127.0.0.1", PORT), H).serve_forever()
```

后台运行：`python3 /root/hermes-chat-api.py &` 或 `terminal(background=true)`

### 2. nginx 反向代理

在 server 块中添加：
```nginx
location /api/chat {
    proxy_pass http://127.0.0.1:9120/chat;
    proxy_set_header Host $host;
    proxy_read_timeout 60s;
}
```

### 3. 聊天 HTML 页面

单文件静态页，POST 到 `/api/chat`，渲染对话。放在 `/var/www/pmlophy.com/chat.html`。

## 坑点

- certbot 重新运行后会覆盖手动修改的 nginx 配置，需补回 location 块
- Python bytes literal 不能含非 ASCII 字符，中文需 `encode("utf-8")`
- 浏览器打开 API URL 时需支持 GET（返回文档页），否则 501

## 验证

```bash
# GET 文档页
curl https://pmlophy.com/api/chat

# POST 对话
curl -X POST https://pmlophy.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好"}'
```
