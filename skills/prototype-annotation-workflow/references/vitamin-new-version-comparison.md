# ≥维生素新版 vs 我们的版本（0912 最新对比）

对比对象（用户 0912 确认：维他命取最新那套，与我们的合成两套对比）：
- **维他命最新**：`/root/notes/vitamin-course/vitamin-prototype-annotation/`（9/10 更新，106 行精简 SKILL + 4 references + 3 脚本 + examples + 4 组 tests，工程化/生产级）
- **我们的**：`/root/repos/prototype-annotation-skill/`（401 行 SKILL，业务语言 + 评审闭环 + 实战血泪规范，产品/评审向）

结论：**不是谁好谁差，是取舍不同**——他做"通用化/工程化/生产级/可交付团队"，我们做"产品商务视角 + 评审闭环 + 实战踩坑规范"。两方向不可替代，融合是理想方向。9/10 新版相对 0906 对比又补了 tests/examples/诊断接口/三层验证，工程化更完整了。

## 核心差异

| 维度 | 我们 prototype-annotation | 维他命最新 vitamin-prototype-annotation |
|---|---|---|
| 核心定位 | 产品评审视角：给业务方/评审看，业务语言优先，独立面板UI+角标 | 工程实现视角：通用框架、多技术栈、生产部署 |
| 技术栈覆盖 | 偏 React/Vite | **全**：静态HTML/SPA/Vite/Next/Nuxt/SSR/只有构建产物/无法改源码(临时注入) |
| 内容分类 | 5分类(page/interaction/rule/field/pending) + 详情**6-tab** + **待确认=评审问题追踪器**(录入/勾选/解决/导出PRD待办) | 3分类(page-global/global/element)，偏"规则提取"，无评审闭环 |
| 业务语言 | **业务语言标准**(面包屑/中文枚举/英文仅括号)——评审核心价值 | 退回纯技术分类，**丢了"给业务看"这个核心** |
| 运行时 | 富面板UI(6-tab/导出/定位/悬浮可拖) + 实战血泪规范 | 相对简化的角标/抽屉/阅读器 |
| 工程健壮 | 靠实战踩坑规范（ID每页独立/setPointerCapture禁/tab持久化/scroll不重建） | **靠 test 用例(4组)+ check 自动校验 + examples可运行示例 + 诊断接口** |
| 可运行示例 | 无（靠 forge-crm 实例） | **examples/static/**（复制即跑，验证工具用） |
| 自动测试 | 无 | **tests/ 4组**（compile/install/regress/runtime，生产级） |
| 诊断接口 | 无 diagnostics API | **`window.VitaminAnnotations.{ready,diagnostics,refresh,sync}`**，状态分类 visible/hidden/missing-target/missing-view/ambiguous/out-of-context |
| 交付验证 | "跑通流程即可"，验证靠人工 | **三层验证显式区分**："映射完整 ≠ 部署资产齐全 ≠ 页面挂载成功"（杜绝HTTP200=验收） |
| 边界诚实 | 未明说 | **明确**截图/Canvas/跨域iframe/ShadowDOM/top-layer不属于浮层直接覆盖 |

## 维他命最新版新增（相对 0906 对比时）
- **examples/static/** 可运行示例（新项目"直接抄作业"验证工具）
- **4 组自动测试**（compile/install_annotation_kit/regressions/runtime）
- **诊断接口** `window.VitaminAnnotations.diagnostics()` 区分挂载状态与需求正确性
- **hideToolbarWhenEmpty 默认 true**（无标注页不渲染工具栏）
- **三层验证**细分："映射完整 / 部署资产齐全 / 挂载成功"三种不同验证
- 增量更新前置 `--check`（先记已有错误，普通配置错不无条件暂停）

## 维他命版优势（值得吸收，工程化资产）
1. **技术栈适配全**：Next/SSR/只有构建产物/无法改源码（临时注入评审）都能接——我们不偏。
2. **诊断接口**：把"挂载状态"和"需求正确性"分开（visible/hidden/missing-target/...），排查有据。
3. **check_annotation_assets.py** 编译后资产校验：配置完整性/sourceRefs映射/重复ID/缺失选择器——"标完机器先过一遍"。
4. **三层验证**显式分离（映射/资产/挂载），杜绝拿局部证据当全套验收。
5. **examples + tests**：可运行示例 + 自动回归——生产级交付。
6. 边界诚实（截图/Canvas/ShadowDOM 等不直接覆盖）。

## 我们版优势（他版没有，不能丢）
1. **业务语言标准**（面包屑/中文状态/业务语言，英文枚举仅括号）——他版退化成纯技术分类，丢的是"给评审看"这个核心。
2. **详情 6-tab + 待确认=评审问题追踪器 + 导出 PRD 待办（单块/全局分组）**——我们独有评审闭环，他版没有。
3. **实战血泪规范**（ID 每页独立 / drag&click 禁 setPointerCapture / 滚动不重建 / tab 持久化）——踩坑踩出来的，对实际项目极关键。
4. **面板 UI 规范**（悬浮可拖、交互流"按钮→徽章→内容"、初始 preview、type 分类过滤）。

## 融合方向（若优化）
拿他**工程化架构做底**（技术栈适配 + 诊断接口 + check 资产校验 + examples + tests + 三层验证），接我们的**产品视角**（业务语言 + 6-tab + 待确认追踪器 + 实战规范）。分工：兼容/诊断/验证层用他的，内容/展示/评审层用我们的。
> 注：我们的检阅侧 Skill（prototype-annotation-review）已吸收其"三能力"（annotation-scope 边界判断 + check 校验 + examples）作参考；真正融合 = 把维他命 runtime/reference/脚本工程化能力并入我们 standalone skill，同时保留产品层。

## 检阅/对比注意
- 不要因他版"更工程化"就全盘替换——会丢掉产品视角这个核心价值（用户诉求始终是"给业务方/评审看"）。
- 融合是"分层互补"不是"二选一"：兼容性/验证用他，内容/评审用我们。