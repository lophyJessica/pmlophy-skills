# SPA 部署 blank page 排障清单

## 三步检查

### 1. 资源能否加载？
```bash
curl -sk -o /dev/null -w "%{http_code}" https://域名/子路径/
curl -sk -o /dev/null -w "%{http_code}" "https://域名/子路径/assets/index-xxx.js"
```
JS 404 → Vite `base` 或 HTML `<base href>` 不匹配。

### 2. SPA 路由是否 fallback 到 index.html？
```bash
curl -sk -o /dev/null -w "%{http_code}" https://域名/子路径/任意路由
```
返回 200 + HTML 内容 → nginx 正常。返回 404 → 缺 `try_files`。

### 3. React Router basename 是否正确？
```bash
strings dist/assets/index-*.js | grep -o 'basename:[^,;]*'
```
必须等于 `"/子路径"`，不是 `"/"`。

## 三角对齐公式

```
Vite base       = /子路径/
HTML base href  = /子路径/
Router basename = /子路径
nginx try_files = /子路径/index.html
```

四处全部一致 → 页面正常。

## nginx alias 重写循环修复

当 `try_files $uri $uri/ /子路径/index.html` 与 `alias` 冲突时：

```nginx
location /子路径/ {
    alias /var/www/path/子路径/;
    try_files $uri $uri/ @子路径-fallback;
}
location @子路径-fallback {
    rewrite ^ /子路径/index.html last;
}
```

## forge-erp 实例

- alias: `/var/www/pmlophy.com/project/forge-erp/`
- base href: `/project/forge-erp/`
- Router basename: `/project/forge-erp`
- 域名: `https://pmlophy.com/project/forge-erp/`
