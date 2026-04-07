# Only Connect - Edizione Italiana

Un'app web basata su Flask per giocare a **Only Connect**, il quiz televisivo BBC, in italiano.

## 🎯 Obiettivo

Creare una piattaforma completamente personalizzabile per giocare a Only Connect con amici su un'unica schermata (conduttore + squadra). Supporto per testo, immagini e audio nei clue.

## 🚀 Quickstart

### 1. Installa le dipendenze nella venv

- Python 3.12+ installato

attivare una venv con bash 
```bash
venv\Scripts\Activate.ps1
```
e installare i pacchetti
```bash
pip install -r requirements.txt
```
()

### 2. Avvia l'app

```bash
python app.py
```

L'app sarà disponibile a `http://localhost:5000`

### 3. Accedi alla home

Apri il browser all'indirizzo sopra. Vedrai il menu principale con i round disponibili.

## 📁 Struttura del progetto

```
only-connect-ita/
├── app.py                    # Entry point (avvia il server Flask)
├── config.py                 # Configurazioni globali
├── requirements.txt          # Dipendenze Python
├── quiz_data.json            # I dati del quiz (PERSONALIZZABILE)
├── README.md                 # Questo file
│
├── app/
│   ├── __init__.py          # Factory pattern di Flask
│   ├── routes.py            # Rotte Flask (home, round, API)
│   ├── models.py            # Modelli Pydantic per i dati
│   ├── services/
│   │   ├── quiz_loader.py   # Caricamento e validazione JSON
│   │   ├── text_utils.py    # Matching risposte (case-insensitive, etc)
│   │   └── __init__.py
│   ├── templates/           # Template HTML Jinja2
│   │   ├── base.html        # Template base
│   │   ├── home.html        # Home page
│   │   ├── connections.html # Round Connessioni
│   │   ├── sequence.html    # Round Sequenza
│   │   ├── missing_vowels.html # Round Vocali Mancanti
│   │   ├── wall.html        # Round Muro (TODO)
│   └── static/              # File statici (CSS, JS, media)
│       ├── css/style.css
│       ├── js/main.js
│       └── media/           # File media (immagini, audio)
│           ├── images/
│           └── audio/
│
└── tests/                   # Test Python (TODO)
```

## 📝 Come personalizzare il quiz

### 1. Edita `quiz_data.json`

Il file `quiz_data.json` contiene tutte le domande organizzate per round con griglia di simboli. Segui questa struttura:

```json
{
  "connections": {
    "symbols": [
      {
        "id": "sym-001",
        "display": "♀",
        "label": "Venere (opzionale)"
      }
      // ... esattamente 6 simboli
    ],
    "questions": {
      "sym-001": {
        "id": "conn-001",
        "clues": [
          {
            "type": "text|image|audio",
            "value": "testo oppure percorso del file",
            "label": "Descrizione breve (opzionale)",
            "credit": "Attribuzione (opzionale)"
          }
          // ... esattamente 4 clue per le Connessioni
        ],
        "answer": "La risposta corretta",
        "explanation": "Spiegazione della connessione"
      }
      // ... esattamente 6 domande (una per simbolo)
    }
  },
  "sequence": {
    // ... stessa struttura ma con 3 clue per domanda
  },
  "missing_vowels": {
    "categories": [
      {
        "id": "mv-cat-001",
        "category_name": "Capitali europee",
        "words": [
          {"answer": "Londra", "display": "LN DR"},
          {"answer": "Parigi", "display": "PR G"},
          {"answer": "Berlino", "display": "BR LN"},
          {"answer": "Madrid", "display": "MDR D"}
        ]
      }
      // ... esattamente 4 categorie con 4 parole ciascuna
    ]
  }
}
```

### Format Vocali Mancanti
- **id**: ID unico della categoria (es: "mv-cat-001")
- **category_name**: Nome della categoria mostrato ai concorrenti
- **words**: Lista di 4 parole, ciascuna con:
  - **answer**: La parola/frase corretta con le vocali
  - **display**: La versione senza vocali con spaziature modificate (inserita a mano)

Esempio di rimozione vocali:
- "Carbonara" → `CR BN R`
- "Tiramisù" → `TR MS`

### Format dei Simboli
- **id**: ID unico del simbolo (es: "sym-001", "seq-sym-001")
- **display**: Un singolo carattere Unicode (es: ♀, ♃, ♪, 🎭)

