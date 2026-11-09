# 多 Agent 并行编排模式

> 强盛科技进销存 + WMS 双项目实战验证（2026-07-05 ~ 07-06）

## 工具分工

| Agent | 擅长 | 给什么活 |
|:--|:--|:--|
| 反重力（Gemini） | 前端页面生成、UI组件 | 单据列表/表单/详情、Swagger文档页面 |
| Codex（GPT-5.5） | 批量文件重构、架构迁移 | localStorage→Dexie.js、ER图+DDL、跨文件搜索替换 |

## 并行三原则

1. **文件隔离**：不同 Agent 不碰同一目录——Codex A 改 api/、Codex B 改 pages/、反重力改 public/
2. **依赖同步**：改了 package.json 的 Agent 必须在输出前跑 `npm install`（Codex 多次忘装 dexie 导致构建失败）
3. **路径规范**：指令中只用项目名+相对路径（`进销存Traininng/front-prototype/src/`），不用 `/Users/xxx/` 绝对路径——跨机器不兼容

## 红线禁止补丁

多线程指令专用红线：
```
- 不同 Agent 不碰同一目录（防文件冲突+安全拦截）
- 改了 package.json 依赖必须同步运行 npm install
- 路径用项目名+相对路径，不用绝对路径
```

## 线程上限

实测 5 线程（1反重力 + 4 Codex）稳定。6 以上人脑审查过载，不推荐。

## 成本

- 反重力 Gemini：免费
- Codex GPT-5.5：$5/天（5线程 × 批量重构任务）
- Mac Hermes computer-use A2A：~$1/次（140K token），**不推荐投产**——GUI权限审批+Electron焦点丢失导致死循环
