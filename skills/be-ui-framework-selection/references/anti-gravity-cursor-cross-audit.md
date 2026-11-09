# 反重力 vs Cursor 分工与交叉审计(实战验证)

> 2026-07-30 补充: 基于 forge-erp 全量 Ant Design 迁移 + Cursor P0-P2 审计的完整闭环。

## 分工矩阵

| | 反重力/Gemini | Cursor(Agent 模式) |
|------|:---:|:---:|
| 速度 | 极快,梭哈全量页面 | 较慢,逐个文件改 |
| 精度 | 低,叠代码不删旧,自作主张 | 高,精准定位+全局审计 |
| 适用 | 从零搭建/批量创建 | 精确修复/全局审计 |
| 坑 | 重复路由树,valueType 乱加,居中表单 | 有时改不生效(需清缓存) |

## 组合工作流

```
反重力批量生成 → Cursor 只读审计 → Cursor 精确修复 → 验证通过
```

## 反重力易犯错误(必查清单)

1. **叠罗汉** — 修改代码后不删旧,导致路由树翻倍(3→5→12套)
2. **valueType 乱加** — ProTable 列自动加 `valueType:'select'`,label 污染 cell value
3. **表单居中** — 给 Form 外层加 max-w 居中容器
4. **冗余行** — 一次指令修复一个 bug,可能连带改动无关文件
5. **不删缓存** — 改源码后 build 产物仍有旧逻辑(Vite 缓存未清理)

## Cursor 审计五步法

```
@codebase 审计以下5项,只读不改:
1. 搜"SKU00"或其他编码 → 列出位置,判断一致性
2. 搜"BrowserRouter\|createBrowserRouter" → 列出路由定义
3. 搜"SUPPLIER.*navigate\|SUPPLIER.*to=" → 列出角色跳转
4. 检查 src/pages/ 文件是否都在路由中注册
5. 列出所有 mock 数据文件,确认数据源唯一性

每项输出: 文件:行号 → 内容 → 严重度(高/中/低) → 建议
```

## 真实案例

反重力梭哈全量 antd 迁移后,Cursor 审计发现:

### P0(阻断)
- 供应商编码 SUP001 vs VEND001 三处不一致 → 报价匹配全挂
- 主数据双份定义(purchaseOrder.ts ↔ baseData.ts) → 商品缺 SP-007

### P1(安全)
- 无角色路由守卫 → 供应商能访问 /purchase/orders
- 合同/通知用 localStorage 不用 Dexie → 数据分裂

### P2(优化)
- App.tsx 内 Layout 死代码 → 1814→785 行
- 5 次 commit 全量修复,build 均通过

## 红线

- 反重力生成后必须 Cursor 审计。不要反重力自己改自己的 bug
- 不要同一个 Agent 自己审自己——"不会说自己错了"
- Cursor 用 Agent 模式(只读审计),不动代码
