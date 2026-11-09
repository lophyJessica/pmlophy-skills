# A2A：VPS Hermes → Mac Hermes → Antigravity

## 架构

```
VPS 杰西卡（我）         Mac Hermes（工具版）       Antigravity
    │                        │                        │
    ├─ 出五段曲指令 ──→ 飞书 ──→ 用户复制 ──→ 粘贴执行 ──→ 跑代码
    │                        │                        │
    ←────────── 飞书 ←── 用户贴结果 ←─── 复制结果 ←────┘
```

用户只做一次复制粘贴（指令→Mac, 结果→飞书），思考全在 VPS 完成。

## Mac 端安装

```bash
# 安装 CLI（不是 brew install hermes——官网最新方式）
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Mac Hermes 启动
~/.hermes/hermes-agent/venv/bin/hermes chat

# 给 Mac 端加 computer-use 权限
~/.hermes/hermes-agent/venv/bin/hermes computer-use doctor
```

## Mac Hermes 身份

- 不传 persona（SOUL.md）——保持裸机 Hermes，不克隆杰西卡
- 不连飞书网关——VPS 已管理
- 工具保持默认——Computer Use 是关键

## Computer Use 所需权限

- 系统设置 > 隐私与安全性 > 辅助功能
- 系统设置 > 隐私与安全性 > 屏幕录制

## 验证

在 Mac Hermes 中输入：

> 打开访达，看看桌面有什么文件

确认它能截屏、识别、操控。
