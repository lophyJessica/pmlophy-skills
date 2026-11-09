# 全新 VPS 开通 + forge-scrm 后端部署（2026-08-24 实测）

场景：新买/新开通 VPS（如 Lisa 8C8G、搬瓦工），从零装栈并部署 forge-scrm（FastAPI + MySQL + React 前端）。与"已有 VPS 上前端 dist 部署"不同，这是**全栈冷启动**。

## 1. 开通后第一件事：SSH 连通性排查矩阵

新机刚开通典型症状：`ping` 通但所有端口 refused。**不要硬试端口**，按顺序查：

1. **商家面板/开通邮件查 SSH 端口**——新机端口不一定是习惯的 2222（本会话：Lisa 新机默认 5817，旧机才是 2222）。面板写的端口才是准的。
2. 商家镜像可能 `PubkeyAuthentication no`（默认关公钥认证）→ ssh-copy-id 装完 key 仍弹密码。确认：`grep -E "PubkeyAuthentication" /etc/ssh/sshd_config`。修复：`sed -i "s/^#\?PubkeyAuthentication no/PubkeyAuthentication yes/" /etc/ssh/sshd_config && systemctl restart ssh`。
3. `authorized_keys` 可能重复（多次 ssh-copy-id）→ `sort -u` 去重，`chmod 600`。
4. Mac 私钥若非默认名（如 id_ed25519_vps）→ 每次 `-i` 指定，或写 `~/.ssh/config` 别名（Host jiefu-vps / Port / IdentityFile），以后一条 `ssh jiefu-vps` 进入。
5. **VPS→新机 也要免密**：把 VPS 自己的公钥（如 `~/.ssh/id_ed25519_forge.pub`）append 到新机 `authorized_keys`——这样 Hermes（VPS 侧）能免密管理新机，部署脚本才能从 VPS 直接 ssh 进新机执行。

## 2. 换 SSH 端口（用户习惯端口）

```bash
sed -i "s/^#\?Port .*/Port 2222/" /etc/ssh/sshd_config && systemctl restart ssh
ss -tlnp | grep ':2222'   # 确认新端口在听
```

注意：改完后旧端口立即失效；先在当前会话内测试新端口能连再退出，防锁死。

## 3. 基础加固 + 软件栈

```bash
apt-get update   # 必须真实跑通（`apt-get update -qq` 太快=缓存没刷新，装包会 "no installation candidate"）
DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server nginx python3-venv python3-pip ufw fail2ban
```

- MySQL 8 建库建用户（utf8mb4），root 走 socket 认证（Ubuntu 默认）
- UFW：放行 ssh/http/https 再 `ufw --force enable`（顺序反了会把自己锁出去）

## 4. forge-scrm 后端部署（FastAPI + SQLAlchemy + Alembic → MySQL）

### 4.1 StrEnum / Python 版本不匹配（必踩，选对修法）

- 症状：后端启动报 `ImportError: cannot import name 'StrEnum' from 'enum'`（StrEnum 是 Python 3.11+）。**根因常是开发机与 VPS 的 Python 版本不一致**——如 Mac 是 3.14 而 Ubuntu 22.04 系统 Python 是 3.10。
- **先确认开发机 Python 版本**（`python3 --version`），再用修法决定治本还是治标：
- **修法 A（治本，推荐）：升级 VPS 到 3.11+ 并重建 venv**，与开发机对齐，代码保持用 `StrEnum`：
  ```bash
  # Ubuntu 22.04 apt 默认也是 3.10，用 deadsnakes PPA 装 3.11
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq software-properties-common
  add-apt-repository -y ppa:deadsnakes/ppa
  apt-get update -qq
  apt-get install -y -qq python3.11 python3.11-venv
  # 重建后端 venv（先备份旧 .venv）
  cd /opt/forge-scrm/backend
  [ -d .venv ] && mv .venv .venv.bak-py310-$(date +%H%M%S)
  /usr/bin/python3.11 -m venv .venv
  ./.venv/bin/pip install --upgrade pip -q
  ./.venv/bin/pip install -r requirements.txt -q
  ./.venv/bin/python --version   # 确认 python3.11
  ```
- **修法 B（治标，代码零改动时）：enums.py 顶部插兼容层**——适合旧机不能换 Python 的场景：
  ```python
  try:
      from enum import StrEnum
  except ImportError:
      from enum import Enum
      class StrEnum(str, Enum):
          def __str__(self) -> str:
              return self.value
  ```
- 同类语法（3.11+ 才有的）都要扫一遍：`grep -rn "StrEnum" app/`。
- **升级后重启验证**：`systemctl restart forge-scrm-api && systemctl is-active` + 端口监听（`ss -ltnp | grep 8647`）+ `journalctl -u forge-scrm-api -n` 看是否还有新报错——**换 Python 后常暴露出下一层问题（见 4.5）**。

