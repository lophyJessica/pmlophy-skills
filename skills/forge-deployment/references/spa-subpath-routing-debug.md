# SPA 子路径路由调试实战

> 2026-07-22 copy-wms 路由修复全记录。React + Vite + HashRouter/BrowserRouter + nginx alias。

## 症状

用户反馈:部署在 `https://pmlophy.com/project/copy-wms/` 的 SPA,点击侧边栏导航后 URL 跳转到域名根路径 `https://pmlophy.com/wave/management`(缺少 /project/copy-wms/ 前缀)。

## 排查顺序(按优先级,不要跳过)

### 1. vite base 是否配置

```
vite.config.ts: base: '/project/copy-wms/'
```

编译后 `<script src="/project/copy-wms/assets/...">` 而非 `<script src="/assets/...">`。

### 2. nginx try_files 是否正确

```nginx
location /project/copy-wms/ {
    alias /var/www/pmlophy.com/project/copy-wms/;
    try_files $uri $uri/ /project/copy-wms/index.html;  # SPA fallback
}
```

验证: `curl -sk https://pmlophy.com/project/copy-wms/wave/management` → 200(返回 index.html 而非 404)

### 3. React Router 配置

- **HashRouter**: URL 为 `/#/wave/management`,nginx 无需特殊处理
- **BrowserRouter**: URL 为 `/wave/management`,需要有 nginx fallback

### 4. basename 检查

HashRouter/BrowserRouter 的 basename 是否与部署路径一致:
```tsx
<HashRouter basename="/project/copy-wms">
```

### 5. 导航方式(关键!很容易漏)

以下方式都可能导致路径错误:

| 导航方式 | 风险 |
|----------|------|
| `<a href="/wave/management">` | 绝对路径,绕过 Router,直接跳域名根 |
| `<button onClick={() => navigate('/wave/management')}>` | 绝对路径,同上 |
| `<base href="/project/copy-wms/">` in index.html | 劫持所有相对路径,与 Router 冲突 |
| `navigate('wave/management')` (无前导/) | 相对路径,在当前位置拼接 |
| `navigate(\`\${B}/wave/management\`)` | B 变量为空或拼接错误 |

### 6. 终极诊断:Puppeteer 实测

当所有静态检查都找不到根因时,用 Puppeteer 实际点击导航看浏览器行为:

```js
const pp = require('puppeteer');
const b = await pp.launch({headless:true,args:['--no-sandbox']});
const p = await b.newPage();
p.on('framenavigated', f => console.log('NAV:', f.url()));
await p.goto('https://pmlophy.com/project/copy-wms/', {waitUntil:'networkidle2'});
// 展开折叠菜单
await p.evaluate(() => document.querySelectorAll('button').forEach(b=>b.click()));
// 点击目标按钮
await p.evaluate(() => {
  const bs = document.querySelectorAll('button');
  for(const b of bs) {
    if(b.textContent?.trim()==='波次管理' && b.offsetParent) { b.click(); break; }
  }
});
await new Promise(r=>setTimeout(r,3000));
console.log('FINAL:', p.url());
```

实际输出揭示了路径重复问题:`/project/copy-wms/project/copy-wms/wave/management`。

## 本次实战结论

copy-wms 的导航使用 `<button>` 而非 `<a>`,且 navigate() 使用了不带前导 `/` 的相对路径,导致在子路径页面拼出双重路径。修复:所有 navigate() 调用使用完整绝对路径 `/project/copy-wms/xxx`。

## 检查清单

- [ ] vite base = 部署路径
- [ ] nginx alias + try_files fallback
- [ ] Router basename = 部署路径
- [ ] index.html 中没有 `<base href>` (除非确定需要)
- [ ] 所有导航使用 Router 的 Link/useNavigate,不用 `<a href>` 或 `window.location`
- [ ] 导航路径以 `/` 开头(绝对路径)或以 basename 变量开头
- [ ] Puppeteer 实测至少 2 个不同页面