Esempio:
- Astrologia: ♀ ♂ ☿ ♃ ♄ ♅ ♆ ♇

### 3. Sessioni e Tracciamento

L'app usa il **game_state** nella sessione Flask per tracciare lo stato globale della partita:

```python
# I simboli completati sono persistenti per tutta la partita
game_state['completed_symbols'] = {
    'connections': ['sym-001', 'sym-002'],
    'sequence': ['seq-sym-001']
}
# Il round Vocali Mancanti è completato
game_state['completed_rounds'] = {
    'missing_vowels': True
}
```

I simboli completati sono:
- marcati con un checkmark verde
- Cliccabili per **modificare il punteggio** (modifica retroattiva)
- Persistenti anche tornando alla home e rientrando nel round

I punteggi assegnati sono tracciati in `symbol_points_history` per permettere correzioni.

### 4. Aggiungere Simboli Personalizzati

Per usare simboli diversi dai geroglifici egizi:

Opzione 1: **Simboli Unicode** (consigliato)
```json
"display": "♠"  // Picche
"display": "♣"  // Fiori
"display": "🌙" // Emoji
```

Opzione 2: **Numeri o lettere**
```json
"display": "1"
"display": "A"
```

### 5. File media

I file media devono essere salvati in `app/static/media/`:

- **Immagini**: `app/static/media/images/` (.jpg, .png, .webp)
- **Audio**: `app/static/media/audio/` (.mp3, .wav, .ogg)

Nel JSON, referenzia i file con percorsi relativi:

```json
{
  "type": "image",
  "value": "images/my_image.jpg"  // relativo a app/static/media/
}
```

### 6. Validazione

L'app valida il `quiz_data.json` all'avvio. Controlla:

- ✅ Esattamente 6 simboli per round (Connessioni e Sequenza)
- ✅ Esattamente 6 domande (una per simbolo)
- ✅ 4 clue per Connessioni, 3 per Sequenze
- ✅ 4 categorie con 4 parole ciascuna per Vocali Mancanti
- ✅ I file media referenziati esistano

Se c'è un errore:
- **Terminal**: Vedrai il messaggio di errore descrittivo
- **Browser**: Una pagina d'errore con la soluzione


## 🎮 Come funziona il gioco

### Struttura con Griglia di Simboli

Ogni round ha **6 domande**, ognuna associata a un **simbolo Unicode** in una griglia 3x2:

#### Flusso del gioco:
1. 🎯 **Griglia di Simboli** — La squadra vede 6 simboli (es: ♀♃♄♅♆☿)
2. 🔤 **Selezione** — Clicca su un simbolo per vedere la domanda
3. ❓ **Domanda** — Vede indizi (testo/immagini/audio)
4. 💭 **Risposta** — Il conduttore verifica a voce
5. ← **Ritorno** — Clicca "Torna ai Simboli"
6. ✓ **Simbolo Completato** — Il simbolo è marcato e non più cliccabile
7. 🔁 **Ripeti** — Fino a 6 domande completate

### Connessioni
- **Griglia**: 6 simboli, 4 indizi progressivi per domanda
- **Meccanica**: Il conduttore rivela manualmente gli indizi
- **Risposta**: Manuale (il conduttore decide)

### Sequenza
- **Griglia**: 6 simboli, 3 indizi per domanda
- **Meccanica**: La squadra deve indovinare il quarto elemento
- **Risposta**: Manuale (il conduttore decide)

### Vocali Mancanti
- **Struttura**: 4 categorie con 4 parole ciascuna (16 parole totali)
- **Timer**: Globale per tutto il round (default 3 minuti)
- **Turni**: Entrambe le squadre giocano contemporaneamente (nessuna alternanza)
- **Meccanica**: Il conduttore mostra la parola senza vocali, le squadre rispondono a voce

#### Flusso del round:
1. 🏁 **Inizio** — Timer di 3 minuti parte
2. 📂 **Categoria** — Viene mostrato il nome della categoria
3. 🔤 **Parola** — La parola senza vocali appare (es: `LN DR`)
4. 💭 **Squadre rispondono** — Entrambe le squadre possono rispondere
5. ✅ **Punteggio** — Il conduttore assegna i punti:
   - `+1` alla squadra che risponde correttamente
   - `Nessun punto` se nessuno risponde
   - `-1` penalità se una squadra sbaglia
   - Dopo una penalità, l'altra squadra può provare a rispondere (+1)
