# jarvis-voice「刷新后历史空」回归——根因 + 排查（2026-08-20）

> 罗宾网页版。紧接"播报中发消息失效"修复之后出现：**刷新页面后整个聊天列表历史变空**。
> 服务端历史明明在（jarvis.db messages 表 590 条），前端却读取不到 → 刷新后列表空。

## 症状与排障

- 服务端历史存在：`/var/lib/jarvis/jarvis.db` 的 `messages` 表有数据（lophy 330 条 / lophy-jarvis 223 条），`get_history` 能返回。
- 前端 `loadCloudHistory` + `getLocalMessages()` 合并显示；刷新走 Mount 时的 `refreshHistory()`。
- 关键排除：history 接口 404 是 **favicon.ico**（无害，根路径没图标正常），**不是**历史请求 404——别被误导。

## 根因（Cursor"修一处 bug"顺手删了另一处关键行）

给 Cursor 修"播报中发消息失效"竞态时，它**把 `handleLoginSuccess` 里的 `await clearLocalMessages()` 删掉了**（还把函数从 async 改成普通箭头函数）。

- 旧版 `handleLoginSuccess`：async → `setAuthToken`/`setUsername` 前 `await clearLocalMessages()`（登录后清空本地 Dexie 缓存，避免串用户 + 强制 refreshHistory 以服务端为准）。
- Cursor 版：只 `setAuthToken(token)` + `setUsername(...)`，`clearLocalMessages()` 没了。

后果：本地 Dexie 缓存未按用户隔离/未正确以服务端为准回填，配合 refreshHistory 的合并（`mergeMessages(local, server)`）出现空结果 → 刷新后列表空。

**判断方法（diff 新旧源码）**：VPS `/root/repos` 是旧版不含 Cursor 修复，用户 Mac 的 App.tsx 是 Cursor 改后版——`diff` 两者，会发现除了预期 guard/abort 改动，**还有一处不该动的 `handleLoginSuccess` 被改了**（clearLocalMessages 被删）。这就是回归点。

## 教训（通用，不只本项目）

1. **Agent 修一个 bug 可能顺手删/改掉"看起来无关但关键"的相邻代码**（登录/历史同步这类容易被当冗余的缓存清理）。修完后**必须 diff 确认只动了预期范围**，不是只看"build 通过"。
2. **"刷新后列表空"这类症状，别只看发送/存储侧**——先确认服务端有数据（`jarvis.db` messages 表），再进前端看"加载/合并/缓存清理"侧；缓存的"清理"逻辑被误删极常见。
3. 修复指令的红线要写**"只改 [明确函数/范围]，不准动 handleLoginSuccess/refreshHistory/历史同步逻辑"**——明确列出不许碰的相邻关键点。
4. 若 agent 删了把"用户隔离/缓存清理"当"冗余"，恢复它即可（它是有存在理由的），但要理解它为什么存在（防串用户 + 强制服务端为准）。
