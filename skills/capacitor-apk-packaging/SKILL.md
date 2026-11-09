---
name: capacitor-apk-packaging
description: Package a Vite/React web app into a self-signed Android APK via Capacitor — Mac Android env setup, gradle build, and the WebView-specific pitfalls (isDev misdetection, API base URL, AudioWorklet fake-success, CORS preflight, input clear timing).
---

# Capacitor APK 打包（Web 应用 → 自用 Android APK）

> 2026-08-04/05 罗宾 APK 实战沉淀。用户场景：自用 APK 直接安装，**不上架、不签名发布**（debug APK 即可）。用户已配好 Mac Android 环境并声明"以后要反复迭代"。

## 触发条件

- 用户要把现有 Web 项目（React/Vite）打成手机 APK 自用
- 上架 = 开源 + 审核麻烦 → 直接出 debug APK 手机安装

## 环境准备（Mac，一次性）

```bash
brew install --cask android-studio        # 完整环境（含 SDK）
# 首次启动引导装 SDK 组件（platforms/build-tools/platform-tools）
echo 'export ANDROID_HOME=$HOME/Library/Android/sdk' >> ~/.zshrc
echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin' >> ~/.zshrc
source ~/.zshrc
```

**JDK 坑**：Capacitor 新版要 **Java 21**（不是 17）。用 JDK 17 报 `无效的源发行版：21`。M 芯片路径 `/opt/homebrew/opt/openjdk@21/bin`。

## Capacitor 集成 + 打包（每次迭代）

```bash
cd <project>/app                          # 项目代码目录
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap init "App名" "com.<domain>.<app>" --web-dir=dist
npx cap add android
# 每次改完前端：
npm run build
npx cap sync android
cd android && ./gradlew assembleDebug
# 产物：android/app/build/outputs/apk/debug/app-debug.apk
```

## WebView 特定坑（APK 与浏览器行为差异——必查清单）

### 1. isDev 误判 → 免登录直接进主界面
Capacitor WebView 加载 `https://localhost`（内部服务器），前端 `hostname === 'localhost'` 判定为开发环境跳过登录。
```ts
// 修：Capacitor 原生环境不算 isDev
const isCapacitor = typeof window !== 'undefined' && Boolean((window as any).Capacitor?.isNativePlatform?.())
const isDev = !isCapacitor && (hostname === 'localhost' || hostname === '127.0.0.1')
```

### 2. API 相对路径打到 https://localhost → 网络失败
Web 版相对路径 `/p/jarvis/...` 解析到部署域名；APK 里 origin 是 `https://localhost` → 请求打到 Capacitor 本地服务器。**所有 API 路径必须经过 base 函数**：
```ts
// src/api/base.ts
export function getApiBase(): string {
  if (Capacitor.isNativePlatform()) return 'https://pmlophy.com'   // 完整域名
  return ''                                                         // 浏览器相对路径
}
// 每个 API URL：getApiBase() + '/p/jarvis/...'
// 逐个文件接入：auth/hermes/asrStream/history/docUpload/TTS —— 漏一个就是一个接口挂
```

### 3. CORS preflight（nginx 侧）——见 deployment-network-diagnostics skill
APK origin=`https://localhost` 跨域 → OPTIONS 预检 → nginx `auth_request` 拦（预检不带 token）→ 401。修：location 加 `if ($request_method = OPTIONS) { return 204; }` + `add_header Access-Control-Allow-Headers "content-type, authorization"`。**每个带 auth 的 location 逐个 grep Allow-Headers**（history 漏了 authorization → 预检 204 但真实 GET 不发，症状隐蔽）。

### 4. AudioWorklet 假成功 → 语音 chunk=0
Android WebView 里 `addModule` 可能成功但**不产出 PCM** → 会话 start 200 但 chunk 无流量 → 百度 -3101。**APK 环境强制 MediaRecorder**（`preferWebmStreamingCapture()`），浏览器保持 AudioWorklet。

### 5. webm 不能发 asr-stream/chunk（契约是 PCM）
MediaRecorder 产 `audio/webm;codecs=opus`，后端 `asr-stream/chunk` 只认 `audio/pcm`，webm 全被忽略（日志 `非 PCM，已忽略`）。**webm 走整段 `/asr`**（后端 ffmpeg 转 PCM → 识别），APK 不做流式跟嘴。