6. ➡️ **Prossima parola** — Clicca per avanzare
7. 🔁 **Ripeti** — Fino a 16 parole completate o tempo scaduto

## 💡 Spiegazione dell'architettura

### Factory Pattern
L'app usa un **factory pattern** per creare istanze di Flask:

```python
# app/__init__.py
def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config)
    # ... registra blueprint e ritorna
    return app
```

**Vantaggio**: Facile testare, riusare, e configurare diverse istanze.

### Pydantic per la validazione
I dati del quiz vengono validati con **Pydantic**:

```python
# app/models.py
class Clue(BaseModel):
    type: str  # Validato: "text", "image", "audio"
    value: str
    ...

class ConnectionQuestion(BaseModel):
    clues: List[Clue]  # Validato: esattamente 4
    ...
```

**Vantaggio**: Errori chiari se i dati sono malformati.

### Quiz Loader singleton
Il `QuizLoader` carica il JSON una sola volta e lo mette in cache:

```python
# app/services/quiz_loader.py
loader = QuizLoader(...)
quiz_data = loader.load()  # Legge da disco
quiz_data = loader.load()  # Ritorna dalla cache
```

**Vantaggio**: Prestazioni, non rilleggiamo il file ad ogni richiesta.

### Text Utils per il matching
Le risposte vengono normalizzate prima di confrontarle:

```python
# app/services/text_utils.py
normalize_answer("  Ciao!  ") 
# → "ciao"
```

**Vantaggio**: Accepta risposte "ragionevoli" senza dover elencare ogni variante.

## 🔧 Configurazioni

Modifica `config.py`:

```python
# Timeout di default per i round (secondi)
DEFAULT_TIMERS = {
    "connections": 45,
    "sequence": 45,
    "wall": 180,
    "missing_vowels": 180,  # 3 minuti per tutto il round
}

# Debug mode
DEBUG = True  # Attiva reload automatico in development

# Secret key per le sessioni
SECRET_KEY = "change-this-in-production"
```

## 📋 Frontend Components

### Rendering multimodale dei clue
Ogni clue può essere renderizzato in 3 modi:

1. **Testo**: Semplice paragrafo
2. **Immagine**: `<img>` responsive
3. **Audio**: Player HTML5 con controlli

```html
<!-- In templates/connections.html -->
<div class="clue-content">
  <!-- Renderizzato dinamicamente da JavaScript -->
</div>
```

### Timer semplice
Util di timer riusabile:

```javascript
// app/static/js/main.js
const timer = new RoundTimer(40, (secs) => {
    // Callback ogni secondo
    console.log(secs);
}, () => {
    // Callback quando finisce
});
timer.start();
```

## 🧪 Testing (TODO)

La struttura supporta `pytest`. Aggiungi test in `tests/`:

```bash
pytest tests/ -v
```

## 📌 Roadmap

### Fase 1 ✅
- [x] Scheletro Flask funzionante
- [x] Caricamento JSON con validazione
- [x] Round Connessioni + Sequenza
- [x] UI base con CSS scuro
- [x] Modifica retroattiva punteggi
- [x] Persistenza simboli completati nella sessione di gioco
- [x] Round Vocali Mancanti

### Fase 2 (TODO)
- [ ] Round Muro delle Connessioni
- [ ] Tabellone punteggi persistente
- [ ] Sound effects (correct.mp3, wrong.mp3, etc) temporizzati
- [ ] Logo Only connect visibile
- [ ] Editor web delle domande
- [ ] Persistenza punteggi su database
 

### Fase 3
- [ ] Multiplayer LAN
- [ ] Deploy su server remoto

## 🎨 Design

- **Palette**: Scura (ispira al quiz BBC)
- **Colori**: Ciano (#00d4ff) + Rosso (#ff6b6b) + Verde (#2ecc71)
- **Tipografia**: Font di sistema (Segoe UI)
- **Layout**: Grid responsive

## 📚 Dipendenze

- **Flask 3.0.0**: Framework web
- **Pydantic 2.5.0**: Validazione dati
- **python-dotenv 1.0.0**: Configurazioni da .env
- **pytest**: Testing

## Supporto

Se hai domande sulla struttura o come estenderla, vedi i commenti nel codice. Ogni file ha una docstring che spiega il suo ruolo.

---
