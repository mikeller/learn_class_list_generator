# UC Learn Class List Generator - Build System
# Creates a distributable ZIP file with all necessary components

# Variables
ZIP_NAME = generate_classlist.zip
BUILD_DIR = build
DIST_DIR = $(BUILD_DIR)/generate_classlist

# Files to include in the distribution
CORE_FILES = \
	scraper_python3_self_contained.py \
	portable_scraper.py \
	manual_scraper.py \
	uc_learn_scraper.py \
	requirements.txt \
	GENERATE_CLASSLIST.bat \
	README.txt

DRIVER_FILES = \
	chromedriver.exe \
	geckodriver.exe

# Default target
.PHONY: all
all: $(ZIP_NAME)

# Create the distributable ZIP file
$(ZIP_NAME): $(CORE_FILES) $(DRIVER_FILES)
	@echo "Building distributable package..."
	@mkdir -p $(DIST_DIR)
	@echo "Copying core files..."
	@cp $(CORE_FILES) $(DIST_DIR)/
	@echo "Copying browser drivers..."
	@cp $(DRIVER_FILES) $(DIST_DIR)/
	@echo "Creating ZIP archive..."
	@cd $(BUILD_DIR) && zip -r ../$(ZIP_NAME) generate_classlist/
	@echo "Package created: $(ZIP_NAME)"
	@echo "Size: $$(du -h $(ZIP_NAME) | cut -f1)"

# Clean build artifacts
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR)
	@rm -f $(ZIP_NAME)
	@echo "Clean complete."

# Verify all required files exist
.PHONY: check
check:
	@echo "Checking for required files..."
	@for file in $(CORE_FILES) $(DRIVER_FILES); do \
		if [ ! -f "$$file" ]; then \
			echo "ERROR: Missing file: $$file"; \
			exit 1; \
		else \
			echo "✓ $$file"; \
		fi; \
	done
	@echo "All required files present."

# Show package contents
.PHONY: list
list: $(ZIP_NAME)
	@echo "Contents of $(ZIP_NAME):"
	@unzip -l $(ZIP_NAME)

# Test the package by extracting to temp directory
.PHONY: test
test: $(ZIP_NAME)
	@echo "Testing package extraction..."
	@mkdir -p test_extract
	@cd test_extract && unzip -q ../$(ZIP_NAME)
	@echo "Testing batch file presence..."
	@test -f test_extract/generate_classlist/GENERATE_CLASSLIST.bat || (echo "ERROR: Batch file missing"; exit 1)
	@echo "Testing Python files..."
	@test -f test_extract/generate_classlist/scraper_python3_self_contained.py || (echo "ERROR: Main Python file missing"; exit 1)
	@rm -rf test_extract
	@echo "Package test passed!"

# Show help
.PHONY: help
help:
	@echo "UC Learn Class List Generator - Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  all     - Build the distributable ZIP file (default)"
	@echo "  clean   - Remove build artifacts and ZIP file"
	@echo "  check   - Verify all required files are present"
	@echo "  list    - Show contents of the built ZIP file"
	@echo "  test    - Test the built package by extracting it"
	@echo "  help    - Show this help message"
	@echo ""
	@echo "Output:"
	@echo "  $(ZIP_NAME) - Ready-to-distribute package"

# Make targets that don't create files
.PHONY: all clean check list test help