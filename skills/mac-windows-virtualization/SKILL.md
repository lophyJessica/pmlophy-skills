---
name: mac-windows-virtualization
description: 在 Apple Silicon Mac 上跑 Windows 虚拟机（Parallels/UTM）——装 Windows 11 ARM、跑 Windows-only 软件/游戏（国服 LOL 等）、性能分配、网络被代理拦截的坑。当用户想在 M 系 Mac 上玩 Windows 游戏/用 Windows 软件时使用。
---

# Mac 跑 Windows 虚拟机（Apple Silicon）

> 2026-08-11 实测（M1 Max 64GB + Parallels Desktop + Windows 11 ARM 装国服 LOL）

## 核心事实（先讲清，避免走弯路）

- **M1/M2/M3/M4（ARM）不能装传统双系统（Boot Camp 是 Intel Mac 专用）**——只有虚拟机（Parallels/UTM）或转译层（CrossOver/Game Porting Toolkit）
- **游戏选型三角**（用户实测决策）：
  - Mac 原生版（如 LOL 外服）→ 零折腾直接玩，但**国服腾讯 LOL 无 Mac 版**
  - 云游戏（腾讯 START 等）→ 国服可用、无封号风险，但**卡 + 排队久**（用户实测后排除）
  - 虚拟机（Parallels）→ 本地跑国服，**首选**；代价是 TP 反作弊小概率检测风险（正常玩没事）
- **Windows 11 不激活可免费长期用**（右下角水印 + 不能个性化，但玩游戏完全无影响）——安装时密钥页选"跳过/我没有产品密钥"，不用买授权

## 2026-08-22 更新：国服 LOL 先验证 WeGame M 系列 Mac 客户端

不要把“国服 LOL = 必须先装 Windows/Parallels”作为默认前提。WeGame 官网当前提供 **Mac 端测试版**，并明确区分 Intel 版与 M 系列版；因此 Apple Silicon Mac（包括 M1 Max）应先走官方 WeGame M 系列客户端路径，再考虑 Windows 虚拟机。

推荐决策顺序：

```text
1. WeGame 官方 Mac M 系列测试版 → 安装/登录/启动国服 LOL → 与朋友实测
2. 若官方 Mac 路径不可用、功能不完整或无法组队，再试 Parallels + Windows 11 ARM
3. 若虚拟机方案仍不稳定，再考虑真实 Windows 设备或云电脑
```

这比“先下载 Parallels、再装 Windows、再验证国服”更省时间，也避免为一个尚未确认的兼容性问题先占用大量磁盘。

## 2026-08-22 更新：M1 Max 10C/24GPU/64GB 的资源建议

用户设备是 **M1 Max：10 核 CPU、24 核 GPU、64GB 统一内存**。运行 Windows 11 ARM + LOL 时，第一轮建议：

```text
虚拟 CPU：4 核起步（最多先试 5 核）
虚拟内存：8GB 起步，必要时试 12GB
虚拟磁盘：80GB 动态扩展
图形：Automatic / 游戏优先
```

Parallels 官方建议 Apple Silicon 虚拟机不要分配超过宿主机一半 CPU；10 核 CPU 不要一上来分 8–10 核。Apple Silicon 使用统一内存，系统内存也承担图形用途，因此给 Windows 更多 RAM 不等于 FPS 线性提升。

**诊断顺序：**

- CPU/内存分配主要影响系统响应、加载和帧时间稳定性；
- 硬盘容量本身基本不直接提高 FPS，磁盘快满才可能影响更新、缓存和整体卡顿；
- 虚拟 GPU/图形驱动、Windows ARM 兼容层、WeGame 客户端和反作弊更可能是 FPS/启动稳定性的瓶颈；
- 不要同时修改 CPU、内存、画质三个变量，一次只改一个并记录结果。

游戏测试先进入训练模式，再与朋友匹配；不要首次启动就打排位。
- **Parallels 试用到期不是只显示水印**：官方试用期为 14 天完整功能；到期后 Parallels/虚拟机通常不能继续运行。Windows 11 未激活本身可以继续测试（主要是水印和个性化限制），但不要把 Windows 水印和 Parallels 试用期限混为一谈。


1. **虚拟机没网络 → 多半是 Mac 上的代理/流量拦截工具**（Clash TUN、Antify 等）劫持了 vmnet 流量。诊断顺序：
   - Windows `ipconfig` 有 IP（Parallels NAT 是 `10.211.55.x`，网关 `10.211.55.1`）= 网卡 OK，问题在上游
   - `ping 114.114.114.114` 不通 + `ping 10.211.55.1` 也不通 = 虚拟网卡/转发层断
   - **先关 Mac 上的代理工具（Clash 退出/关 TUN）试**——本次根因是 Antify 拦截，Clash 关了也没用，Antify 处理掉才通
