#!/usr/bin/env python3
"""JSON → docx。

用法：
    python render.py <简历.json> <输出.docx> [--template assets/template.docx]

依赖：python-docx。模板可选；缺省时新建空白文档。
中文字体固定为随包提供的 Noto Sans CJK SC（assets/），渲染时显式指定 eastAsia，
避免因系统缺字导致 PDF 中文变方块。本脚本只做排版，不生成任何简历内容。
"""

import argparse
import json
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

FONT_NAME = "Noto Sans CJK SC"


def _apply_font(run, size=None, bold=None, color=None):
    run.font.name = FONT_NAME
    # 中文字体必须写在 w:eastAsia，否则 Word/WPS 对中文仍走默认字体
    run._element.rPr.rFonts.set(qn("w:eastAsia"), FONT_NAME)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def _para(doc, text, size=10.5, bold=False, align=None, color=None, space_after=2):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    r = p.add_run(text)
    _apply_font(r, size=size, bold=bold, color=color)
    return p


def _section_title(doc, text):
    p = _para(doc, text, size=13, bold=True, space_after=3)
    # 标题下缘画一条细线，充当分隔线
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "999999")
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p


def _set_normal_style(doc):
    style = doc.styles["Normal"]
    style.font.name = FONT_NAME
    style.element.rPr.rFonts.set(qn("w:eastAsia"), FONT_NAME)
    style.font.size = Pt(10.5)


def build(doc, data):
    _set_normal_style(doc)

    # 姓名
    _para(doc, data.get("name", ""), size=22, bold=True,
          align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)

    # 一句话定位
    if data.get("positioning"):
        _para(doc, data["positioning"], size=11, align=WD_ALIGN_PARAGRAPH.CENTER,
              color=RGBColor(0x33, 0x33, 0x33), space_after=4)

    # 联系方式，按存在字段拼一行
    contact = data.get("contact", {})
    contact_parts = []
    for key in ("phone", "email", "wechat", "city", "github", "portfolio"):
        val = str(contact.get(key, "")).strip()
        if val:
            contact_parts.append(val)
    if contact_parts:
        _para(doc, "  |  ".join(contact_parts), size=9,
              align=WD_ALIGN_PARAGRAPH.CENTER,
              color=RGBColor(0x66, 0x66, 0x66), space_after=6)

    for section in data.get("sections", []):
        _section_title(doc, section.get("title", ""))

        for item in section.get("items", []):
            if isinstance(item, str):
                # skills 等纯文本条目
                _para(doc, item, size=10.5)
            else:
                # 带标题行的条目：title + subtitle + dates
                header = item.get("title", "")
                if item.get("subtitle"):
                    header += "　" + item["subtitle"]
                if item.get("dates"):
                    header += "　" + item["dates"]
                _para(doc, header, size=11, bold=True, space_after=2)
                for bullet in item.get("bullets", []):
                    bp = doc.add_paragraph(bullet, style="List Bullet")
                    bp.paragraph_format.space_after = Pt(2)
                    for run in bp.runs:
                        _apply_font(run, size=10.5)


def main():
    parser = argparse.ArgumentParser(description="JSON → docx 渲染")
    parser.add_argument("input", help="简历 JSON 文件")
    parser.add_argument("output", help="输出 docx 路径")
    parser.add_argument("--template", default=None,
                        help="可选模板 docx；缺省时新建空白文档")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = Document(args.template) if args.template and os.path.exists(args.template) else Document()
    build(doc, data)
    doc.core_properties.title = data.get("name", "简历")

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    doc.save(args.output)
    print(f"已生成 {args.output}")


if __name__ == "__main__":
    main()
