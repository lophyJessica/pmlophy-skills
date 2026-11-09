# VPS部署后问题诊断优先级

## 铁律: 用户是PM，不是开发者

绝不发出以下指令:
- "打开 src/pages/xxx.tsx 看一下第几行"
- "在你的 Mac 上跑 grep"
- "手动改一下这行代码"
- "npm run build 试一下"

改为:
- 先在VPS侧诊断(检查构建产物、缓存、nginx)
- 需要改代码时发精确指令给反重力/Cursor
- 用户在浏览器验证即可

## 部署后视觉问题诊断顺序

发现bug/旧数据显示 → 优先按此顺序排查，不应直接跳去改源码:

### 1. 存储层(最常见)
- IndexedDB 旧数据未清 → F12 → Application → IndexedDB → Delete database
- localStorage 旧角色/状态残留 → Application → Local Storage → 删对应key
- 清完后硬刷新: Cmd+Shift+R

### 2. 构建产物层(Vite多文件问题)
反重力/Gemini经常在App.tsx中重复生成多套路由树，Vite拆出多个index JS文件:
```bash
# 查看有多少个index JS
ls /var/www/pmlophy.com/project/<project>/assets/index-*.js | wc -l
# 查看哪个JS包含特定bug(pattern替换为实际搜索词)
for f in /var/www/pmlophy.com/project/<project>/assets/index-*.js; do
  hits=$(strings "$f" | grep -c 'buggy_pattern')
  echo "$hits $(basename $f)"
done
```
找到hits=0的干净文件后，修改index.html的script src切换到它。

### 3. Nginx/浏览器缓存
- 确认index.html引用的JS文件名是最新的
- Cmd+Shift+R硬刷新
- F12 → Network → 勾选Disable cache

### 4. 最后才怀疑源码
确认以上三层都排除了，再用 A2A 指令派 Agent 修改。
