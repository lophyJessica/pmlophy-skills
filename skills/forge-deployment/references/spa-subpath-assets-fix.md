# SPA 子路径部署: 资源加载修复

> 当 React/Vite SPA 部署在 `/subPath/` 下,页面空白或资源 404 时的标准修复流程。

## 症状
- HTML 加载成功(200),但页面空白
- 浏览器 F12 → 资源 `/assets/xxx.js` 返回 404
- JS 文件请求的是根路径 `/assets/`,而非 `/subPath/assets/`

## 根因
1. Vite 构建默认生成绝对路径: `<script src="/assets/index-xxx.js">`
2. `<base href="/subPath/">` 只影响**相对**路径,不影响以 `/` 开头的绝对路径
3. nginx `alias` + `try_files $uri /subPath/index.html` 可能内部重定向循环

## 三步修复(按顺序执行,不走回头路)

### 1. HTML: 绝对路径改相对 + 加 base 标签

```html
<head>
  <meta charset="UTF-8" />
  <base href="/subPath/" />   <!-- 必须放第一行 -->
  ...
  <script type="module" src="assets/index-xxx.js"></script>  <!-- 去掉开头的 / -->
  <link rel="stylesheet" href="assets/index-xxx.css">        <!-- 去掉开头的 / -->
</head>
```

### 2. nginx: alias + @fallback 避免重定向循环

```nginx
location /subPath/ {
    alias /var/www/example.com/tools/subPath/;
    try_files $uri $uri/ @subPathFallback;
}
location @subPathFallback {
    rewrite ^ /subPath/index.html last;
}
```

**为什么不用 `try_files $uri $uri/ /subPath/index.html`?**
→ alias 内部重定向后会被同一个 location 块再次匹配,导致重定向循环(nginx error log: "rewrite or internal redirection cycle")。用 `@named_location` + `rewrite ... last` 相当于告诉 nginx"重新开始匹配请求",会正确找到 HTML 文件。

### 3. 验证

```bash
curl -sk -o /dev/null -w "%{http_code}" https://domain.com/subPath/
curl -sk -o /dev/null -w "%{http_code} %{size_download}" https://domain.com/subPath/assets/index-xxx.js
```

JS 文件 200 + 大小 > 100KB → 负载正常加载。

## 适用于

- React/Vite/Vue SPA 部署在 nginx 子目录
- 多个 SPA 共用一个域名,各自在子路径 `/app1/` `/app2/`
- 不想单独配域名或 server block 的场景

## 已验证的实例

| 项目 | URL | 部署日期 |
|------|-----|---------|
| geshuiCode | pmlophy.com/geshuiCode/ | 2026-07-27 |
| liushuiCode | pmlophy.com/liushuiCode/ | 2026-07-27 |
| forge-erp | pmlophy.com/project/forge-erp/ | 2026-07-15 |
| forge-wms | pmlophy.com/project/forge-wms/ | 2026-07-15 |
