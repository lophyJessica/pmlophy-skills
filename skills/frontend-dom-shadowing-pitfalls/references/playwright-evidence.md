# Playwright 服务器端取证模板（无 GUI VPS）

## 安装（一次性）

```bash
mkdir -p /tmp/pwtest && cd /tmp/pwtest
npm init -y && npm i playwright@1.49.1
npx playwright install chromium
```

## 取证脚本骨架（登录态 + fiber 读取 + style 真实性检查）

```js
// check.cjs
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('https://SITE/', { waitUntil: 'networkidle' });
  await page.fill('#username', 'USER');
  await page.fill('#password', 'PASS');
  await page.click('button:has-text("登")');
  await page.waitForTimeout(3000);
  await page.goto('https://SITE/TARGET-PATH', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  const r = await page.evaluate(() => {
    // 定位目标元素后向上爬到 form
    const kw = [...document.querySelectorAll('input')].find(i => i.placeholder === '占位符');
    let el = kw; while (el && el.tagName !== 'FORM') el = el.parentElement;
    const fk = Object.keys(el).find(k => k.startsWith('__reactFiber$'));
    const f = el[fk];
    return {
      styleAttr: (el.getAttribute('style') || 'NULL').slice(0, 60),
      isRealCSSStyle: el.style instanceof CSSStyleDeclaration,   // false = 被遮蔽/替换
      fiberPropsStyle: f && f.memoizedProps && f.memoizedProps.style
        ? JSON.stringify(f.memoizedProps.style).slice(0, 60) : 'NONE',
      computedBg: getComputedStyle(el).backgroundColor,
      formCount: document.querySelectorAll('form').length,
    };
  });
  console.log(JSON.stringify(r, null, 1));
  await page.screenshot({ path: '/tmp/evidence.png' });
  await browser.close();
})();
```

## 关键判读

- `isRealCSSStyle: false` → style 被替换成普通对象，查 form 内 named control 是否叫 `style`（或 name/title/action/title 等 HTML 原生属性名）。
- `fiberPropsStyle` 有值 + `styleAttr: NULL` → React 层正确，写入环节被遮蔽，不是缓存/构建问题。
- bundle grep 注意：Rollup 会把共享样式对象提升到 chunk 前部（如 `Ji={background:...}`），使用点只有 `style:Ji` 引用——查引用不查字面量。

## 对比技巧

用正常页面与异常页面各跑一遍同样的 evaluate，diff 两边 `styleAttr / fiberPropsStyle / formCount`，差异点即根因所在层。
