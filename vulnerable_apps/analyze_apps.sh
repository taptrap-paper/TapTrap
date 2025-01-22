#!/bin/bash

APK_DIR="$1"
OUTPUT_DIR="$2"
LOG_DIR="$3"
PARALLELISM="$4"
TIMEOUT_DURATION="60m"
PYTHON="$5"

if [[ $# -ne 5 ]]; then
    echo "Usage: $0 <APK_DIR> <OUTPUT_DIR> <LOG_DIR> <PARALLELISM> <PYTHON>"
    exit 1
fi


# Detect the operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    TIMEOUT_CMD="gtimeout"
    if ! command -v gtimeout &> /dev/null; then
        echo "gtimeout is not installed. Please install it with 'brew install coreutils'."
        exit 1
    fi
else
    # Linux/Other Unix-based systems
    TIMEOUT_CMD="timeout"
    if ! command -v timeout &> /dev/null; then
        echo "timeout command is not available. Please install it."
        exit 1
    fi
fi

if [[ ! -d "$APK_DIR" ]]; then
    echo "APK_DIR does not exist"
    exit 1
fi

if [[ ! -d "$OUTPUT_DIR" ]]; then
    echo "OUTPUT_DIR does not exist"
    mkdir -p "$OUTPUT_DIR"
fi

if [[ ! -d "$LOG_DIR" ]]; then
    echo "LOG_DIR does not exist"
    mkdir -p "$LOG_DIR"
fi

find "$APK_DIR" -maxdepth 1 -type f -name "*.apk" | parallel --joblog "$LOG_DIR/joblog.log" \
         --results "$LOG_DIR" \
         --resume \
         --progress \
         --eta \
         --jobs "$PARALLELISM" \
        $TIMEOUT_CMD "$TIMEOUT_DURATION" $PYTHON VulnTap/VulnTap/analyzer.py -apk {} -output "$OUTPUT_DIR"