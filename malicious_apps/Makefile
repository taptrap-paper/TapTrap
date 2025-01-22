DEVICE_SERIAL ?= ${MALTAP_DEVICE_SERIAL}

RESULT_BASE_DIR := $(shell realpath ${MALTAP_RESULT_DIR})
RESULT_DIR ?= $(RESULT_BASE_DIR)/$(shell date +"%Y-%m-%d")

# if MALTAP_FORCE_RESULT_DIR is set, then we will overwrite the RESULT_DIR, not considering the date
ifdef MALTAP_FORCE_RESULT_DIR
	RESULT_DIR := $(MALTAP_FORCE_RESULT_DIR)
endif

FRAMEWORK_OUTPUT_DIR ?= $(RESULT_DIR)/android_framework
DB_PATH ?= $(RESULT_DIR)/db.sqlite
CACHE_DIR ?= $(RESULT_DIR)/cache
APK_DIR ?= $(shell realpath ${MALTAP_APK_DIR})
LOG_DIR ?= $(RESULT_DIR)/logs
PARALLELISM ?= 8

MALTAPEXTRACT_JAR := MalTapExtract/build/libs/MalTapExtract-1.0-SNAPSHOT.jar

# Phony targets
.PHONY: all pull_framework analyze_framework gather_animations help

all: help

build_maltapextract: $(MALTAPEXTRACT_JAR)

$(MALTAPEXTRACT_JAR): $(wildcard MalTapExtract/src/**/*)
	@echo "Building MalTapExtract"
	@cd MalTapExtract && ./gradlew clean build
	@echo "MalTapExtract JAR built at $(MALTAPEXTRACT_JAR)"

pull_framework: build_maltapextract
	@echo "Pulling framework from device $(DEVICE_SERIAL)"
	@mkdir -p $(FRAMEWORK_OUTPUT_DIR)
	@./pull_framework.sh $(FRAMEWORK_OUTPUT_DIR) $(DEVICE_SERIAL)

analyze_framework: build_maltapextract
	@echo "Analyzing framework"
	@./analyze_framework.sh $(FRAMEWORK_OUTPUT_DIR)/framework-res.apk $(DB_PATH) $(CACHE_DIR)

gather_animations: build_maltapextract
	@echo "Gathering animations"
	@./gather_animations.sh $(CACHE_DIR) $(DB_PATH) $(APK_DIR) $(LOG_DIR) $(PARALLELISM)

analyze_animations:
	@echo "Analyzing animations"
	@./analyze_animations.sh $(DB_PATH) $(LOG_DIR)

help:
	@echo "Makefile targets:"
	@echo "  pull_framework: Pull the framework from $(DEVICE_SERIAL) and store it in $(FRAMEWORK_OUTPUT_DIR)"
	@echo "  analyze_framework: Analyze the framework"
	@echo "  gather_animations: Gather animations from the APKs in $(APK_DIR)"
	@echo "  analyze_animations: Analyze the animations"