# CMS 原型部署到 VPS（评审/出图的前置）

用途：把 `99-产品原型prototype/` 构建产物发到 `https://pmlophy.com/project/cms/`，供评审、挂标注、出整页红框图。原型 vite 的 `base` 已经是 `/project/cms/`，**不要改代码**。

## 一、构建（在 VPS 上）

VPS 可用内存常年只有 ~900MB，网关自己占几百 MB，**构建要用 systemd-run 关进独立 cgroup**，否则可能把网关 OOM 掉（历史上 Chrome 裸跑被杀过多次）：

```
cd /root/repos/cms-project/99-产品原型prototype
systemd-run --scope -q -p MemoryMax=900M -p MemorySwapMax=0 --unit=npmci-$$ npm install --no-audit --no-fund
systemd-run --scope -q -p MemoryMax=1200M -p MemorySwapMax=0 --unit=npmbuild-$$ npm run build
```

- `npm run build` = `tsc -b && vite build`；正常输出 86 modules、`dist/assets/index-*.js` 约 800KB。
- 构建会改动仓库里入库的 `dist/` 和 `package-lock.json`——**提交时只提该提的**（规则文件/源码），别把 dist 与 lock 的噪声一起提。

## 二、发布 + nginx

```
D=/var/www/pmlophy.com/project/cms
mkdir -p "$D" && rm -rf "$D"/* && cp -a dist/. "$D"/
```

nginx 站点文件是 `/etc/nginx/sites-enabled/pmlophy.com`（普通文件，不是软链）。在 `/project/forge-crm/` 那个 location 后面插入（照现有写法，**必须带 `try_files` 回退**，否则 BrowserRouter 的深链接直接 404）：

```
    # 外销 CMS 前端原型
    location /project/cms/ {
        alias /var/www/pmlophy.com/project/cms/;
        try_files $uri $uri/ /project/cms/index.html;
    }
```

- 改前先备份：`cp -a $F $F.bak-$(date +%Y%m%d)-cms`；改完 `nginx -t` 再 `systemctl restart nginx`（本项目 nginx 改配置一律 **restart 不是 reload**）。
- 插入用 python 逐字符串替换 + `assert s.count(anchor)==1`，并先 `grep -q 'location /project/cms/'` 判重——重复插块会让 `nginx -t` 失败。

## 三、验收三件套（缺一不可）

```
curl -s -o /dev/null -w "%{http_code}\n" https://pmlophy.com/project/cms/          # 首页 200
curl -s -o /dev/null -w "%{http_code}\n" https://pmlophy.com/project/cms/auth/tags # 深链接 200（验 try_files）
curl -s -o /dev/null -w "%{http_code}\n" "https://pmlophy.com$(grep -o '/project/cms/assets/[^"]*\.js' $D/index.html | head -1)"
```

再**截一张图确认真的渲染**（200 不代表没白屏）：

```
systemd-run --scope -q -p MemoryMax=700M -p MemorySwapMax=0 --unit=shot-$$ \
  /root/.agent-browser/browsers/chrome-155.0.8059.84/chrome --headless=new --no-sandbox \
  --disable-gpu --hide-scrollbars --window-size=1450,1400 --virtual-time-budget=6000 \
  --screenshot=/tmp/x.png https://pmlophy.com/project/cms/auth/tags
```

判读：**不要用「深色像素占比」判断是否白屏**——这套原型是浅色 UI + 数据要从 IndexedDB 加载，深色占比会低到 0.1% 看着像空页。正确做法是看图里有没有顶栏/左侧菜单/页面标题这些框架文字（`vision_analyze` 问「是完整后台界面、空白页还是加载中」）。`正在加载本地标签数据...` 是正常的加载态，不是白屏。

## 三之二、导购端（V销冠）原型 + 首页卡片

导购端工程在 `cms-src/guide-app/guide-app/99-产品原型prototype`（React 18 + zustand，vite `base: './'` + **HashRouter**）：

- 相对资源路径 + HashRouter → 子路径部署天然没问题，但 nginx location 仍照同一套写（`alias /var/www/pmlophy.com/project/guide-app/` + `try_files`）。
- 构建同样套 `systemd-run` 限内存；产物约 250KB。
- 验收：首页 200 + `./assets/index-*.js` 200，再**用手机尺寸截图**（`--window-size=430,900 --virtual-time-budget=6000`）确认渲染——正确页面能看到「任务 / 待完成 / 已完成 / 已过期」+ 任务卡片 + 底部导航（任务 / 用户管理 / 我的）。

**每上线一个原型，必须同时给作品集首页加卡**——用户会直接问「这里没加呢」。首页是 `/var/www/pmlophy.com/index.html`（静态单文件，非入库）：

```html
    <a href="/project/xxx/" class="card">
      <div class="card-title">外销CMS 原型</div>
      <div class="card-desc">一句话说清覆盖什么模块 / 当前在做什么</div>
      <div class="card-version">原型 · 迭代中</div>
    </a>
```

- 改前 `cp -a index.html index.html.bak-$(date +%Y%m%d)-加xx卡`；插入锚点用 `sc-jxc-course.html` 那张卡（`assert s.count(anchor)==1`），新卡插在它前面、紧跟项目类卡片之后。
- 改完核：`curl -s https://pmlophy.com/ | grep -c 'project/xxx'` 应为 1，并截图确认卡在第二行（`vision_analyze` 问“第几行第几个”）。

## 四、相关服务排障

评测/自检报告的上传端是 `jarvis-file`（`/opt/jarvis-file.py`，监听 127.0.0.1:8871；nginx `location /p/jarvis/file` → `127.0.0.1:8871/file`）。上传返回 **502** 时先 `systemctl status jarvis-file`，服务停了就 `systemctl start jarvis-file`，再用 `curl -F "file=@x.md" -H "X-Jarvis-User: ai-reports"` 复测到落盘路径为止。
