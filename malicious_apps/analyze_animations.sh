#!/bin/bash

PROJECT_DIR="./MalTapAnalyze"
DB_PATH="$1"
LOG_DIR="$2"

if [ -z "$DB_PATH" ] || [ -z "$LOG_DIR" ]; then
  echo "Usage: $0 <DB_PATH> <LOG_DIR>"
  exit 1
fi

cd "$PROJECT_DIR" && ./gradlew testRelease --tests "*.run" -Ddatabase="$DB_PATH" --warning-mode all