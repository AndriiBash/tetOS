#!/bin/sh
set -e

echo "🚀 Starting TetOS..."

# Go to project root (important if script is run from elsewhere)
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# 1. Check python3
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Error: python3 is not installed."
    echo "➡️  Please install Python 3 first."
    exit 1
fi

# 2. Check server directory
if [ ! -d "server" ]; then
    echo "❌ Error: 'server/' directory not found."
    echo "➡️  Please create it and place server.jar inside:"
    echo " mkdir server"
    exit 1
fi

# 3. Check server.jar
if [ ! -f "server/server.jar" ]; then
    echo "❌ Error: server/server.jar not found."
    echo "➡️  Download Minecraft server and place it here:"
    echo "    server/server.jar"
    exit 1
fi

# 4. Check Python dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Checking Python dependencies..."
    pip3 install -r requirements.txt >/dev/null 2>&1 || {
        echo "❌ Error: Failed to install Python dependencies."
        exit 1
    }
else
    echo "⚠️  Warning: requirements.txt not found, skipping dependency check."
fi

# 5. Run TetOS
echo "✅ All checks passed."
echo "▶️  Launching TetOS..."

python3 src/python_scripts/main.py
