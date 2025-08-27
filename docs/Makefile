# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Build HTML documentation
html:
	@echo "Building HTML documentation..."
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "✅ HTML documentation built successfully!"

# Build PDF documentation
pdf:
	@echo "Building PDF documentation..."
	@$(SPHINXBUILD) -M latexpdf "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "✅ PDF documentation built successfully!"

# Build Markdown documentation
markdown:
	@echo "Building Markdown documentation..."
	@$(SPHINXBUILD) -M markdown "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "✅ Markdown documentation built successfully!"

# Build text documentation
text:
	@echo "Building text documentation..."
	@$(SPHINXBUILD) -M text "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "✅ Text documentation built successfully!"

# Build all documentation formats
all: html pdf markdown text
	@echo "✅ All documentation formats built successfully!"

# Clean build directory
clean:
	@echo "Cleaning build directory..."
	@rm -rf "$(BUILDDIR)"
	@echo "✅ Build directory cleaned!"

# Clean and rebuild
rebuild: clean html
	@echo "✅ Documentation rebuilt successfully!"

# Install dependencies
install-deps:
	@echo "Installing documentation dependencies..."
	@pip install sphinx sphinx-rtd-theme myst-parser sphinx-markdown-builder
	@echo "✅ Dependencies installed successfully!"

# Check documentation
check:
	@echo "Checking documentation..."
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "✅ Documentation check completed!"

# Serve documentation locally
serve:
	@echo "Starting local documentation server..."
	@cd "$(BUILDDIR)/html" && python -m http.server 8000
	@echo "🌐 Documentation available at http://localhost:8000"

# Quick build (HTML only, no warnings)
quick:
	@echo "Building HTML documentation (quick mode)..."
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" -W --keep-going $(O)
	@echo "✅ Quick build completed!"

# Development build with auto-reload
dev:
	@echo "Starting development server with auto-reload..."
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "🔄 Starting auto-reload server..."
	@cd "$(BUILDDIR)/html" && python -m http.server 8000

# Build and open in browser (macOS)
open: html
	@echo "Opening documentation in browser..."
	@open "$(BUILDDIR)/html/index.html"

# Build and open in browser (Linux)
open-linux: html
	@echo "Opening documentation in browser..."
	@xdg-open "$(BUILDDIR)/html/index.html"

# Build and open in browser (Windows)
open-windows: html
	@echo "Opening documentation in browser..."
	@start "$(BUILDDIR)/html/index.html"

# Show build status
status:
	@echo "Documentation build status:"
	@echo "  Source directory: $(SOURCEDIR)"
	@echo "  Build directory: $(BUILDDIR)"
	@echo "  Sphinx build: $(SPHINXBUILD)"
	@if [ -d "$(BUILDDIR)" ]; then \
		echo "  Build directory exists: ✅"; \
		echo "  Build contents:"; \
		ls -la "$(BUILDDIR)"; \
	else \
		echo "  Build directory exists: ❌"; \
	fi

# Default target
.DEFAULT_GOAL := help

# Phony targets
.PHONY: help html pdf markdown text all clean rebuild install-deps check serve quick dev open open-linux open-windows status 