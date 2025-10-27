#!/usr/bin/env bash
set -euo pipefail
echo "Select process via PROC env (uploader|payment|analytics). Default=uploader"
PROC=${PROC:-uploader}
case "$PROC" in
  uploader) python -m bots.uploader_bot.main ;;
  payment) python -m bots.payment_bot.main ;;
  analytics) python -m bots.analytics_bot.main ;;
  *) echo "Unknown PROC: $PROC"; exit 1 ;;
esac
