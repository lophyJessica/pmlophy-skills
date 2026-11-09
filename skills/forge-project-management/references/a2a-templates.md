# A2A 指令模板

## ERP 审计指令
```
Context:
forge-erp 前端项目，经多轮迭代后需做四维对齐审计。

Request:
逐文件交叉对比，找出不一致项：
1. Context对齐：context/ vs PRD术语/单号前缀/边界约束
2. PRD与原型对齐：prd-docs/ Demo PRD vs front-prototype/src/pages/ tsx
3. 流程对齐：context/流程 vs PRD状态机
4. 功能清单对齐：context/03 vs prd-docs/实际目录 vs pages/实际页面

Output format:
P0/P1/P2分级清单，每条：严重级|维度|问题|源文件|目标文件|修复方向

红线禁止：只审计不改代码，禁止commit/push
```

## WMS 审计指令
```
Context:
forge-wms 前端项目，经多轮迭代后需做四维对齐审计。

Request:
逐文件交叉对比，找出不一致项：
1. Context对齐：context/ vs PRD术语/单号前缀/边界约束
2. PRD与原型对齐：prd-docs/ Demo PRD vs front-prototype/src/pages/ tsx
3. 流程对齐：context/流程 vs PRD状态机
4. 功能清单对齐：context/03 vs prd-docs/实际目录 vs pages/实际页面

Output format:
P0/P1/P2分级清单，每条：严重级|维度|问题|源文件|目标文件|修复方向

红线禁止：只审计不改代码，禁止commit/push
```

## 页面修复指令(反重力)
```
Context:
forge-<erp|wms> 前端项目，需要修复以下PRD对齐问题：
[列出具体问题+文件路径]

Request:
1. cd forge-<erp|wms>/front-prototype
2. [逐条列出具体修复操作]
3. npm run build，打包 dist.zip

Output format:
编译成功 → dist.zip
编译失败 → 逐条错误明细

红线禁止：
- [具体约束]
- 禁止改 vite.config、tsconfig、package.json
- 禁止 npm audit fix
- 禁止 git commit 或 push
```

## 菜单/UI 改动指令(反重力)
```
Context:
forge-<erp|wms> 前端项目，侧边栏菜单需做交互调整。[说明具体问题]

Request:
1. cd forge-<erp|wms>/front-prototype
2. 找到侧边栏组件 [Sidebar.tsx / NavMenu.tsx]
3. [具体改动描述]
4. npm run build，打包 dist.zip

红线禁止：
- 只改菜单交互/样式，不碰其他页面逻辑
- 禁止改 vite.config、tsconfig、package.json
- 禁止 npm audit fix
- 禁止 git commit 或 push
```