2. **Antify 是什么 + 正确解法（用户 0811 纠正）**：Antify 是用户特意装的**免 TUN 强制代理工具**——专为反重力（Google Antigravity）设计，让反重力不用开全局 TUN 也能正常登录/拉模型（TUN 会费流量、拖慢网速、和内网冲突）。它按进程劫持流量，所以会把 Parallels 也一起代理 → 虚拟机断网。**正确解法 = Antify 里加白名单/规则：Parallels（虚拟机进程/vmnet）→ 直连，不走代理规则**——一劳永逸，不是每次关 Antify。遇到类似"虚拟机上不了网"先想到：白名单放行，而不是停用用户的常驻工具。
2. **Parallels 自动配置（4CPU+8GB）就是玩 LOL 的最优值**——不用手动改，改反而浪费
3. 网速慢/下载大文件时，代理工具的"加速"模式可能反过来拦虚拟机的流量——下载/游戏中如断网先怀疑它
4. **Windows 重启异常/卡死 → 先别点"重置"**（用户 0811 实测）：刚装完系统重启时卡住/提示异常，多半是首启更新没跑完，**先试 Parallels 里"重启虚拟机"/强制关机再开**，数据基本都在；重置 = 重装 Windows + 重下 LOL（20GB）——最后手段。看到"重置"提示先救，别急着点。

## 资源分配与虚拟机关机后的释放

- Parallels 中设置的 CPU 核数和内存（例如 8 核、16GB）是**虚拟机运行时的资源上限/配置值**，不是永久从 Mac 硬件中划走的资源。
- Windows 虚拟机**完全关机**后，分配给它的内存会释放回 macOS；虚拟 CPU 也不再持续占用宿主机的 CPU 调度资源，macOS 可以按需使用整台机器的 CPU、统一内存和 GPU。
- “完全关机”要和“暂停/挂起”区分：暂停可能保留 Windows 的运行状态和内存镜像，不能按完全关机理解。
- 因此回答资源问题前，先确认虚拟机当前状态；不要把 Parallels 的配置值误说成宿主机永久锁定的资源。
- 对本例：M1 Max 10 核 CPU、64GB 统一内存，Windows 配置 8 核、16GB；虚拟机关闭后，这 8 核/16GB 不会继续被 Windows 占用。运行期间则应保留足够资源给 macOS，不宜默认把大部分 CPU 和内存都分给虚拟机。


- **M1 Max 跑 LOL：低画质 60-90fps 流畅；高画质 30-40fps 卡顿**——虚拟机里 LOL 卡顿的根源是 **Parallels 虚拟 GPU 性能上限**（Windows 拿不到真实显卡，虚拟化开销），不是 Mac 性能不够，也不是内存/CPU 不够
- **加资源（内存 8→12G、CPU 4→6 核）治标不治本**：能改善系统响应/加载，但画面帧率（GPU 瓶颈）提升有限——LOL 瓶颈在显卡，加 CPU/内存帮不了虚拟 GPU
- **真正解法（组合拳）**：
  1. LOL 游戏内设置 → 视频 → 画质调低/性能优先 + 分辨率降（如 1920x1080 → 1600x900）
  2. Parallels 配置 → 选项 → 关"平滑鼠标/平滑滚动"（消除点击迟钝——输入映射延迟）
  3. Windows 里关动画/特效 + 关后台（Windows Update/Defender 扫描——刚装完系统在后台跑吃资源）
  4. Parallels 优化模式选"游戏/更快虚拟机"
- 用户实测症状："登录试了下，点击比较迟钝、有点卡"——就是虚拟 GPU + 平滑鼠标两个叠加，降画质 + 关平滑即可丝滑
- 想要高画质丝滑的国服 LOL：只能真机 Windows（另一台电脑）或云游戏——虚拟机是"能玩"（低画质），不是"全特效"方案
- 网络游戏反作弊（腾讯 TP）：虚拟机有小概率检测/封号风险——正常游玩一般没事，接受再上

## 2026-08-28 追加：为游戏续费 Parallels 前先过"场景三问"

用户 Parallels 试用到期后询问购买，真实需求是跑国服 LOL。**先问场景再谈付费**：

- **虚拟机跑 LOL 是三重劣势叠加**：x86 游戏在 ARM 上要转译 + 虚拟 GPU 性能损耗 + 反作弊（ACE/TP）对虚拟机环境检测——Parallels 付费也不保证能玩，CrossOver 或云游戏（START/腾讯先锋）往往才是更优解。
- **频率判断**：偶尔玩 → 云游戏一杯奶茶钱解决；长期上分 → 真实 Windows 机器；为这个场景续费 Parallels（498+）大概率是沉没成本心理。本次用户听完后决定不折腾、直接卸载。
- 卸载姿势：Parallels 菜单自带 Uninstall → 提示删虚拟机镜像时选删（几十 GB）；残留检查 `~/Library/Preferences/com.parallels*` 和 `~/Parallels`。
- **已有 skill 结论仍有效**：真要 Mac 玩国服，先试 WeGame 官方 M 系列 Mac 测试版（本 skill 0822 更新），别默认上虚拟机。

## 相关

- 本地大模型部署与 Mac 硬件认知：`mac-local-llm-deployment` / `apple-silicon-local-llm`
- 二手 Mac 验机：`used-apple-device-verification`
