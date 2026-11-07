"""指令开工前校验：四层防护 + 规格八条 + 五段式
用法：python3 check.py 指令文件.md [--keywords 词1,词2]
退出码 0=PASS 1=FAIL
"""
import re, sys, os

SECTIONS = {
    "Context": ["Context", "背景", "上下文"],
    "Request": ["Request", "要求", "需求"],
    "Output": ["Output format", "Output", "输出格式", "交付格式"],
    "红线": ["红线", "禁止", "不许", "不得"],
    "Checkpoint": ["Checkpoint", "检查点", "分阶段", "停下来", "确认后再", "我确认后再"],
}

SPEC = {
    "1 受众": ["给谁看", "受众", "读者", "面向", "给领导", "给运营", "给研发", "评审", "用户看"],
    "2 概念定义": ["定义", "概念", "口径", "什么叫", "含义", "边界"],
    "3 时长/量": ["时长", "秒", "分钟", "预计", "工作量", "规模"],
    "4 术语口径": ["术语", "专业词", "大白话", "禁用词", "不叫", "改叫"],
    "5 对象称呼": ["真名", "编号", "标签名", "命名", "称呼"],
    "6 数据基准": ["基准", "事实源", "数据源", "白名单", "只能使用", "不许新增", "验算"],
    "7 结构": ["阶段", "步骤", "分几段", "结构", "起止", "时间分配"],
    "8 交付内容": ["文案", "清单", "全文", "逐条", "字段", "脚本"],
}

SELFTEST = ["自检", "校验", "验证", "SHA", "哈希", "比对", "抽样", "核对", "误差", "不一致"]
STOP_POINTS = ["先交", "先报", "停下来", "确认后再", "我确认", "核准后", "审阅后", "不要直接", "不要一上来"]
LOOSE = ["一起看", "做完报我一下", "有问题告诉我", "差不多了", "尽量", "适当", "视情况"]
PATH_PAT = re.compile(r"(/Users/|/root/|/home/|E:\\\\|C:\\\\|~/)")


def hit(text, words):
    return [w for w in words if w.lower() in text.lower()]


def main():
    if len(sys.argv) < 2:
        print("用法: python3 check.py 指令文件.md [--keywords 词1,词2]")
        sys.exit(2)
    path = sys.argv[1]
    if not os.path.exists(path):
        print("文件不存在:", path)
        sys.exit(2)
    text = open(path, encoding="utf-8").read()
    fails, warns = [], []

    print("=" * 56)
    print("指令开工前校验", os.path.basename(path), f"({len(text)} 字符)")
    print("=" * 56)

    print("\n[五段式]")
    for name, kws in SECTIONS.items():
        got = hit(text, kws)
        print(f"  {'OK  ' if got else 'MISS'} {name:12s}" + (f"  <- {got[0]}" if got else ""))
        if not got:
            fails.append(f"缺段: {name}")

    print("\n[规格八条]")
    for name, kws in SPEC.items():
        got = hit(text, kws)
        print(f"  {'OK  ' if got else 'MISS'} {name}")
        if not got:
            warns.append(f"规格可能未覆盖: {name}")

    print("\n[自检要求]")
    got = hit(text, SELFTEST)
    if got:
        print(f"  OK  命中 {len(got)} 个: {', '.join(got[:5])}")
    else:
        print("  MISS 没有任何自检要求")
        fails.append("缺自检要求（agent 会只回'已完成'）")

    print("\n[Checkpoint 硬停止点]")
    sp = hit(text, STOP_POINTS)
    if sp:
        print(f"  OK  命中: {', '.join(sp[:4])}")
    else:
        print("  MISS 没有明确的停止点")
        fails.append("Checkpoint 无停止点（agent 会一口气跑完）")

    print("\n[目标路径]")
    mp = PATH_PAT.findall(text)
    if mp:
        print(f"  OK  出现 {len(mp)} 处绝对路径")
    else:
        print("  WARN 没有绝对路径，agent 可能开错目录")
        warns.append("未标清目标仓库/工作区绝对路径")

    print("\n[松散用语]")
    lo = hit(text, LOOSE)
    if lo:
        print(f"  WARN 出现: {', '.join(lo)}")
        warns.append(f"松散用语: {', '.join(lo)}")
    else:
        print("  OK  无")

    if "--keywords" in sys.argv:
        kws = sys.argv[sys.argv.index("--keywords") + 1].split(",")
        print("\n[自定义禁用词]")
        for k in kws:
            if k.strip() and k.strip() in text:
                print(f"  WARN 指令里出现了「{k}」")

    print("\n" + "=" * 56)
    if fails:
        print("FAIL  必须先修:")
        for f in fails:
            print("  x", f)
    if warns:
        print(("FAIL  另:" if fails else "PASS（有提醒）:"))
        for w in warns:
            print("  !", w)
    if not fails and not warns:
        print("PASS  四层齐全，可以发")
    elif not fails:
        print("\n判定: PASS（提醒项建议补上）")
    print("=" * 56)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
