# Only Connect - Edizione Italiana

Un'app web basata su Flask per giocare a **Only Connect**, il quiz televisivo BBC, in italiano.

## Istruzioni

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

### 2. Avvia l'app

```bash
python app.py
```

L'app sarà disponibile in locale a `http://localhost:5000`

### 3. Accedi alla home

Apri il browser all'indirizzo sopra.

## 👥 Scelta delle squadre

I nomi e i colori delle squadre si scelgono **dall'interfaccia**, direttamente dalla home page. I valori eventualmente presenti nel JSON del quiz vengono **ignorati** (vedi [Format Squadre](#format-squadre)).

- In alto nella home c'è il tabellone con le due squadre (default: **Team 1** e **Team 2**) e il pulsante **✏️ Modifica squadre**.
- Il pulsante apre una finestra in cui, per ogni squadra, puoi scrivere il **nome** e scegliere un **colore** da una tavolozza.
- Il nome e il colore scelti vengono mantenuti in **tutte le schermate** dove compare la squadra (tabelloni, banner "Di turno", schermata vincitore, ecc.).
- La gestione del punteggio non cambia: le squadre scelte **conservano i punti** per tutta la partita.
- Il pulsante **🔄 Resetta Gioco** azzera punteggi e progressi ma **mantiene** i nomi e i colori scelti. I nomi/colori tornano ai default solo se si cancella la sessione del browser.

> Le scelte sono salvate nella sessione del browser: ogni dispositivo/browser ha le proprie squadre.

## Caricare il Quiz

### Opzione 1: Quiz default (quiz_data.json)
Avvia l'app normalmente:
```bash
python app.py
```
L'app caricherà il file `quiz_data.json`, che è un semplice quiz "placheolder" con dati generati, dalla root del progetto. Questo è il modello per i quiz personalizzati.

### Opzione 2: Quiz personalizzato

**Passo 1:** Vai alla cartella `quiz_files/` nella root del progetto:
```
only_connect_ita/
├── quiz_files/
│   ├── addio_al_zedlibato.json
│   ├── granuzzo_home_edition.json
│   └── medium_difficulty_1.json   ← usa questo come esempio
├── quiz_data.json
├── app.py
└── ...
```

