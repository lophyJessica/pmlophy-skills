# 复杂交互的标注作用域：取证、判定、修法

适用于 SPA（React Router，BrowserRouter/HashRouter 均同）里带弹窗、抽屉、多步向导、展开行的页面。

## 一、失效模式对照表

| 现象 | 机器上看到的证据 | 根因 |
|---|---|---|
| 整页 0 角标 | 该页 config 的 id 集合非空，`.vpa-badge` 数为 0 | config `page` 与真实 pathname 不一致（菜单改过名、或写的是重定向路由 / 伪子路由） |
| 角标缺号（如 1、2、4 缺 3） | `[data-anno='...']` 元素在 DOM 里存在 | 锚点不存在于源码 / 元素在不可见状态 / 横向溢出被可见性判断跳过 |
| 同一屏出现重复序号 | badge 列表形如 `1,3,1,2,3,4` | 两个作用域的标注同时命中同一 URL（宿主页与弹窗各自从 1 编号，或共用一条 routeMatcher） |
| 弹窗打开前 0 个、打开后突然多出一组 | 宿主页角标 + 弹窗角标并存 | 标注模型只有 page 层，没有 state 层 |
| 面板里条数对、页面上 0 角标 | 面板条目 4 条，`.vpa-badge` 为 0 | 匹配是对的，问题在渲染层或浏览器执行的是旧 runtime（见 §三 的版本核对） |

## 二、取证命令（只读，先在仓库里跑）

```bash
# 1. config 里该页的标注 id/selector（以 jq 为准，别看 markdown）
jq -r '.annotations[] | [.id, (.page//"-"), (.routeMatcher//"NO-MATCHER"), .target.selector] | @tsv' annotation.config.json

# 2. 源码里真实存在的锚点，按 key 计数（>1 即重复锚点）
cd src && grep -rho "data-anno=[\"'][^\"']*[\"']" . | sed 's/data-anno=.//;s/.$//' | sort | uniq -c | sort -rn
# 注意锚点可能写成表达式：data-anno={index === 0 ? 'xxx' : undefined} —— 只 grep 字符串字面量会漏判成"锚点不存在"

# 3. 路由表里真实存在的 path（重定向路由要单独认出来）
grep -rn 'path="/' App.tsx | sed 's/:.*path/: path/'
grep -rn 'Navigate to=' App.tsx   # 这些 path 不能作为 annotation.page
```

两个差集必须为空：`config selector − 源码锚点`、`源码锚点 − config selector`；`config page − 路由表`、`路由表 − config page`（只对本次要标注的页面算，别把全站路由当缺口）。

## 三、线上实测（判死活的唯一标准）

```js
// 打开目标页后，逐页跑
[...document.querySelectorAll('[data-anno]')].map(e => e.dataset.anno)   // 页面实际锚点
// 点入口出角标，再收集序号
document.querySelector('.vpa-entry').click()
[...document.querySelectorAll('.vpa-badge')].map(b => b.textContent.trim())
// 角标 0 时先看面板条目数：面板有、角标没有 = 匹配没问题，是渲染/执行版本问题
document.querySelector('.vpa-panel-toggle').click()
```

每个要标注的页面都要跑一遍：**有条件出现的状态（弹窗/步骤）必须真触发后再数一次**，否则少掉的角标会算成「漏标」。

**「改了但没生效」先核对执行的脚本版本，别急着改代码**：浏览器 `<script src>` 走的是缓存，`fetch(url, {cache:'no-store'})` 拿到的内容不代表页面执行的也是这份。判法：在 runtime 里临时塞一个 `window.__VPA_MEASURE.push(...)` 之类的可观测标记，点入口后读它——标记没增长就说明执行的是旧文件。治根是给 `index.html` 里 annotation-kit 的三处引用（runtime.js / runtime.css / override.css）都带 `?v=YYYYMMDDx` 并每次发版递增；只给其中一处加等于没加。

## 四、修法方向（按可落地程度排序）

1. **先上一版拦截校验**（不改 runtime）：编译期做上面两个差集，锚点缺失、page 不在路由表、同一 routeMatcher 分组内角标重号，任一命中直接报错不许发版。这一层能拦下最多问题，且不改动已有 runtime。
2. **再上作用域模型**：标注块增加 `state` / `scopeLabel`（弹窗/抽屉/步骤标识，面板上以标签展示），runtime 在 `currentPageMatches` 之后按「当前激活状态」二次过滤；序号在同屏可见作用域内连续唯一。
3. **`routeMatcher` 用在该用的地方**：覆盖同一页面的多个等价真实路由（`create` / `edit/:id` / `look/:id`），不用它把多个作用域压成同一个匹配，也不要窄到只覆盖其中一个路由。
4. **元素找不到时不要静默跳过**：面板里把这类块列出来并标「需操作后查看」，评审才知道要触发弹窗/切步骤，不会误以为没标注。

## 五、编译期校验：三条必跑命令

```bash
# 1) 编译（覆盖写入原型 public 下的 bundle）
python <skill>/scripts/compile_annotations.py "<本迭代 annotations>/annotation.workspace.json"

# 2) 校验：锚点存在性 + 路由命中 + 分组角标唯一
python <skill>/scripts/check_annotation_assets.py <原型>/public/annotation-kit --src <原型>/src --routes <原型>/src/App.tsx

# 3) 构建
npm run build
```

`check_annotation_assets.py` 的两道可选校验缺了等于没校：`--src` 抓「锚点在源码里根本不存在」，`--routes` 抓「page 命中不到真实路由 / 只命中重定向路由」——这两类错编译全绿、页面上 0 角标，只有这一步能拦。通配路由（`/tools/*`）与参数路由会降级为 warning，不误判。

**校验脚本自己是"拦截有效"的第 0 步**：改完校验先拿历史真 bug 反向验一遍（把 page 指到重定向路由、把 selector 改成不存在的锚点、把两个块的 id 改成同一个），三条都要报错才算这层校验真的有用，别只看「当前产物过」就收工。

## 六、检阅时的沟通口径

- 问题归到一句：「标注只有页面层，没有状态层」——比逐条列 bug 更能让用户判断要不要重构。
- 给用户两个可选路径：只做拦截校验（救当前这套）还是重做作用域模型（治根），让用户拍板，不要自己替他选。
- 判完根因再动结构，别边猜边修：同一现象先分清是「匹配不到」「锚点不存在」还是「执行了旧脚本」，三者修法完全不同。
