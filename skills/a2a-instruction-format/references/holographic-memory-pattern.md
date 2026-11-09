# Holographic Memory Provider — Usage Pattern

> 2026-07-25 实战总结

## 激活

```bash
hermes memory status                           # 查看状态
hermes config set memory.provider holographic  # 激活
hermes memory status                           # 验证
```

DB: `~/.hermes/memory_store.db` (SQLite)

## 操作

| 操作 | 用途 |
|------|------|
| `fact_store(action='add', content='...', category='project', tags='...')` | 存知识 |
| `fact_store(action='search', query='SPD')` | 关键词搜索 |
| `fact_store(action='probe', entity='SPD')` | 查某实体所有事实 |
| `fact_store(action='related', fact_id=5)` | 查关联 |
| `fact_store(action='reason', entities=['A','B'])` | 多实体推理 |
| `fact_store(action='list')` | 列出全部 |
| `fact_store(action='contradict')` | 矛盾检测 |
| `fact_store(action='update', fact_id=5, content='...')` | 更新 |
| `fact_store(action='remove', fact_id=5)` | 删除 |
| `fact_feedback(fact_id=5, helpful=true)` | 点赞/踩(影响信任评分) |

信任评分: 起始 0.5, 点赞升高, 被踩→自动遗忘

## 两通道分工 (关键)

| | memory (内置) | fact_store (Holographic) |
|------|------|------|
| 存储 | MEMORY.md 文本 | SQLite |
| 容量 | 10000 chars | 不限 |
| 用途 | 快捷上下文,每 session 注入提示词 | 深层知识,语义搜索 |
| 何时用 | 铁律/偏好/环境/当前状态 | 项目知识/SPD结论/技术方案 |
| 新 session | 自动加载 | 需主动 probe/search |

## 切 Holographic 后必须改习惯

之前 91 条全存进 `memory`(内置), Holographic 空=浪费。
切后必须: 重要知识→`fact_store`,快捷上下文→`memory`。

**2026-07-25 踩坑:** 新 session 连接后,agent 继续用旧习惯 `memory` 工具,没用 `fact_store`。结果 Holographic 0 条事实。用户追问"不是给你加了新的存储记忆方式了吗?"才发现没在用。切完后**必须立即用 `fact_store` 存第一条事实**验证可用。

## 新 session 第一个动作

```python
# 不要直接聊天,先检查 Holographic
fact_store(action='search', query='spd 补货')
# 如果有结果 → Holographic 在正常工作
# 如果 0 条 → 内置 memory 加载了,但 Holographic 需要手动 probe
```

## 新 session 恢复流程

```python
# 1. 搜索关键实体
fact_store(action='probe', entity='SPD')
fact_store(action='probe', entity='forge-crm')

# 2. 列出近期事实
fact_store(action='list')

# 3. 必要时用 session_search 查老会话
```

结论: 不需要撑长 session。`/new` = 内置记忆自动加载 + 搜索 Holographic 即时恢复。

## 官方源码实证（2026-08-09 读 /usr/local/lib/hermes-agent/plugins/memory/holographic/ 后定稿）

Holographic = Hermes 内置插件：HRR 相位向量（1024维）+ FTS5 全文 + Jaccard 重排 + 信任权重 四层混合检索（`retrieval.py` 的 FactRetriever）。这是**官方设计**的"存储+快速检索"能力，不是只能当数据库。

### 必须用官方 fact_store，禁止 SQL 直插
- **直接 `sqlite3` INSERT 到 facts 表 = 僵尸记忆**：绕过触发器 → `facts_fts` 没索引 + `hrr_vector` 为 NULL → search/probe 永远搜不到（占空间但调不出来）。已实测：SQL 写入 3 条后 `search` 返回 0。
- 正确写入：`fact_store(action='add', content=..., tags='关键词,逗号分隔')` —— 官方自动建 FTS 索引 + 生成向量。
- **tags 是中文检索的关键**：FTS5 默认 unicode61 分词器不切中文词，content 整句当一个 token；tags 短词反而能精确命中。存中文知识必带 tags。

### search 与 probe 的分工（实测）
- `search(query)` = FTS5 混合检索，中文推荐（tags 命中 fts_rank=1.0 精准）。**中文检索用 search 不要用 probe**。
- `probe(entity)` = 实体向量检索，只在 add 时传了 entities 参数才准；不带 entities 的 fact 排位靠后（实测 score 0.24 低分）。
- 检索分数低（0.2x）是"无实体/短句"的正常现象，不代表记忆丢了——用对工具（search+tags）后 fts_rank 可达 1.0。

### 记忆分流策略（方案 B，用户 2026-08-09 定稿）
MEMORY.md 满（20000 上限）时：低频/细节条目迁 fact_store（官方 add 带 tags），MEMORY 留摘要（"细节在 fact_store xxx"）。迁移必须官方 add（非 SQL 直插），迁后 search 验证能查到。可用 `hermes config set memory.memory_char_limit 20000` 调上限。
