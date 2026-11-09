# Forge 部署常见问题

## 反重力/Codex 打包的 dist.zip 路径不稳定

反重力和 Codex 打包 dist 时，zip 内部路径不统一，可能嵌套一层：

- 正常：`dist/index.html`、`dist/assets/...`
- 异常：`wms-dist/dist/index.html` 或 `dist/dist/index.html`

部署时不要硬编码 `mv /tmp/pkg-new/dist/*`，改用自动定位：

```bash
cd /root/.hermes/cache/documents
rm -rf /tmp/pkg-new 2>/dev/null
unzip -o <file>.zip -d /tmp/pkg-new 2>&1 | tail -2

# 自动找到 index.html 所在的目录
SRC=$(dirname $(find /tmp/pkg-new -name "index.html" | head -1))

rm -rf /var/www/pmlophy.com/project/forge-<erp|wms>/* 2>/dev/null
cp -r "$SRC"/* /var/www/pmlophy.com/project/forge-<erp|wms>/ 2>/dev/null
rm -rf /tmp/pkg-new /var/www/pmlophy.com/project/forge-<erp|wms>/__MACOSX 2>/dev/null

curl -sk -o /dev/null -w "%{http_code}\n" https://pmlophy.com/project/forge-<erp|wms>/
```

## 部署完验证

项目在 `/project/forge-erp/` 和 `/project/forge-wms/`，每个有独立的 nginx location + alias。

## nginx 配置要点

- ERP 和 WMS 各有独立 `location` 块，用 `alias` 而非 `root`
- `try_files $uri $uri/ /project/forge-<name>/index.html` 处理 SPA 路由
- HashRouter 的路由在 `#` 后面，服务器看不到，`try_files` 兜底即可
- 不要共用根 location 的 `try_files`，否则旧路径的 `/wms/` 请求会被错误路由
