# Vulnerable App Detection

This directory contains the code to detect apps vulnerable to TapTrap.

## Folder structure

- `/VulnTap` contains code for the detection of vulnerable apps
- `/results/2025-01-09`: results of the analysis

## Run the analysis

- define the following environment variables
  - `VULNTAP_RESULT_DIR`: The directory to store the results to
  - `VULNTAP_APK_DIR`: The directory that contains the APKs to analyze
  - `VULNTAP_PARALLELISM`: How many instances of the tool should run at a time
- execute the following steps in the following order:
  - `make setup`: sets up the environment
  - `make run`: analyzes the APKs
- the results are located in `$VULNTAP_RESULT_DIR/<current_date>/output`
- Run `python aggregate_results.py --result_dir $VULNTAP_RESULT_DIR/<current_date>/output` to aggregate the results