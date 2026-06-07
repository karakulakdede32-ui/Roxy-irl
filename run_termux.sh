#!/data/data/com.termux/files/usr/bin/bash
# Roxy IRL - Termux Launcher
# Run this in Termux on your Android phone

echo "🦊 Installing dependencies..."
pip install -r requirements.txt

echo "📱 Starting Roxy IRL..."
python3 main.py