### 4.2 systemd 服务缺 .env 直接启动失败

- 症状：`journalctl -u forge-scrm-api` 显示 `Failed to load environment files: No such file or directory` + `Failed to run 'start' task`。
- 根因：unit 里 `EnvironmentFile=/opt/forge-scrm/backend/.env`，但 .env 没创建（.env 被 .gitignore 排除，clone 下来不存在）。
- 修法：先创建 .env（DEEPSEEK_API_KEY / JWT_SECRET / DATABASE_URL=mysql+pymysql://<user>:<pass>@127.0.0.1:3306/<db>?charset=utf8mb4）`chmod 600`，再 `systemctl restart`。

### 4.3 alembic 迁移到 MySQL

```bash
export DATABASE_URL="mysql+pymysql://<user>:<pass>@127.0.0.1:3306/<db>?charset=utf8mb4"
alembic upgrade head
mysql -u<user> -p<pass> <db> -e "SHOW TABLES;"   # 验证表数 = 字段清单 + alembic_version
```

### 4.4 验证链

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8647/docs          # 200 = app 活着
mysql -u<user> -p<pass> <db> -e "SELECT id, username, role FROM user;"     # 种子账号在
curl -s -X POST http://127.0.0.1:8647/api/auth/login -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'                          # 返回 JWT = 认证链通
```

### 4.5 ⚠️ 换 Python / 重装 venv 后连到 SQLite 而非 MySQL（rsync --delete 清掉 .env，2026-08-25 实测）

- **症状**（继承 4.1 换 Python 后）：`systemctl restart forge-scrm-api` 重启后仍 `active(failed)`，日志报 `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: user`，而 `systemctl is-active mysql` 是 active、`SHOW DATABASES` 也有 `forge_scrm` 库——**明明 MySQL 在，后端却连 SQLite**。
- **根因**：`backend/.env`（含 `DATABASE_URL=mysql+pymysql://...`）被**部署脚本的 `rsync --delete` 清掉/覆盖**了。纯 rsync 部署（见 SKILL.md「部署方式铁律」）里常写 `rsync -avz --delete ../backend/ root@<vps>:/opt/forge-scrm/backend/`——`--delete` 会把远端 `.env`（本地 .gitignore 排除、不在工作区）连带删掉。`.env` 一丢，SQLAlchemy 回退默认 SQLite，于是 `no such table`。
- **修复**：恢复 `.env`（DATABASE_URL 指回 MySQL，含 `mysql+pymysql://<user>:<pass>@127.0.0.1:3306/<db>?charset=utf8mb4`）`chmod 600` → `systemctl restart forge-scrm-api` → 再验证 4.4。
- **防御（部署脚本层）**：rsync backend 时**必须排除 `.env`**（`--exclude='.env'`），`.env` 走独立 `rsync`/手动/模板归档恢复，绝不让 `--delete` 碰它。同时保持 SKILL.md「迁移警示」的 `.env.example` 入库 + 真实 `.env` 单独管理。
- **教训**：换 Python / 重装 venv 成功 ≠ 部署完成——重启后**必须看 journalctl 下一层错误**（本会话 StrEnum 过了又暴露 SQLite 问题），并核对 SQLAlchemy 实际连的是 MySQL 还是回退 SQLite（查日志 `OperationalError` 报的是 `sqlite3` 还是 `pymysql`）。

## 5. nginx 子域名站点 + CF DNS

- 前端 dist root + `location /api/ { proxy_pass http://127.0.0.1:<port>; proxy_read_timeout 300s; }`（DeepSeek 同步分析可能>100s，超时要放大）。
- Cloudflare 加 A 记录 `scrm → 新机IP`，**DNS only（灰云）直连**——CF 橙云有 100s 超时 + WAF 拦裸 curl 的坑。
- 本机验证带 Host 头：`curl -H "Host: scrm.pmlophy.com" http://127.0.0.1/`。
- **用户浏览器打不开但服务器 curl 全通**：先查用户本地 DNS（`nslookup` 看返回 IP）和代理（Clash 规则可能把新域名走代理节点）；服务器侧解析用公共 DNS（1.1.1.1/8.8.8.8）验证，别只看本机。

## 6. 部署脚本去新机化（POC 机 → 最终机 可复用）

新机是 POC（48h/30 天退款窗口）时，部署脚本必须**参数化**（IP/SSH 端口/密码/域名抽成变量），最终机（如旧机升级 8C8G）重建时改变量即用。完整 8 阶段脚本：加固 → MySQL 初始化 → git clone → 后端 venv+依赖 → 前端 build → systemd → nginx → 状态汇总。