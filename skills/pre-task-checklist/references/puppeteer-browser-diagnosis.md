# Puppeteer 浏览器诊断技巧

> copy-wms 路由调试实战总结(2026-07-22)

## 场景

前端页面行为异常(如路由跳转路径错误),通过看源码无法快速定位,需要**实际渲染页面并追踪交互行为**。

## 适用条件

- 页面部署在 VPS 上,可访问
- 需要追踪点击、导航、URL 变化
- 需要检查实际 DOM 结构(非源码,是编译后的运行时行为)

## 步骤

1. 安装 Puppeteer(已在 VPS /tmp 目录):
   ```
   cd /tmp && npm install puppeteer --no-save
   ```

2. 启动 headless Chrome,打开目标页面,等待渲染:
   ```js
   const b = await pp.launch({headless:true, args:['--no-sandbox']});
   const p = await b.newPage();
   p.on('framenavigated', f => console.log('NAV:', f.url()));
   await p.goto(url, {waitUntil:'networkidle2', timeout:15000});
   ```

3. 抓取 DOM 结构(确认元素类型、可见性):
   ```js
   await p.evaluate(() => {
     return Array.from(document.querySelectorAll('a,button')).map(el => ({
       tag: el.tagName, text: el.textContent?.trim(), visible: el.offsetParent!==null
     }));
   });
   ```

4. 模拟交互:展开折叠菜单、点击按钮:
   ```js
   await p.evaluate(() => document.querySelectorAll('button').forEach(b=>b.click()));
   await p.evaluate(() => {
     const bs = document.querySelectorAll('button');
     for(const b of bs) {
       if(b.textContent?.trim()==='目标按钮名' && b.offsetParent) { b.click(); break; }
     }
   });
   ```

5. 检查结果:URL、hash、页面状态:
   ```js
   console.log('URL:', p.url());
   console.log('HASH:', await p.evaluate(() => location.hash));
   ```

## 实战发现

copy-wms 调试中 Puppeteer 揭示了:
- 导航元素全是 `<button>` 而非 `<a>`,所以 `<base href>` 和 `<Link>` 修复无效
- 实际点击后的 URL 是 `/project/copy-wms/project/copy-wms/wave/management`(路径重复),定位到 `navigate()` 使用相对路径而非绝对路径
- 之前 6 轮手工 patch 都是在猜,一次 Puppeteer 实测直接定位根因

## 关键原则

**不看源码猜行为,看运行时实际行为。** 编译后的 JS 和实际 DOM 可能与源码差异巨大。
