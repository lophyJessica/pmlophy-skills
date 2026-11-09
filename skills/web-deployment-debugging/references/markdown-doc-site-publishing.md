# Markdown 文档 → 门户 HTML 发布（含 Mermaid 图）

把 md 长文渲染成可发布的门户页（pmlophy.com/docs/）、让 mermaid 图真的画出来、并维护一个门户在线编辑器。

## 发布链路
1. 源文件集中放构建目录（md + `build.py`），改 md 后重建，不要在 HTML 上直接改。
2. `build.py`：python-markdown 渲染 md → `out-<名>.html`（模板内联 CSS，样式对齐既有页）。
3. 部署：`cp out-<名>.html /var/www/pmlophy.com/docs/<名>.html && chmod 644 /var/www/pmlophy.com/docs/*.html`。
4. 验证（必做，别只发不看）：
   `curl -sk https://pmlophy.com/docs/<名>.html --resolve pmlophy.com:443:127.0.0.1 -o /dev/null -w '%{http_code} %{size_download}'`
   再断言产物里的关键结构（见下），而不是只看 200。

## Mermaid 渲染——最容易翻车的一环
- **python-markdown 的 fenced_code 会 HTML 转义代码块内容**：`-->` 变 `--&gt;`、`"` 变 `&quot;`。mermaid 拿到转义串会解析失败或画错。
  **修法**：把 fenced mermaid 块换成 `<pre class="mermaid">` 时，对捕获内容做 `html.unescape()`：
  ```python
  pat = re.compile(r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.S)
  html = pat.sub(lambda m: '<pre class="mermaid">' + html_module.unescape(m.group(1)) + '</pre>', html)
  ```
  ⚠️ 替换串别写成 raw string——`r"…\"mermaid\"…"` 会把反斜杠写进 HTML（`class=\"mermaid\"`），页面上属性就废了。
- **验证**：渲染后断言每个 `<pre class="mermaid">` 块内**不含** `--&gt;` / `&quot;`；块数 = md 里 mermaid 代码块数；顺带看块内容首行是不是 `flowchart`/`mindmap`。
- **mermaid 块不要放进 blockquote（`>` 引用）里**——嵌套 fenced code 解析不对，会退化成纯文本；mermaid 一律放顶层。
- **节点标签里不要用 `<br/>`**：同样被转义成字面量。要分行就用短标签。
- **各平台 mermaid 支持不一致**：门户 / 语雀 / 公司 wiki 通常能渲染；**编辑器内置 md 预览（如 Cursor）常常不画**，且随版本变。定稿后必须在真正的发布页过一眼，别拿编辑器预览当最终效果。

## 门户在线编辑器（doc-edit 小服务）
- 结构：stdlib `http.server` + 令牌文件（`hmac.compare_digest` 校验）+ 白名单文件名 + systemd unit + nginx：
  ```
  location /doc-edit/ { proxy_pass http://127.0.0.1:8095; }
  ```
- **`proxy_pass` 不要带 URI 尾缀**（只写 host:port）→ 保留 `/doc-edit/` 前缀，handler 按 `/doc-edit/load`、`/doc-edit/save` 匹配；带尾缀会把前缀剥掉导致 404。
- 保存即重渲染：POST 内容 → 写回 md → 跑 `build.py` → cp 到 `/var/www` → 返回结果。
- **坑：systemd 用的解释器可能缺构建依赖**。服务以 `/usr/bin/python3` 运行，而登录 shell 的 `python3` 是 venv（有 `markdown`）→ 保存时报 `ModuleNotFoundError: No module named 'markdown'`，读能读、写就废。**修法**：`apt-get install -y python3-markdown`（或把 ExecStart 指向确实装了依赖的解释器），然后 `systemctl restart <服务>`。
- **部署后必须真跑一次完整保存链路**（curl POST 原样写回 + 复核门户 200），不要只看 `systemctl is-active`——服务活着但保存会炸。
- 令牌这类凭据只放在服务器上的文件里，聊天/前端输入框只用于回填，不落明文到对话。

## 与其他 skill 的关系
- nginx location / restart 行为、Cloudflare 缓存、静态目录权限：见本 skill 主体的对应小节。
- 若产物是评审/交付档（自包含、base64 内嵌图、导入语雀/Confluence）→ 走 `prd-doc-authoring`。
