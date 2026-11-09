---
name: product-research-comparison
description: "Research and compare products (hardware, software, services) for purchase decisions — structured comparison tables, tiered recommendations, and price-aware decision frameworks."
version: 1.0.0
author: Agent
platforms: [macos, windows, linux]
metadata:
  tags: [shopping, comparison, research, hardware, software]
---

# Product Research & Comparison

## Trigger

User asks to research or compare products for a purchase decision — keyboards, mice, monitors, software tools, services, etc. The user wants actionable recommendations, not just information dumps.

## Workflow

### Step 1: Understand constraints
Before searching, clarify:
- **Budget** — hard ceiling? flexible range?
- **Platform/ecosystem** — Mac, Windows, Linux? Compatibility matters.
- **Priority** — what's the actual pain point? (e.g. "hand fatigue" → ergonomics, not just "best mouse")
- **Must-haves vs nice-to-haves**

### Step 1.5: For listings and stranger-to-stranger purchases, verify before investing
For second-hand marketplaces, rentals, sublets, and other listings where the seller's identity or rights matter, treat every self-description as an unverified claim. Do not move directly from chat to an in-person meeting or payment.

Use an evidence funnel:

1. Verify identity/role: owner, authorized sublessor, or intermediary;
2. Verify rights: ownership or written subletting authorization;
3. Verify the item/property type and material conditions;
4. Verify who will sign the contract and who receives payment;
5. Verify the complete cost: price, deposit, utilities, fees, and refund rules;
6. Request cross-checkable evidence (redacted contract/authorization, video, address/entrance/details);
7. Only then arrange an inspection;
8. Pay only after the on-site facts and written terms match.

If a key fact changes between the listing/chat and the meeting—for example, “direct from owner” becomes “sublet” or “套中套”—drop the listing. Do not argue, keep spending time, or let a promised pickup or a small courtesy gift lower the verification standard.

For this user, present the funnel and decision threshold directly. Do not inflate it into a long “steelman” debate; the useful output is the evidence checklist and the stop condition.

### Step 2: Research
- Try multiple sources: Reddit (community consensus), RTINGS (objective testing), official specs
- If web_search is unavailable, use curl to fetch API/search results
- **Fallback**: if sources block scraping, use knowledge but BE HONEST about what's from memory vs verified

### Step 3: Structure the output

Use this format (user responds well to it):

```markdown
## Category 1: [Product Type]

| Model | Price | Key Spec 1 | Key Spec 2 | Compatibility | Best For |
|-------|:-----:|------------|------------|---------------|----------|
| ...   | ...   | ...        | ...        | ...           | ...      |

## Category 2: [Product Type]
...

## 🏆 Recommended Combos

### Budget Tier (~¥XXX)
Product A + Product B
> Trade-offs

### Sweet Spot (~¥XXX)
Product C + Product D  
> Why this is the best value

### Premium / Special-Need (~¥XXX)
Product E + Product F
> When to choose this

## Quick Decision Matrix

| Your Situation | Buy This |
|---------------|----------|
| Scenario 1    | Combo X  |
| Scenario 2    | Combo Y  |
```

### Step 3.5: Separate official capability from channel availability
For AI products, models, providers, and newly announced features, distinguish these claims explicitly:

1. **Official capability** — what the first-party documentation says the base product/model supports.
2. **Exact model or feature identifier** — verify the precise slug/name; do not infer capability from a family name or marketing label.
3. **Access channel availability** — official API, aggregator, relay, subscription, IDE integration, and local wrapper may expose different models or formats.
4. **Current account/config availability** — the user's configured provider may not expose the newly announced variant yet.

Never conclude that an aggregator or subscription supports a feature merely because the upstream vendor does. Report it as "officially available upstream; channel support unverified" until tested or documented. For multimodal AI in particular, verify image input modality, request format, endpoint compatibility, and whether the exact model slug is exposed.

