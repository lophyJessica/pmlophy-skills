# React SPA 子路径部署 debug 清单

> 来源: forge-erp(2026-07-29)、geshuiCode/liushuiCode(2026-07-28)、copy-wms(2026-07-22)

## 症状速查

| 症状 | 根因 | 修复 |
|------|------|------|
| nginx 200 但页面 404/空白 | BrowserRouter basename=`/` 而非 `/project/xxx/` | 设 `basename="/project/xxx/"` |
| 资源 404(JS/CSS) | 绝对路径 `/assets/` 在子目录下不存在 | 相对路径 `./assets/` + `<base href="/project/xxx/">` 或 绝对路径 `/project/xxx/assets/` |
| nginx 500/internal redirect cycle | alias + try_files 回写循环 | 用 `@fallback` named location |
| URL 路径重复拼接 | 按钮用相对路径 navigate | 统一为绝对路径 `${B}/xxx` |
| `<base>` 导致 HashRouter 失效 | `<base>` 劫持所有 href | 删 `<base>`,HashRouter 不需要 |
| CDN 资源可加载但页面交互异常 | Tailwind CDN 在生产环境不稳定 | npm install tailwindcss 代替 CDN |

## 分步诊断

```
1. curl -sk -o /dev/null -w "%{http_code}" URL → 确认 nginx 返回 200(index.html)
2. curl -sk URL | grep "script.*src\|link.*href" → 确认资源路径格式
3. strings dist/assets/*.js | grep "basename" → 确认 React Router basename
4. strings dist/assets/*.js | grep "supplier-quote\|route.*path" → 确认路由编译进了 bundle
5. nginx -t && tail -3 /var/log/nginx/error.log → 确认 nginx 配置与错误
```

## nginx SPA 标准配置(带 @fallback)

```nginx
location /project/xxx/ {
    alias /var/www/pmlophy.com/project/xxx/;
    try_files $uri $uri/ @xxx-spa;
}
location @xxx-spa {
    rewrite ^ /project/xxx/index.html last;
}
```

不用 `try_files $uri $uri/ /project/xxx/index.html` —— alias 路径下可能触发重写循环。
