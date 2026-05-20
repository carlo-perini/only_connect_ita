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
    QUIZ_DATA_FILE = BASE_DIR / "quiz_files" / "medium_difficulty_1.json"
    QUIZ_DATA_FILE_DISPLAY = "quiz_data.json (default)"

# Cartelle statiche (dove i template cercheranno i media)
MEDIA_DIR = BASE_DIR / "app" / "static" / "media"
IMAGES_DIR = MEDIA_DIR / "images"
AUDIO_DIR = MEDIA_DIR / "audio"

# Timeout default per i round (in secondi)
DEFAULT_TIMERS = {
    "connections": 40,
    "sequence": 40,
    "wall": 10, # 150
    "missing_vowels": 30, # 180
}

# Colori per le righe del Muro delle Connessioni (riga 1, 2, 3, 4)
WALL_ROW_COLORS = [
    "#6A4C93",   # Viola
    "#1982C4",   # Blu
    "#8AC926",   # Verde
    "#FFCA3A",   # Giallo
]

# Frase di benvenuto nella pagina iniziale
LANDING_SUBTITLE = "Se i quiz fossero ostacoli da superare, le domande che potete trovare in un quiz orario pre-cena sarebbero lo scalino prima del portone di casa. Le domande di Only connect, invece, la cordigliera delle Ande. Per il lungo."

# ==================== TUTORIAL ====================
# Dati di esempio per i tutorial (un round per tipo di gioco)

TUTORIAL_CONNECTIONS = {
    "id": "tutorial-conn",
    "clues": [
        {"type": "text", "value": "Ago"},
        {"type": "text", "value": "Volante"},
        {"type": "text", "value": "Pagliaccio"},
        {"type": "text", "value": "Palla"}
    ],
    "answer": "Pesce ___",
    "explanation": "Sono diverse specie di pesce"
}

TUTORIAL_SEQUENCE = {
    "id": "tutorial-seq",
    "clues": [
        {"type": "text", "value": "7 marzo 2021"},
        {"type": "text", "value": "3 luglio 2021"},
        {"type": "text", "value": "22 gennaio 2022"}
    ],
    "answer": "11 febbraio 2022",
    "sequence_rule": "Date come moltiplicazione",
    "explanation": "7 marzo 2021 --> 7 x 3 = 21, 3 luglio 2021 --> 3 x 7 = 21, 22 gennaio 2022 --> 22 x 1 = 22; la prossima combinazione è 11 x 2 = 22"
}

TUTORIAL_WALL = {
    "groups": [
        {"connection": "Composte da opposti", "items": ["Agrodolce", "Pianoforte", "Chiaroscuro", "Saliscendi"]},
        {"connection": "Mosse nello scacchi", "items": ["Arrocco", "Barbiere", "Difesa olandese", "Apertura"]},
        {"connection": "Nei segnali stradali", "items": ["Pedone", "Punto esclamativo", "Bicicletta", "Freccia"]},
        {"connection": "Elementi di scrittura musicale", "items": ["Legatura", "Chiave", "Battuta", "Scala"]}
    ]
}

TUTORIAL_MISSING_VOWELS = {
    "categories": [
        {
            "id": "tut-mv-1",
            "category_name": "Puoi trovare in bagno...",
            "words": [
                {"answer": "Saponetta", "display": "SP NTT"},
                {"answer": "Spazzolino", "display": "S PZ ZLN"},
                {"answer": "Telefono", "display": "TLFN"},
                {"answer": "Rasoio", "display": "R S"}
            ]
        }
    ]
}

# Modalità debug
DEBUG = os.getenv("FLASK_ENV") == "development"

# Secret key per le sessioni Flask
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-in-production")
