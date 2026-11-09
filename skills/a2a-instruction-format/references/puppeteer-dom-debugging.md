# Puppeteer DOM Debugging for Frontend Routing

> When route/URL fixes don't work via normal code analysis, use Puppeteer
> on VPS to inspect the actual DOM and trace navigation calls.

## When to Use

- `<a href>`, `<base>`, and React `Link`/`basename` fixes don't move the URL
- User says "URL 没改变" after multiple route fixes
- Need to verify what ACTUALLY happens on a click (not what the code says)

## Technique

```javascript
// 1. Check element tag type (a vs button)
const nav = await p.evaluate(() => {
  const items = [];
  document.querySelectorAll('a,button,li').forEach(el => {
    const t = el.textContent?.trim()?.substring(0,40);
    if(t && t.length<40) items.push({tag:el.tagName, text:t});
  });
  return items;
});

// 2. Expand menus before clicking sub-items
await p.evaluate(() => document.querySelectorAll('button').forEach(b=>b.click()));
await new Promise(r=>setTimeout(r,1000));

// 3. Click target and observe final URL
await p.evaluate(() => {
  const bs = document.querySelectorAll('button');
  for(const b of bs) {
    if(b.textContent?.trim()==='目标文本' && b.offsetParent) { b.click(); break; }
  }
});
await new Promise(r=>setTimeout(r,3000));
console.log('FINAL URL:', page.url());
```

## Real Case: copy-wms (2026-07-22)

- Symptom: 点击菜单跳转到根域名而非 `/project/copy-wms/`
- Tried: `<base href>`, React Router `basename`, `<a href>` replacement — all failed
- Discovery: Navigation items were `<button>` tags with `onClick={navigate()}`
- Root cause: `navigate()` used relative paths, browser appended to current path
- Fix: Add leading `/` to all `navigate()` calls

## Key Insight

Do NOT assume navigation elements are `<a>` tags or `<Link>` components.
Always inspect with Puppeteer to see the actual DOM.