**Passo 2:** Metti il tuo quiz .json in `quiz_files/` seguendo la [struttura personalizzabile](#-come-personalizzare-il-quiz).

**Passo 3:** Crea (o modifica) un file `.env` nella root del progetto e scrivi la riga per selezionare il caricamento del quiz:
```env
QUIZ_DATA_FILE=quiz_files/<nome_quiz>.json
```

**Passo 4:** Avvia l'app:
```bash
python app.py
```

L'app caricherà il file specificato in `.env`.

### Cambiare Quiz al Volo (PowerShell)

Se non vuoi editare `.env` ogni volta, da PowerShell:
```powershell
# Attiva venv
.\venv\Scripts\Activate.ps1

# Imposta la variabile d'ambiente e avvia
$env:QUIZ_DATA_FILE="quiz_files/quiz_geografia.json"
python app.py
```

### Priorità di caricamento
1. Variabile d'ambiente `QUIZ_DATA_FILE` (da `.env` o PowerShell)
2. File `quiz_data.json` nella radice (default)

## 📁 Struttura del progetto

```
only-connect-ita/
├── app.py                    # Entry point (avvia il server Flask)
├── config.py                 # Configurazioni globali
├── requirements.txt          # Dipendenze Python
├── .env                      # Variabili d'ambiente (non versionare)
├── quiz_data.json            # Quiz di default (placeholder)
├── quiz_files/               # Cartella con quiz personalizzati
│   ├── addio_al_zedlibato.json
│   ├── granuzzo_home_edition.json
│   └── medium_difficulty_1.json
├── README.md                 # Questo file
│
├── app/
│   ├── __init__.py           # Factory pattern di Flask
│   ├── routes.py             # Rotte Flask (home, round, API)
│   ├── models.py             # Modelli Pydantic per i dati
│   ├── services/
│   │   ├── __init__.py
│   │   ├── quiz_loader.py    # Caricamento e validazione JSON
│   │   └── text_utils.py     # Matching risposte (case-insensitive, etc)
│   ├── templates/            # Template HTML Jinja2
│   │   ├── base.html         # Template base
│   │   ├── landing.html      # Pagina iniziale
│   │   ├── home.html         # Home con punteggi e round
│   │   ├── choose_team.html  # Scelta squadra
│   │   ├── round_symbols.html    # Griglia simboli
│   │   ├── round_completed.html  # Round completato
│   │   ├── connections.html  # Round Connessioni
│   │   ├── sequence.html     # Round Sequenza
│   │   ├── wall.html         # Round Muro
│   │   ├── wall_symbols.html # Simboli Muro
│   │   ├── missing_vowels.html   # Round Vocali Mancanti
│   │   └── winner.html       # Schermata vincitore
│   └── static/               # File statici (CSS, JS, media)
│       ├── css/style.css
│       ├── js/main.js
│       └── media/            # File media (immagini, audio)
│           ├── images/
│           └── audio/
│
└── tests/
    └── test_models.py        # Test modelli Pydantic
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
    "symbols": [
      // ... esattamente 6 simboli (stessa struttura di connections)
    ],
    "questions": {
      "seq-sym-001": {
        "id": "seq-001",
        "clues": [
          // ... esattamente 3 clue (text, image o audio)
        ],
        "answer": "Il quarto elemento della sequenza",
        "sequence_rule": "Descrizione della regola",
        "explanation": "Spiegazione della sequenza"
      }
      // ... esattamente 6 domande (una per simbolo)
    }
  },
  "wall": {
    "symbols": [
      {"id": "wall-1", "display": "𓃭", "label": "Leone"},
      {"id": "wall-2", "display": "𓈗", "label": "Acqua"}
    ],
    "questions": {
      "wall-1": {
        "groups": [
          {
            "connection": "Tipi di pasta",
            "items": ["Penne", "Fusilli", "Rigatoni", "Farfalle"]
          },
          {
            "connection": "Capitali europee",
            "items": ["Roma", "Berlino", "Madrid", "Lisbona"]
          },
          // ... esattamente 4 gruppi da 4 elementi
        ]
      },
      "wall-2": {
        "groups": [
          // ... seconda griglia del muro
        ]
      }
    }
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
      // ... da 4 a 5 categorie con 4 parole ciascuna
    ]
  }
}
```

### Format Squadre
Le squadre **non** si definiscono più nel JSON: nome e colore si scelgono dalla home (vedi [Scelta delle squadre](#-scelta-delle-squadre)).

- La proprietà `teams` nel JSON è **opzionale** e viene **ignorata**: un quiz può essere caricato anche senza di essa.
- Se presente per compatibilità, non ha alcun effetto sui nomi/colori usati in gioco.

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

### 2. Aggiungere Simboli Personalizzati

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

### 3. File media

I file media devono essere salvati in `app/static/media/`:

- **Immagini**: `app/static/media/images/` (.jpg, .png, .webp)
- **Audio**: `app/static/media/audio/` (.mp3, .wav, .ogg)

Nel JSON, referenzia i file con percorsi relativi:

**Esempio con immagine:**
```json
{
  "type": "image",
  "value": "images/my_image.jpg",  // relativo a app/static/media/
  "label": "Descrizione (opzionale)"
}
```

**Esempio con audio:**
```json
{
  "type": "audio",
  "value": "audio/canzone.mp3",  // relativo a app/static/media/
  "label": "Ascolta questo brano",
  "start_time": 45  // Inizia al 45° secondo (opzionale)
}
```

**Esempio con audio (formato minuti:secondi):**
```json
{
  "type": "audio",
  "value": "audio/canzone.mp3",
  "label": "Ascolta dal minuto 1:30",
  "start_time": "1:30"  // Inizia al minuto 1 e 30 secondi (opzionale)
}
```

**Nota su start_time:**
- Puoi usare secondi come numero: `"start_time": 90` (90 secondi)
- Oppure il formato minuti:secondi: `"start_time": "1:30"` (1 minuto e 30 secondi)
- Se omesso, l'audio parte da 0 (inizio)

**Esempio con testo:**
```json
{
  "type": "text",
  "value": "Testo dell'indizio",
  "label": "Descrizione (opzionale)"
}
```

### 5b. Scaricare audio da YouTube con yt-dlp

Puoi estrarre facilmente l'audio da YouTube direttamente nel progetto:

**Passo 1: Installa yt-dlp** (attiva la venv prima)
```powershell
pip install yt-dlp
```

**Passo 2: Scarica l'audio dalla venv attiva**
```powershell
yt-dlp -f "ba/b" --extract-audio --audio-format mp3 -o "app/static/media/audio/%(title)s.mp3" "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Breakdown del comando:**
- `-f "ba/b"` — Scarica il migliore audio disponibile
- `--extract-audio` — Estrae solo l'audio (scarta il video)
- `--audio-format mp3` — Salva come mp3
- `-o "path/%(title)s.mp3"` — Salva in `audio/` con il titolo del video
- `"https://..."` — Sostituisci con il link YouTube vero

**Esempio pratico:**
```powershell
yt-dlp -f "ba/b" --extract-audio --audio-format mp3 -o "app/static/media/audio/%(title)s.mp3" "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Il file audio sarà salvato direttamente in `app/static/media/audio/` pronto da usare nel JSON! 🎵

### 5c. Formule e notazione matematica (LaTeX)

Puoi usare sintassi **LaTeX** negli indizi (`value`), nelle risposte (`answer`), nelle spiegazioni (`explanation`), nelle regole di sequenza (`sequence_rule`), e nelle connessioni del muro (`connection`). L'app usa [KaTeX](https://katex.org/) per renderizzare le formule nel browser.

#### Delimitatori

| Sintassi | Tipo | Esempio |
|----------|------|---------|
| `$...$` | Inline (nel testo) | `$E = mc^2$` |
| `$$...$$` | Display (blocco centrato) | `$$\int_0^\infty e^{-x} dx = 1$$` |

#### Esempi nel JSON

Bisogna raddoppiare i backslash nei blocchi JSON!

**Indizio con formula inline:**
```json
{
  "type": "text",
  "value": "L'equazione $E = mc^2$ di Einstein",
  "label": "Fisica"
}
```

**Indizio con formula display (blocco):**
```json
{
  "type": "text",
  "value": "$$\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}$$",
  "label": "Serie"
}
```

**Risposta con formula:**
```json
{
  "answer": "$\\pi$ (pi greco)",
  "explanation": "Tutti gli indizi portano a $\\pi \\approx 3.14159$"
}
```

**Connessione del muro con formula:**
```json
{
  "connection": "Costanti matematiche ($e$, $\\pi$, $\\phi$, $\\sqrt{2}$)",
  "items": ["2.718...", "3.14159...", "1.618...", "1.414..."]
}
```

#### Sintassi LaTeX comune

| Cosa | Sintassi | Risultato |
|------|----------|-----------|
| Esponente | `$x^2$` | x² |
| Pedice | `$x_n$` | xₙ |
| Frazione | `$\\frac{a}{b}$` | a/b |
| Radice | `$\\sqrt{x}$` | √x |
| Integrale | `$\\int_a^b f(x) dx$` | ∫ |
| Sommatoria | `$\\sum_{i=1}^n i$` | Σ |
| Lettere greche | `$\\alpha, \\beta, \\gamma, \\pi$` | α, β, γ, π |
| Infinito | `$\\infty$` | ∞ |
| Freccia | `$\\rightarrow$` | → |
| Diverso | `$\\neq$` | ≠ |
| Maggiore uguale | `$\\geq$` | ≥ |
| Matrice | `$\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$` | matrice 2x2 |

> **Nota**: Nel JSON i backslash `\` devono essere raddoppiati: scrivi `\\frac` invece di `\frac`.

Per la lista completa delle funzioni supportate: [KaTeX Supported Functions](https://katex.org/docs/supported)

### 6. Validazione

L'app valida il `quiz_data.json` all'avvio. Controlla:

- ✅ Esattamente 6 simboli per round (Connessioni e Sequenza)
- ✅ Esattamente 6 domande (una per simbolo)
- ✅ 4 clue per Connessioni, 3 per Sequenze
- ✅ 2 simboli per Muro, 2 griglie diverse
- ✅ 4 gruppi da 4 elementi per ogni griglia del Muro
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
5. ← **Ritorno** — Clicca "Torna ai simboli"
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

### Muro delle Connessioni
- **Struttura**: 2 simboli, 2 griglie diverse
- **Griglia**: 4x4 (16 elementi), 4 gruppi da 4 elementi + 1 connessione nascosta
- **Timer**: Globale per tutto il round (default 2.5 minuti)
- **Turni**: Alternati tra le squadre (squadra 1 gioca il primo muro, squadra 2 il secondo)
- **Meccanica**: La squadra deve trovare i 4 gruppi di elementi con una connessione nascosta
- **Punti**: 0-8 punti assegnabili solo alla squadra di turno

#### Flusso del round:
1. 🎯 **Scelta Team** — Seleziona quale team inizia
2. 🔤 **Scelta Simbolo** — Vede 2 simboli corrispondenti a 2 griglie diverse
3. 🏁 **Inizio Griglia** — Clicca "Avvia Round", timer di 2.5 minuti parte
4. 🔗 **Selezione Elementi** — La squadra clicca su 4 elementi per formare un gruppo
5. ✅ **Auto-verifica** — Quando seleziona 4 elementi, il sistema controlla automaticamente:
   - ✓ Se appartengono allo stesso gruppo → Move in alto con `colore-riga-esima` e transizione animata
   - ✗ Se sono elementi diversi → Shake animation (3 tentativi/vite dopo aver trovato 2 gruppi)
6. 📊 **Risultati** — Dopo tutti i 4 gruppi (o fine tempo):
   - Carte con le connessioni rivelabili al click
   - Pulsanti per assegnare 0-8 punti al team di turno
7. ➡️ **Prossimo Simbolo** — Ritorna alla griglia simboli, team alterna
8. 🔁 **Ripeti** — 2 simboli completati (uno per squadra) = round completato

#### Colori per riga (configurabili):
```python
# config.py
WALL_ROW_COLORS = [
    "#6A4C93",   # Viola (riga 1)
    "#1982C4",   # Blu (riga 2)
    "#8AC926",   # Verde (riga 3)
    "#FFCA3A"    # Giallo (riga 4)
]
```

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
- [x] Flask
- [x] Caricamento JSON quiz
- [x] Round Connessioni e sequenza
- [x] UI base con CSS
- [x] Modifica retroattiva punteggi
- [x] Persistenza simboli completati nella sessione di gioco
- [x] Round vocali e immagini
- [x] Round Muro delle connessioni

### Fase 2
- [x] Landing e victory pages
- [x] Musiche per ogni round + sigla inziale
- [x] Sound effects temporizzati
- [x] Formattazione LaTex
- [ ] Immagine come answer da poter inserire nei round di immagini
- [ ] Punteggi scritti sopra le clue card in sequenze e connessioni come nel bbc

### Fase 3
- [ ] Show automatico di tutti i clue a risposta team di turno errata
- [ ] Possibilità di prenotarsi per rispondere in missing vowels
- [ ] Ruoli a scelta per la parita (giocatore/master)
- [ ] Persistenza punteggi su qualche file/DB (non in debug)
- [ ] Editor web delle domande
- [ ] Deploy su server remoto per multiplayer

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