### 6. 麦克风权限
AndroidManifest.xml 必须加：
```xml
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS"/>
```
WebView getUserMedia 需要 manifest 声明，否则 logcat `No audio device will be available`。

### 7. 输入框发送后不立即清空
根因：`onSend` 是 async，Promise 等整轮回复 resolve → `setInput('')` 被 React 批处理拖到回复结束。修：**拆分发送流程**——同步阶段 `flushSync(() => setInput(''))` 立即清空 + 校验失败恢复；异步 `void executeSendTurn(ctx)` 后台跑。发送后用户新打字不被清：输入框为空且 1.5s 无打字才写入（语音结果防覆盖）。

### 8. 打字卡顿（WebView 重渲染）
三层根因 + 修法：
- **input state 在顶层组件**：每击键触发整页（含消息列表）重渲染 → 抽成 memo 子组件（ComposerStack 内部持有 input state）
- **消息列表全量 DOM**：无虚拟化 → 懒渲染最近 100 条 + "显示全部"入口
- **memo 被内联箭头破坏**：`onCopy={(text) => void copyText(text)}` 每次新建函数引用 → 稳定引用 `onCopy={copyText}`
- 击键不会触发 Dexie 保存（仅 messages 变更时写入）——别乱加防抖

### 9. 识别文本不显示（整段 /asr 分支）
根因：识别区 UI 按 status 分两套逻辑——`recording/transcribing` 用打字机 `displayedAsrText`，`thinking` 等只用 `transcript`。整段 /asr 在 transcribing 末尾才拿全文，打字机 display 还是空 → 面板一直显示占位符；随后 sendMessage 立刻切 thinking 又换分支，全文很难露出。浏览器流式正常是因为 streamingTranscript 多次更新。
修法（只改 APK 分支）：
- `applyAsrLiveText`：APK 下 `flushSync` 同时写 `streamingTranscript` + `transcript`；浏览器仍只写 streaming
- 识别区统一 `displayedAsrText || liveAsrText` 兜底（打字机未跟上直接显示全文）
- thinking/speaking 且有识别文本时继续用 streaming 面板，不切空 transcript 分支
- 清空时机：回合结束且 status==='idle' 才清（TTS 播报期间保留显示）

### 10. 整段识别"全量出现" → 打字机动画
APK 走 webm 整段 /asr，**物理上无流式中间结果**（停止说话才识别）——全量文本出现是架构限制不是 bug。要"跟嘴感"只能加**打字机动画**（全量文本逐字 reveal，40-50ms/字，视觉渐进非真流式）。

**坑：不能复用浏览器的 useTypewriterFollowAlong**——它是为流式增量设计的：`charMs = floor((gap * 0.95) / suffixLen)`，浏览器每次只多几个字 → charMs 合理；APK 一次塞全文 → suffixLen 巨大 → charMs 被压到 MIN_CHAR_MS → 整段弹出。**整段场景要独立打字机**：`setInterval` 固定 45ms/字从空串 +1，动画完成后再 sendMessage（避免切 thinking 打断显示）。

### 11. 录音中"定时 /asr"近似跟嘴（v128 定稿）
APK 无法真流式，但可以**录音过程中周期性调整段 /asr** 实现近似跟嘴：
- 累积 webm，约 1.2s（首包）/ 1.8s 调一次 `POST /asr`，结果实时替换识别区
- **防堆积**：上一次未返回前不发下一次
- 字节增长 ≥2800 提前触发（不只按时间）
- 停止后：abort 在途预览 → 最终 /asr → 打字机收尾 → 发送
- 用户验收标准：识别完整性第一，跟嘴是体验加分；文案显示"正在识别…"而非"结束后识别"

### 12. 热更新（server.url 远程加载）——v130 定稿
打包本地文件 = 每次改代码都要重装 APK（发送→卸载→保存→安装→登录，用户明确嫌烦）。**改成 WebView 加载远程 URL**，部署即更新：
```ts
// capacitor.config.ts
server: {
  url: 'https://pmlophy.com/jarvis-voice/',
  cleartext: false, // 仅 https
  allowNavigation: ['pmlophy.com', '*.pmlophy.com'],
}
```
- 重装 APK 只需一次（带 server.url 的壳），之后永远不用重装
- **改了 capacitor.config.ts 必须 `npx cap sync android` 再打包**——本会话实测：config 里 server.url 正确、cat capacitor.config.json 也有，但 APK 仍加载本地文件（断网能打开），根因就是改配置后没重新 sync。sync 后重新打包才生效。
- **isCapacitorNative() 与 origin 无关**（Capacitor 注入全局）→ 远程加载后 APK 语音分支（webm /asr）仍生效，不会退化成浏览器 PCM 分支
- 同源后 getApiBase() 返回 '' 也能通，现有返回完整域名无冲突
- 登录 token 存 localStorage，热更新（重载）不丢
- 代价：首屏依赖网络、离线不可用（服务在 VPS，可接受）

