#!/usr/bin/env bash
# docx → pdf（依赖 LibreOffice headless）。
#
# 用法：
#     bash to_pdf.sh <输入.docx> [输出.pdf]
#
# 会自动把随包字体 assets/NotoSansCJKsc-Regular.otf 复制到当前用户的字体目录，
# 保证 PDF 中文不缺字（复用 Common Pitfalls #3 的离线字体方案）。
# macOS: brew install --cask libreoffice；Ubuntu: sudo apt install libreoffice

set -euo pipefail

input="${1:?用法: to_pdf.sh <输入.docx> [输出.pdf]}"

# --- 解析脚本所在目录，定位随包字体 ---
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
font="$script_dir/../assets/NotoSansCJKsc-Regular.otf"

# --- 把随包字体装进用户字体目录，供 LibreOffice 使用 ---
if [ -f "$font" ]; then
    case "$(uname -s)" in
        Darwin)              font_dir="$HOME/Library/Fonts" ;;
        MINGW*|MSYS*|CYGWIN*) font_dir="${LOCALAPPDATA:-$HOME/AppData/Local}/Microsoft/Windows/Fonts" ;;
        *)                   font_dir="$HOME/.local/share/fonts" ;;
    esac
    if [ ! -f "$font_dir/NotoSansCJKsc-Regular.otf" ]; then
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
if [ -z "$SOFFICE" ]; then
    echo "错误：未找到 LibreOffice（libreoffice/soffice）。" >&2
    echo "  macOS: brew install --cask libreoffice" >&2
    echo "  Ubuntu: sudo apt install libreoffice" >&2
    exit 1
fi

outdir="$(dirname "$input")"
[ -d "$outdir" ] || outdir="."

# LibreOffice 会把同名 PDF 写到 --outdir
"$SOFFICE" --headless --convert-to pdf --outdir "$outdir" "$input" >/dev/null

generated="${input%.docx}.pdf"
if [ "$#" -ge 2 ]; then
    mv "$generated" "$2"
    echo "已生成 $2"
else
    echo "已生成 $generated"
fi
