#!/bin/bash
# ═══════════════════════════════════════════════
# add-report.sh — 快速添加新报告到 WislicAIWorld
# 用法: ./add-report.sh <html文件路径> <分类> [标题]
# 示例: ./add-report.sh ~/Downloads/daily-0330.html daily "宏观日报 2026-03-30"
# ═══════════════════════════════════════════════

set -e

if [ $# -lt 2 ]; then
  echo "用法: $0 <html文件路径> <分类: daily|flash|deep|other> [标题]"
  echo "示例: $0 ~/Downloads/report.html daily \"宏观日报 2026-03-30\""
  exit 1
fi

SRC="$1"
CATEGORY="$2"
TODAY=$(date +%Y-%m-%d)
TITLE="${3:-Report $TODAY}"
FILENAME=$(basename "$SRC")

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST_DIR="$SCRIPT_DIR/reports/$CATEGORY"
DEST_FILE="$DEST_DIR/$FILENAME"

# 检查文件
if [ ! -f "$SRC" ]; then
  echo "❌ 文件不存在: $SRC"
  exit 1
fi

# 检查分类
if [ ! -d "$DEST_DIR" ]; then
  echo "📁 创建分类目录: $DEST_DIR"
  mkdir -p "$DEST_DIR"
fi

# 复制文件
cp "$SRC" "$DEST_FILE"
echo "✅ 已复制: $DEST_FILE"

# 更新 reports.json
RELATIVE_PATH="reports/$CATEGORY/$FILENAME"
python3 -c "
import json
with open('$SCRIPT_DIR/reports.json', 'r') as f:
    data = json.load(f)

new_entry = {
    'title': '$TITLE',
    'category': '$CATEGORY',
    'date': '$TODAY',
    'file': '$RELATIVE_PATH'
}

data['reports'].insert(0, new_entry)

with open('$SCRIPT_DIR/reports.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'✅ 已更新 reports.json: {new_entry[\"title\"]}')
"

echo ""
echo "📋 下一步:"
echo "   cd $SCRIPT_DIR"
echo "   git add ."
echo "   git commit -m \"add: $TITLE\""
echo "   git push"
