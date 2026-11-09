# CC Switch + Kscope 中转站模型发现与定价

## 模型发现
CC Switch 通过调用 OpenAI 兼容的 `/v1/models` 端点获取模型列表。

**Base URL 必须带 `/v1` 后缀：**
```
https://api.kscopeai.com/v1
```
填 `https://api.kscopeai.com`（不带 `/v1`）会导致模型列表为空。

## Kscope 定价
用户套餐：39 元人民币 / 月，获得标称 $500 美元额度，月底清零。
另有 $200 Codex 独立额度。

实际成本：每 $1 标称额度 ≈ ¥0.078，性价比极高。
不建议过度节省额度，应优先保障任务质量。

## GPT-5.6 三个档位
| 档位 | 输入/M | 输出/M | 场景 |
|------|--------|--------|------|
| Sol | $5.00 | $30.00 | 长目标复杂任务、全局审计、梭哈迁移 |
| Terra | $2.50 | $15.00 | 日常开发、中等复杂度 |
| Luna | $1.00 | $6.00 | 简单修改、高频低成本调用 |

注：以上为 OpenAI 官方标价，Kscope 实际扣费倍率可能不同，最终以 Kscope 后台显示为准。

## Sol 最佳用法
Sol 适合**长目标模式**：一次提供完整 Context + Request + 红线 + Checkpoint，让模型持续执行并自测。
多次碎片化请求比一次长执行更烧额度（每次请求有固定消耗或重复上下文输入）。

## Codex 桌面端配置
- 在 CC Switch 中添加 Kscope 供应商
- Base URL: `https://api.kscopeai.com/v1`
- API Key: 从 Kscope 后台获取
- 模型选择：`5.6 Sol`，推理档位 `高`
