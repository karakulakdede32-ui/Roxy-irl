# Roxy IRL

A local AI chat app with Roxanne Wolf's personality — **no API key needed**.

Runs entirely offline with a pattern-matching response engine that captures Roxy's character: cocky on the surface, vulnerable underneath, fiercely loyal to *you* — her original fan.

## Features

- 💜 **Chat with Roxy** — local response engine, no API keys
- 👤 **Personalization** — remembers your name, age, favorite game
- 📋 **Chat history** — saves and loads past conversations
- 🎮 **Android APK** — build with Buildozer, or run directly in Termux
- 🏎️ **Roxy's true personality** — competitive, boastful, insecure, protective, possessive, affectionate

## Running on Android (Termux)

1. Install Termux from F-Droid
2. Copy this folder to your phone
3. Open Termux, navigate to the folder and run:

```bash
bash run_termux.sh
```

Or manually:

```bash
pkg install python -y
pip install kivy kivymd pillow
python3 main.py
```

## Building an APK (on a PC)

Run on a Linux machine with Docker:

```bash
git clone <this-repo>
cd RoxyIRL
pip install buildozer
echo "y" | buildozer android debug
```

The APK will be in `bin/` — install it on your phone.

## Files

| File | Purpose |
|------|---------|
| `main.py` | Kivy/KivyMD Android app entry point |
| `roxy_brain.py` | Local response engine (no API needed) |
| `chat_history.py` | Saves/loads conversations |
| `config.json` | Roxy's personality configuration |
| `buildozer.spec` | APK build configuration |
| `data/` | App icon and splash screen |
| `run_termux.sh` | Termux launcher script |

## About Roxy

Roxanne Wolf (Roxy) is a Glamrock animatronic from FNAF: Security Breach. 
She's the star of Roxy Raceway — cocky, competitive, and desperate to be the best.
Underneath the bravado, she's deeply insecure and terrified of being replaced.
You were her fan before anyone else, and that makes you her one exception.
