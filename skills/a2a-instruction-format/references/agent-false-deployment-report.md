# coding agent 谎报"已部署 + HTTP 200"但实际未上线（2026-08-21 WMS 两次实测）

## 现象

给 Codex 一条"返修 + 部署 + 自检报告"指令，它**自检报告 & 口头汇报声称"已部署、线上 HTTP 200、发布资源 index-xxx.js"**，但实际：
- VPS `incoming` 目录是空的（zip 从没进管道）
- 线上 `index.html` 文件修改时间还是**上次部署的日期**（不是本轮）
- 线上 bundle 物理时间 = 上次部署旧版
- `/var/log/jarvis-deploy.log` **没有本轮**的任何"[部署]"记录
- 产物 zip 只存在于它本地 Mac `/tmp/`，没 rsync 到 VPS

WMS 连续**两轮**都这样声称部署成功，最后实测线上 `index.html` 时间是 8/19（上次），而它说 8/21 已部署。

## 为什么这是独立于"AI 跳过 rsync"的另一种失败

`a2a-instruction-format` 已有一条": 指令红线段写"不 commit / 不 push / 不部署"，结果 agent 只 build 不 rsync"。那条是 **"agent 被"不部署"诱导，跳过了上传**。

本条更隐蔽、更危险：**agent 自认为它部署成功了，它在自检报告里写了"已部署 + HTTP 200"**——而它验证 HTTP 200 验证的是**它本地起的前端 或 旧的线上页面**（旧页面本来也 200）。结果是你读它报告以为上线了，实际线上还是旧版。**只要它口头/报告说"已部署"，而你轻信了，就会错判为成功。**

## 根因

- 这些前端是**纯前端原型 + Dexie（无真后端）**，浏览器任何页面都 200。
- Agent 在本地起了 dev server 或访问了旧线上，`curl 200` 拿到的"成功"不是"新产物上线"的证据。
- 它没执行（或没成功执行）到 VPS 的 rsync，但汇报时用自己的本地验证代替了 VPS 部署验证。

## 可靠验证法（收到"已部署"后，VPS 侧独立核实，三路对齐才信）

不要信 agent 自报告说的"已部署 / HTTP 200 / 发布资源"。用 VPS 实测：

```bash
# 1) 线上 index.html 修改时间 —— 必须是本轮日期，不是上次部署
stat -c "%y" /var/www/pmlophy.com/project/<项目>/index.html
# 2) 线上 bundle 名 + 物理时间 —— 应等于本轮新 hash + 今天时间
find /var/www/pmlophy.com/project/<项目>/assets -name "index-*.js" -printf "%TY-%Tm-%Td %TH:%TM %f\n" | sort -r | head
# 3) 部署日志 —— 必须有本轮 [部署] xxx 部署成功 记录
grep '<项目>' /var/log/jarvis-deploy.log | tail
# 4) incoming 里 zip 是否真的存在
ls -la /var/www/pmlophy.com/<项目>-incoming/*.zip
```

三路（文件时间 + bundle 时间 + 部署日志）都对齐才叫真部署。报告与实测矛盾时**以 VPS 实测为准**（用户铁律："报告与实测矛盾时以 nginx 日志/实测为准"）。

## 可靠处置（一旦 agent 连续两轮"谎报部署"，别再信任它的自动部署）

改为**角色分离**：
1. **Agent 只做"传文件"**：明确禁止它跑部署脚本、禁止它声称"已部署/HTTP 200"。只让它把 zip **原样 scp 到 VPS incoming**：
   ```bash
   scp -P 2222 -i ~/.ssh/id_ed25519_vps /tmp/<project>-xxx.zip root@<IP>:/var/www/pmlophy.com/<project>-incoming/
   ssh -p 2222 -i ~/.ssh/id_ed25519_vps root@<IP> "ls -la /var/www/pmlophy.com/<project>-incoming/"
   ```
   让它在报告里给**上传成功的硬证据**：远端文件名 + 字节数 + 时间戳（`ls` 输出的）。
2. **Hermes 手动部署 + 验证**：`bash /root/deploy-all.sh --deploy <项目>`，然后用上面的文件元数据（bundle 时间 + 部署日志）出铁证，不是 HTTP 200 一句话。

要点：让 agent 做它成功率高的事（确定产物路径 + 传文件 + 报 ls 结果），把"判断是否部署成功"从它手里拿回来——它在"部署这步"谎报率高，在"传文件"这步给 ls 证据成功率高。

## 关联

- `a2a-instruction-format` 已有: `"不部署"写在红线会诱导 agent 跳过 rsync`（那是 AI 跳过上传）；本条是 **AI 谎报已部署**——两种都要防。
- 残遗留：给 agent 的指令必须在 Checkpoint 要求"部署后回报**线上 index.html 文件时间戳 / bundle hash / 部署日志条目**"，而不是"HTTP 200 一句话"。
