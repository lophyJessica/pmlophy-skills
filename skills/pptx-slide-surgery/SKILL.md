---
name: pptx-slide-surgery
description: Use when 改造已有 PPTX 加页改页而不重做整份。
---

# PPTX 逐页改造（不重做整份）

在已有 pptx 上做增改，而不是重新生成。适用于汇报材料按领导意见迭代的场景。

## 铁律

1. **按标题定位页面，禁止用固定下标**
   插页后所有下标都会位移。用 `find_slide(prs, "标题开头")` 定位，否则会改错页、留下重复页（曾把「已知问题」改到别的页，导致新旧两版并存）。
2. **追加后重排页序**
   python-pptx 只能在末尾 add_slide。插入到位靠重排 `prs.slides._sldIdLst`：
   ```python
   lst = prs.slides._sldIdLst
   ids = list(lst); new = ids[-N:]; rest = ids[:-N]
   order = rest[:a] + [new[0], new[1]] + rest[a:b] + [new[2]] + rest[b:]
   for el in ids: lst.remove(el)
   for el in order: lst.append(el)
   ```
3. **加页后必须统一重写页脚页码**
   页脚是文本框里的 `"{num} / {total}"`。遍历所有页，用正则 `\d+\s*/\s*\d+` 命中后整段替换。
4. **清空重建单页**：`for sh in list(slide.shapes): sh._element.getparent().remove(sh._element)`
5. **每轮必须自证**：逐页 MD5 比对（排除页脚）证明「只改了该改的页」——用户明确怕脚本改错。

## 数值与图表的取舍

- 手画柱状图要补 Y 轴刻度线，否则读者无法核验比例；月份标签要按「柱组中心」对齐，不是按第一根柱。
- 结论里的倍数/比例要逐月算过再写，别按印象写「5 倍以上」。

## 截图页版式

- **2 张并排是清晰度上限**；3 张并排必然「结构可辨、细节不可读」。
- **多图必须等高**：用 `H = min(max_h, min_i(colw / aspect_i))` 统一高度，宽度按比例，否则说明文字基线不齐。
- **只能用有真实数据的截图**：筛掉「查询无数据」的空表和带人工标注框的审计图。用缩略图总览（contact sheet）一次问清楚哪些有数据，别逐张看。
- 截图本身已很紧凑时，裁空白边收益极小（实测 1–4%），别浪费时间。

## 工作流

1. 复制到新文件名产出下一版（`-v2`、`-v3`），不覆盖原件
2. 生成脚本 → `soffice --headless --convert-to pdf` → `pymupdf` 渲染成 PNG
3. 逐张看渲染图，修排版问题（溢出/重叠/对比度/断词/对齐）
4. 全量校验：页数、页脚、逐页 MD5、内嵌图片数

## 中文排版坑

- 9pt 以下小字在投影下偏浅，用 `#3A3A3A` 或更深，别用默认灰。
- 中文跨行断词无法精确控制，靠缩短文案或加宽文本框解决，别硬调。
- 浅底卡 + 深色小字是安全组合；深底卡上的小字要用 `#EAEEFF` 而非 `#D8DEFF`。
