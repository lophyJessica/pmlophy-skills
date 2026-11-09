# forge-crm 试点记录（2026-08-08，MVP 跑通）

## 试点范围
- 项目: forge-crm（Mac 主开发库 /Users/liulongfei/个人文件/forge-crm/；VPS 镜像 /root/repos/forge-crm）
- 页面: 线索列表页（HashRouter `#/leads`，前端 front-prototype/src/pages/LeadsList.tsx）
- 技术栈: React + TS + Tailwind + Vite

## 关键路径
| 项 | 位置 |
|---|---|
| 执行侧 Skill | 项目根 `vitamin-prototype-annotation/`（git 跟踪；.cursor 被 gitignore 不能放） |
| 线索 PRD | `prd-docs/线索管理/`（主PRD/字段清单/Demo列表/详情/新增编辑/用例推演） |
| 标注目录 | `prd-docs/线索管理/annotations/`（annotation.config.json + pages/leads-list.md + coverage.md + screenshots/） |
| 编译产物 | `front-prototype/public/annotation-kit/annotation.bundle.json`（+ runtime.js/css） |
| 前端入口 | `front-prototype/index.html`（注入 runtime；LeadsList.tsx 加 3 个 data-anno 锚点） |

## 执行命令（Codex 指令里逐字给）
```bash
# 编译标注
python3 vitamin-prototype-annotation/scripts/compile_annotations.py prd-docs/线索管理/annotations/annotation.config.json --output front-prototype/public/annotation-kit/annotation.bundle.json --coverage prd-docs/线索管理/annotations/coverage.md
# build
cd front-prototype && npm run build
# 打包（解压即根！）
rm -f /Users/liulongfei/个人文件/forge-crm/forge-crm.zip
cd /Users/liulongfei/个人文件/forge-crm/front-prototype/dist && zip -rq ../../forge-crm.zip .
# 上传
rsync -avz -e "ssh -p 2222 -i ~/.ssh/id_ed25519_vps" "/Users/liulongfei/个人文件/forge-crm/forge-crm.zip" root@192.220.14.245:/var/www/pmlophy.com/forge-crm-incoming/
# 报告
curl -X POST "https://pmlophy.com/p/jarvis/file/upload" -H "X-Jarvis-User: ai-reports" -F "file=@报告.md"
# 部署（用户确认后）
bash /root/deploy-all.sh --deploy forge-crm
```

## 部署事故（zip 路径）
- Codex 首版打包带 `front-prototype/dist/` 前缀 → deploy-all.sh 解压后验证 404 → 自动回滚
- 手动修复: 解压 → `cp -r front-prototype/dist/* /var/www/pmlophy.com/project/forge-crm/` → 200
- 教训: 指令必须显式要求"zip 解压即根"

## 首版标注问题（验收发现 → 治根）
1. 页面路径写 `/leads`（技术路由）→ 应"线索管理/线索列表"（面包屑）
2. 状态/Tab 写英文枚举（PENDING_ASSIGN/ASSIGNED...）→ 应中文（待分配/我的线索/跟进中）
→ 补"Annotation Language Standard"到执行侧 Skill（英文）+ 检阅侧（中文），重跑

## Codex 主动发现的 5 个"原型 vs PRD 不一致"（标注的增值——标注过程=走查）
1. "我的线索"含 DRAFT，与 Demo 的 ASSIGNED+FOLLOWING 不一致
2. ABANDONED 后原负责人立即显示"撤销放弃"，与 7 天防撞墙保护冲突
3. 超时检查只覆盖 ASSIGNED 无跟进，未覆盖 FOLLOWING 48h 回收 + 10 分钟定时扫描
4. 未实现 Demo 的多值搜索/时间筛选/导出/列宽拖拽/固定列/批量分配
5. 放弃弹窗仅非空校验，未执行"原因≥15字"；放弃后是否清空归属人/分配时间待确认
→ 这些待用户拍板（原型对齐 PRD 或 PRD 对齐原型）

## git 状态
- main 分支开发（git 铁律），执行侧 Skill 补丁走 commit + push main → 用户 Mac pull
- 已提交: 1b54ab0（Skill 初始）+ 95594b0（补语言规范）
