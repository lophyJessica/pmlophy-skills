# 多 Agent 用户级 Skill 目录对照 + 软链接共享方案（2026-09-07 整理）

一份维护、多 agent 共用——避免每个 agent 各存一份 skill（改一处要同步多处的维护灾难）。

## 各 Agent 用户级 Skill 目录

| Agent | 用户级 Skill 目录 | 共享方式/依据 |
|---|---|---|
| Cursor | `~/.cursor/skills/`、`~/.agents/skills/` | 官方还会兼容读 `~/.claude/skills/` 和 `~/.codex/skills/`；路径兼容 ≠ 官方承诺通用软链接 |
| Claude Code | `~/.claude/skills/` | 官方文档明确：个人 Skill 可用软链接（插件 Skill 另有位置） |
| Codex | `~/.agents/skills/`（官方入口）；当前版本默认仍认 `~/.codex/skills/` | 两路径都支持、官方支持扫描软链接；**别两处各装一份**，选一个当入口 |
| Antigravity | `~/.gemini/config/skills/`（CLI：`~/.gemini/antigravity-cli/skills/`） | 官方说明目录位置，**未明确通用软链接** |
| ZCode | `~/.zcode/skills/` | 官方提供外部 Agent 导入，可选「软链」或「复制」，优先用内置导入 |
| WorkBuddy | `~/.workbuddy/skills/` | 本机安装包模板用此路径，无公开说明，版本需确认 |
| TRAE 国内版 | `~/.trae-cn/skills/`（CLI：`~/.traecli/skills/`） | 官方说明目录/格式，**未明确通用软链接** |

## 共享方案（唯一源 + 软链/复制）

1. **唯一源选 `~/.agents/skills/`**——它是 Codex 官方入口 + Cursor 也读，**共享度最高**。
2. **支持软链的 → 软链指向 `~/.agents/skills/`**：Claude Code（官方明确）、Codex、ZCode、Cursor。
3. **官方未明确支持软链的 → 用复制兜底**：Antigravity、WorkBuddy、TRAE（先试软链，不认再复制）。

一句话：**`~/.agents/skills/` 当真源，能软链的软链、不支持的复制——一份维护，全员一致。**

## 反向统一（用户 0907 洞察）

**"分发"和"统一"是同一件事的两面**，都是操作文件系统。ego lite 既然能精准把 skill 写进每个 agent 的目录（见本文档所在 skill 的"安装与兼容"），**反过来把各 agent 的 skill 统一到一处、再分发回去，同样可行**——不必手动一个个软链，让 ego（或一个脚本）自动把真源 skill 目录软链/分发到各 agent 目录，加/改一个 skill 分发一次即全员更新。

## 实操提醒

- 软链接前先确认各 agent 认的 **skill 格式一致**（都认 `SKILL.md` + 目录结构）；格式/目录名有差异时需做"同源 + 各 agent 兼容层"。
- 目录都是**隐藏文件夹**（`.`开头）——访达里用 `⌘+Shift+G` 输路径前往，或 `⌘+Shift+.` 切换显示隐藏文件。
- 验证某 agent 装了哪些 skill：`ls ~/.agents/skills/`（每 skill 一个目录，内含 `SKILL.md`）。
