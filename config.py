"""
Configurazioni dell'app Only Connect.

Questo file centralizza tutte le impostazioni:
- Percorsi ai file
- Timeout di default per i round
- Impostazioni di debug
"""

import os
from pathlib import Path

# Cartella radice del progetto
BASE_DIR = Path(__file__).resolve().parent

# File JSON con i dati del quiz
QUIZ_DATA_FILE = BASE_DIR / "quiz_data.json"

# Cartelle statiche (dove i template cercheranno i media)
MEDIA_DIR = BASE_DIR / "app" / "static" / "media"
IMAGES_DIR = MEDIA_DIR / "images"
AUDIO_DIR = MEDIA_DIR / "audio"

# Timeout default per i round (in secondi)
DEFAULT_TIMERS = {
    "connections": 40,
    "sequence": 40,
    "wall": 180,
    "missing_vowels": 180,
}

# Modalità debug
DEBUG = os.getenv("FLASK_ENV") == "development"

# Secret key per le sessioni Flask
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-in-production")
