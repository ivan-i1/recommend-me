#!/bin/bash
set -euo pipefail

# Absolute path — quoted to handle spaces in directory names
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 15th of every month at 3:00 AM
CRON_SCHEDULE="0 3 15 * *"

# Inner quotes escaped so the cron daemon receives them correctly
CRON_COMMAND="cd \"$PROJECT_DIR\" && docker compose --profile data-only run --rm data python update_providers.py && docker compose --profile data-only run --rm data python add_new_movies.py >> \"$PROJECT_DIR/logs/updates.log\" 2>&1"

CRON_JOB="$CRON_SCHEDULE $CRON_COMMAND"

# Get existing crontab (empty if none) — avoids pipefail on first-time setup
EXISTING_CRONTAB=$(crontab -l 2>/dev/null || echo "")

# Remove any old entry for these scripts then add the new one
(echo "$EXISTING_CRONTAB" | grep -v "update_providers.py"; echo "$CRON_JOB") | crontab -

echo "Cron job configured successfully."
echo ""
echo "Schedule : 15th of every month at 3:00 AM"
echo "Command  : $CRON_COMMAND"
echo ""
echo "Current crontab:"
crontab -l
