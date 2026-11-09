# 把反代接进 Hermes 的某个 profile

适用：反代（CLIProxyAPI 等）已跑通，想把它当某个 profile 的模型用——通常是非主力 profile，当高档模型的试验场，主 agent 不动。

下文以 `jarvis` profile、provider 名 `cpa`、模型 `claude-opus-5-5-high` 为例，按实际替换。

## 0 前置：验 OpenAI 兼容端点

Hermes 走 `/v1/chat/completions`，不是 Anthropic 的 `/v1/messages`：

```bash
curl -s -X POST http://127.0.0.1:8317/v1/chat/completions \
  -H "Authorization: Bearer <key>" -H "content-type: application/json" \
  -d '{"model":"claude-opus-5-5-high","max_tokens":50,"messages":[{"role":"user","content":"你好"}]}' | head -c 300
```

返回里带 `choices[0].message.content` 即可用；带 `reasoning_content` 说明思考链也在。200 但内容空 → 别接，先查模型。

## 1 看现状（只读）

```bash
python3 -c "
import yaml
c=yaml.safe_load(open('/root/.hermes/profiles/<profile>/config.yaml'))
print('model:', c.get('model'))
for k,v in (c.get('providers') or {}).items():
    print(' ', k, '->', (v or {}).get('base_url'))
print('fallback:', c.get('fallback_model'))
"
```

记下原主模型与 fallback，回滚时要靠它。

## 2 备份

```bash
cd /root/.hermes/profiles/<profile>
TS=$(date +%Y%m%d-%H%M%S)
cp config.yaml config.yaml.bak-cpa-$TS && cp .env .env.bak-cpa-$TS
ls -la *.bak-cpa-$TS .env.bak-cpa-$TS
```

## 3 改配置（文本级，不整份重写）

**不要 `yaml.safe_load` 之后 `yaml.dump` 回去**——会丢光注释和字段顺序。用行级替换：

```bash
cd /root/.hermes/profiles/<profile> && python3 - <<'PYEOF'
p='config.yaml'
lines=open(p,encoding='utf-8').read().split('\n')

# 1) 改 model 段三个字段
out=[]; in_model=False
for l in lines:
    if l=='model:':
        in_model=True; out.append(l); continue
    if in_model:
        if l.startswith('  model: '): out.append('  model: claude-opus-5-5-high'); continue
        if l.startswith('  provider: '): out.append('  provider: custom:cpa'); continue
        if l.startswith('  default: '): out.append('  default: claude-opus-5-5-high'); continue
        in_model=False
    out.append(l)
lines=out

# 2) providers 下插入新条目
block=[
'  cpa:',
'    api: http://127.0.0.1:8317/v1',
'    base_url: http://127.0.0.1:8317/v1',
'    enabled: true',
'    key_env: CPA_API_KEY',
'    models:',
'      - claude-opus-5-5-high',
'      - gemini-4-argon-high',
]
out=[]; done=False
for l in lines:
    out.append(l)
    if l=='providers:' and not done:
        out.extend(block); done=True
open(p,'w',encoding='utf-8').write('\n'.join(out))
print('inserted' if done else 'FAILED: no providers:')
PYEOF
```

三个易错点：

- `model.default` 必须跟 `model.model` 一起改，只改前者会让默认值跟实际路由对不上。
- provider 的 `api` 和 `base_url` 两个键都要写，不同版本读的字段不一样。
- `key_env` 只是变量名，真 key 在 `.env` 里。

## 4 key 进 .env

```bash
cd /root/.hermes/profiles/<profile>
grep -q "^CPA_API_KEY=" .env || echo "CPA_API_KEY=<key>" >> .env
grep -c "^CPA_API_KEY=" .env
```

## 5 校验（改完必跑）

```bash
python3 -c "
import yaml
c=yaml.safe_load(open('config.yaml'))
print('model:', c['model'])
print('provider:', c['providers']['cpa'])
" && sed -n '/^model:/,/^[a-z_]*:/p' config.yaml | head -6
```

YAML 能解析、model 段三行都对、provider 条目在列，才算改完。

## 6 交付：重启与回滚都交给用户

```bash
# 生效
systemctl --user restart hermes-gateway && bash /root/hermes-wait.sh

# 回滚（罗宾不能用时）
cd /root/.hermes/profiles/<profile> && cp config.yaml.bak-cpa-<TS> config.yaml && systemctl --user restart hermes-gateway && bash /root/hermes-wait.sh
```

网关重启会同时影响所有 profile，必须用户手动执行并确认时机；交付时把两条命令一起给出，不要让用户临时再问。

排查：`journalctl --user -u hermes-gateway -n 50 --no-pager | grep -iE "<profile>|provider|error"`。

## 附：顺带把 auxiliary.vision 也接过来

主模型能跑不等于视觉能用。Hermes 的识图走**独立配置段** `auxiliary.vision`，跟 `model` 是两回事——改主模型不会带动它，它也不会因为主模型可用就自动可用。

同一个反代可以同时当视觉源（Gemini 原生吃图）：

```yaml
auxiliary:
  vision:
    provider: custom:cpa
    model: gemini-4-argon-high
    base_url: http://127.0.0.1:8317/v1
    key_env: CPA_API_KEY
```

三条纪律：

- **key 用该 profile 自己的 `.env`**。不同 profile 的 `.env` 是隔离的，别假设另一个 profile 有的 key 这边也有——先 `grep -oE "^[A-Z_]+=" <profile>/.env | sort` 看清有什么，再决定用哪个 provider。缺 key 时优先复用该 profile 已有的，而不是新加供应商（新加的第三方 key 可能早已过期，白配一轮）。
- **验证必须发真图问内容**，不能只测 chat 通不通。一张已有截图 + 「图里左上角标题是什么」这类唯一答案的问题，回答对才算链路通：

```bash
python3 - <<'PYEOF'
import base64, json, urllib.request
img = base64.b64encode(open('/tmp/frame.jpg','rb').read()).decode()
body = {"model":"gemini-4-argon-high","max_tokens":100,"messages":[{"role":"user","content":[
  {"type":"text","text":"这张图里左上角的标题写的是什么？只回答标题文字。"},
  {"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+img}}]}]}
# 用 /v1/chat/completions，Hermes 侧也是这个格式
PYEOF
```

- **配额分组要跟着切**：Claude 组打满时 Gemini 组通常还有量（两份独立池），视觉挂 Gemini 组正好用掉闲置额度，不会跟主模型抢。

## 判据速查

| 现象 | 先查 |
|---|---|
| 起来后报模型不存在 | 模型 ID 是否在反代 `/v1/models` 列表里（要全名，如 `claude-opus-5-5-high`） |
| 报 401 | profile `.env` 里的 key 与反代 `access.api-keys` 是否一致 |
| 报 429 | 该模型额度紧或反代被风控（见主 SKILL 的 429 一节），换个额度宽的模型先跑通 |
| 改了没反应 | 网关没重启；`model.provider` 是否带 `custom:` 前缀 |