### Step 3.6: Research newly announced AI features with primary-source triangulation
Use this order:

1. First-party announcement/release notes;
2. First-party API/model documentation;
3. First-party pricing/limits documentation;
4. Independent reporting for security, implementation details, and caveats;
5. Community reports only as clearly labeled anecdotal evidence.

Record the release date and beta/experimental status. When sources conflict, prefer the exact first-party API documentation over search snippets or third-party summaries.

### Step 3.7: End with a user-specific implication
After the factual summary, map the finding to the user's current stack without changing configuration automatically. State:
- what is newly possible;
- what remains unverified;
- what would need a low-risk test;
- what should not be changed yet.

For provider/model changes, do not recommend switching, restarting, or editing configuration solely from a news result. Preserve the user's current working setup until the exact route is verified.



- **DON'T claim "free tier is enough" without checking the reset mechanism.** 免费额度分「每月重置」和「一次性总额度」两种，含义完全不同——断言某免费层"够用"前必须查官方定价页/FAQ 确认重置机制（2026-08-26 用户追问 Tavily"是每月都有会重置，还是总免费额度"——官方 FAQ 证实 `1000 API credits / month, reset on the first day of each month`；Brave 官方是 `$5 in free credits every month` = 1000 次/月，与 Tavily 相同）。**第三方对比表的免费量经常过期**（曾有文章写 Brave "2,000/mo free"，官方页面实为 1000/mo）——以官方页面为准，顺带给出超量后的成本曲线（如 Tavily PAYG $0.008/credit 无月费）。
- **DON'T guess current prices.** If the user corrects a price, update immediately and thank them. Market prices shift; what was ¥300 last month could be ¥500 now. Prefer the user's JD search over your memory.
- **DON'T annualize the trial cost.** 试错成本必须按**实际付款周期 + 退款政策**算，不能把季付/年付折算成月费来评估风险（2026-08-26 用户纠正：ZgoCloud $78/季 是整季一次性付 ≈¥560 且特价买断不可退款，我写成"¥187/月可试一个月"被纠正——风险敞口差 3 倍）。评估时问清三件事：①最小付款单位（月/季/年）②退款政策/窗口 ③是否特价买断（买断=全额风险）。对比表价格必须标注真实付款金额+计费周期，不写折算月价。反过来，**可月付可停 = 试错成本低一个量级**（如 GigsGigsCloud 6C6G $79/月能只付一个月试，比 ZgoCloud 赌整季强）——选型时主动把这个维度标出来。
- **DON'T recommend products that don't exist.** If the user mentions a model you don't recognize, search first. If nothing comes up, ask them to verify the name or share a link.
- **Reddit often blocks curl requests** — don't loop trying; fall back to other sources or your own knowledge with a transparency note.
- **RTINGS is JS-rendered** — curl won't get actual review content. Mention it as a reference for the user to check themselves.
- **Don't over-research.** The user wants a decision, not a PhD thesis. 3-5 options per category is enough. Stop when you have enough to make a confident recommendation.

## Reference Files

- `references/purchase-links-template.md` — template for tracking purchase links and final decisions
- `references/local-llm-hardware-selection.md` — 本地大模型选型速查（Qwen3 量化显存对应 / Apple Silicon 内存带宽档位 / Ollama 一键跑；用户考虑二手 M1 Ultra 时参考）
- `references/used-macbook-buying.md` — 二手 MacBook 选购完整指南（统一内存/带宽选型、M 系列档位、14vs16寸散热、9 项验机清单、无头骑士/美版/MagSafe 坑、购买决策框架——2026-08 用户实测沉淀）
- `references/cn2-gia-vps-selection.md` — CN2 GIA VPS 选型调研快照（2026-08 行情：搬瓦工 DC6/DMIT/HostDare/ZgoCloud 候选池、用户需求=6C6G/≤350元/IP80+/1G端口/放弃住宅IP、ZgoCloud 双赌待定、价格变动决策前重查）
