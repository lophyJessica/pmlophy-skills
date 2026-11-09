---
name: web-app-to-apk
description: 把现有 Web 应用（React/Vite 等）打包成自用 Android APK——方案选型、Mac 安卓环境搭建、Capacitor 打包流程、WebView 能力边界。当用户想把罗宾/网页项目做成手机 App 时使用。
---

# Web 应用打包自用 APK

> 用户场景（2026-08-04 定）：**自用 APK，不上架**。上架 = 开源 + 审核麻烦（隐私权限），自用直接安装（Android 允许"未知来源"）。用户明确"以后要反复迭代"，所以 Mac 装 Android 环境是长期投资。

## 方案选型（先想清楚目的，再动手）

| 方案 | 速度 | 质量 | 适用 |
|---|---|---|---|
| **PWA 添加到主屏幕** | 0 开发（5 分钟） | 接近 App | 只要桌面入口/全屏，先验证值不值得做 |
| **WebView 套壳（Capacitor）** | 1-2 天 | 较好 | 自用 APK 首选，npm 生态直接集成 |
| **原生重写（RN/Flutter）** | 数周 | 最好 | 要上架/要原生能力，自用没必要 |

**推荐路径**：先 PWA 验证手机体验 → 确认值得 → Capacitor 打包。**不要先装环境再想目的**。

## 关键决策点

1. **上架 vs 自用**：上架 = 开源 + 审核 + 签名麻烦；自用 = 直接装 APK，跳过 Play 签名。用户已定自用。
2. **Mac 有无 Android 环境**：没有则二选一——
   - Mac 装 Android Studio（用户选了这个，理由：以后反复迭代要反复打包，装一次长期受益）
   - VPS 打包（Linux SDK，但 1.9GB 内存小、下载大、慢）——不推荐
   - 在线打包（GitHub Actions）——有学习成本，不推荐自用场景
3. **WebView 能力边界（打包前必须验证，2026-08-05 修正）**：
   - **AudioWorklet 在 Android WebView 不可靠**：`addModule` 可能"假成功"（不报错）但**不产出 PCM** → 会话 start 200 但 chunk=0 → 后端百度报 -3101 wait audio over time。症状就是"语音卡住/识别不出"。**APK 原生壳必须跳过 AudioWorklet，强制 MediaRecorder**（`Capacitor.isNativePlatform()` 检测）
   - getUserMedia 麦克风：需声明权限（RECORD_AUDIO）+ WebView 运行时授权弹窗
   - IndexedDB/localStorage：支持 ✅
   - SSE 长连接：WebView 无微信那种截断问题（微信内置浏览器 X5 内核才截断）

## Mac 安卓环境搭建（Homebrew）

```bash
# 方案 A：Android Studio 一步到位（用户选这个，含 SDK+模拟器+命令行工具）
brew install --cask android-studio
# 首次启动引导装 SDK（选 API 34 或默认）

# 方案 B：纯命令行（不要 IDE 时更轻）
# brew install openjdk@17
# brew install --cask android-commandlinetools android-platform-tools
# sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"

# 环境变量（加到 ~/.zshrc）
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin
```

验证：`java -version`（JDK 17）+ `adb version`。下载慢用代理（用户有 100Mbps + 代理）。

## Capacitor 打包流程

```bash
cd <项目>/app   # 前端目录
npm install @capacitor/core @capacitor/cli
npx cap init "罗宾" "com.robin.app" --web-dir=dist
npx cap add android
npm run build && npx cap sync
npx cap open android        # 打开 Android Studio 手动构建
# 或命令行直接出 APK：
cd android && ./gradlew assembleDebug
# 产物：android/app/build/outputs/apk/debug/app-debug.apk
```

**环境坑**：
- **JDK 必须 21**（不是 17）：Capacitor 新版编译报 `无效的源发行版：21` → `brew install openjdk@21`，PATH 指向 21；换版本后 `./gradlew clean` 重构建
- 验证：`java -version`（21.x）+ `adb version` + `echo $ANDROID_HOME`

