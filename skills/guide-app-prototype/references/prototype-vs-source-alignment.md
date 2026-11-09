# 原型 vs 外销源码：逐页对照的量化方法

用户说「按源码对照复刻」时，肉眼逐页读两边代码是最慢且最不可靠的做法——19 个页面、其中 orderDetail 2546 行 / orderList 1873 行，读完已经没有上下文判断力了。且原型本来就该 mock 化，大量差异是预期内的，混在一起看会把真缺陷淹掉。

## 一、配对与量化

两边 views 目录同名结构（`src/views/<模块>/<页>.vue`），直接按相对路径配对；`find` 出两边的 `.vue` 清单做集合差先拿到「缺哪几页」，再对交集的每一页跑 difflib。

```python
import difflib
sm = difflib.SequenceMatcher(None, src_lines, proto_lines, autojunk=False)
blocks = [o for o in sm.get_opcodes() if o[0] != 'equal']   # 差异块数 = 页面的改动粒度指标
```

`autojunk=False` 必加：文件上千行时默认的启发式会把重复片段当垃圾丢掉，差异块数会算少。

输出一张每页「差异块数」的表当基线，然后才细看每块内容——先知道哪几页最远，就不会从第一页开始硬啃。

## 二、分类：mock 化 vs 真缺陷

块内任一行命中下面这组标记，就归为 **mock 化**（预期内，不派活）：

```
lan\. | useAppStore | storeToRefs | mock | Mock | useBridgeMock | dsBridge
vchatAPI | useCurrentInstance | globalProperties | lastRoute | from '@/api | @/store/app | @/router
```

理由：原型把多语言字典 `lan` 换成硬编码中文、把 `window.dsBridge`/`vchat` 换成 `useBridgeMock`、把 `@/api/*` 换成 `@/mock/*`、把 `useCurrentInstance` 换成直接引用——这些是**架构替换而非走样**，不需要派 agent 逐个改回。

剩下的块才是真缺陷候选。实测一次的比例约「mock 化 2/3、真缺陷 1/3」，且真缺陷里一半是表单属性书写顺序这类语义相同的噪音，要人再筛一遍才派活。

## 三、真缺陷的典型形态（按严重度）

| 形态 | 例子 | 判据 |
|---|---|---|
| 组件被替换 | 源码 VOS `Loading` → 原型 `van-loading`；VOS `Empty`/`FosButton` 被换通用组件 | 违反「VOS 组件一个不许替换」，视觉与动效全错 |
| 结构块被删 | `publicDialog.vue` 少了 `.public-dialog-body` 包裹层，`max-height:90%` / `overflow:hidden` 一并丢 | 弹窗高度与滚动行为跟源码不一致，且这类差异肉眼不看 CSS 发现不了 |
| 整段逻辑缺失 | `task/detail.vue` 缺 `downloadImageToBase64()`（远程图转 base64 用于分享） | 功能真缺，不是样式问题 |
| 原型自造状态 | `orderList.vue` 多出源码没有的 `--search-focus` class | 反向差异：原型比源码多，要么补进源码要么删 |
| props 契约改造走样 | 源码 `props.hasAuthorize` / `props.accountListData` → 原型 `hasAuthorize.value` / store 取值 | 只要值一致可接受；要核 mock 里的字段名是否源码真有的（自造 `whatsAppAccountAvatar` 这类字段就是要改的） |
| 死代码 | `TabPlaceholder.vue`、`DependencyCheck.vue` 全库无引用 | 低优先，顺手清 |
| 多语言取值源不一致 | 原型 `appStore.workLan`，源码 `appStore.lan` | 改回 `lan`；改完若文案取不到，停下报差异，不许自己塞硬编码中文顶上 |
| 组件显式注册 | 原型多写 `[Icon.name]: Icon`，源码没有 | 先核实当前 VOS 版本是否必需：必需则保留并写明原因，不必要的才删，别直接照源码抹掉 |

属性书写顺序不同（`:textColor` 放在 `:disabled` 前还是后）不算缺陷，别写进指令派活。

### 补 404 页：搬 `notFound.vue` 必改三处

- `<style lang="less">` 改 `scss`——原型不用 less，原样搬过来编译不过。
- 图片路径 `../images/invalid.png` 改 `@/images/invalid.png`；源码写的是相对当前文件的路径，照搬到 `src/views/` 下指向不存在的目录。
- 路由末尾补 `{ path: '/:pathMatch(.*)*', name: 'notFound', component: () => import('@/views/notFound.vue') }`，其余路由一条不动。

顺带做一次 `src/images` 的文件名差集：源码有而原型缺的（`invalid.png`、`default-avatar.png`、`arrow.png`、`change.png`、`icon.png` 等）逐个拷过去。同名文件不覆盖。

**「同名但内容不同」先剥编码再下结论，别直接停**：原型里的 SVG 常带 UTF-8 BOM（文件头 `EF BB BF`），源码那份没有，于是两边 md5 不同、字节数差 3，看着像内容冲突，实际图形逐字节一致。判法：读成 bytes，剥掉开头的 BOM（以及比较时归一化 CRLF/LF）再比，一致就按源码版本覆盖，不算冲突；剥完仍有差异才停下来问。不做这一步会让 agent 在 `src/images/tabbar/` 那 8 个图标上整轮停住等裁决，白等一轮。

## 四、派活前的两个判断

1. **等价架构不算缺页**：源码 `home/index.vue` 的容器职责（keep-alive、底部导航、props 下发、空账号态）在原型里已由 `App.vue` + store 承担，照抄会造出两套外壳。只核对 Tab 顺序/active 态/空态文案。
2. **mock 化的部分仍要对形态**：接口换 mock 是允许的，但 mock 的数据量、分页行为、空态与异常态覆盖要跟真实接口返回一致，不能只塞几行好看的数据。数据量最大的三页（orderList / orderDetail / activityList）是重点。

## 五、写进给 agent 的指令时

- 按严重度分阶段，每阶段结束必须停；两个阶段不许连做。
- 给「已对齐、禁改」的页面清单（差异块为 0 的那几页），否则 agent 会把它们重写一遍制造新差异。
- 红线里点名「不许替换源码组件」「不许新建 views/home/index.vue 去对拷容器」「不许为通过对照简化页面」「判断不了停下来问」。
- 报告要落盘成文件（`ai-reports/` 下按阶段命名），不写在聊天里。
