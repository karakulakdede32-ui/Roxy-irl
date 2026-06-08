"""
Model Manager — handles Ollama for local AI on Android.
Lets you browse, download, and switch between models (including RP models).
"""

import json
import os
import threading
import time

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ── Curated model list with roleplay ratings ───────────────────────────
RECOMMENDED_MODELS = [
    {
        "name": "llama3.2:1b",
        "size": "~800MB",
        "ram": "~1GB",
        "rp_rating": "★★★☆☆",
        "desc": "Meta's latest — fast, ok for roleplay, runs on any phone",
        "speed": "Very Fast",
    },
    {
        "name": "llama3.2:3b",
        "size": "~2GB",
        "ram": "~3GB",
        "rp_rating": "★★★★☆",
        "desc": "Best quality-for-size. Great roleplay, needs 3GB RAM",
        "speed": "Fast",
    },
    {
        "name": "qwen2.5:1.5b",
        "size": "~1GB",
        "ram": "~2GB",
        "rp_rating": "★★★★☆",
        "desc": "Excellent for its size! Strong roleplay, Chinese model",
        "speed": "Fast",
    },
    {
        "name": "qwen2.5:3b",
        "size": "~2GB",
        "ram": "~3GB",
        "rp_rating": "★★★★☆",
        "desc": "Very smart, good RP. One of the best small models",
        "speed": "Medium",
    },
    {
        "name": "tinyllama:latest",
        "size": "~700MB",
        "ram": "~1GB",
        "rp_rating": "★★★☆☆",
        "desc": "Smallest decent model. Runs on anything, basic RP",
        "speed": "Very Fast",
    },
    {
        "name": "dolphin-llama3:8b",
        "size": "~4.5GB",
        "ram": "~6GB",
        "rp_rating": "★★★★★",
        "desc": "BEST for roleplay! Fine-tuned for uncensored RP",
        "speed": "Slow (needs 6GB RAM)",
    },
    {
        "name": "mistral:7b",
        "size": "~4GB",
        "ram": "~5GB",
        "rp_rating": "★★★★☆",
        "desc": "Solid all-rounder. Good RP, widely used",
        "speed": "Slow (needs 5GB RAM)",
    },
    {
        "name": "phi3:mini",
        "size": "~2.5GB",
        "ram": "~3GB",
        "rp_rating": "★★★☆☆",
        "desc": "Microsoft's 3.8B model. Smart but stiff RP",
        "speed": "Medium",
    },
]


class ModelManager:
    """Communicates with Ollama to manage and use local AI models."""

    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.available = False
        self.installed_models = []
        self.active_model = None
        self.error = None
        self._check_lock = threading.Lock()

        if HAS_REQUESTS:
            threading.Thread(target=self.refresh, daemon=True).start()

    def refresh(self):
        """Check Ollama status and list installed models."""
        with self._check_lock:
            try:
                r = requests.get(f"{self.base_url}/api/tags", timeout=3)
                if r.status_code == 200:
                    data = r.json()
                    self.installed_models = [
                        {"name": m["name"], "size": m.get("size", 0)}
                        for m in data.get("models", [])
                    ]
                    self.available = True
                    self.error = None
                    if self.installed_models and not self.active_model:
                        self.active_model = self.installed_models[0]["name"]
                else:
                    self.available = False
                    self.error = "Ollama not responding"
            except requests.ConnectionError:
                self.available = False
                self.error = "Ollama not installed / not running"
            except Exception as e:
                self.available = False
                self.error = str(e)

    def set_model(self, model_name):
        """Switch the active model."""
        self.active_model = model_name

    def generate(self, prompt, temperature=0.85, max_tokens=200, timeout=60):
        """Generate a response using the active model."""
        if not self.available or not self.active_model:
            raise Exception("No Ollama model available")

        r = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.active_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            },
            timeout=timeout,
        )

        if r.status_code == 200:
            return r.json().get("response", "").strip()
        raise Exception(f"Ollama error: {r.status_code}")

    def pull_model(self, model_name, progress_callback=None):
        """Download a model. Progress callback gets {'status': str, 'completed': int, 'total': int}."""
        if not HAS_REQUESTS:
            raise Exception("requests library not available")

        try:
            r = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name, "stream": True},
                stream=True,
                timeout=5,
            )

            if r.status_code != 200:
                raise Exception(f"Pull failed: {r.status_code}")

            for line in r.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if progress_callback:
                            progress_callback(data)
                        if data.get("status") == "success":
                            self.refresh()
                            self.active_model = model_name
                            return True
                    except json.JSONDecodeError:
                        pass

            return False
        except Exception as e:
            raise Exception(f"Failed to pull model: {e}")

    def delete_model(self, model_name):
        """Remove an installed model."""
        if not HAS_REQUESTS:
            return False
        try:
            r = requests.delete(
                f"{self.base_url}/api/delete",
                json={"name": model_name},
                timeout=10,
            )
            if r.status_code == 200:
                self.refresh()
                return True
            return False
        except Exception:
            return False

    def get_status_text(self):
        """Human-readable status."""
        if not HAS_REQUESTS:
            return "requests not installed"
        if not self.available:
            return self.error or "Ollama unavailable"
        models = len(self.installed_models)
        active = self.active_model or "none"
        return f"Active: {active} | {models} model(s) installed"
