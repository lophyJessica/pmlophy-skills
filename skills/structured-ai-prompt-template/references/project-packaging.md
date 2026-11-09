# 项目包分发铁律

> 2026-07-06 四次翻车后总结。用户极度反感不完整的项目包。

## 唯一正确做法

```bash
# 全目录打包，不手动挑文件
zip -rq project.zip . -x "node_modules/*" "dist/*" "__MACOSX/*" ".git/*" ".DS_Store"

# 发前逐项核实
unzip -l project.zip | grep -E "CLAUDE|DESIGN|AGENTS|context/|prd-docs/|templates/|prompt/|提示词/|.cursor"
```

## 铁律

1. **绝不手动挑文件** — 用 `zip -r .` 全目录，不用脑记
2. **绝不拆分包** — 代码+文档一个包（不是"先代码再补文档"）
3. **只用 .zip** — 不用 .tar.gz（Mac 体验差）
4. **发前用 `unzip -l` 逐项核实** — 确认 context/prd-docs/templates/prompt/CLAUDE.md/DESIGN.md/.cursor 全部在
5. **命名统一** — forge-erp.zip / forge-wms.zip，不加 complete/full/docs 等后缀

## 反面教材

- 第一次：只打了 `src/`，无文档
- 第二次：拆成代码包+文档补丁包两份
- 第三次：漏了 CLAUDE.md、.cursor 规则
- 第四次：WMS 漏了 DESIGN.md
- 每次：命名混乱（complete/full/docs/v2/v3/final）
