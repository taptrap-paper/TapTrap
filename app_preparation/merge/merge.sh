#!/bin/bash

if [[ "$#" -ne 3 ]]; then
    echo "Usage: $0 <APK_DIR> <OUT_DIR> <APK_LIST>"
    exit 1
fi

APK_DIR="$1"
OUT_DIR="$2"
APK_LIST="$3"

parallel \
    --jobs 25 \
    --joblog joblog.log \
    --resume \
    --progress \
    python merge.py $APK_DIR {} $OUT_DIR :::: $APK_LIST