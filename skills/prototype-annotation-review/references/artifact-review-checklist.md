# 原型标注 Codex 产物审阅清单

## 1. 证据定位

- 最新 AI 自检报告：`/var/lib/jarvis/files/ai-reports/`
- 项目 incoming：`/var/www/pmlophy.com/<project>-incoming/`
- 部署日志：`/var/log/jarvis-deploy.log`
- 正式目录：`/var/www/pmlophy.com/project/<project>/`

先按时间排序，确认报告、ZIP、部署日志属于同一轮任务。

## 2. ZIP 核验

```bash
ZIP=/var/www/pmlophy.com/<project>-incoming/<artifact>.zip
stat -c '%n | %s bytes | %y' "$ZIP"
unzip -l "$ZIP" | sed -n '1,30p'
```

必须确认：

- ZIP 真实存在；
- 第一层有 `index.html`；
- 包含 `annotation-kit/runtime.js`；
- 包含 `annotation-kit/runtime.css`；
- 包含 `annotation-kit/annotation.bundle.json`；
- 报告中的大小、SHA-256 与远端文件一致。

## 3. Bundle 静态核验

解析 `annotation.bundle.json`，至少记录：

- 标注总数；
- 页面模板数；
- selector 数量及重复情况；
- `sourceRefs` 缺失数；
- workspace coverage 是否全量映射；
- 每页 annotation id 是否从 1 连续；
- bundle selector 是否能在源码或构建产物中找到对应 `data-anno`。

## 4. 运行时专项核验

遇到 runtime 修复时，必须检查真实特征而不是只看报告：

- SPA 路由切换后，徽章和已打开标注清单是否都刷新为当前页面；
- 路由切换后旧页 popup、旧页待确认数据是否关闭/隔离；
- `localStorage` key、待办导出文件名是否按项目和页面隔离；
- 页面入口按钮、徽章、清单点击、高亮定位是否仍可用；
- 滚动事件是否仍只测量徽章，不重建滚动容器。

## 5. 上传与部署分级

```text
Codex build 通过       ≠ 已上传
ZIP 到 incoming        ≠ 已部署
正式目录文件更新       ≠ 功能验收完成
HTTP 200               ≠ 新版本生效
```

只有以下证据都成立，才能写“已部署并验证”：

1. 部署脚本成功；
2. `/var/log/jarvis-deploy.log` 有本轮包名；
3. 正式目录的 `index.html`/runtime/bundle 时间或 hash 更新；
4. 线上 HTTP 正常；
5. 本轮修复对应的页面功能实测通过。

如果 incoming 有包但正式目录仍是旧 hash，结论必须写：

```text
已修改、已构建、已上传；尚未正式部署，待部署后验收。
```
