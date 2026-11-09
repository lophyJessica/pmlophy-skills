# VPS 图片/文件 path 存储方案（根治"聊天图片历史刷新丢失"）

## 问题
前端把图片 **base64 塞进消息 content**，导致三个问题：
1. 云端历史膨胀（一条图几 MB，200 条历史爆内存/存储）
2. 跨设备/换浏览器/清缓存后图片不可见（本地 Dexie 没了就丢）
3. 超大 base64 塞 content 导致点击预览组件解析失败（"点不开"）

后端 `get_history` 还会主动剥离 image_url base64（只留 text），加剧刷新丢失。

## 根治方案
**图片上传 VPS 存 path，消息 content 只存轻量 path，前端渲染时拼 URL。**

```
前端发送带图消息：
  1. 图片 base64 → Blob/File
  2. POST /p/jarvis/file/upload → 得磁盘 path（/var/lib/jarvis/files/{user}/{ts}-{hash}-{name}）
  3. 消息 content 里 image_url.url = path（不再是 base64）
  4. 云端历史只存轻量 path（不膨胀）
渲染/点击：
  5. 前端把 path 拼成完整 URL 展示（img src）+ 点击大图
```

## 后端（jarvis-file.py，8871）——可复用
原服务只有 `POST /file/upload`（只存不读）。补 `GET /file/get`：
- 防路径穿越：`realpath` + `os.path.commonpath([base,target])==base` 校验
- 按扩展名给 Content-Type（图片 inline / 文档 attachment）
- Cache-Control: public, max-age=31536000
- upload 接口顺带返回 `url` 字段给前端直接用

## nginx 双前缀要点
`jarvis-voice` 用 `/p/jarvis/file`，`jarvis-local` 用 `/p/jarvis-local/file`，两者 proxy_pass 到同一 8871。
**各 location 的 proxy_pass 必须带 URI（`proxy_pass http://127.0.0.1:8871/file`）**，否则裸 host:port 保留完整 URI 到 8871 → 404（见 SKILL.md nginx proxy_pass 尾缀坑）。

## 前端（Cursor 指令要点）
- 发送前 `uploadChatImageRefs`：base64 → uploadJarvisFile → content 存 path；上传失败降级回 base64（不丢图）
- `resolveMessageImageUrl`：`getApiBase() + /p/jarvis/file/get?path=` + encodeURIComponent 拼可访问 URL
- 渲染用 Ant Design `Image.PreviewGroup`（或等价）支持点击大图
- 保留旧 `mergeMessageContent` 兼容本地缓存 base64（可选）
- 注意：历史旧记录仍是 base64 需重发才变 path；换设备后靠服务端 path URL 兜底

## 验证
1. 直连 8871 `/file/get?path=...` 200 + content-type image/png + 字节一致
2. 走 nginx 公网 `/p/jarvis/file/get?...` 200 + 字节一致（跨设备可达）
3. 前端：发图 → 消息 content 是 path 非 base64 → 图上显示 → 点击大图 → 刷新仍显示 → 换浏览器也显示
