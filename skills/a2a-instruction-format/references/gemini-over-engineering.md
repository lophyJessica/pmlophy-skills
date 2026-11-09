# Gemini 反重力常见翻车模式

## 1. 乱做主张 (Over-engineering)

症状: 让反重力删一行跳转逻辑,它顺手重写整个路由层,添加新组件,拆分文件,甚至新建 5-12 套重复路由树,导致 bundle 膨胀。

根因: Gemini 倾向"优化"——你让删一行,它觉得"顺便重构更好"。

对策:
- 指令硬约束: "只删不增、只删不改、不新建组件、不拆分文件"
- 梭哈后检查: `strings bundle.js | grep -c basename` 应为 1
- 迭代修复超过 2 次仍然越改越坏 → 放弃 Gemini → 人工定位源码行号 → 直接精确修改

## 2. Vite 缓存误判

症状: 源码已改成正确,但 build 产物仍有旧 bug。grep strings 检查发现 SUPPLIER 跳转数/路由树数不变甚至增加。

根因: Vite 的 node_modules/.vite 缓存了旧的编译结果。

对策: `rm -rf dist node_modules/.vite && npm run build` 强制清缓存重编译。清完用 strings 验证。

## 3. 重复路由树

症状: 反重力每次迭代都在 App.tsx 中创建新的 Routes 定义,从不删除旧的。bundle 中出现 Syt/oCt/ewt 多个同功能路由树。

对策: 
- 指令明确要求: "搜索所有 basename 出现位置,删除重复定义,只保留一套 Routes"
- build 后 strings 检查: `grep -c "basename.*project/forge-erp"` 应为 1
