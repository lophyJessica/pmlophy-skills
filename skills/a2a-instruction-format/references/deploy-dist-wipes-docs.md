# forge 部署怪癖与修复

## dist 部署会清空目标目录

`rm -rf /var/www/pmlophy.com/project/forge-erp/* && cp -r dist/* /var/www/pmlophy.com/project/forge-erp/` 会清空目标目录中**所有**文件，包括非构建产物。

**会被冲掉的：**
- `docs/flow/index.html` — 产品结构图渲染页
- `docs/flow/flowchart.md` — mermaid 源文件
- `docs/api/` 下的 Swagger 文件

**部署后的恢复命令：**
```bash
# 重新创建 docs 子目录并恢复文件
mkdir -p /var/www/pmlophy.com/project/forge-erp/docs/flow
mkdir -p /var/www/pmlophy.com/project/forge-wms/docs/flow
cp /root/notes/projects/forge-erp/docs/flow/index.html /var/www/pmlophy.com/project/forge-erp/docs/flow/
cp /root/notes/projects/forge-wms/docs/flow/index.html /var/www/pmlophy.com/project/forge-wms/docs/flow/
cp /root/notes/projects/forge-erp/docs/产品结构图_api.md /var/www/pmlophy.com/project/forge-erp/docs/flow/flowchart.md
cp /root/notes/projects/forge-wms/docs/产品结构图_flow.md /var/www/pmlophy.com/project/forge-wms/docs/flow/flowchart.md
```

## nginx 配置顺序

具体子路径必须放在通用路径之前：
```nginx
# 先匹配 docs/flow/ → 再匹配 /project/forge-erp/
location /project/forge-erp/docs/flow/ { ... }
location /project/forge-erp/ { ... }
```

## 文件权限

`write_file` 写入的文件默认权限可能是 600，nginx 无法读取 → 403。部署后检查：
```bash
chmod 644 /var/www/pmlophy.com/project/forge-*/docs/flow/index.html
```

## VPS 不能 push GitHub

VPS 没有 GitHub token。任何时候都不要从 VPS 做 git push。需要把文件放到仓库时，发内容给用户让用户自己在 Mac 上操作。
