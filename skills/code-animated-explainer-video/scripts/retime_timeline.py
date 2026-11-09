"""按分段旁白音频的真实时长，重排一条动效页的整条时间轴。

适用：动效页把「每段文案」固定写在一批时间窗口里（SUBS / PHASES / MSG），而你希望
槽位 = 实际语音时长 + 气口，而不是先拍一个总时长再往里塞文案。

用法：
  1) 先确认音频目录里有 v01.mp3..vNN.mp3（与旁白文稿顺序一致）
  2) 改下面的 BASE / GAP / OLD_WINDOWS
  3) 先备份会被改的文件（index.html / build_voice.py / shot.py / mix.py）
  4) python retime_timeline.py

它做四件事：
  * 分段线性映射旧时间 → 新时间（每段内部等比压缩/拉伸）
  * 重写 index.html 里 MSG 的 t（dur 夹到本槽位上限）、SUBS 的 s/e、PHASES 的 s/e
  * 重写 build_voice.py 的每条时间与 DUR、shot.py 的 DUR、mix.py 的 -t
  * 打印新时长表，便于人工核对

注意：改完后屏幕文案若有钉死的总时长字符串（如 't+"s / 240.0s"'），要改成用 DUR 常量拼。
"""
import re
import subprocess

BASE = "/root/video-demo-seq"      # 项目目录
AUD = f"{BASE}/audio"              # 分段 TTS 音频目录（v01.mp3 …）
GAP = 1.5                          # 每段尾部气口（秒）

# 旧文案窗口，顺序与 audio/vNN.mp3 一致
OLD_WINDOWS = [(0, 15), (15, 28), (28, 40)]   # ← 按项目实际填
PHASE_BOUNDS = [0, 15, 240]                   # 阶段边界（旧时间轴上的秒数）
PHASE_NAMES = ["总览", "① 第一步", "全链路"]    # 与边界一一对应（段数 = len(bounds)-1）


def dur_of(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    ).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def build_windows():
    durs = [dur_of(f"{AUD}/v{i:02d}.mp3") for i in range(1, len(OLD_WINDOWS) + 1)]
    slots = [d + GAP for d in durs]
    starts, acc = [], 0.0
    for s in slots:
        starts.append(acc)
        acc += s
    new_windows = [(round(starts[i], 2), round(starts[i] + slots[i], 2)) for i in range(len(OLD_WINDOWS))]
    return durs, new_windows, round(acc, 2)


def remap(t, old_windows, new_windows):
    t = float(t)
    for i, (os_, oe) in enumerate(old_windows):
        if os_ <= t < oe:
            frac = (t - os_) / (oe - os_)
            return round(new_windows[i][0] + frac * (new_windows[i][1] - new_windows[i][0]), 2)
    if t >= old_windows[-1][1]:
        return round(new_windows[-1][1] + (t - old_windows[-1][1]), 2)
    return round(new_windows[0][0], 2)


def main():
    durs, new_windows, total = build_windows()
    old_total = OLD_WINDOWS[-1][1]
    print(f"旧总时长 {old_total}s → 新总时长 {total}s")

    # ---- index.html ----
    html = open(f"{BASE}/index.html", encoding="utf-8").read()

    def fix_msg(m):
        t, d = float(m.group(1)), float(m.group(2))
        nt = remap(t, OLD_WINDOWS, new_windows)
        for s, e in new_windows:            # 动画不跨出本槽位
            if s <= nt < e:
                d = min(d, max(2.0, (e - nt) - 0.2))
                break
        return f"t:{nt:g},  dur:{round(d, 2):g}"

    html = re.sub(r"t:(\d+(?:\.\d+)?),\s*dur:(\d+(?:\.\d+)?)", fix_msg, html)

    def fix_sub(m):
        s, e, txt = int(m.group(1)), int(m.group(2)), m.group(3)
        return "{{s:{:g}, e:{:g}, txt:'{}'}}".format(
            remap(s, OLD_WINDOWS, new_windows), remap(e, OLD_WINDOWS, new_windows), txt)

    html = re.sub(r"\{s:(\d+),\s*e:(\d+),\s*txt:'([^']*)'\}", fix_sub, html)

    bounds = [0] + [remap(b, OLD_WINDOWS, new_windows) for b in PHASE_BOUNDS[1:-1]] + [total]
    ph = ",\n".join(
        "  {{s:{:g},  e:{:g}, name:'{}'}}".format(bounds[i], bounds[i + 1], PHASE_NAMES[i])
        for i in range(len(PHASE_NAMES))
    )
    html = re.sub(r"const PHASES = \[.*?\];", "const PHASES = [\n" + ph + ",\n];", html, flags=re.S)
    open(f"{BASE}/index.html", "w", encoding="utf-8").write(html)

    # ---- build_voice.py ----
    path = f"{BASE}/build_voice.py"
    bv = open(path, encoding="utf-8").read()
    lines = re.findall(r"\((\d+),\s*(\d+),\s*\"([^\"]*)\"\)", bv)
    entries = [
        "  ({:g},   {:g},  \"{}\")".format(new_windows[i][0], new_windows[i][1], txt)
        for i, (_s, _e, txt) in enumerate(lines)
    ]
    bv = re.sub(r"VOICE = \[.*?\n\]", "VOICE = [\n" + ",\n".join(entries) + ",\n]", bv, flags=re.S)
    bv = re.sub(r"^DUR = [\d.]+", f"DUR = {total}", bv, flags=re.M)
    open(path, "w", encoding="utf-8").write(bv)

    # ---- shot.py / mix.py ----
    for name, pattern, repl in (
        ("shot.py", r"FPS, DUR = 30, [\d.]+", f"FPS, DUR = 30, {total}"),
        ("mix.py", r'"-t","[\d.]+"', f'"-t","{total}"'),
    ):
        p = f"{BASE}/{name}"
        src = open(p, encoding="utf-8").read()
        open(p, "w", encoding="utf-8").write(re.sub(pattern, repl, src))

    print("已更新 index.html / build_voice.py / shot.py / mix.py")
    for i, (s, e) in enumerate(new_windows):
        print(f"  {i + 1:02d} {s:>6.2f} - {e:>6.2f}  (语音 {durs[i]:.2f}s)")
    print("\n下一步：重建旁白轨 → 渲染帧 → 混音 → loudnorm → 三项校验")


if __name__ == "__main__":
    main()