### 12b. 断网测试法——热更新是否生效的一步定位
APK 打开 → **关掉 WiFi/流量** → 重开 APK：
- **能打开/能进界面** = 加载的是打包进 APK 的本地文件（server.url 没生效）→ 查 config + cap sync + 重打包
- **打不开/白屏** = 加载远程 URL（热更新生效）→ 问题在缓存（见 §13）
这是最可靠的一步定位，比猜"是不是缓存"快得多。本会话实测：断网能打开 → 实锤 server.url 未生效 → sync 重打包解决。

**调试热更新：不要改手机系统时间**——用户曾想改系统时间"加速热更新"，这是无效且有害的（HTTPS/TLS 证书校验依赖系统时钟，改时间会导致连接失败/白屏）。热更新靠 nginx 缓存头 + WebView 重载，与系统时间无关。

### 13. 热更新缓存策略（nginx）
远程加载后 WebView 有 HTTP 缓存，**部署了新代码但 APK 可能还跑旧版**（症状：改了什么看不到）。nginx 配：
```nginx
location /jarvis-voice/ {
    # HTML 不缓存（每次重开拉最新）
    location ~ \.html?$ { add_header Cache-Control "no-cache, no-store, must-revalidate"; expires 0; }
    # 带 hash 的 assets 长缓存（hash 变了自动拉新）
    location ~ \.(js|css|png|jpg|svg|woff2?)$ { expires 30d; add_header Cache-Control "public, max-age=2592000, immutable"; }
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```
**版本角标（调试热更新是否生效的关键工具）**：页面角落显示 `APP_VERSION` 常量（如 v132，12px/opacity 0.4/不挡操作）。APK 重开看角标：显示新版 = 热更新生效；显示旧版 = WebView 缓存还挡着。角标位置用 `env(safe-area-inset-*)` + `viewport-fit=cover` 防曲面屏裁切（右下角在曲面屏会被切，改左下角）。**最终位置教训（v134）**：手机端左下/右下都不合适——输入框占用整个下方区域，角标会被遮挡/挡操作，**应放右上角**（`position: fixed; top/right` + safe-area-inset-top/right，z-index 低于顶栏避免盖住按钮；微信内置浏览器提示条存在时额外 top 下移）。

### 14. 热更新后卡顿判断：先对照手机浏览器
热更新后 APK 变卡（打字/语音）——**先别怀疑热更新本身**。用手机 Chrome/Safari 打开同一 URL 对照测试：
- **浏览器流畅** = 前端没问题，卡顿在 APK WebView 渲染性能（Android WebView < 手机 Chrome，硬件加速/渲染层差异）→ 记录为已知限制或查 WebView 配置
- **浏览器也卡** = v{n} 优化没到位 → 继续让 Cursor 调前端
本会话实例：热更新后 APK 打字卡，但手机浏览器打字流畅 → 判定 WebView 渲染性能问题，不是热更新回归。

### 15. 切后台流式中断 → APK 原生保活（2026-10 罗宾）
现象：APK 发消息切到别的 App/锁屏，思考回复就停。根因：**系统退后台冻结 WebView JS 主线程 → fetch 的 getReader() 流中断**（app/src/api/hermes.ts 的 response.body.getReader()）。浏览器无此问题（PC 不冻结）。

**核心方案（前台 Service 保活 + 不 pause WebView）**：
- `KeepAliveService`（前台 Service）：startForeground + 常驻通知（通知渠道）+ `START_STICKY` + `PARTIAL_WAKE_LOCK`
- `MainActivity`：onCreate/onStart/onResume/onPause/onUserLeaveHint 都 `startForegroundService`；onPause 先 `super.onPause()` 再 `webView.onResume()+resumeTimers()` 不让 JS 挂起（读流不中断）
- AndroidManifest：注册 `<service android:name=".KeepAliveService" android:foregroundServiceType="dataSync"/>` + 权限 `FOREGROUND_SERVICE`/`FOREGROUND_SERVICE_DATA_SYNC`/`WAKE_LOCK`/`REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`/`POST_NOTIFICATIONS`(Android13+)
- MainActivity 引导加电池优化白名单（仅首次弹系统页）；Android13+ 申请 POST_NOTIFICATIONS

