# 飞书多维表格 API 手搓（2026-08-16 实测验证通过）

在 VPS/终端用 curl 直接调飞书 API（对应 make 的 HTTP 模块两步：拿 token → 调 bitable API）。
全程实测：读（tables 列表）code:0 成功；写（records）首次 91403 Forbidden（见坑）。

## 前置（一次性）
- 飞书开放平台 open.feishu.cn 创建企业自建应用 → App ID + App Secret
- 权限管理开通：`bitable:app`（读写——写场景必须）+ `bitable:app:readonly`（只读）
- wiki 链接转 base 还需：`wiki:node:read`（否则 get_node 报 99991672）
- 发布版本（2026-08-16 实测：权限变更后无需重新发布，即时生效）

## 1. 拿 tenant_access_token（2 小时有效——每次调用前重新取）
```bash
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['tenant_access_token'])")
# 成功返回: {"code":0,"expire":7200,"msg":"ok","tenant_access_token":"t-..."}
```

## 2. wiki 链接 → base token（用户给的是 wiki/ 开头的链接时）
飞书知识库（wiki）里的表格，链接格式 `https://xxx.feishu.cn/wiki/<wiki_token>`。
API 操作 bitable 需要 base 的 app_token——先转换：
```bash
curl -s -X GET "https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token=<WIKI_TOKEN>" \
  -H "Authorization: Bearer $TOKEN"
# 成功: {"code":0,"data":{"node":{"obj_token":"V0GT...","obj_type":"bitable",...}}}
# obj_token = base 的 app_token（API 用这个）；obj_type=bitable 确认是多维表格
# 失败: code 99991672 = 缺 wiki:node:read 权限 → 补开
```
⚠️ 若用户直接给 `base/<app_token>?table=<table_id>` 格式链接——跳过此步直接用。

## 3. 读表格列表（拿 table_id）
```bash
curl -s -X GET "https://open.feishu.cn/open-apis/bitable/v1/apps/<APP_TOKEN>/tables" \
  -H "Authorization: Bearer $TOKEN"
# 成功: {"code":0,"data":{"items":[{"name":"每周选题库","table_id":"tblXxxx"}]}}
```

## 4. 写记录（往表格插一行）
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/<APP_TOKEN>/tables/<TABLE_ID>/records" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"选题类型":"成本计算类","视频标题":"企业培训获客成本怎么算？","核心角度":"算清账才不白投","流量潜力":"高"}}'
# 成功: code 0 + record 对象
# 失败: {"code":91403,"msg":"Forbidden"} —— 见坑
```

## ⚠️ 91403 Forbidden（读通写不通）排查
- **表格分享权限**：API 写需要表格对应用"可编辑"——表格右上角 分享 → 权限改为"组织内可编辑"（只"可阅读"写不进）
- **权限缓存延迟**：bitable:app 刚开通可能未生效——等几分钟或重新发布再试
- 读（tables）和写（records）分开验证——读通不代表写通

## make 集成（把上面两步变成 HTTP 模块）
- HTTP 模块 1: POST tenant_access_token（拿 token）
- HTTP 模块 2: POST records（带 token——引用模块 1 输出的 tenant_access_token）
- token 每 2 小时过期——长场景/定时场景每次跑都先取 token（两步串联即可）

## ⚠️ make 侧两个坑（2026-08-16 实踩）
- **Authorization 头必须带 "Bearer " 前缀**：HTTP 模块 2 的 Headers 加 `Authorization`，Value = `Bearer `（含空格）+ 点选模块 1 的 `data.tenant_access_token`——只填 token 不加 Bearer 前缀 → 飞书报 99991661 "Missing access token for authorization"
- **单测下游模块 = 上游引用全空**：单独 "Run this module" 跑 HTTP 模块 2 时，模块 1 的 token 不在本次运行里（报缺 token ≠ 配置错）——先 Run 模块 1 再 Run 模块 2，或直接 Run once 从 Webhook 完整链路跑
