.PHONY: all clean test build-cli build-wasm install help

# Default target
all: build-cli

help:
	@echo "Trilingual Dictionary - Build Targets"
	@echo ""
	@echo "  make sample-db    - Generate sample database"
	@echo "  make build-cli    - Build CLI application"
	@echo "  make build-wasm   - Build WebAssembly module"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make install      - Install CLI to /usr/local/bin"
	@echo ""

# Generate sample database
sample-db:
	@echo "Generating sample database..."
	cd data/sample && python3 generate_samples.py

# Build CLI
build-cli:
	@echo "Building CLI..."
	cd cmd/dict && go build -o dict
	@echo "✓ Built: cmd/dict/dict"

# Build WASM
build-wasm:
	@echo "Building WASM..."
	cd wasm && make build
	@echo "✓ Built: wasm/main.wasm"

# Install WASM to web assets
install-wasm: build-wasm
	cd wasm && make install

# Run tests
test:
	@echo "Running Go tests..."
	cd core && go test ./...

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f cmd/dict/dict
	rm -f wasm/main.wasm
	rm -f web/src/assets/main.wasm
	rm -f web/src/assets/wasm_exec.js
	@echo "✓ Cleaned"

# Install CLI to system
install: build-cli
	@echo "Installing to /usr/local/bin..."
	cp cmd/dict/dict /usr/local/bin/dict
	@echo "✓ Installed: /usr/local/bin/dict"

# Development setup
dev-setup: sample-db build-cli
	@echo "Development environment ready!"
	@echo "Try: ./cmd/dict/dict cat"