**3 个实坑（Cursor 首版就踩，必须返工）**：
1. **startForegroundService 缺服务存活校验**：startForeground() 前多次调用 startForegroundService → `ForegroundServiceDidNotStartInTime` Crash。修法（已实测正确）：静态 `started`/`starting` 双标志 + `synchronized(LOCK)` 保护；`start()` 里 `started||starting` 直接 return；`onStartCommand` 置 `started=true,starting=false`；`onDestroy` 重置两标志 → **START_STICKY 重建后能自愈**（进程被杀重启不卡死）。`startForegroundService` 抛 RuntimeException 时重置 `starting` 防崩溃后卡死。静态标志不设超时会残留——必须依赖 onDestroy 重置来保证进程重建可恢复。
2. **WakeLock 在 Service 全局持到 onDestroy**：App 一起就持着 CPU 不休眠 = 异常耗电 → 系统反而更狠杀后台。**只在退后台(onPause) acquire、回前台(onResume) release**，别 in onCreate 一把持到底。修法（已实测正确）：acquire/release 均做 `if (wl != null && wl.isHeld())` 判断——onPause/onResume 会被系统反复触发，**重复 release 未 held 的锁会抛异常**；`setReferenceCounted(false)` 保留；Service onDestroy 兜底 release。
3. **Manifest service 缺 `android:exported="false"`**：targetSdk 36/Android 12+ 显式要求，否则服务启动异常（内部服务必须 false）。

**验证法**：发一条流式思考对话 → 切到别的 App/锁屏 → 回来看回复是否继续完成。注意：**Cursor 改的是原生层在用户 Mac，未 push 前 VPS 仓库看不到真实文件（目录还是旧 MainActivity.java）——必须用户 push 后 git pull 才能逐行核验，自报≠可见。**

**实测结论**：这套方案**真机验证通过**——切后台 + 锁屏后流式思考回复继续完成（用户验收"可以后台"）。只改原生层，热更新（§12）不受影响；打包仍走 `npm run build && npx cap sync android` → `cd android && ./gradlew assembleDebug`（产物 `android/app/build/outputs/apk/debug/app-debug.apk`）。国产 ROM 仍可能在更激进省电模式下介入，届时不是代码 bug，而是要走系统放行（常驻通知 + 电池白名单）。

## 验证清单（每次重装 APK 后）

```
✅ 桌面图标名正确（strings.xml app_name）
✅ 登录页出现（非免登录）
✅ 登录成功（API 走完整域名）
✅ 聊天/历史/播报
✅ 语音：说话 → VPS 日志 POST /asr（webm 整段 200）→ 识别出文本
✅ 打字：发送后立即清空；打字中不被清
✅ 浏览器模式回归（PCM 流式逻辑不能动）
```

## 红线

- 浏览器端 PCM + AudioWorklet 流式逻辑**禁止改动**（APK 用 MediaRecorder 分支，两套并存）
- 不 commit/push（用户确认后）
- 版本快照 versions/v{n}/ + AGENTS.md 更新（配合 git 基线铁律）
- **协作节奏（用户两次纠正"别急"）**：指令发给 Cursor/Codex 后**不要催、不要反复追问进度**——等它跑完主动汇报。用户自己盯着工具跑，催问是噪音。用户说"慢点别急"= 立即停止催促转待命。
- **push 确认**：VPS 拉仓库显示 "Already up to date" 时先问用户是否 push 过（用户曾纠正"我 push 不需要时间的，你别那么急"），不要假设没提交

## 产物自动流转管道（2026-08-05 建成，罗宾迭代标配；审查门禁方案 A）

Cursor/Codex 改完代码不再让用户手动搬运——两条弱耦合管道（不用 A2A、不用 git 当管道）：

```
管道 1（部署）：Cursor build → zip 在项目根目录 → Mac rsync 上传 VPS incoming/
  → VPS cron 每分钟 --check 只检测（写 pending 标记+日志，【不自动部署】）
  → 用户审报告确认 → 手动 bash /root/deploy-all.sh --deploy <项目> → 热更新生效
管道 2（报告）：AI 生成自检报告.md（任务/文件清单/改动点/自检结果/遗留风险）
  → curl 上传 jarvis-file（X-Jarvis-User: ai-reports）→ 杰西卡读目录审核 → digest 给用户
用户只做：发指令 + 审报告拍板 + 确认部署 + 最后实测
```