**打包/运行坑（详见 jarvis-dev references/capacitor-apk-packaging.md）**：
- `--web-dir` 必须指向构建输出目录（Vite 是 dist）
- 每次前端改动：`npm run build && npx cap sync`（同步新 bundle）
- **isDev 误判免登录**：Capacitor WebView 加载 `https://localhost` → 前端 `hostname==='localhost'` 判为开发环境 → 需 `Capacitor.isNativePlatform()` 排除原生壳
- **API 相对路径网络失败**：WebView origin 是 localhost → 相对路径 `/p/jarvis/...` 打到本地服务器 → 需 `getApiBase()` 原生环境返回完整域名 `https://pmlophy.com`，浏览器返回 ''
- **CORS 预检被 nginx auth_request 拦**（登录/历史通但聊天失败）：APK 跨域发 OPTIONS 预检（不带 Authorization 头）→ auth_request 401 → nginx 该 location 加 `if ($request_method = OPTIONS) { return 204; }` + CORS 头；凡是有 auth_request 的 location 都要补
- **CORS Allow-Headers 缺 authorization → 能聊但拉不到历史**（2026-08-04 实锤）：APK 里聊天正常但历史为空——chat/completions 的 location 加了 `Access-Control-Allow-Headers "content-type, authorization"`，但 history 的 location 只写了 `"content-type"`。后果：OPTIONS 预检返回 204（看起来放行了），**但浏览器判定预检失败 → 真实 GET 请求根本不发出**（nginx 日志只见 OPTIONS 不见 GET）。修复：所有带 auth 的 location 的 Allow-Headers 必须含 `authorization`，逐个检查不能只修一个。
- **每个被 APK 调用的 nginx location 都要检查 CORS**（不只带 auth 的）：asr-stream 要放行 `x-session-id` 头（chunk 用自定义头），/tts 是另一个 location 也要 `OPTIONS 204 + Allow-Headers`。症状：某功能网页正常、APK 里完全没请求/请求失败 → 大概率是该 location 缺 CORS。**APK 全功能验收时逐个功能对照 nginx 日志，缺哪个 location 补哪个。**
- **APK 语音卡住排查**（2026-08-05 实锤）：asr-stream/start 有请求（200）但 **chunk 一条都没有**（后端日志 `chunk=0 bytes=0`，百度报 -3101 wait audio over time）→ 不是后端问题，是 **APK 端麦克风采集/流式上传没启动**。两步查：① nginx 日志确认 chunk 是否到达（没到 = 前端没发）② 前端排查 AudioWorklet 是否工作（Android WebView 支持有限，失败应降级 MediaRecorder webm→/asr）。VPS 侧 CORS 修好后仍无 chunk，就是 WebView 采集层问题，交给 Cursor 在 APK 环境强制降级路径。
- **webm 不能发 asr-stream/chunk（2026-08-05 v121 实锤）**：强制 MediaRecorder 后前端把 webm 切片发 chunk，但后端 `asr-stream/chunk` 契约是 **PCM-only**（`if 'pcm' in ctype`）→ 日志 `chunk content-type='audio/webm;codecs=opus' 非 PCM，已忽略` → chunk=0 识别不出。**正确分流**：浏览器 = PCM+AudioWorklet → chunk 流式跟嘴；APK/WebView = MediaRecorder 攒 webm → end 后整段 POST `/asr`（Content-Type: audio/webm）拿最终文本，不做流式跟嘴。改前端前先看后端日志确认 chunk 的 content-type，别把 webm 硬塞给 PCM 接口。
- **APK 打字卡顿**（2026-08-05 v120）：WebView 里 React 重渲染开销更大，三个根因：① `input` state 在组件顶层，每次击键触发整页（含 200 条消息）重渲染 ② 消息列表全量 DOM 无虚拟化 ③ memo 组件被内联箭头函数破坏（`onCopy={(t,k)=>...}` 每次新建引用）。修法：输入框抽独立 memo 组件持有 input state、消息列表 memo + 稳定引用、默认懒渲染最近 100 条。**回归坑**：重构后发送清空 input 的时序会变（发送后文字残留要等一会才清、打字中可能被语音识别结果覆盖清空）——发送要立即清空，语音识别文本只在空闲时写入，别覆盖正在输入的内容。
- **排查技巧：看 nginx access log 区分 OPTIONS vs GET**——APK 跨域问题先看日志：只有 OPTIONS（204）没有后续 GET = 预检通过但浏览器拦截真实请求（CORS 头缺项）；OPTIONS 401 = auth_request 拦截预检。两种症状不同，修法不同。
- **排查前先确认拉的代码是最新**：本地改过没 push 时，VPS `git pull` 拉到旧版会误判"代码没改"。先 grep `getApiBase` 确认版本，再判断是前端还是 nginx 问题。
- 麦克风权限：AndroidManifest.xml 加 `<uses-permission android:name="android.permission.RECORD_AUDIO"/>` + `MODIFY_AUDIO_SETTINGS`
- 应用名：`android/.../values/strings.xml` 的 `app_name` + `capacitor.config.ts` 的 `appName` 两处改
- 自用安装：手机开"未知来源"，直接传 APK 安装

