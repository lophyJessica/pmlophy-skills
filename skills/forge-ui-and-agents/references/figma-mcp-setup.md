# Figma MCP 接入指南

## 背景

反重力/Gemini 视觉审美差——裸写 UI 不专业。Figma MCP 让 AI 直接从设计稿读取颜色/间距/字号/组件层级,不再猜。

## 接入步骤

### 1. Figma 注册 + Token

- 注册: https://www.figma.com/
- 头像 → Settings → Personal access tokens → Generate new token
- 免费账号可用,但有限制(只读团队文件和社区文件)

### 2. 反重力 MCP 配置

```json
{
  "mcpServers": {
    "figma-custom": {
      "command": "npx",
      "args": [
        "-y",
        "figma-developer-mcp",
        "--figma-api-key=你的Figma Token",
        "--stdio"
      ]
    }
  }
}
```

### 3. 可用工具

| 工具 | 说明 |
|------|------|
| `get_figma_data` | 读取 Figma 设计稿的节点结构/颜色/间距/文本 |
| `download_figma_images` | 导出 Figma 图层为图片 |

### 4. 工作流

1. Figma 画一个页面(仪表盘/列表/表单)
2. 复制 Figma 文件链接
3. 给反重力指令: "用 get_figma_data 读取这个设计稿,生成 React + Ant Design Pro 代码"

### 5. 与现有方案的互补

| 方案 | 适用 | 工具 |
|------|------|------|
| Figma MCP | 有设计稿的新页面 | 反重力 + Figma |
| ProLayout 骨架 | 无设计稿,B端标准页面 | 反重力 + Ant Design Pro |
| @chrome 复刻 | 有竞品参考 | Codex @chrome |
| 截屏微调 | 小范围样式调整 | Gemini |
