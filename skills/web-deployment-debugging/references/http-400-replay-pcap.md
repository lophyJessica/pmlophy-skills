# 前端 → API 400 无日志排障：pcap 抓真实请求体重放复现

> 场景：前端报 HTTP 400，但用简单构造的请求复现不了（200），服务端又没留请求日志。
> 2026-08-26 罗宾 400 invalid_image_url 实踩（根因：历史消息里 image_url 是服务器本地路径 /var/lib/jarvis/files/...，Hermes 校验拒绝）。

## 为什么需要这招

前端发全量历史（200 条 messages）时，400 藏在某一条历史消息里。逐条猜测组合复现效率极低——**真实请求体里就有答案，抓下来重放即可**。

## 步骤

### 1. 确认 400 且请求确实到达后端
```bash
grep '/p/jarvis/v1/chat/completions' /var/log/nginx/access.log | tail -3
# 400 180 = 响应 180 字节，很小的 JSON 错误
```

### 2. 起 tcpdump 抓 loopback 上的后端端口（nginx→后端是 127.0.0.1 流量）
```bash
tcpdump -i lo -w /tmp/cap.pcap 'port 8642' 2>/dev/null &   # 后台
# 让用户在前端再触发一次请求（"发条消息"）
```
⚠️ `-w` 二进制 pcap 才完整；`-A` 文本模式会丢/乱码（中文变点号、gzip 响应不可读）。

### 3. 从 pcap 提取 TCP payload 重组请求体
写小脚本（python，解析 pcap 头 + TCP 段，按 seq 排序重组）：
```python
# 提取 src_port→dst_port 的 TCP payload，按 seq 升序拼接，去重合并
# 找到 JSON body 起点（第一个 '{'），按 Content-Length 截取
```
存为 /tmp/req-extracted.json。参考实现：pcap 全局头 24 字节（linktype 在 offset 20）→ 包记录头 16 字节（incl_len）→ 以太网 14 字节（VLAN 18）→ IP 头（ihl）→ TCP 头（data offset）→ payload。

### 4. 重放拿响应体
```bash
KEY=$(grep -E '^API_SERVER_KEY=' /root/.hermes/.env | cut -d= -f2)
curl -sS -m 60 http://127.0.0.1:8642/p/jarvis/v1/chat/completions \
  -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' -d @/tmp/req-extracted.json
# → {"error":{"message":"Image inputs must use http(s) URLs or data:image/... URLs.",
#     "param":"messages[175].content","code":"invalid_image_url"}}
```

### 5. 定位具体消息
python 读请求体 JSON，打印 messages[175] 的 content 结构 → 发现 image_url 是 `/var/lib/jarvis/files/...` 本地路径。

## 关键判读

- 400 响应 180 字节左右 → Hermes api_server.py 的 `_multimodal_validation_error`（content 数组里 image_url 非法）——校验规则：只接受 `http(s)://` 或 `data:image/` 开头
- 请求到了后端（tcpdump 抓到 POST）但后端零响应包（只有 ACK）→ 请求被挂起/框架层拒绝，看 nginx 同秒是否已记 400（可能 auth_request 或 aiohttp 层拦截）
- nginx `auth_request` 失败返回 401（不是 400）——前端显示 400 时先排除 auth_request

## 教训

- 400 错误体极小（180B）且服务端不记日志时，**抓真实请求体重放**是最快路径，别猜组合
- 前端发送全量历史时，**任何一条历史消息的非法内容都会让整个请求 400**——前端发送前必须清洗（见 jarvis-dev 的 sanitizeMessages 坑）
