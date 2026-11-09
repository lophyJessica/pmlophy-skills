# vivo 公司工作机实测(2026-08-31)

用户入职 vivo(外包,联想?不——实测是 HP),拿到公司 Windows 工作机。此文件记录实测硬件与结论,供日后排查直接对照。

## 机型(来自用户发来的 DxDiag.txt)
- **品牌机型**: HP EliteBook 830 13 inch G11 Notebook PC
- **系统**: Windows 11 专业版 64-bit (Build 26200)
- **CPU**: Intel Core Ultra 7 155U (14 CPUs) ~1.7GHz
- **内存**: 16GB RAM
- **GPU**: Intel Graphics(核显,无独显),Feature Level 12_2,Display Memory 9154MB(共享)
- **BIOS**: W70 Ver. 01.07.02

## 屏幕/显示(眼睛难受排查关键)
- **笔记本内置屏**: 13 寸,Current Mode **1920×1200 @60Hz**,Native Mode 同=满格
- **外接屏**: 最初 DELL P2422H(24寸 1080p),后用户换成 **Pro2820(28寸 1080p)**,仍是 1920×1080 @60Hz。公司备货只有 1080p,没有 2K/4K,用户已接受凑合用(缩放调到位 + 放远看缓解)。若申请屏,27寸 2K 是甜点位,用"UI 审查看像素"的业务理由提。
- **DPI**: User/System DPI Setting = **144 DPI = 150%**(笔记本缩放)
- **拓扑**: Display Topology = Extend(双屏扩展)
- **还有第三块**: Citrix Indirect Display Adapter(Citrix 远程虚拟屏,Current Mode Unknown)

## 结论
三块实体屏分辨率全部满格、非"分辨率太低"。用户"眼睛要瞎"的真因 = 13 寸小屏 150% 仍偏小 + 双屏混合 DPI(笔记本 150% vs 外接 100%)拖窗口发虚。修复方向:统一外接屏缩放至 150% + 辅助功能文本大小调大 + 夜间模式。

## 关键限制(2026-08-31 用户明确)
- **公司飞书明令禁止发图片**:用户原话"明面上说不让发" = IT 管控,**不要当飞书应用权限问题去排查**(已确认无意义)。
- 键盘在笔记本上(外接屏不能用作主操作台),主工作靠 13 寸笔记本屏。
- 公司机为联想台式?否,实测 HP。之前交接文档写"配联想台式机"与实际不符,以本 DxDiag 实测为准。

## 备注
用户从 M1 Max Mac 切到 Windows 第一天,情绪上"难受"为主,已接受继续用 Windows。沟通上先共情、别主动推销工具,用户要才给(Everything/PowerToys/Wox 等"找回 Mac 手感"方案)。