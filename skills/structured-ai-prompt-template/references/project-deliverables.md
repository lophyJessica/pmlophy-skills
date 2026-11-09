# 项目文件打包规范

## 铁律

给用户发项目文件时：

1. **整包不打散** — `zip -r` 整个项目根目录，不手动挑选文件
2. **排除** — `node_modules`、`dist`、`.git`、`__MACOSX`、`.DS_Store`
3. **格式** — `.zip`（不是 `.tar.gz`，Mac 原生支持更好）
4. **名称** — 项目名直接命名（`forge-erp.zip`），不加多余后缀
5. **验证** — 发前 `unzip -l` 检查所有关键文件齐全
   - context/ 全部
   - prd-docs/ 全部
   - templates/、prompt/、提示词/
   - AGENTS.md、CLAUDE.md、DESIGN.md
   - .cursor/rules/、.agents/rules/
   - front-prototype/src/ 全部
   - front-prototype/public/（含 docs/）
6. **绝不** — 拆成代码包+文档补丁包，一个项目一个完整包

## 正确命令

```bash
cd /path/to/project
zip -rq /tmp/project-name.zip . \
  -x "front-prototype/node_modules/*" \
  -x "front-prototype/dist/*" \
  -x "__MACOSX/*" \
  -x ".git/*" \
  -x ".DS_Store"

# 验证
unzip -l /tmp/project-name.zip | grep -E "AGENTS|CLAUDE|DESIGN|context|prd-docs|templates|提示词" | head -20
```

## 历史教训

- 2026-07-06：手动挑文件打包，四次上传全部漏文件（context、prd-docs、templates、CLAUDE.md、DESIGN.md、.cursor/rules），用户多次纠正后才补全。此后只用全目录打包。
