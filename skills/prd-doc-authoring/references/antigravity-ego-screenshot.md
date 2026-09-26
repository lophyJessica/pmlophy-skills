# 批量截图执行：反重力 + ego lite（法拉利 + 导航眼睛）

用于给评审PRD/标注补角标区域截图这类"打开线上原型、逐个 data-anno 区域截图"的批量活。

## 分工（用户 2026-09-25 比喻）
- **反重力（Antigravity）= 法拉利（执行主力）**：读指令、跑 shell、写文件、判断该截哪个区域。
- **ego lite = 导航 + 眼睛**：给反重力提供浏览器能力——打开网页、定位元素、截图。防止反重力自己找元素漂移。
- "得搭配，不然他会漂移"——egolite 负责定位网页元素，反重力判断"这个区域对应哪个角标"。

## 前提
- 反重力（Antigravity）兼容读 `~/.agents/skills/ego-browser`（skill 目录，非 App 界面）。指令开头：先读该 skill 确认调 ego 的命令格式。
- egolite 应用必须已启动（onboarding 完成）；若反重力报 503 = ego 没启动，让用户 Cmd+Q 完全退出重开。
- 备份用法：Cursor 内置浏览器（用户上班可替代，定位区域+截图同效）。

## 核心工作流（验过的，反重力自己跑通的）
1. 先 `grep data-anno` 从项目源码确认每个角标的锚点存在（不猜锚点存在才截）。
2. 用 `page.evaluate` 拿每个 `[data-anno='...']` 的 `getBoundingClientRect()`，取 x/y/width/height。
3. `page.screenshot({path, clip:{x,y,width,height}})` 聚焦截该区域（clip 加小 padding 防切边）。
4. 弹窗角标需先触发：点对应按钮 → 弹窗出现 → 截（同 clip 或整弹窗）。
5. 页面级角标截整页（`page.screenshot({path})` 不带 clip）。
6. 截图前 `evaluate body.innerText` 验证页面非空态；详情页先点进真实数据行（如 LEAD20260717-0016）别截空路由。
7. 每个角标存 `images/中文名-角标号.png`（如 `线索列表页-L2-状态页签与线索池视图.png`），完成后 ls 核对张数 = 角标数。

## 关键命令片段
```bash
# 从标注 config 拿角标 → data-anno selector 映射
python3 -c "import json; d=json.load(open('annotations/annotation.config.json')); [print(a['id'],a['type'],a.get('target',{}).get('selector','')) for a in d['annotations']]"
```
ego 里定位区域：
```js
const el = document.querySelector("[data-anno='leads-status-tabs']");
const r = el.getBoundingClientRect();
// 返回 {x,y,width,height} 给 screenshot clip
```

## 红线
- 只截图，不改业务代码、不 commit、不 push（截图存仓库由用户决定推送）。
- 截不到该角标就如实报告"无法触发"（可能状态不对），不硬凑、不脑补、不伪造截图。
- 弹窗截不到先查是否需特定状态（草稿/跟进中/已分配）才显示该按钮。
- 主路径优先 Playwright+Pillow 本机自动画框（省额度，见 SKILL 主体）；反重力+ego 是满足"批量截区域图"的备用/交付前整页红框图方案。
