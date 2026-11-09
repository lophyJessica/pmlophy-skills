# Forge 部署常见坑与恢复 SOP

## 1. dist 部署会冲掉 docs/flow/ 文件

`docs/flow/index.html` 和 `docs/flow/flowchart.md` 是手动创建的渲染页面，不在 `npm run build` 的 Vite 输出里。每次部署 dist 都会清空这两个文件。

**恢复命令:**
```bash
mkdir -p /var/www/pmlophy.com/project/forge-erp/docs/flow
mkdir -p /var/www/pmlophy.com/project/forge-wms/docs/flow
cp /root/notes/projects/forge-erp/docs/flow/index.html /var/www/pmlophy.com/project/forge-erp/docs/flow/
cp /root/notes/projects/forge-erp/docs/flow/flowchart.md /var/www/pmlophy.com/project/forge-erp/docs/flow/
cp /root/notes/projects/forge-wms/docs/flow/index.html /var/www/pmlophy.com/project/forge-wms/docs/flow/
cp /root/notes/projects/forge-wms/docs/flow/flowchart.md /var/www/pmlophy.com/project/forge-wms/docs/flow/
chmod 644 /var/www/pmlophy.com/project/forge-erp/docs/flow/* /var/www/pmlophy.com/project/forge-wms/docs/flow/*
nginx -t && systemctl reload nginx
```

> ⚠️ 注意：恢复命令中的 flowchart.md 源路径是 `docs/flow/flowchart.md`，不是 `docs/产品结构图_flow.md`。详见下面第 5 节。

## 2. 部署后 docs 路径规范

| 路径 | 内容 |
|------|------|
| `/docs/api/` | Swagger API 文档 |
| `/docs/flow/` | 产品结构图 mermaid 渲染页面 |

访问方式:
- `https://pmlophy.com/project/forge-erp/docs/flow/` → 渲染后的产品结构图
- `https://pmlophy.com/project/forge-erp/docs/api/` → Swagger

## 3. VPS 无法 push GitHub

VPS 无 GitHub token，不要 commit + push。文件修改走飞书附件 → 用户 Mac → commit + push 流程。

## 4. 部署后校验清单

- [ ] ERP 主页 200
- [ ] WMS 主页 200
- [ ] docs/flow/ 200(非 403)
- [ ] docs/api/ 200(非 403)
- [ ] docs/flow/ 渲染出 mermaid 图(非空白页)
- [ ] 缩放按钮可用(不截断、不撑开页面)

## 5. 同名文件陷阱——两路径复制的错位

**现象**: 用户在 Mac 更新 markdown → push → VPS pull → 复制到部署目录 → 页面不显示新内容。排查 N 轮才发现根因。

**根因**: 源仓库里同时存在两条 markdown 文件，内容不同:
- `docs/产品结构图_flow.md` — 旧版或子集（e.g. 11310 字节，只有出库链）
- `docs/flow/flowchart.md` — 最新更新版（e.g. 15876 字节，含入库链）

部署恢复命令抄错了源路径，一直用旧的 `产品结构图_flow.md` → 部署目录永远看不到新增内容。

**排查方法**:
```bash
wc -c docs/产品结构图_flow.md docs/flow/flowchart.md   # 对比字节数
grep -c "INBOUND\|入库" docs/flow/flowchart.md          # 确认新内容位置
```

**教训**: 涉及 markdown 内容更新的部署恢复时，先 `wc -c` 对比源文件和系统里的同名文件，确认复制了正确的版本。不存在"只有一份"，很容易踩同名双路径的坑。

**本次实战记录** (2026-07-16 WMS 入库链): 入库链更新在 `docs/flow/flowchart.md`(15876字节)，部署恢复命令反复复制 `docs/产品结构图_flow.md`(11310字节)，用户刷新 9 轮都没看到入库链。最后用 `wc -c` 对比发现两文件不等长才定位。
