#!/bin/bash
# Setup script for web application

set -e

echo "Setting up Trilingual Dictionary Web App..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✓ Node.js found: $(node --version)"

# Install dependencies
echo ""
echo "Installing npm dependencies..."
npm install

# Create assets directory if it doesn't exist
mkdir -p src/assets

# Copy database
echo ""
echo "Copying dictionary database..."
if [ -f ../dictionary.db ]; then
    cp ../dictionary.db src/assets/
    echo "✓ Database copied to src/assets/"
else
    echo "❌ Database not found. Run: cd ../data/sample && python3 generate_samples.py"
    exit 1
fi

# Copy SQL.js WASM file
echo ""
echo "Copying SQL.js WASM file..."
if [ -f node_modules/sql.js/dist/sql-wasm.wasm ]; then
    cp node_modules/sql.js/dist/sql-wasm.wasm src/assets/
    echo "✓ SQL.js WASM copied to src/assets/"
else
    echo "⚠️  SQL.js WASM not found in node_modules. Will be loaded from CDN."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start development server: npm start"
echo "  2. Open browser to: http://localhost:4200"
echo "  3. Build for production: ng build --configuration production"
echo ""
