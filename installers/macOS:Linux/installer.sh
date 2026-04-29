#!/bin/bash
set -e

echo "🚀 TetOS installer started..."

# ====== CONFIG ======
PROJECT_DIR="$(pwd)"
REPO_URL="https://github.com/AndriiBash/tetOS.git"
TETOS_DIR="$PROJECT_DIR/tetOS"

SERVER_DIR="$TETOS_DIR/server"
SERVER_JAR="$SERVER_DIR/server.jar"
SERVER_URL="https://piston-data.mojang.com/v1/objects/64bb6d763bed0a9f1d632ec347938594144943ed/server.jar"

ENV_FILE="$TETOS_DIR/src/.env"

# ====== CHECKS ======
if ! command -v git >/dev/null; then
    echo "❌ git is not installed"
    exit 1
fi

if ! command -v java >/dev/null; then
    echo "❌ Java is not installed"
    echo "➡️  Please install Java 17+"
    exit 1
fi

if ! command -v python3 >/dev/null; then
    echo "❌ python3 is not installed"
    exit 1
fi

# ====== 1. Clone TetOS ======
if [ ! -d "$TETOS_DIR" ]; then
    echo "📦 Cloning TetOS..."
    git clone "$REPO_URL" "$TETOS_DIR"
else
    echo "🔄 Updating TetOS..."
    cd "$TETOS_DIR"
    git pull
fi

cd "$TETOS_DIR"

# ====== 2. Install Python deps ======
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# ====== 3. Setup server folder ======
mkdir -p "$SERVER_DIR"

# ====== 4. Download server.jar ======
if [ ! -f "$SERVER_JAR" ]; then
    echo "⬇️  Downloading Minecraft server..."
    curl -L "$SERVER_URL" -o "$SERVER_JAR"
fi

# ====== 5. Generate eula.txt ======
if [ ! -f "$SERVER_DIR/eula.txt" ]; then
    echo "🧾 Generating eula.txt..."
    cd "$SERVER_DIR"
    java -jar server.jar || true
    cd "$TETOS_DIR"
fi

# ====== 6. Accept EULA ======
if [ -f "$SERVER_DIR/eula.txt" ]; then
    echo "✅ Accepting EULA..."
    sed -i.bak 's/eula=false/eula=true/' "$SERVER_DIR/eula.txt"
    rm "$SERVER_DIR/eula.txt.bak"
fi

# ====== 7. Create .env ======
ENV_FILE="$TETOS_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "🧪 Creating .env file..."
    echo 'TELEGRAM_TOKEN="PUT_YOUR_TELEGRAM:TOKEN_HERE"' > "$ENV_FILE"
fi

# ====== 8. Clean ======
echo "🧹 Removing installer files..."
rm -rf "$TETOS_DIR/installers"


# ====== DONE ======
echo ""
echo "=========================================="
echo "✅ TetOS installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit Telegram token:"
echo "   nano tetOS/.env"
echo ""
echo "2. Run TetOS:"
echo "   tetOS/run.sh"
echo "=========================================="
