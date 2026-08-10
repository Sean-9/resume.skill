#!/usr/bin/env python3
"""JSON → 纯文本。

用法：
    python to_text.py <简历.json> <输出.txt>

给 BOSS 直聘等平台直接粘贴用：无表格、无制表符、无项目符号，段落间空行分隔，
粘贴后不乱。内容与 render.py 一致，只换表现形态。
"""

import argparse
import json
import os

CONTACT_KEYS = ("phone", "email", "wechat", "city", "github", "portfolio")


def build_lines(data):
    lines = [data.get("name", "")]
    if data.get("positioning"):
        lines.append(data["positioning"])

    contact = data.get("contact", {})
    contact_parts = [str(contact[k]).strip() for k in CONTACT_KEYS
                     if str(contact.get(k, "")).strip()]
    if contact_parts:
        lines.append(" | ".join(contact_parts))
    lines.append("")

    for section in data.get("sections", []):
        lines.append(section.get("title", ""))
        lines.append("")
        for item in section.get("items", []):
            if isinstance(item, str):
                lines.append(item)
            else:
                header = item.get("title", "")
                if item.get("subtitle"):
                    header += " | " + item["subtitle"]
                if item.get("dates"):
                    header += " | " + item["dates"]
                lines.append(header)
                if item.get("note"):
                    lines.append(item["note"])
                for bullet in item.get("bullets", []):
                    lines.append(bullet)
            lines.append("")

    return lines


def main():
    parser = argparse.ArgumentParser(description="JSON → 纯文本")
    parser.add_argument("input", help="简历 JSON 文件")
    parser.add_argument("output", help="输出 txt 路径")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    text = "\n".join(build_lines(data)).rstrip("\n") + "\n"

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"已生成 {args.output}")


if __name__ == "__main__":
    main()
