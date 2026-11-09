# 飞书开放平台推送对接（forge-scrm 数据报告，0828 全链路实测 code=0）

> 场景：给企业外人员（个人飞书账号）推送系统消息（interactive 卡片）。记录从建应用到发卡片成功的完整路径、每个坑及绕法。

## 最终方案（定稿）

企业自建应用 + `im/v1/messages`，`receive_id_type=open_id`。

## 关键决策记录

1. **webhook 群机器人 vs 企业自建应用**：webhook 要求接收人先进群；企业应用可私聊直发、加接收人只需换 ID。选企业应用。
2. **user_id vs open_id（本次最大坑）**：接收人是**个人飞书账号**（未加入任何企业组织）→ **没有 user_id**（那是企业租户内成员标识）。发消息报 99992360 "not a valid user_id" 即此因。解法：open_id（ou_ 开头）。
3. **个人账号搜不到自建应用/无法私聊应用**：自建应用只对本组织成员可见，个人账号不在组织内 → "让用户给应用发消息取 ID" 此路不通。唯一通路 = 手机号换 open_id。

## 换取 open_id 的实操路径（已验证）

1. 开发者后台 → 权限管理开通：
   - `im:message`（发消息）——实测加了不用发版即生效（部分权限需发版，以界面提示为准）
   - `contact:user.id:readonly`（手机号/邮箱换用户 ID）
   - ⚠️ 字段级权限（如 `contact:user.base:readonly`）≠ 接口级权限，开错照样 99991672
2. 开发者后台 → **API 调试台** → 搜 `batch_get_id` →「通过手机号或邮箱获取用户 ID」
3. 填参：Authorization 点「获取 Token」自动填；`user_id_type=open_id`；请求体只留 `{"mobiles": ["11位裸号"]}`（不加 +86；emails/include_resigned 删掉）
4. 返回 `data.user_list[0].user_id` = ou_ 开头 open_id

## 发送链路（VPS Python 实测 code=0）

```python
# 1. token：POST /open-apis/auth/v3/tenant_access_token/internal {app_id, app_secret}
#    返回 tenant_access_token + expire(7200s)，缓存至过期前 5 分钟
# 2. 发卡片：POST /open-apis/im/v1/messages?receive_id_type=open_id
#    body = {"receive_id": open_id, "msg_type": "interactive",
#            "content": json.dumps(card, ensure_ascii=False)}   ← content 是字符串化 JSON
#    code 99991663/99991661 = token 失效 → 刷新重试一次
```

安全：凭据走环境变量 FEISHU_APP_ID / FEISHU_APP_SECRET / FEISHU_PUSH_OPEN_IDS（逗号分隔多人）；token/secret 不落日志不落数据库。

## 排障速查（本次全踩过）

| 报错 | 根因 | 解法 |
|---|---|---|
| 99991672 缺 scope | 接口级权限没开 / 开成了字段级权限 | 按报错列出的 scope 名开通 |
| 99992360 invalid user_id | 接收人是个人账号无 user_id，或 ID 抄错 | 换 open_id |
| 99992351 invalid open_id | 拿 user_id 的值传 open_id 参数 | 用 batch_get_id 换正确的 ou_ ID |
| token OK 但发消息 400 | 看 code 对照本表 | — |

## 卡片内容设计（0828 用户验收反馈沉淀）

- **卡片必须含报告全文**（概览+折叠全文，28KB 字节级截断+灰字提示兜底）——用户拍板"飞书的就在飞书闭环"，不做跳转系统链接/免登录分享 token
- **推送任务生命周期**：状态机含终态保护——已推送=凭证**不可删除**（用户验收明确：删了就查无对账，防脏数据）；已取消=终态不可再发（后端要防绕过前端重发）；推送中=禁止取消/删除（防并发脏状态）；待推送/失败=可取消可删
- 删除必须 Modal.confirm 二次确认，文案注明"已推送的飞书消息不会撤回"

## 调试台小白操作（用户非工程师，逐步指导）

左侧搜索框输接口名 → 点进接口 → Authorization 点「获取 Token」自动填 → 填 query/body → 「开始调试」→ 右侧「调试结果」。给用户可直接粘贴的 JSON 请求体，别让他手拼。

## 凭据记录（0828 定稿）

- 应用：新媒体运营自动化 `cli_aa1b8f3794b91cc6`（Secret 用户部署时自行配置，不在文档存）
- 首个接收人 open_id：`ou_234ed4a687adfc3fe5c1ba283ba39d44`（姐夫，个人账号）
- 废弃：cli_aa1b953dd1f8dd1c、cli_aa0b2b6235b89d11（测试用，其 Secret 曾在聊天出现，应重置）
