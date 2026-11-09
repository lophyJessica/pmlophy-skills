# 项目交付规则（发 zip 包给用户）

> 2026-07-06 教训：连续 4 次发不完整项目包，漏 context/prd-docs/templates/DESIGN/CLAUDE/.cursor。

## 铁律

1. 整包不打散：`zip -r project.zip . -x "node_modules/*" "dist/*" ".git/*"`
2. 不手动挑文件：用全目录 `.` 打包，不做手动目录列表
3. 发前验证：`unzip -l` 确认关键目录全在
4. 不发 tar.gz：Mac 用户要 zip
5. 不发补丁包：一个项目一个包
6. 命名简洁：`项目名.zip`，不加后缀

## 检查清单

- context/ 目录有文件
- prd-docs/ 目录有文件
- templates/ 目录有文件
- CLAUDE.md 存在
- DESIGN.md 存在
- AGENTS.md 存在
- 提示词/ 目录有文件（如适用）

## 禁止

- 手动指定目录列表
- 分包发送
- 发前不验证
