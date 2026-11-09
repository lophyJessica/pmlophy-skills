# Skill 库设置与发布（~/.agents/skills 真源 → 各 agent 镜像；pmlophy-skills 归档）

## 单一真源模型
- 真源 `~/.agents/skills/`：每个 skill 是一个软链，指向 skill 真正所在处（项目仓库 `skills/<skill>` 或聚合库）。
- 各 agent 的 skills 目录各做一个软链 → `~/.agents/skills/<skill>`：Cursor `~/.cursor/skills`、Codex `~/.codex/skills`、Claude Code `~/.claude/skills`、Antigravity `~/.gemini/config/skills`、WorkBuddy `~/.workbuddy/skills`、TRAE `~/.trae-cn/skills`、ZCode `~/.zcode/skills`。
- 软链=改源一处全部同步。Mac 用户级 skill 目录是隐藏文件夹（Finder `⌘+Shift+G` 输路径看）。

## 挂载（每行独立、禁 `#`、幂等）
```bash
mkdir -p ~/.agents/skills
ln -sfn <源路径>/<skill> ~/.agents/skills/<skill>
# 各 agent 同理，target 换对应目录；重复跑不报错（ln -sfn 覆盖）
```

## 移除某 skill
`rm -f ~/.agents/skills/<skill>`（及各 agent 镜像）——只删软链本身，不删源文件。

## 发布到 GitHub（pmlophy-skills 聚合库）的边界
- 只发**用户方法论 / agent 可复用 skill**：prd-backfill、prd-requirement-review、prototype-annotation(+review)、de-ai-tone、a2a-instruction-format、structured-ai-prompt-template、ai-coding/*、pm-*、old-system-ui-clone 系。
- **不发 Hermes 内部运维 skill**（vps-administration、feishu-push-integration、forge-deployment、hermes-* 等）——含内部部署/IP/端口/凭据细节，上公开仓库=泄露内部环境。深度 references 案例同理留 Hermes 内部。
- 一个 skill 按场景分版（如老系统复刻：原版 CDP/Playwright vs 办公适配版=Cursor 内置浏览器），两版都进聚合库，README 标注各自用途与适用机器。

## 收编散装 skill（把分散在各 agent 的真实目录收进单一真源）

散装 = 某 agent 的 skills 目录里是**真实文件夹**（非软链，早期直接装/Git clone 进去，没进真源）。目标：真目录只留一处，各 agent 全指向软链。

**方法论 4 步**：
1. 盘点：扫所有 agent 的 skills 目录，`ls -la` 区分 软链（`->`）vs 真实目录（散装，才是要收编的）。实际常只有少数 agent 有散装，其余已是纯软链。
2. 判归属：每个散装真目录——pmlophy-skills 已有同名？→ 直接换软链用源版本（如旧副本 prototype-annotation 换软链后自动用源 v2.1）；是"孤儿"（任何源都没有）？→ 下一问；含敏感/内部信息？→ 留 agent 本地，不进公开仓库。
3. 判孤儿要不要收编：通用方法论 → 收进 pmlophy-skills（版本化+单源）+换软链；**内容不明先读它的 SKILL.md 鉴定再决定删不删**（用户铁律"不知道对应什么先不删"——别冒险）。
4. 换软链：真目录搬进源 → 注册 `~/.agents/skills` 索引 → 删 agent 里真目录 → `ln` 软链。

**换软链命令模式**（每行独立、禁 `#`）：
```bash
cp -r <agent>/skills/<name> <聚合库>/skills/<name>
ln -sfn <聚合库>/skills/<name> ~/.agents/skills/<name>
rm -rf <agent>/skills/<name>
ln -sfn ~/.agents/skills/<name> <agent>/skills/<name>
```

**红线条**：的 `rm -rf` 删的只是 agent 里的**重复副本**——确认真源在聚合库/GitHub 完好才删；**agent 内部文件别碰**（Codex `.system`、`.DS_Store`、各 agent 的 `.json` 迁移标记）；内容不明的孤儿先看完再决定，别删。收编后提交推送聚合库 + 补 README 条目。

## 第三方 skill 采纳（如维他命 agent-skills）
- 进聚合库前先判适用：方法/门禁/模板可整体采纳，脚本/自动化层看用户环境能否驱动（办公机锁网/Google 不可用时，CDP 自动化脚本可能跑不动，采集改走 Cursor 内置浏览器人工截图+结构存 md）。
- **保留一份上游忠实版供与上游 diff** + 另做一份用户适配版（改采集车头/场景到用户环境），不要只改在原版上（否则下次 diff 上游更新会混）。
- 适配点写在 SKILL.md 顶部（如"采集车头：Cursor 内置浏览器"），方法层不动。
