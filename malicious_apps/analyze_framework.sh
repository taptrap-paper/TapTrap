#!/bin/bash

# Assigning variables
JAR_FILE="./MalTapExtract/build/libs/MalTapExtract-1.0-SNAPSHOT.jar"

FRAMEWORK_APK="$1"
DB_PATH="$2"
CACHE_DIR="$3"

# Ensure correct usage
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <FRAMEWORK_APK> <DB_PATH> <CACHE_DIR>"
    exit 1
fi

# Running the Java application
echo "Running analysis with $JAR_FILE..."
java -jar "$JAR_FILE" -apk "$FRAMEWORK_APK" -framework -cache "$CACHE_DIR" -database "$DB_PATH"

# Check if the command finished successfully
if [ $? -eq 0 ]; then
    echo "Analysis completed successfully."
else
    echo "Error: Analysis failed. Please check the input files and logs."
    exit 1
fi