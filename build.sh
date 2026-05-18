#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

python manage.py migrate --noinput

FIXTURE_PATH="$SCRIPT_DIR/initial_data.json"

if [ -f "$FIXTURE_PATH" ]; then
  REPO_COUNT="$(python manage.py shell -c "from apps.repositories.models import Repository; print(Repository.objects.count())" | tail -n 1 | tr -d '[:space:]')"

  if [ "$REPO_COUNT" = "0" ]; then
    python manage.py loaddata "$FIXTURE_PATH"
  else
    echo "Skipping initial_data.json load because repository data already exists."
  fi
else
  echo "Skipping fixture load because initial_data.json was not found at $FIXTURE_PATH."
fi
