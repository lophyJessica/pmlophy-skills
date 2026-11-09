# jarvis-voice 播报中发消息失效（并发竞态）——复现 + 根因 + 修复方向

> 2026-08-20 实测。罗宾（jarvis-voice 网页版）与文字版 jarvis（复制同款代码）均有此 bug。

## 现象（用户 100% 复现）

- 罗宾在**播报中（speaking）**，用户立即在输入框发一条文字消息。
- 效果：那条消息**暂时不回答、且从聊天列表消失**。
- 过一会儿（旧回合真正结束后）消息**又出来**，并且**带了回复**。

## 为什么是竞态（根因，App.tsx 发送链路）

发送链路两个函数：
- `prepareSendTurn`（L521）：`cancelSpeech()` → 把新消息写进 `messagesRef.current` 并 `setMessages` → `transitionTo('thinking')` → 新 `AbortController` 赋给 `activeRequestRef.current`。**注意它只 cancelSpeech()，没有 abort 正在跑的上一个回合的 activeRequestRef。**
- `executeSendTurn`（L562）：`await streamChatCompletion(...)` → 成功后 `L582 setMessages(nextMessages)`（用**自己快照 pendingMessages** 重建列表）→ L601 `persistTurn` → L604 `waitForSpeechDrain()` 等播报 → L607 `transitionTo('idle')`。

**竞态时序**：
```
上一回合 executeSendTurn 完成后进入 L604 waitForSpeechDrain() 阻塞等播报
（此时 status='speaking'，activeRequestRef 仍是上一回合的 controller）

用户播报中发消息
→ 新回合 prepareSendTurn：cancelSpeech() 停播报、入列新消息、transitionTo('thinking')
→ 新回合 executeSendTurn 开始 streamChatCompletion（新请求）

上一回合 waitForSpeechDrain() 因 cancelSpeech 触发的播报结束而 resolve 返回
→ 上一回合走到 L582 setMessages(nextMessages)：用【它自己的 pendingMessages，不含用户刚发的新消息】覆盖界面
   → 用户刚发的消息从聊天列表"消失"
→ L630 finally: activeRequestRef.current === 上一回合 controller？此时已是新回合 controller → 不误清（=== 判断挡住了）
→ 新回合 streamChatCompletion 完成 → L582 再次 setMessages(含新消息+回复) → 消息"又出来且带回复"
```

## 根因一句话

**发送链路缺"新回合打断/串行旧回合"的互斥保护**：`prepareSendTurn` 没 abort 旧回合，且 `executeSendTurn` 的 `setMessages/persistTurn/transitionTo('idle')` 没有"仅当前回合可写"的 guard，导致播报中旧回合用旧快照覆盖 UI、把新消息临时顶掉。

## 修复方向（彻底方案 = abort 旧回合 + guard 双保险，都在 app/src/App.tsx）

1. **prepareSendTurn 开头**（cancelSpeech() 之前）插入：
   ```
   activeRequestRef.current?.abort()
   activeRequestRef.current = null
   ```
   发新消息时先打断还在跑的旧回合请求，避免两回合并发。

2. **executeSendTurn 内 L580-584**（setMessages/setHistory/setConnectionState）加当前回合 guard：
   ```
   if (activeRequestRef.current === requestController) {
     ... setMessages / setHistory / setConnectionState / setAssistantStreamingText
   }
   ```
   若期间已切到新回合（activeRequestRef 指向别的 controller），旧回合不再写 UI——`messagesRef` 的更新也应放进 guard 内。

3. **L601 persistTurn 与 L607 transitionTo('idle') 加相同 guard**：
   ```
   if (activeRequestRef.current === requestController) await persistTurn(nextMessages)
   if (activeRequestRef.current === requestController && statusRef...) transitionTo('idle')
   ```
   旧回合被新回合打断后，不再 persist 旧历史、不再把状态切回 idle。

## 排障要点

- 现象"消息消失后稍后带回复又出现" = 强竞态信号（不是真丢，是 setMessages 覆盖回退 + 最终一致）。
- 不要把这类归因到后端/网络——`messagesRef` 引用 + 无 guard 的 `setMessages` 是典型前端状态竞态。
- 修复后复现验证：让罗宾说一句长话（播报中）→ 立即发文字 → 期望新消息立即上列表、旧播报停、正常思考回复这条新消息，不再"消失/滞后"。
- 文字版 jarvis 是同款复制代码，同样问题——修好罗宾版后，按罗宾实际改动给 jarvis 出独立指令（AGENTS.md 铁律：jarvis 与 jarvis-voice 物理隔离，禁止跨项目改代码，指令分开写）。

---

## 附：部署 jarvis-voice 的 deploy-all.sh 路径坑（2026-08-20 实测）

- **jarvis-voice 部署在根路径** `https://pmlophy.com/jarvis-voice/`（不是 `/project/{name}/`）。
- 但 `deploy-all.sh` 的验证 URL 硬编码为 `https://pmlophy.com/project/$(basename "$DEST")/` → 对 jarvis-voice 验出 `/project/jarvis-voice/` = **404** → 脚本误判"部署失败"触发回滚。
- **实际文件已成功部署**（线上 index.html 已是新 bundle，`/jarvis-voice/` + 新 bundle 都 200）；回滚也因 backup 无旧版本走"保留当前状态"。**部署实际成功，只是日志报假失败。**
- **判断"真失败 vs 误报"**：绕开脚本——`grep -o 'index-[A-Za-z0-9]*\.js' /var/www/pmlophy.com/jarvis-voice/index.html` 确认线上已是新 bundle + `curl 正确的根路径`/新 bundle = 200。
- **修复建议**：deploy-all.sh 的 URL 构造特判 jarvis-voice（或对非 /project/ 部署的项目改用 `https://pmlophy.com/${DIRNAME}/`）。
- **另**：部署前确认 `{项目}-backup/` 目录存在——不存在则 `mv` 旧目录报 `No such file or directory` + copytree `FileExistsError`。
