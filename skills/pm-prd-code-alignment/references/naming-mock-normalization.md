# 命名统一 / Mock 一致性 / SKU 重定基（大规模文档规范化）

场景：走查发现 PRD 文档层大面积不一致（字段命名、Mock 跨单据引用、SKU 商品集分裂），需全项目规范化。2026-07 forge-wms 实战验证。

## 关键洞察

1. **多数 PRD 字段在代码里没有对应（前端是子集 Demo）。** forge 实测：约 400 字段中仅 15% 与代码直接一致、16% 语义对应、**69% 代码查不到**。含义：命名统一不是"对齐代码"，而是**为全项目定一套命名规范**（落成 `context/12-字段命名规范.md` 这类宪法文档），PRD 作为权威、代码后续（二期）补齐。**绝不把 PRD 反向阉割成 Demo 的简化字段。**

2. **字段编码 camelCase，枚举值 UPPER_SNAKE，两者严格分开。** Codex/反重力 常把枚举值也 camelCase（错，如 `pendingReceive`）。规范里必须显式写死这条通则——只举一个 `ENABLED` 例子不够，agent 会把状态值也 camel 掉。校验时专门 grep 枚举值大小写。事实源：代码里 BaseDataStatus(ENABLED/DISABLED)、TransferStatus(DRAFT/COMPLETED/VOIDED) 都是 UPPER。

3. **命名对齐方向 vs 业务逻辑对齐方向相反。** 业务逻辑遵循本 skill 原则3（改代码不改 PRD）；但**命名规范**是文档滞后于代码约定 → 改文档去对齐代码/已定样板（如 `area_code→zoneCode`，货位文档追齐库区/商品档案样板）。

## 三类命名字段定稿口径（forge 实战）

- **单号**：语义前缀 + `No`（rcvNo/putNo/waveNo/pickNo/checkNo/pkgNo/dshNo/ckNo/transferNo/blNo/flNo）；跨单引用上游 = `source+语义+No`（sourceOrderNo）；禁用泛化 `id`。
- **商品**：product 系（productCode/productName/productBarcode/productSpec/unit）；弃 sku_code 系。行快照里 `spec`/`unit` 可保持裸写（与商品档案主数据一致）。
- **数量**：保留业务粒度只转 camelCase（actualReceiveQty/lineTransferOutQty/qtyOnHandAfter），不塌成 Demo 简化字段。

## Mock 跨单据引用链一致性

走查高发 bug——下游 mock 引用了对不上的上游。三类：
- 退回/不通过的单据不该有下游产物（退回的 CHECK 不该有已包装 PKG/FL）。
- 用例引用了基础数据里未定义的单号（DSH-0002 无源）。
- 跨模块单号错配（库存查询场景引 TR-0001 却写成别的 SKU/数量）。

不变量：任一 mock 引用另一单据号(TR/FL/PKG/CHECK/DSH/WAVE/BL)，被引单据必须在其源头文档真实存在，且 SKU/数量/仓库/状态/时点一致；全局唯一号(FL)不得重复。

## SKU / 商品主数据重定基

多模块 mock 各写各的商品集 → 收敛到商品档案 SSOT（如 SKU001~007 + 前端 seed）。1:1 双射映射，**编码+名称+单位一起换，数值与场景逻辑原样保留**。语义弱匹配可接受（跨域商品本无完美对应）。换后须核：batchManaged 场景、错扫场景"错品≠主商品"等约束。

## 大规模执行策略（防翻车）——核心

- **打样先行**：先拿一个代表性模块（如入库）跑，按五维验证规范落地正确（字段camelCase / 枚举UPPER_SNAKE / 单号No / 商品product / 数量保留粒度），锁定标准后再推广其余模块。**打样往往抓出通则漏洞（如枚举大小写），避免污染全部模块。**
- **报告先行**：侵入性/系统性改动（命名 400 处、SKU 210 处）先只出"影响面报告"（文件+行+现值+建议映射，**零改动**），人工审批映射后再执行。零改动报告指令再大也安全。
- **分模块分批**：每批一个模块，跑→push→pull 复验→下一批；封顶 2-3 并行；碰同一批文件的指令绝不同时跑。

> A2A 执行/git 同步验证的操作细节见 `structured-ai-prompt-template/references/a2a-git-verify-loop.md`。
