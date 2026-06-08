#!/data/data/com.termux/files/usr/bin/bash
# Roxy IRL — Full Ollama setup for Termux (Android)
# This gives Roxy a REAL local AI brain running on your phone!
# Run: bash setup_ollama.sh

set -e

echo "================================================"
echo "  🦊 Roxy IRL — Local AI Setup"
echo "================================================"
echo ""

# Install Ollama
if ! command -v ollama &> /dev/null; then
    echo "📥 Downloading Ollama for ARM64..."
    curl -L https://ollama.com/download/ollama-linux-arm64 -o $PREFIX/bin/ollama
    chmod +x $PREFIX/bin/ollama
    echo "✅ Ollama installed!"
else
    echo "✅ Ollama already installed"
fi

# Kill any existing Ollama
pkill ollama 2>/dev/null || true

# Start Ollama
echo "🚀 Starting Ollama server..."
ollama serve &
sleep 3

# Install Python deps
echo "📦 Installing Python packages..."
pip install kivy kivymd requests 2>/dev/null || pip3 install kivy kivymd requests

echo ""
echo "================================================"
echo "  📋 Pick a model to download:"
echo "================================================"
echo ""
echo "  🏆 BEST ROLEPLAY (needs ~6GB RAM):"
echo "     [1] dolphin-llama3:8b  (4.5GB) ★★★★★"
echo ""
echo "  ⭐ GREAT ALL-ROUNDER (needs ~3GB RAM):"
echo "     [2] llama3.2:3b        (2GB)  ★★★★"
echo "     [3] qwen2.5:3b         (2GB)  ★★★★"
echo ""
echo "  ✅ FAST & LIGHT (works on any phone):"
echo "     [4] llama3.2:1b        (800MB) ★★★"
echo "     [5] tinyllama          (700MB) ★★★"
echo "     [6] qwen2.5:1.5b       (1GB)  ★★★★"
echo ""
echo "  [0] Skip, I'll pick later"
echo ""

read -p "  Choose (0-6): " choice

case $choice in
    1) MODEL="dolphin-llama3:8b" ;;
    2) MODEL="llama3.2:3b" ;;
    3) MODEL="qwen2.5:3b" ;;
    4) MODEL="llama3.2:1b" ;;
    5) MODEL="tinyllama" ;;
    6) MODEL="qwen2.5:1.5b" ;;
    *) MODEL="" ;;
esac

if [ -n "$MODEL" ]; then
    echo ""
    echo "📦 Downloading $MODEL..."
    echo "   This may take a few minutes depending on model size."
    ollama pull "$MODEL"
    echo "✅ Model downloaded!"
fi

echo ""
echo "================================================"
echo "  ✅ Setup complete!"
echo "================================================"
echo ""
echo "  Run Roxy:  python3 main.py"
echo ""
echo "  To manage models later:"
echo "    ollama list              # List installed models"
echo "    ollama pull <model>      # Download a model"
echo "    ollama remove <model>    # Delete a model"
echo ""
echo "  Or manage models from inside the app:"
echo "    Settings -> AI Models"
echo ""
