#!/usr/bin/env bash
# docx → pdf。
#
# 用法：
#     bash to_pdf.sh <输入.docx> [输出.pdf]
#
# 依赖链：
#   1. 优先用 LibreOffice headless 转换（观感与 Word 最接近）；
#   2. 若本机没有 LibreOffice，自动降级：当输入 docx 同目录存在同名 .json 时，
#      调用 scripts/render_pdf.py（pymupdf）直接从 JSON 渲染 PDF，版式同 typography.md。
#
# 会自动把随包字体 assets/ 下的 Noto 字体复制到当前用户的字体目录，
# 保证 PDF 中文不缺字（复用 Common Pitfalls #3 的离线字体方案）。
# macOS: brew install --cask libreoffice；Ubuntu: sudo apt install libreoffice
# 降级依赖：python3 + pymupdf

set -euo pipefail

input="${1:?用法: to_pdf.sh <输入.docx> [输出.pdf]}"
output="${2:-}"

# --- 解析脚本所在目录，定位随包字体（.otf 或 .ttc 均可，脚本自动探测） ---
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
assets_dir="$script_dir/../assets"
font=""
for candidate in "$assets_dir/NotoSansCJKsc-Regular.otf" "$assets_dir/NotoSansCJK-Regular.ttc"; do
    if [ -f "$candidate" ]; then
        font="$candidate"
        break
    fi
done

# --- 把随包字体装进用户字体目录，供 LibreOffice 使用 ---
if [ -n "$font" ]; then
    case "$(uname -s)" in
        Darwin)              font_dir="$HOME/Library/Fonts" ;;
        MINGW*|MSYS*|CYGWIN*) font_dir="${LOCALAPPDATA:-$HOME/AppData/Local}/Microsoft/Windows/Fonts" ;;
        *)                   font_dir="$HOME/.local/share/fonts" ;;
    esac
    if [ ! -f "$font_dir/$(basename "$font")" ]; then
        mkdir -p "$font_dir"
        cp "$font" "$font_dir/"
        command -v fc-cache >/dev/null 2>&1 && fc-cache -f >/dev/null 2>&1 || true
    fi
fi

# --- 定位 LibreOffice 可执行文件 ---
SOFFICE=""
for c in libreoffice soffice; do
    if command -v "$c" >/dev/null 2>&1; then
        SOFFICE="$c"
        break
    fi
done

outdir="$(dirname "$input")"
[ -d "$outdir" ] || outdir="."
json="${input%.docx}.json"
dest="${output:-${input%.docx}.pdf}"

if [ -n "$SOFFICE" ]; then
    # LibreOffice 会把同名 PDF 写到 --outdir
    "$SOFFICE" --headless --convert-to pdf --outdir "$outdir" "$input" >/dev/null
    generated="${input%.docx}.pdf"
    if [ "$generated" != "$dest" ]; then
        mv "$generated" "$dest"
    fi
    echo "已生成 $dest"
else
    if [ ! -f "$json" ]; then
        echo "错误：未找到 LibreOffice（libreoffice/soffice），且同目录无 $json 可降级。" >&2
        echo "  macOS: brew install --cask libreoffice" >&2
        echo "  Ubuntu: sudo apt install libreoffice" >&2
        echo "  或直接用 render_pdf.py：python \"$script_dir/render_pdf.py\" <简历.json> <输出.pdf>" >&2
        exit 1
    fi
    echo "警告：未找到 LibreOffice，降级用 render_pdf.py（pymupdf）从 JSON 渲染。" >&2
    python "$script_dir/render_pdf.py" "$json" "$dest" --font "$font"
fi
