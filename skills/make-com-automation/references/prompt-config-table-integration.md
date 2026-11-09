# 提示词配置表接入与非技术用户交付参考

## 1. 已验证的场景链

### 场景 1：选题生成

```text
VPS 表单（可选 ref）
→ Webhook
→ HTTP：获取 tenant_access_token
→ HTTP：wiki get_node 获取 bitable obj_token
→ HTTP：读取 records（包含分页）
→ Iterator(items)
→ Filter：fields.场景 = 场景 1
→ JSON Create JSON：构建 DeepSeek model + messages 请求体
→ DeepSeek Make an API Call
→ Parse JSON（选题数组）
→ Create JSON（每条记录 fields）
→ HTTP 写入《每周选题库》
```

### 场景 2：脚本生成

```text
VPS 表单（type/topic/info/action）
→ Webhook
→ HTTP：获取 tenant_access_token
→ HTTP：wiki get_node 获取 bitable obj_token
→ HTTP：读取 records（包含分页）
→ Iterator(items)
→ Filter：fields.场景 = 场景 2
→ JSON Create JSON：构建 DeepSeek model + messages 请求体
→ DeepSeek Make an API Call
→ 原有 Create JSON（处理脚本长文本）
→ HTTP 写入《脚本库》
```

两条链都是串行 Bundle 流，不是并行模块链。修改配置表不会自动运行；真正触发是下一次 VPS 表单按钮 POST Webhook，Make 在该次运行重新读取配置表。

## 2. Wiki Bitable 读取顺序

针对 `my.feishu.cn/wiki/<wiki_token>`：

1. 获取 tenant token；
2. `GET /wiki/v2/spaces/get_node?token=<wiki_token>`；
3. 从 `data.node.obj_token` 取 Bitable app token，并确认 `obj_type=bitable`；
4. 用 obj token 读取 tables/fields/records；
5. records 有分页时，在 records HTTP 中开启分页；
6. Iterator 使用最终分页后的 `data.data.items[]`（以当前映射面板的真实结构为准）；
7. Filter 按 `fields.场景` 只保留目标场景。

不要直接把 wiki token 当 Bitable app token；不要把 `data.obj_token` 当成正确路径。读取/映射步骤要用之前验证过的同一工作流 App 身份，不要误用 Hermes 自身飞书 App。

## 3. Make 运行与验证

- 下游 HTTP/Iterator/DS 依赖上游输出时，单独 Run 可能出现空 token、空 obj_token 或空数组；优先从 Webhook 点完整 Run once。
- Iterator 正式模块路径：`Tools → Flow control → Iterator`；Array 选择 records 最终输出的 `items[]`。
- 过滤器：场景 1/2分别使用 `fields.场景 = 场景 1/场景 2`。
- 修改数据结构后，要重新在模块的 Data structure 下拉中选中正确结构，避免编辑了结构但模块仍引用旧定义。
- DeepSeek 的 Make an API Call 与普通 HTTP 配置不同。动态长提示词不要替换整个 DS Body，也不要把 HTTP 的 Data structure 选项套过来；用 JSON Create JSON 构建完整 `model + messages[]`，system.content 映射提示词，user.content 保留输入。
- 场景 1输出 15 个选题 JSON，需要 Parse JSON/后续逐条写入；场景 2输出一篇脚本，不需要 Parse JSON。

## 4. 非技术用户交付边界

用户手册只说明：

```text
飞书《提示词配置表》：修改生成规则
→ 保存云端
→ VPS 表单：填写本次业务输入并点击生成按钮
→ 自动化读取最新提示词并生成
→ 飞书《每周选题库》/《脚本库》查看结果
```

必须明确：保存提示词表不会自动触发；按钮才是触发器。场景 2的 `type/topic/info/action` 是当前固定输入契约；增加/删除字段需要通知维护者同步网页、Webhook、提示词映射和结果字段，这属于半自动方案。

