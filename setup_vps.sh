#!/bin/bash
# ==============================================================
# One-Click VPS Setup Script for Telegram DRM Bot
# Supports Ubuntu 20.04 / 22.04 / 24.04 & Debian 10 / 11 / 12
# ==============================================================

set -e

echo "=============================================="
echo " Starting Telegram DRM Bot VPS Setup "
echo "=============================================="

# 1. Update packages
echo "[1/6] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Install essential system packages
echo "[2/6] Installing dependencies (python, ffmpeg, aria2, cmake, etc.)..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    ffmpeg \
    aria2 \
    mediainfo

# 3. Build & Install Bento4 (for mp4decrypt)
if ! command -v mp4decrypt &> /dev/null; then
    echo "[3/6] Installing Bento4 (mp4decrypt)..."
    TMP_DIR=$(mktemp -d)
    git clone https://github.com/axiomatic-systems/Bento4.git "$TMP_DIR/Bento4"
    cd "$TMP_DIR/Bento4"
    mkdir cmakebuild
    cd cmakebuild
    cmake -DCMAKE_BUILD_TYPE=Release ..
    make -j$(nproc)
    sudo make install
    rm -rf "$TMP_DIR"
    echo "Bento4 installed successfully!"
else
    echo "[3/6] Bento4 (mp4decrypt) is already installed."
fi

# Return to script directory
cd "$(dirname "$0")"

# 4. Setup Python Virtual Environment
echo "[4/6] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 5. Make scripts executable
echo "[5/6] Setting script permissions..."
chmod +x start.sh setup_vps.sh

# 6. Check for .env file
echo "[6/6] Checking configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.sample" ]; then
        cp .env.sample .env
        echo "Created .env file from .env.sample."
    fi
    echo "⚠️  IMPORTANT: Please edit .env file with your BOT_TOKEN, API_ID, and API_HASH before starting!"
    echo "Run: nano .env"
else
    echo "✅ .env file exists."
fi

echo "=============================================="
echo " Setup Completed Successfully!"
echo "=============================================="
echo "To start the bot manually:"
echo "  source venv/bin/activate && python3 main.py"
echo ""
echo "Or using the start script:"
echo "  ./start.sh"
echo "=============================================="