## 热更新（部署即更新，免重装，2026-08-05 v130-v133 打通）

**动机**：用户重装 APK 要走"发送→卸载→保存→安装→登录"五步，太烦。改成 WebView 加载远程 URL，改代码部署 VPS 后 APK 刷新即新版，**永不再重装**。

```ts
// capacitor.config.ts 加 server 段
server: {
  url: 'https://pmlophy.com/jarvis-voice/',  // 远程加载
  cleartext: false,                          // 仅 https
  allowNavigation: ['pmlophy.com', '*.pmlophy.com'],
}
```

**坑（用户实测踩过，v130 版）**：
- **改 config 后必须 `npx cap sync android` 再重新打包**，否则壳仍加载打包进 APK 的本地 assets 快照（`android/app/src/main/assets/public/`），server.url 不生效。**验证方法：断网打开 APK——能打开 = 还在加载本地快照（热更新未生效）；打不开/白屏 = 加载远程（生效）**。用户当时 `cat app/src/main/assets/capacitor.config.json` 看到配置已同步，但装的 APK 是旧壳——**配置在源码里≠配置在已装的 APK 里**，必须重新打包安装一次"热更新壳"，之后才永久免重装。
- **nginx 缓存策略**：HTML 必须 no-cache（否则 WebView 缓存旧 index.html 永远看不到新版本），assets 带 hash 可长缓存：
  ```nginx
  location /jarvis-voice/ {
      location ~ \.(js|css|png|jpg|svg|woff2?)$ { expires 30d; add_header Cache-Control "public, max-age=2592000, immutable"; }
      location ~ \.html?$ { add_header Cache-Control "no-cache, no-store, must-revalidate"; expires 0; }
      add_header Cache-Control "no-cache, no-store, must-revalidate";
      try_files $uri $uri/ /jarvis-voice/index.html;
  }
  ```
- **版本角标（验证热更新的关键）**：页面角落加版本号角标（12px/opacity 0.4/pointer-events none），部署后 APK 重开看角标确认加载的是新版。角标位置避开下方输入区——手机端输入框占满底部，左下/右下都不合适，放**右上角**（safe-area-inset-top/right）。
- **热更新不影响 APK 判定**：`isCapacitorNative()` 只看 Capacitor 注入的全局，与 origin（localhost vs pmlophy.com）无关 → APK 语音分支（webm 整段 /asr）保持生效，不会被远程加载改成浏览器 PCM 流式分支。
- 热更新后打字卡 ≠ 热更新问题：手机浏览器（也是远程加载）流畅 = 前端没问题，是 Android WebView 渲染性能本身比系统浏览器弱。

## APK 语音识别区显示 + 打字机（2026-08-05 v124-v128）

