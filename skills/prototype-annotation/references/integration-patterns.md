# 集成模式

## 决策树

选用侵入性最小的可行集成方式：

1. 无法改源码：用浏览器注入或书签脚本展示已有标注 Markdown。
2. 可编辑静态 HTML：复制 `annotation-kit/`，在每个 HTML 入口注入一条样式表与一条模块脚本。
3. React/Vite/Vue SPA：复制 `public/annotation-kit/` 或根目录 `annotation-kit/`，在 `index.html` 注入标签。
4. Next/Nuxt 或 SSR：优先 public 资源目录加 layout/head 注入；除非必要，避免改写客户端组件。
5. 生成物原型：在产出 `index.html` 旁放置运行时文件；避免改已生成的 bundle。

## 静态 HTML

目标形态示例：

```html
<link rel="stylesheet" href="./annotation-kit/runtime.css">
<script type="module" src="./annotation-kit/runtime.js"></script>
```

将编译好的 `annotation-kit/annotation.bundle.json` 放在 `runtime.js` 旁。运行时仅将 `annotation.config.json` 用作遗留或极小 demo 回退。

接近生产的用法：将源 Markdown 编译进 `annotation-kit/annotation.bundle.json`。多模块共享同一运行时时，通过 `annotation.workspace.json` 编译各 config，不要手工合并模块 config。

### 路由与 initialMode 配置

`page` / `routeMatcher` 规则见 SKILL.md §2.2，本节只保留 initialMode 与静态页写法。

- 单页静态 HTML 时，将标注 `page` 设为 `"*"`；不要仅为命名该文件而强行写 routeMatcher。
- 默认将 `runtime.initialMode` 设为 `"preview"`。仅教学、评审或其他以标注为先、需一进页就显示角标的场景，才设为 `"annotate"`。

## React、Vite、Vue 与普通 SPA

优先使用 public 资源：

```txt
public/
  annotation-kit/
    runtime.js
    runtime.css
    annotation.bundle.json
```

注入根 `index.html`：

```html
<link rel="stylesheet" href="/annotation-kit/runtime.css">
<script type="module" src="/annotation-kit/runtime.js"></script>
```

除非无法改 HTML 入口，不要将运行时 import 进应用组件。

## 仅有构建产物

若只有 `dist/` 或导出的静态文件，将 `annotation-kit/` 拷入该产出并在导出 HTML 中注入标签。须说明：若未同步改源项目，每次重新构建后须重复集成步骤。

## 选择器提示（data-anno）

仅在需要时添加 `data-anno`：

```jsx
<section data-anno="module-filter-bar">
  ...
</section>
```

规则：

- 提示加在模块根节点，不要每个按钮都加。
- 使用小写 kebab-case。
- 命名保持业务可读。
- 不要通过 `data-anno` 承载状态或行为。
- 对 modal、drawer、popover、手风琴或页签面板，将 `data-anno` 放在可见模块根上。运行时在该根出现可见屏幕矩形前隐藏角标，DOM 或属性变化后重新测量。

## 运行时行为要求

运行时须满足：

- 通过 DOM 测量在 overlay 层渲染角标。
- 在滚动、缩放、路由变化与 DOM 变更时重新计算。
- 对隐藏、已脱离文档、零尺寸与视口外目标跳过角标，不要将角标硬夹到视口角落。
- 不改变目标元素的布局、尺寸或定位。
- `z-index` 高于业务 UI，弹层高于角标。
- 宿主页面叠层较高时，从 bundle 读取 `runtime.zIndexBase`；不要改写宿主 z-index。
- 弹层与触发角标至少相距 8px，避免缩放手柄挡住同列其他角标。
- 在角标、弹层、工具栏控件与缩放手柄内阻止事件冒泡。
- 不依赖框架专有 API，同时支持静态页与 SPA 导航。

## 只读内容流

运行时无持久化与编辑模式，内容单向流动：

- 用户或 Codex 在项目中更新标注 Markdown。
- 编译器校验 coverage 并生成 `annotation.bundle.json`。
- 按常规 Git/构建/部署流程发布 bundle，而非业务 PRD。
- 运行时拉取并渲染已发布 bundle。
- 刷新时无缓存读取 bundle，同步已打开弹层与过期角标，不重载业务页。
- 「查看全部」渲染合并文档并提供 Markdown 下载。编译器也可通过 `htmlOutput` 输出独立 HTML。

不要在标注运行时中引入编辑控件、草稿、保存适配器、写入 API 或鉴权。

## Mermaid 渲染

Mermaid 为可选能力，且不应破坏低侵入集成。

配置示例：

```json
{
  "mermaid": {
    "enabled": true,
    "src": "/annotation-kit/vendor/mermaid.min.js",
    "options": {
      "theme": "default"
    }
  }
}
```

规则：

- 使用围栏 Markdown 块：```` ```mermaid ````。
- 若宿主应用已提供 Mermaid，复用 `window.mermaid`。
- 仅在配置时加载 `mermaid.src`。
- 内网/后台原型优先本地 vendor 的 Mermaid，而非 CDN。
- 若 Mermaid 无法加载，回退为展示源码。
