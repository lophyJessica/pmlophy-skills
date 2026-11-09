# Clash/Hysteria2 Config Review Checklist (2026-07-26)

## Key config params for hysteria2 node

```yaml
proxies:
  - name: "LA-NTT-hy2"
    type: hysteria2
    server: 192.220.14.245
    port: 46058
    password: "..."
    sni: www.bing.com
    skip-cert-verify: true
    fast-open: true
    ignore-client-bandwidth: true   # inside node, not at top level
    # no mtu: → dynamic MTU probing enabled
```

## Common pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| DNS leak: using domestic DNS (223.5.5.5/119.29.29.29) | Google/GitHub域名被劫持 | Add fake-ip-filter |
| ignore-client-bandwidth at top level | No effect | Inside node definition |
| disable-mtu-discovery at top level | No effect | Inside node definition |
| Fixed MTU (mtu: 1350) | Worse than dynamic | Remove/comment mtu |
| HTTPS probe fails (desktop app) | Token input never appears | Need /api/status or /health endpoint |

## DNS leak fix

```yaml
dns:
  enable: true
  enhanced-mode: fake-ip
  nameserver:
    - 223.5.5.5
    - 119.29.29.29
  fake-ip-filter:
    - "*.lan"
    - "localhost.ptlogin2.qq.com"
```

## Performance

- Sing-box (46058): no mtu fix + ignore-client-bandwidth: true → dynamic → faster
- Standalone hysteria2 (443): mtu:1350 + disable_mtu_discovery:true → fixed → slower
- Recommendation: remove mtu from both, let QUIC auto-negotiate