- **识别区不显示文本（v124 根因）**：UI 按 `status` 分两套逻辑——`recording/transcribing` 用打字机 `displayedAsrText`，`thinking` 只用 `transcript`。APK 整段 /asr 在 transcribing 末尾才拿全文 → 打字机 display 还是 '' → 面板一直显示占位符，随后 sendMessage 切 thinking 又换分支。修法：显示统一 `displayedAsrText || liveAsrText`，thinking/speaking 期间有识别文本就继续用 streaming 面板，idle 才清空。
- **打字机动画不生效（v127 根因）**：`useTypewriterFollowAlong` 是给**浏览器流式增量**写的（`charMs = gap*0.95/suffixLen`）——浏览器每次只多几个字 charMs 合理；APK 一次塞全文 → suffixLen 巨大 → charMs 压到 MIN 值 → 看起来整段弹出。**修法：APK 专用独立 setInterval 打字机（固定 45ms/字），不复用流式 hook**。
- **APK 跟嘴（v128）**：MediaRecorder webm 整段 /asr 本身无中间结果，近似跟嘴 = 录音中**周期性**（1.2s 首包/1.8s 后续）把累积 webm POST /asr 实时替换识别区 + 防堆积（上一次未返回不发下一次），停止后最终 /asr + 打字机 → 发送。
- **发送后输入框立即清空（v122 根因）**：`sendMessage` 是 async，Promise 要等**整轮回复结束**才 resolve——若 `setInput('')` 依赖该 Promise（await onSend 之后）或与 `transitionTo('thinking')` 同帧合并，界面会长时间保留原文直到回复完成才清。修法：拆分 `prepareSendTurn`（同步校验+入队+thinking，同步 return）+ `executeSendTurn`（异步对话 void 后台跑）；`flushSync(() => setInput(''))` 点击立即清空；仅校验失败恢复文字；语音识别结果只在输入框空且 1.5s 无打字时写入（setTextIfIdle）。

## 后台保活（切应用后 WebView 冻结、流式中断，native 层修）

**症状**：WebView 套壳 App 发消息后切到别的应用，思考回复就停止。**根因**：Android 系统在 App 退后台时冻结 WebView 的 JS 主线程 → 流式 fetch（`response.body.getReader()`）中断。**不是前端 fetch 代码的问题，是原生层冻结问题——改原生，不动 src/**。

**核心方案：前台 Service（startForeground）+ 常驻通知**——让 App 退后台也处于"前台服务"态，不被系统冻结 WebView。这是最有效的保活。

```java
// KeepAliveService.java（包 com.<app>.*）：startForeground + START_STICKY + 通知渠道
public class KeepAliveService extends Service {
    // onCreate: 建通知渠道 NotificationChannel
    // onStartCommand: startForeground(NOTIF_ID, 通知"XX在后台保持运行") → 返回 START_STICKY
    // Service 需持有/感知 WebView，确保退后台 WebView 不销毁、JS 主线程不被冻
}
```

**极守活增强（minSdk 24 / target 36 都支持）**：
- AndroidManifest 注册 Service + 权限 `FOREGROUND_SERVICE`、`WAKE_LOCK`、`REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`
- 启动时引导用户把 App 加入忽略电池优化白名单（防锁屏/后台被杀）
- WebView 生命周期：Service 存活时 WebView 持活，**退后台不要手动 pause/销毁 WebView**（那是 JS 冻结主因），恢复时正常 resume

**关键坑（native 保活）**：
- Capacitor WebView 加载 `server.url` 远程 URL 时，**空 Service 没用**——Service 必须跟 WebView 生命周期挂钩，否则 Service 活着但页面还冻结。要"维持 WebView/JS 运行"，不是起个空 Service。
- **改动边界**：保活是原生层(native Java/Kotlin + AndroidManifest)的事，**不要动 src/ 前端 fetch 逻辑**（根因在原生冻结，不在 fetch 代码）。写 Cursor/Codex 指令时明确"只改 app/android 原生层"。
- **通知常驻可接受**：用户确认罗宾使用频率不高，通知栏常驻可接受——保活用前台 Service + 通知是顺理成章的；若用户反感常驻通知，再权衡是否降级。

## 相关经验（2026-08-04 会话）

- **协作节奏：不要催用户/AI**（用户两次纠正"你别那么急啊""慢点别急杰西卡"）：等 Cursor/Codex 改代码时，用户说"还在改"就停下待命，不重复追问进度、不催打包、不抢跑下一步。VPS 侧能做的做完（备份/改 nginx/验证），剩下的等用户发包——**每轮只做一个动作，用户说等就等**。
- **手机硬件麦克风比电脑强**：手机（阵列+降噪）识别明显更准——语音功能在手机上价值更高，是打包动机
- **微信内置浏览器 SSE 截断**（读一小段就停）：是 X5 内核问题不是 App 问题——前端加 MicroMessenger UA 检测提示"用系统浏览器打开"即可，见 jarvis-dev 的 wechat-inapp-browser reference
- **项目结构**：罗宾已整理为 `app/`（代码）+ 根目录（文档），打包在 app/ 下执行
