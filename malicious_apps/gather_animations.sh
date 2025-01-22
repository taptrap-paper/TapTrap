#!/bin/bash

JAR_FILE="./MalTapExtract/build/libs/MalTapExtract-1.0-SNAPSHOT.jar"
CACHE_DIR="$1"
DB_PATH="$2"
APK_DIR="$3"
LOG_DIR="$4"
PARALLELISM="$5"

echo "Parallelism: $PARALLELISM"

# Check if all the required arguments are provided
if [[ $# -ne 5 ]]; then
    echo "Usage: ./gather_animations.sh <cache_dir> <db_path> <apk_dir> <log_dir> <parallelism>"
    exit 1
fi

# Check if the cache directory exists
if [[ ! -d "$CACHE_DIR" ]]; then
    echo "Cache directory not found!"
    exit 1
fi

# Check if the APK dir exists
if [[ ! -d "$APK_DIR" ]]; then
    echo "APK dir not found!"
    exit 1
fi

# If the log directory does not exist, create it
if [[ ! -d "$LOG_DIR" ]]; then
    mkdir -p "$LOG_DIR"
fi

find "$APK_DIR" -maxdepth 1 -type f -name "*.apk" | parallel --joblog "$LOG_DIR/joblog.log" \
         --results "$LOG_DIR" \
         --resume \
         --progress \
         --eta \
         --jobs "$PARALLELISM" \
         java -jar "$JAR_FILE" -apk {} -database "$DB_PATH" -cache "$CACHE_DIR"