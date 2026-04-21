"""
Configurazioni dell'app Only Connect.

Questo file centralizza tutte le impostazioni:
- Percorsi ai file
- Timeout di default per i round
- Impostazioni di debug
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cartella radice del progetto
BASE_DIR = Path(__file__).resolve().parent

# Carica le variabili d'ambiente dal file .env
load_dotenv(BASE_DIR / ".env")

# File JSON con i dati del quiz
# Leggi da variabile d'ambiente QUIZ_DATA_FILE, altrimenti usa il default
quiz_file_env = os.getenv("QUIZ_DATA_FILE")
if quiz_file_env:
    quiz_file_path = Path(quiz_file_env)
    # Se è un percorso relativo, risolvilo dalla BASE_DIR
    if not quiz_file_path.is_absolute():
        QUIZ_DATA_FILE = BASE_DIR / quiz_file_path
        QUIZ_DATA_FILE_DISPLAY = quiz_file_env  # Mostra il percorso relativo (es: quiz_files/quiz_storia.json)
    else:
        QUIZ_DATA_FILE = quiz_file_path
        QUIZ_DATA_FILE_DISPLAY = str(quiz_file_path)  # Mostra il percorso assoluto
else:
    QUIZ_DATA_FILE = BASE_DIR / "quiz_data.json"
    QUIZ_DATA_FILE_DISPLAY = "quiz_data.json (default)"

# Cartelle statiche (dove i template cercheranno i media)
MEDIA_DIR = BASE_DIR / "app" / "static" / "media"
IMAGES_DIR = MEDIA_DIR / "images"
AUDIO_DIR = MEDIA_DIR / "audio"

# Timeout default per i round (in secondi)
DEFAULT_TIMERS = {
    "connections": 40,
    "sequence": 40,
    "wall": 150,
    "missing_vowels": 180,
}

# Colori per le righe del Muro delle Connessioni (riga 1, 2, 3, 4)
WALL_ROW_COLORS = [
    "#6A4C93",   # Viola
    "#1982C4",   # Blu
    "#8AC926",   # Verde
    "#FFCA3A",   # Giallo
]

# Modalità debug
DEBUG = os.getenv("FLASK_ENV") == "development"

# Secret key per le sessioni Flask
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-in-production")
