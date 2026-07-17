#!/bin/zsh

set -o pipefail

input_pdf="$1"

show_error() {
    /usr/bin/osascript -e "display alert \"提取 PDF 页码失败\" message \"$1\" as critical"
}

if [[ -z "$input_pdf" || ! -f "$input_pdf" ]]; then
    show_error "请先在 LaunchBar 中选中一个 PDF，然后按 Tab 发送到本动作。"
    exit 1
fi

if [[ "${input_pdf:l}" != *.pdf ]]; then
    show_error "所选文件不是 PDF。"
    exit 1
fi

page_range=$(/usr/bin/osascript -e 'text returned of (display dialog "输入页码范围，例如 12-27 或 1-3,8,10-12：" with title "提取 PDF 页码" default answer "")' 2>/dev/null)
dialog_status=$?
if (( dialog_status != 0 )) || [[ -z "$page_range" ]]; then
    exit 0
fi

safe_range=$(print -r -- "$page_range" | /usr/bin/tr -cd '0-9,-')
if [[ -z "$safe_range" ]]; then
    show_error "页码范围只能包含数字、逗号和连字符。"
    exit 1
fi

folder=${input_pdf:h}
base_name=${input_pdf:t:r}
output_pdf="$folder/${base_name}_第${safe_range}页.pdf"
counter=2
while [[ -e "$output_pdf" ]]; do
    output_pdf="$folder/${base_name}_第${safe_range}页-${counter}.pdf"
    (( counter++ ))
done

script_dir=${0:A:h}
if ! /usr/bin/osascript -l JavaScript "$script_dir/extract_pages.js" "$input_pdf" "$page_range" "$output_pdf"; then
    show_error "请检查页码范围是否正确，且未超出 PDF 页数。"
    exit 1
fi

/usr/bin/osascript -e "display notification \"$(/usr/bin/basename "$output_pdf")\" with title \"已提取 PDF 页码\""
