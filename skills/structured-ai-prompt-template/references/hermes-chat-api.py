#!/usr/bin/env python3
"""Hermes Chat API bridge — exposes hermes chat as a REST endpoint.
Usage: python3 hermes-chat-api.py   # starts on port 9120
Then nginx proxy: /api/chat → http://127.0.0.1:9120/chat
"""
import subprocess, json, os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 9120
HTML_PAGE = """<!DOCTYPE html>
<html lang="zh">
<head><meta charset="UTF-8"><title>Hermes Chat API</title>
<style>body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;max-width:600px;margin:50px auto;padding:20px;background:#0f172a;color:#e2e8f0}
code{background:#1e293b;padding:2px 6px;border-radius:4px}h1{color:#38bdf8}</style></head>
<body>
<h1>Hermes Chat API</h1>
<p>POST <code>/api/chat</code></p>
<pre>{"message": "input"}</pre>
<p>Return: <code>{"reply": "output"}</code></p>
</body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))

    def do_POST(self):
        if self.path != "/chat":
            self.send_error(404); return
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n))
            msg = body.get("message", "")
            if not msg:
                self.send_error(400); return
            r = subprocess.run(
                ["hermes", "chat", "-q", msg, "-Q"],
                capture_output=True, text=True, timeout=60,
                env={**os.environ, "HOME": "/root"}
            )
            reply = r.stdout.strip() or r.stderr.strip()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self.send_error(500, str(e))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

HTTPServer(("127.0.0.1", PORT), H).serve_forever()
