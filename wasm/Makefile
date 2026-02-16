.PHONY: build clean install

GOROOT := $(shell go env GOROOT)
WEB_ASSETS := ../web/src/assets

build:
	GOOS=js GOARCH=wasm go build -o main.wasm

install: build
	@mkdir -p $(WEB_ASSETS)
	cp main.wasm $(WEB_ASSETS)/
	cp $(GOROOT)/misc/wasm/wasm_exec.js $(WEB_ASSETS)/
	cp ../dictionary.db $(WEB_ASSETS)/
	@echo "✓ WASM files copied to $(WEB_ASSETS)"

clean:
	rm -f main.wasm
	rm -f $(WEB_ASSETS)/main.wasm
	rm -f $(WEB_ASSETS)/wasm_exec.js

dev: build
	@echo "Build complete. Serve with: python3 -m http.server 8080"
