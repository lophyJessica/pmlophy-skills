# Make 场景一/二提示词配置表改造：实战参考

## 用户视角的最终职责分工

```text
飞书《提示词配置表》：维护场景 1/2 的 System Prompt
VPS 表单页：提交本次业务输入并触发 Webhook
Make：读取最新提示词、调用 DeepSeek、写回飞书结果表
飞书结果表：《每周选题库》《脚本库》
```

保存提示词表本身不会触发生成。真正触发点是下一次点击 VPS 表单页的生成按钮；Make 在这次新运行中重新读取提示词。

## 场景 1 已验证链路

```text
Webhook
→ HTTP：tenant_access_token
→ HTTP：wiki get_node，取得 bitable obj_token
→ HTTP：records + 分页
→ Iterator（Tools → Flow control → Iterator）拆 items[]
→ Filter：fields.场景 = 场景 1
→ Create JSON：构造 DeepSeek chat request body
→ DeepSeek Make an API Call
→ Parse JSON
→ Create JSON
→ HTTP 写《每周选题库》
```

## 场景 2 已验证链路

```text
Webhook（type/topic/info/action）
→ HTTP：tenant_access_token
→ HTTP：wiki get_node
→ HTTP：records + 分页
→ Iterator 拆 items[]
→ Filter：fields.场景 = 场景 2
→ Create JSON：构造 DeepSeek chat request body
→ DeepSeek Make an API Call
→ 原有 Create JSON（处理多行脚本）
→ HTTP 写《脚本库》
```

场景 1/2 的 records 读取都保留分页；表格当前只有少量记录不代表可以省略分页。

## 关键配置事实

- Wiki 表格必须先 `wiki/v2/spaces/get_node`，从 `data.node.obj_token` 得到 bitable app token。
- records 数组路径以实际输出为准，实测为 `HTTP → Data → data → items[]`；Iterator 的 Array 必须选最深层 `items[]`。
- Iterator 的正式名称是 `Tools → Flow control → Iterator`，不是 Array aggregator。
- Filter 取 Iterator 输出中的 `fields → 场景`，值严格是 `场景 1` 或 `场景 2`。
- 下游模块依赖上游 token/obj_token/records 时，不能单独 Run this module 判断链路；必须底部 `Run once` 从 Webhook 跑完整串行流程。单独运行下游会导致上游映射为空。
- Make 是串行 Bundle 流：上游数组经 Iterator 拆成多个 Bundle，后续模块按 Bundle 逐个处理；不要描述成并行模块链。

## DeepSeek 模块与 HTTP 模块的边界

DeepSeek `Make an API Call` 的 Body 配置界面不同于 HTTP 模块，不能把 HTTP 的 `Body input method: Data structure` 经验直接套到 DeepSeek。

当动态长提示词直接塞进 DeepSeek Raw Body 导致 `invalid type: string` 或 JSON 反序列化失败时，稳妥模式是：

```text
Iterator/Filter
→ JSON → Create JSON（先构造完整 {model,messages} 请求体）
→ DeepSeek Make an API Call（Body 引用 Create JSON 完整输出）
```

Create JSON 示例结构：

```json
{
  "model": "deepseek-v4-flash",
  "messages": [
    {"role": "system", "content": "映射 Iterator.fields.提示词"},
    {"role": "user", "content": "原有 Webhook 输入"}
  ]
}
```

不要把提示词单独替换成 DeepSeek Body，也不要把 `escapeJSON()` 当作完整请求体。场景 2 的四个 Webhook 核心字段仍是固定契约：`type/topic/info/action`；新增或删除字段必须同步 VPS 表单、Webhook 数据结构和 Make User Prompt，属于半自动方案。

## 步骤纪律

每次只推进一个场景的一步。操作前先说清当前场景、目标模块、这一步和完成标准；不凭记忆断言模块编号、通道或 URL，先看用户截图/当前笔记/官方文档。完成一个场景后再开始另一个。
