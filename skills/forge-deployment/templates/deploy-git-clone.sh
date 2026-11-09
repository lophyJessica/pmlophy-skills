#!/bin/bash
# forge-scrm 部署通道（Mac 执行）— git-clone 部署模式的参考模板
# 适用：部署机 = git clone 仓库 + 本地 build（非 zip-incoming 模式）
# 用法：./deploy/deploy.sh
# 目标机：改 VPS_HOST/VPS_PORT/SSH_KEY 三个变量即可换机（POC 退租→最终机）
set -euo pipefail

# ============ 配置（换机只改这里） ============
VPS_HOST="154.29.158.2"       # POC 机；迁回老机时改成老机 IP
VPS_PORT="2222"
SSH_KEY="$HOME/.ssh/id_ed25519_vps"   # Mac 私钥；不存在自动回退 id_ed25519
REMOTE_DIR="/opt/forge-scrm"          # 新机上仓库路径
SERVICE="forge-scrm-api"
DOMAIN="http://scrm.pmlophy.com"

# 自动探测私钥（Mac 可能用 id_ed25519_vps 或默认名）
[ -f "$SSH_KEY" ] || SSH_KEY="$HOME/.ssh/id_ed25519"
SSH_OPTS=(-i "$SSH_KEY" -p "$VPS_PORT" -o StrictHostKeyChecking=no)

echo "===== [1/5] 本地构建前端 ====="
cd "$(dirname "$0")/../frontend"
npm run build 2>&1 | tail -4

echo ""
echo "===== [2/5] 同步 dist 到新机 ====="
rsync -avz -e "ssh -i $SSH_KEY -p $VPS_PORT" \
  dist/ "root@$VPS_HOST:$REMOTE_DIR/frontend/dist/" 2>&1 | tail -3

echo ""
echo "===== [3/5] 新机 git pull（代码同步） ====="
ssh "${SSH_OPTS[@]}" "root@$VPS_HOST" "cd $REMOTE_DIR && git pull origin main 2>&1 | tail -2"

echo ""
echo "===== [4/5] 重启后端 + 刷新 nginx ====="
ssh "${SSH_OPTS[@]}" "root@$VPS_HOST" "
  systemctl restart $SERVICE 2>&1 | tail -1 || true
  systemctl reload nginx 2>/dev/null || systemctl restart nginx
  echo '服务状态:'
  systemctl is-active $SERVICE mysql nginx
"

echo ""
echo "===== [5/5] 线上验证 ====="
sleep 3
echo "首页: $(curl -s -o /dev/null -w '%{http_code}' -m 10 $DOMAIN/)"
echo "title: $(curl -s -m 10 $DOMAIN/ | grep -o '<title>[^<]*</title>' | head -1)"
# ⚠️ 验证路径必须查 openapi.json 真实路由,不能猜:curl -s <后端>/openapi.json | python3 -c "import sys,json;d=json.load(sys.stdin);[print(p) for p in d['paths']]"
# FastAPI 路由前缀常夹模块段(如 /api/auth/login),空 body POST 探测:422=可达(校验拦截),404=未通
echo "API:  $(curl -s -o /dev/null -w '%{http_code}' -m 10 -X POST $DOMAIN/api/auth/login -H 'Content-Type: application/json' -d '{}')（POST /api/auth/login 探测,422=可达,404=未通）"

echo ""
echo "===== 部署完成 ====="