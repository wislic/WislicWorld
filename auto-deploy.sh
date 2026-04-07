#!/bin/bash
export PATH="/opt/homebrew/bin:$PATH"
WATCH_DIR="/Users/wislic/Documents/Claude/WislicWorld"
LOG_PREFIX="[WislicDeploy]"
cd "$WATCH_DIR" || { echo "$LOG_PREFIX 无法进入目录"; exit 1; }
echo "$LOG_PREFIX 启动监听 | $WATCH_DIR"
fswatch -o "$WATCH_DIR" --exclude=".git" --exclude="\.DS_Store" --exclude="auto-deploy\.sh" --latency 3 | while read -r c; do
  sleep 2; cd "$WATCH_DIR" || continue
  CHANGED=$(git status --porcelain)
  [[ -z "$CHANGED" ]] && continue
  SHORT_TIME=$(date '+%Y-%m-%d %H:%M')
  FILE_COUNT=$(echo "$CHANGED" | wc -l | tr -d ' ')
  FIRST_FILE=$(echo "$CHANGED" | head -1 | awk '{print $2}')
  git add .
  [ "$FILE_COUNT" -eq 1 ] && MSG="auto: $SHORT_TIME | $FIRST_FILE" || MSG="auto: $SHORT_TIME | ${FILE_COUNT} 个文件更新"
  git commit -m "$MSG"
  git push origin main && echo "$LOG_PREFIX ✅ $(date '+%H:%M:%S') $MSG" || echo "$LOG_PREFIX ❌ Push 失败"
done
