---
name: vercel-react-best-practices
description: 当要写、评审或重构 React / Next.js 代码时用。来自 Vercel 工程团队的 React 与 Next.js 性能优化准则，覆盖组件写法、页面、数据获取、打包体积与性能优化场景。
license: MIT
metadata:
  author: vercel
  version: "1.0.0"
---

# Vercel React 最佳实践

面向 React 与 Next.js 应用的完整性能优化指南，由 Vercel 维护。共 8 类 70 条规则，按影响优先级排序，用于指导自动化重构与代码生成。

## 何时适用

在以下场景参考本准则：
- 编写新的 React 组件或 Next.js 页面
- 实现数据获取（客户端或服务端）
- 评审代码中的性能问题
- 重构既有 React/Next.js 代码
- 优化打包体积或加载时间

## 按优先级的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|----------|----------|--------|--------|
| 1 | 消除瀑布请求 | CRITICAL | `async-` |
| 2 | 打包体积优化 | CRITICAL | `bundle-` |
| 3 | 服务端性能 | HIGH | `server-` |
| 4 | 客户端数据获取 | MEDIUM-HIGH | `client-` |
| 5 | 重渲染优化 | MEDIUM | `rerender-` |
| 6 | 渲染性能 | MEDIUM | `rendering-` |
| 7 | JavaScript 性能 | LOW-MEDIUM | `js-` |
| 8 | 高级模式 | LOW | `advanced-` |

## 速查

### 1. 消除瀑布请求（CRITICAL）

- `async-cheap-condition-before-await` - 在 await 标志或远程值之前先检查廉价的同步条件
- `async-defer-await` - 将 await 移到实际使用的分支内
- `async-parallel` - 对独立操作用 Promise.all()
- `async-dependencies` - 对部分依赖使用 better-all
- `async-api-routes` - 在 API 路由中尽早启动 promise、尽量晚 await
- `async-suspense-boundaries` - 用 Suspense 流式输出内容

### 2. 打包体积优化（CRITICAL）

- `bundle-barrel-imports` - 直接导入，避免 barrel 文件
- `bundle-analyzable-paths` - 优先静态可分析的导入与文件系统路径，避免过大 bundle 与 trace
- `bundle-dynamic-imports` - 对重型组件使用 next/dynamic
- `bundle-defer-third-party` - 在水合后再加载分析/日志
- `bundle-conditional` - 仅在功能激活时加载模块
- `bundle-preload` - 悬停/聚焦时预加载以提升感知速度

### 3. 服务端性能（HIGH）

- `server-auth-actions` - 像 API 路由一样认证 server actions
- `server-cache-react` - 用 React.cache() 做单次请求去重
- `server-cache-lru` - 用 LRU 缓存做跨请求缓存
- `server-dedup-props` - 避免在 RSC props 中重复序列化
- `server-hoist-static-io` - 将静态 I/O（字体、logo）提升到模块级
- `server-no-shared-module-state` - 在 RSC/SSR 中避免模块级可变请求状态
- `server-serialization` - 最小化传给客户端组件的数据
- `server-parallel-fetching` - 重组组件以并行拉取
- `server-parallel-nested-fetching` - 在 Promise.all 中对每项链式嵌套拉取
- `server-after-nonblocking` - 用 after() 处理非阻塞操作

### 4. 客户端数据获取（MEDIUM-HIGH）

- `client-swr-dedup` - 用 SWR 自动去重请求
- `client-event-listeners` - 去重全局事件监听
- `client-passive-event-listeners` - 滚动使用 passive 监听
- `client-localstorage-schema` - 版本化并最小化 localStorage 数据

### 5. 重渲染优化（MEDIUM）

- `rerender-defer-reads` - 不要订阅仅在回调中使用的 state
- `rerender-memo` - 将昂贵计算抽到 memo 组件
- `rerender-memo-with-default-value` - 提升默认非原始 props
- `rerender-dependencies` - 在 effect 中使用原始类型依赖
- `rerender-derived-state` - 订阅派生布尔值，而非原始值
- `rerender-derived-state-no-effect` - 在渲染时派生 state，而非 effect
- `rerender-functional-setstate` - 用函数式 setState 获得稳定回调
- `rerender-lazy-state-init` - 昂贵初始值向 useState 传函数
- `rerender-simple-expression-in-memo` - 简单原始值不必 memo
- `rerender-split-combined-hooks` - 拆分依赖独立的 hook
- `rerender-move-effect-to-event` - 把交互逻辑放在事件处理器
- `rerender-transitions` - 非紧急更新用 startTransition
- `rerender-use-deferred-value` - 用 useDeferredValue 推迟昂贵渲染以保持输入响应
- `rerender-use-ref-transient-values` - 高频瞬态值用 ref
- `rerender-no-inline-components` - 不要在组件内定义子组件

### 6. 渲染性能（MEDIUM）

- `rendering-animate-svg-wrapper` - 动画包裹 div，而非 SVG 元素
- `rendering-content-visibility` - 长列表用 content-visibility
- `rendering-hoist-jsx` - 将静态 JSX 抽到组件外
- `rendering-svg-precision` - 降低 SVG 坐标精度
- `rendering-hydration-no-flicker` - 客户端专属数据用内联脚本
- `rendering-hydration-suppress-warning` - 抑制预期的不匹配警告
- `rendering-activity` - 显隐用 Activity 组件
- `rendering-conditional-render` - 条件渲染用三元，不用 &&
- `rendering-usetransition-loading` - 加载状态优先 useTransition
- `rendering-resource-hints` - 用 React DOM 资源提示预加载
- `rendering-script-defer-async` - script 标签用 defer 或 async

### 7. JavaScript 性能（LOW-MEDIUM）

- `js-batch-dom-css` - 通过 class 或 cssText 批量改 CSS
- `js-index-maps` - 重复查找时构建 Map
- `js-cache-property-access` - 循环中缓存对象属性
- `js-cache-function-results` - 在模块级 Map 缓存函数结果
- `js-cache-storage` - 缓存 localStorage/sessionStorage 读取
- `js-combine-iterations` - 多次 filter/map 合并为一次循环
- `js-length-check-first` - 昂贵比较前先检查数组长度
- `js-early-exit` - 函数尽早返回
- `js-hoist-regexp` - 在循环外提升 RegExp 创建
- `js-min-max-loop` - 用循环求 min/max，不用 sort
- `js-set-map-lookups` - 用 Set/Map 做 O(1) 查找
- `js-tosorted-immutable` - 用 toSorted() 保持不可变
- `js-flatmap-filter` - 用 flatMap 一次完成 map 与 filter
- `js-request-idle-callback` - 非关键工作推迟到浏览器空闲

### 8. 高级模式（LOW）

- `advanced-effect-event-deps` - 不要把 `useEffectEvent` 结果放进 effect 依赖
- `advanced-event-handler-refs` - 事件处理器存 ref
- `advanced-init-once` - 每次应用加载只初始化一次
- `advanced-use-latest` - 稳定回调 ref 用 useLatest

## 如何使用

阅读单条规则文件以获取详细说明与代码示例：

```
rules/async-parallel.md
rules/bundle-barrel-imports.md
```

每条规则文件包含：
- 简要说明为何重要
- 错误示例与说明
- 正确示例与说明
- 补充背景与参考

## 完整编译文档

全部规则展开后的完整指南见：`AGENTS.md`