**⚠️ 审查门禁铁律（用户原话"不能这么自动化，我还是得把控一下"）**：AI 产物**永不自动部署**。cron 只 `--check` 检测通知，部署必须用户确认后手动 `--deploy`。

组件：Mac `~/.ssh/id_ed25519_vps` 免密 key + VPS `/root/deploy-all.sh`（`--check` 检测 / `--deploy` 部署，幂等：同名已归档跳过）+ cron `*/1 * * * * bash /root/deploy-all.sh --check`（只检测）+ 报告落盘 `/var/lib/jarvis/files/ai-reports/`。完整细节见 skill `ai-artifact-pipeline`。

**规则同步（管道落地最后一步）**：管道跑通后必须把规则写进项目 AI 规则文件，否则 AI 下次不会自动走管道：
- Cursor → `.cursor/rules/artifact-pipeline.mdc`（alwaysApply: true）
- Codex → `AGENTS.md` §2.2
- 反重力 → `.agents/rules/antigravity-rules.md` 追加段
- 改完一次 commit + push，用户 Mac pull 后生效

### 管道多项目推广（通用 deploy-all.sh，2026-08-05，审查门禁版）

单项目管道跑通后推广到 forge-erp/wms/crm 等项目，**用参数化通用脚本**（不要每项目复制一份单项目脚本）：

```bash
# /root/deploy-all.sh 核心：项目映射表，每项 = incoming 目录 → 部署目标
declare -A PROJECTS=(
  ["/var/www/pmlophy.com/jarvis-voice-incoming"]="/var/www/pmlophy.com/jarvis-voice"
  ["/var/www/pmlophy.com/forge-erp-incoming"]="/var/www/pmlophy.com/project/forge-erp"
  ["/var/www/pmlophy.com/forge-wms-incoming"]="/var/www/pmlophy.com/project/forge-wms"
  ["/var/www/pmlophy.com/forge-crm-incoming"]="/var/www/pmlophy.com/project/forge-crm"
  ["/var/www/pmlophy.com/copy-wms-incoming"]="/var/www/pmlophy.com/project/copy-wms"
)
# 用法：
#   bash /root/deploy-all.sh --check            # cron 用：只检测新包写 pending，不部署
#   bash /root/deploy-all.sh --deploy           # 部署所有 pending 包（用户确认后手动跑）
#   bash /root/deploy-all.sh --deploy <项目名>   # 只部署指定项目
# 循环：找最新 zip → 幂等检查 → 解压 → 备份当前 → 部署（python 修相对路径）→ curl 验证 → 归档/回滚
# cron（只检测不部署）: */1 * * * * bash /root/deploy-all.sh --check >> /var/log/jarvis-deploy.log 2>&1
```

- 每项目建 `<项目>-incoming/` + `<项目>-backup/` 目录（VPS 端可提前建好，等用户 git 仓库就绪）
- 验证 URL 用 `https://pmlophy.com/<项目名>/`（静态站部署在 /project/ 下）；失败自动回滚
- **审查门禁是方案 A 核心**：cron 永不自动部署；--deploy 必须用户审报告确认后手动执行（用户原话"不能这么自动化，我得把控一下"）
- **部署目录可提前建，但规则文件要等源码仓库就绪**（VPS 上只有 dist 产物时无法加 .cursor/rules）
- **多仓库 push 冲突规避（用户明确要求）**：用户正给多个项目建 git 基线时，**只 push 管道配置这一个文件/commit**，不碰其他文件——避免与他 git 操作冲突。通用方案文档单独放 `docs/skills/ai-artifact-pipeline.md`（独立 commit），用户 `git pull` 后各项目自行参照

### 免密 SSH 配置坑（管道前置，2026-08-05）

Mac 生成 key 加到 VPS authorized_keys 后 `ssh -i key` **仍要密码** → 根因：VPS sshd 配置 `PubkeyAuthentication no`（默认禁用 key 认证）。修：
```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak-<ts>
sudo sed -i 's/^PubkeyAuthentication no/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sudo sshd -t && sudo systemctl restart ssh
```
**诊断顺序**：key 加了仍要密码 → 先查 `grep PubkeyAuthentication /etc/ssh/sshd_config`，别怀疑 key 权限/路径。这是免密配置的头号坑。
