# VPS 部署: 多 JS 文件与 index.html 引用不一致的排查

## 症状
- 用户本地浏览器正常, VPS 部署后仍显示旧版本行为
- 源码已修复, 重新 build 部署后问题依然存在
- `strings` 检查发现 bundle 中同时存在修好的代码和旧代码

## 根因
Vite 构建产物 `dist/assets/` 下有多个 `index-*.js` 文件(如 11 个),
但 `index.html` 只引用其中一个。如果引用的那个是旧的(携带 bug),
即使目录里有正确的 JS 文件也不会生效。

## 排查步骤

```bash
# 1. 检查引用了哪个 JS
grep "script.*src" /var/www/pmlophy.com/project/forge-*/index.html

# 2. 遍历所有 JS, 找出干净的
for f in /var/www/pmlophy.com/project/forge-erp/assets/index-*.js; do
  hits=$(strings "$f" | grep -c '找bug关键字')
  [ "$hits" -eq 0 ] && echo "CLEAN: $(basename $f)"
done

# 3. 把 HTML 切到干净版本
sed -i 's|index-.*\.js|index-<CLEAN_NAME>.js|' index.html
```

## 为什么会有多个 JS 文件
- 反重力梭哈时可能产生多套路由树副本
- Vite code-splitting 也可能产生多个 chunk
- 关键是: index.html 引用的那个对不对

## 不要做的事
- 不要让用户(P无技术背景)检查代码
- 不要在没查 JS 文件之前就说"源码有问题"
- 优先: 浏览器缓存 → IndexedDB → 构建产物 → 最后才怀疑源码