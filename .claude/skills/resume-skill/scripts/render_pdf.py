#!/usr/bin/env python3
"""JSON → pdf（pymupdf 实现，按 typography.md）。

用法：
    python render_pdf.py <简历.json> <输出.pdf> [--font assets/NotoSansCJKsc-Regular.otf]

依赖：pymupdf。本脚本是 LibreOffice 缺失时的 PDF 兜底，观感与 docx 版一致：
中英同源字体、三级字号、三档间距、日期右对齐、拉丁词不在词中断行、论文标题 note 降级。
"""

import argparse
import json
import os
import re

import pymupdf

# --- typography.md 数值（与 render.py 保持一致） ---
SIZE_NAME = 20
SIZE_POSITIONING = 10.5
SIZE_CONTACT = 9
SIZE_SECTION = 14
SIZE_ENTRY = 11.5
SIZE_BULLET = 10
SIZE_NOTE = 9
SPACE_SECTION = 6.5
SPACE_ENTRY = 2.5
SPACE_ENTRY_HEADER = 2.0
SPACE_BULLET = 1.0
SPACE_NOTE = 1.5
LEADING = 1.32
GRAY = (0.35, 0.35, 0.35)
DARK = (0.13, 0.13, 0.13)

# A4 pt
PW, PH = 595, 842
MARGIN = 57
AVAIL = PW - 2 * MARGIN

# CJK 单字 / 拉丁词(+闭括号) / 其他符号 / 空白 —— 换行只发生在原子边界；
# 闭括号（）)」』】〕）钉在前一词上，避免换行后行首孤悬一个括回
_ATOM = re.compile(
    r"[一-鿿　-〿＀-￯—‘’“”…]"
    r"|[A-Za-z0-9][A-Za-z0-9.\-_]*[）)」』】〕]?"
    r"|[^\s一-鿿　-〿＀-￯]+"
    r"|\s+"
)


def wrap_text(text, font, size, maxwidth):
    """按原子断行：中文可逐字断，拉丁词不在词中间断。"""
    lines, cur = [], ""
    for unit in _ATOM.findall(text):
        if unit.isspace():
            if cur and not cur.endswith(" "):
                cur += " "
            continue
        trial = cur + unit
        if font.text_length(trial, fontsize=size) <= maxwidth:
            cur = trial
        else:
            if cur.strip():
                lines.append(cur.strip())
            cur = unit
    if cur.strip():
        lines.append(cur.strip())
    return lines


class PageCanvas:
    def __init__(self, doc, fontpath):
        self.doc = doc
        self.font = pymupdf.Font(fontfile=fontpath)
        self.fontpath = fontpath
        self.page = self._new_page()
        self.y = MARGIN

    def _new_page(self):
        page = self.doc.new_page(width=PW, height=PH)
        page.insert_font(fontname="f0", fontfile=self.fontpath)
        return page

    def ensure(self, height):
        if self.y + height > PH - MARGIN:
            self.page = self._new_page()
            self.y = MARGIN

    def line_height(self, size):
        return size * LEADING

    def text_width(self, text, size):
        return self.font.text_length(text, fontsize=size)

    def draw(self, text, size, x, color=DARK):
        self.page.insert_text((x, self.y), text, fontname="f0",
                              fontsize=size, color=color)

    def para(self, text, size, color=DARK, indent=0, space_after=0,
             space_before=0, maxwidth=None, right_anchor=None):
        """整段按原子换行后逐行绘制。right_anchor: (文本, size, color) 与首行同一基线右对齐。"""
        self.y += space_before
        width = maxwidth or (AVAIL - indent)
        right_text, right_size, right_color = (right_anchor or (None, None, None))
        if right_text is not None:
            width = max(width - self.text_width(right_text, right_size) - 6, 60)
        lines = wrap_text(text, self.font, size, width)
        first = True
        for ln in lines:
            self.ensure(self.line_height(size))
            self.draw(ln, size, MARGIN + indent, color=color)
            if first and right_text is not None:
                rw = self.text_width(right_text, right_size)
                self.draw(right_text, right_size, PW - MARGIN - rw, color=right_color)
                first = False
            self.y += self.line_height(size)
        self.y += space_after

    def rule(self):
        self.ensure(6)
        self.page.draw_line((MARGIN, self.y - 2), (PW - MARGIN, self.y - 2),
                            color=(0.6, 0.6, 0.6), width=0.7)


def build(data, doc, canvas):
    # H1 姓名
    canvas.para(data.get("name", ""), SIZE_NAME, DARK, space_after=4)

    # 定位语
    if data.get("positioning"):
        canvas.para(data["positioning"], SIZE_POSITIONING, DARK, space_after=4)

    # 联系方式
    contact = data.get("contact", {})
    parts = [str(contact[k]).strip() for k in ("phone", "email", "wechat", "city", "github", "portfolio")
             if str(contact.get(k, "")).strip()]
    if parts:
        canvas.para("  |  ".join(parts), SIZE_CONTACT, GRAY, space_after=2)

    for i, section in enumerate(data.get("sections", [])):
        canvas.para(section.get("title", ""), SIZE_SECTION, DARK,
                    space_before=SPACE_SECTION if i > 0 else 4, space_after=2.5)
        canvas.rule()

        for item in section.get("items", []):
            if isinstance(item, str):
                canvas.para(item, SIZE_BULLET, DARK, space_after=SPACE_ENTRY)
            else:
                header = item.get("title", "")
                if item.get("subtitle"):
                    header += "　" + item["subtitle"]
                canvas.para(header, SIZE_ENTRY, DARK, space_before=SPACE_ENTRY,
                            space_after=SPACE_ENTRY_HEADER,
                            right_anchor=(item.get("dates", ""), SIZE_ENTRY, GRAY) if item.get("dates") else None)
                if item.get("note"):
                    canvas.para(item["note"], SIZE_NOTE, GRAY, indent=10,
                                space_after=SPACE_NOTE)
                for b in item.get("bullets", []):
                    canvas.para("• " + b, SIZE_BULLET, DARK, indent=10,
                                space_after=SPACE_BULLET)


def main():
    parser = argparse.ArgumentParser(description="JSON → pdf 渲染（按 typography.md）")
    parser.add_argument("input", help="简历 JSON 文件")
    parser.add_argument("output", help="输出 pdf 路径")
    parser.add_argument("--font", default=None,
                        help="Noto 字体路径（.otf/.ttc）；缺省时在 assets/ 自动探测")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "..", "assets")
    font_path = args.font
    if not font_path:
        for cand in ("NotoSansCJKsc-Regular.otf", "NotoSansCJK-Regular.ttc"):
            p = os.path.join(assets_dir, cand)
            if os.path.exists(p):
                font_path = p
                break
    if not font_path or not os.path.exists(font_path):
        raise SystemExit("错误：找不到 Noto 字体，请用 --font 指定，或放入 assets/")

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = pymupdf.open()
    canvas = PageCanvas(doc, font_path)
    build(data, doc, canvas)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    doc.save(args.output)
    print(f"已生成 {args.output}（{len(doc)} 页）")


if __name__ == "__main__":
    main()
