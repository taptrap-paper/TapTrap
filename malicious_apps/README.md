# Malicious App Detection

This directory contains the code to detect malicious apps abusing TapTrap.

## Folder structure

- `/MalTapExtract`: code to extract animations from APKs
- `/MalTapAnalyze`: code to analyze animations
- `/results/2025-01-09`: results of the analysis

## Run the analysis

- define the following environment variables
  - `MALTAP_DEVICE_SERIAL`: The serial number of the device from which to pull the `framework-res.apk` (you can retrieve it via `adb devices`)
  - `MALTAP_RESULT_DIR`: The directory to store the results to
  - `MALTAP_APK_DIR`: The directory that contains the APKs to analyze
- execute the following steps in the following order:
  - `make pull_framework`: Pull the `framework-res.apk`
  - `make analyze_framework`: Analyze the `framework-res.apk`
  - `make gather_animations`: Extract animations and interpolators from the APKs
  - `make analyze_animations`: Analyze the animations
- the results are then stored in an SQLite DB located at `$MALTAP_RESULT_DIR/<current_date>/db.sqlite`