#!/usr/bin/env bash
# Extract bots code from zip if bots directory does not exist
if [ ! -d "bots" ] && [ -f "ugcinema-bots-v9-full.zip" ]; then
  echo "Extracting bots code..."
  python - <<'PY'
import zipfile, os
with zipfile.ZipFile('ugcinema-bots-v9-full.zip', 'r') as z:
    z.extractall('.')
PY
fi

set -euo pipefail
echo "Select process via PROC env (uploader|payment|analytics). Default=uploader"
PROC=${PROC:-uploader}
case "$PROC" in
  uploader) python -m bots.uploader_bot.main ;;
  payment) python -m bots.payment_bot.main ;;
  analytics) python -m bots.analytics_bot.main ;;
  *) echo "Unknown PROC: $PROC"; exit 1 ;;
esac
