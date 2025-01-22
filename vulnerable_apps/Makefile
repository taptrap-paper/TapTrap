RESULT_BASE_DIR ?= $(shell realpath ${VULNTAP_RESULT_DIR})
RESULT_DIR ?= $(RESULT_BASE_DIR)/$(shell date +"%Y-%m-%d")
VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
REQUIREMENTS = VulnTap/requirements.txt

# if VULNTAP_FORCE_RESULT_DIR is set, then we will overwrite the RESULT_DIR, not considering the date
ifdef VULNTAP_FORCE_RESULT_DIR
	RESULT_DIR := $(VULNTAP_FORCE_RESULT_DIR)
endif

APK_DIR ?= $(shell realpath ${VULNTAP_APK_DIR})
OUTPUT_DIR ?= $(RESULT_DIR)/output
LOG_DIR ?= $(RESULT_DIR)/logs
PARALLELISM ?= $(VULNTAP_PARALLELISM)

.PHONY: all help setup clean install venv run

all: help

venv:
	python3 -m venv $(VENV_DIR)

setup: install
	@echo "Setup complete. Virtual environment created and dependencies installed."

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)

run: setup
	@echo "Analyzing apps in $(APK_DIR) using Androguard ..."
	@mkdir -p $(OUTPUT_DIR) $(LOG_DIR)
	@./analyze_apps.sh $(APK_DIR) $(OUTPUT_DIR) $(LOG_DIR) $(PARALLELISM) $(PYTHON)

clean:
	rm -r $(VENV_DIR) __pycache__ .pytest_cache

help:
	@echo "Makefile targets:"
	@echo "  setup    - Setup the environment"
	@echo "  run      - Analyze APKs in $(APK_DIR)" and output results to $(OUTPUT_DIR)
	@echo "  clean    - Remove the virtual environment and other temporary files"
	@echo "  help     - Display this help message"