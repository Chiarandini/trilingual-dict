#!/bin/bash
# Install trilingual dictionary CLI globally

set -e

echo "Installing trilingual dictionary CLI..."

# Build the binary
echo "Building CLI binary..."
cd cmd/dict
go build -o dict
cd ../..

# Create install directory
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Copy binary
echo "Installing to $INSTALL_DIR/dict..."
cp cmd/dict/dict "$INSTALL_DIR/dict"
chmod +x "$INSTALL_DIR/dict"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "⚠️  $INSTALL_DIR is not in your PATH"
    echo ""
    echo "Add this to your ~/.zshrc or ~/.bashrc:"
    echo ""
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Then run: source ~/.zshrc"
else
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "You can now run: dict <word>"
fi
