#!/data/data/com.termux/files/usr/bin/bash
# Roxy IRL — Ollama setup for Termux (Android)
# This gives Roxy a REAL local AI brain running on your phone!

echo "🦊 Installing Ollama for Roxy IRL..."
echo ""

# Install Ollama in Termux
echo "📥 Downloading Ollama..."
curl -L https://ollama.com/download/ollama-linux-arm64 -o $PREFIX/bin/ollama
chmod +x $PREFIX/bin/ollama

# Start Ollama server in background
echo "🚀 Starting Ollama server..."
ollama serve &
sleep 3

# Download a small model (tinyllama is ~700MB, runs on most phones)
echo ""
echo "📦 Downloading AI model (this is the big one)..."
echo "    TinyLlama (~700MB) — fast, runs on any phone"
echo "    or use 'ollama pull llama3.2:1b' for Meta's model"
echo ""
ollama pull tinyllama

echo ""
echo "✅ Done! Roxy will now use real AI!"
echo "   Start the chat app with: python3 main.py"
echo ""
echo "📝 NOTE: Run 'ollama serve' before starting the app"
echo "   Add it to your Termux startup if you want it automatic"
