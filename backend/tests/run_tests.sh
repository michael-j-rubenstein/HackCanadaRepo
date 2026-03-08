#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$SCRIPT_DIR/test_results.log"

# Clear previous log
rm -f "$LOG_FILE"

# Clear pytest/python caches
find "$BACKEND_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BACKEND_DIR" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

echo "Running tests..."
echo "Log: $LOG_FILE"

# Run pytest and tee output to log
cd "$BACKEND_DIR"
if pytest tests/test_price_aggregation.py -v -s 2>&1 | tee "$LOG_FILE"; then
    RESULT="PASSED"
else
    RESULT="FAILED"
fi

# Append summary
printf '\n--- Summary ---\nResult: %s\nTimestamp: %s\n' "$RESULT" "$(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
