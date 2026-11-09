# 原型标注系统 多项目铺开（CRM→WMS→ERP）

forge-crm 是成熟样板（skill + runtime + annotations 全在），把标注系统铺到其他前端项目（wms/erp）的标准做法。

## 权威样板结构（forge-crm）
```
prototype-annotation/                  # skill 根（SKILL.md + agents + assets/annotation-kit + scripts + references + tests）
front-prototype/public/annotation-kit/ # runtime.js + runtime.css + annotation.config.json + 两个 schema + annotation.bundle.json
index.html                              # <link runtime.css> + <script src=/.../annotation-kit/runtime.js>
main.tsx / App.tsx                      # vitaminAnnotationRuntime 兜底加载 + boot()
prd-docs/<模块>/annotations/            # 标注源（pages/*.md）+ annotation.config.json + coverage.md
```

## 初始化（架系统，不是铺标注）—— 可交给 Codex
初始化阶段【只搭标注系统架子】：复制 skill + 建 public/annotation-kit/ + 注入 runtime + 空 bundle（annotations=[]）。
- 不铺业务标注、不改业务页面业务逻辑（main/App 注入 runtime 除外）
- runtime.js/css/schema 与 forge-crm 哈希保持一致（不改 runtime 逻辑）
- 验证：build 通过 + 线上 HTTP 200 + 页面出现"原型标注/标注清单"入口 + 点开面板默认不展开、业务标注数=0

## ⚠️ 关键环境差异（必须先摸清）
1. **项目路径必须用 Codex 实际跑的机器（Mac）**：`/Users/liulongfei/个人文件/forge-*`，
   **不能写 VPS 的 `/root/repos/forge-*`**（用户纠正过——Codex 在 Mac 跑，路径写成 VPS 会找不到）。
2. **前端组件库**：forge-crm 是 Shadcn/Tailwind；**wms/erp 在 Mac 上是 React+Ant Design**。
   - 初始化（复制 skill + runtime 注入）**与组件库无关**——两种都能做
   - 但【铺实际标注】时，antd 页面要用 antd 组件结构加 data-anno（和 CRM 的 Shadcn JSX 结构不同）——铺标注那轮指令要按目标组件库写。
3. **VPS 仓库 vs Mac 工作区可能不同步**（Codex 只传 zip 不 push → VPS /root/repos 落后）——查代码以 Mac 工作区/线上 zip 为准，别拿 VPS 旧目录判断组件栈。

## 部署
- zip 必须"解压即根"（cd dist && zip 的顶层是 index.html，不带 dist/ 前缀）
- rsync 到 `<项目>-incoming/`；VPS deploy-all.sh 验证 URL 用 /project/ 前缀
- **某些项目 cron 只检测不自动部署**——WMS 实测需手动 `bash /root/deploy-all.sh --deploy forge-wms`
- 每次部署后：线上 annotation.bundle.json 的标注块数/id 独立从1 都要重新核（不能只看"部署完成"日志）

## 自检报告命名
- 让 Codex 报告文件名带【项目名】（如 forge-wms-...），否则通用名"AI自检报告-标注系统初始化.md"在 VPS 积累后难分辨是哪项目。
