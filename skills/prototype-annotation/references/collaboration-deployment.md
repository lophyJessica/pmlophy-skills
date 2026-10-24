# 协作与部署

## 只读架构

页面运行时是只读标注查看器。源码与 bundle 分离、编译发版门禁见 SKILL.md §3.3 与 §7.1。迭代上线后原型端清空标注的操作见 §4.3。

```txt
annotations 源 (md + config) -> 编译 -> annotation.bundle.json -> 部署到原型 public/annotation-kit
runtime 只读展示 bundle；不在浏览器内写回 Markdown
```

不要添加浏览器编辑器、草稿存储、save 端点、持久化适配器、账号体系或标注写入 API。

## 本地使用

必备组件：

- `annotation-kit/runtime.js`
- `annotation-kit/runtime.css`
- `annotation-kit/annotation.bundle.json`
- 位于 PRD 旁或用户指定位置的 `annotations/` 目录

用户直接编辑 Markdown 或请 Codex 更新。重新编译所属 config 或共享工作区清单后，运行时刷新会重读 bundle、更新已打开弹层并移除已删标注。

## 云端使用

将编译好的标注 bundle 与原型一并部署。源 PRD 与源标注 Markdown 可不必放在公开资源中。云端运行时可以：

- 读取已部署 bundle。
- 渲染 Markdown 与 Mermaid。
- 展示角标与弹层。
- 在不整页刷新的情况下刷新已部署 bundle。
- 查看并下载全部标注。

云端运行时不能修改标注 Markdown。变更须走常规源码管理与部署流程。

## 团队协作

沿用项目已有的仓库流程：

```txt
edit annotation Markdown or ask Codex to update it
  -> compile and validate coverage
  -> review diff or pull request
  -> merge
  -> deploy
  -> read-only runtime shows the new version
```

`changelog.md` 记录有意义的标注变更。仅在用户明确需要可恢复快照时，才可选使用 `versions/`。

## 安全边界

因运行时为只读，不需要标注专用账号、写入授权、数据库、冲突解决或文件写入端点。已部署的 Markdown 与 Mermaid 仍会作为页面内容渲染，须保证渲染安全。
