AUTHOR := thombashi
PACKAGE := sqliteschema
BUILD_WORK_DIR := _work
DIST_DIR := $(BUILD_WORK_DIR)/$(PACKAGE)/dist


.PHONY: build
build:
	@rm -rf $(BUILD_WORK_DIR)/
	@mkdir -p $(BUILD_WORK_DIR)/
	@cd $(BUILD_WORK_DIR); \
		git clone https://github.com/$(AUTHOR)/$(PACKAGE).git; \
		cd $(PACKAGE); \
		python setup.py sdist bdist_wheel
	@twine check $(DIST_DIR)/*
	ls -lh $(DIST_DIR)/*

.PHONY: clean
clean:
	@tox -e clean

.PHONY: fmt
fmt:
	@black $(CURDIR)
	@autoflake --in-place --recursive --remove-all-unused-imports --exclude "__init__.py" .
	@isort --apply --recursive

.PHONY: release
release:
	@cd $(BUILD_WORK_DIR)/$(PACKAGE); python setup.py release --sign
	@make clean
