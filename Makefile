AUTHOR := thombashi
PACKAGE := sqliteschema
BUILD_DIR := build
BUILD_WORK_DIR := _work
DIST_DIR := $(BUILD_WORK_DIR)/$(PACKAGE)/dist


.PHONY: build
build:
	@rm -rf $(BUILD_WORK_DIR)/
	@mkdir -p $(BUILD_WORK_DIR)/
	@cd $(BUILD_WORK_DIR); \
		git clone https://github.com/$(AUTHOR)/$(PACKAGE).git; \
		cd $(PACKAGE); \
		python setup.py build
	@twine check $(DIST_DIR)/*
	ls $(DIST_DIR)

.PHONY: clean
clean:
	@rm -rf $(PACKAGE)-*.*.*/ \
		$(BUILD_DIR) \
		$(BUILD_WORK_DIR) \
		dist/ \
		$(DOCS_BUILD_DIR) \
		.eggs/ \
		.pytest_cache/ \
		.tox/ \
		**/*/__pycache__/ \
		*.egg-info/

.PHONY: fmt
fmt:
	@black $(CURDIR)
	@isort --apply --recursive

.PHONY: release
release:
	@cd $(BUILD_WORK_DIR)/$(PACKAGE); python setup.py release --sign
	@rm -rf $(BUILD_WORK_DIR)
