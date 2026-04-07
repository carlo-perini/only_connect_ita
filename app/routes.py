"""
Rotte principali dell'app Flask.

Le rotte Flask gestiscono:
1. Home page
2. Caricamento del quiz
3. Le schermate dei round
4. La griglia di simboli (per Connessioni e Sequenza)
5. La logica di navigazione
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect
from pathlib import Path
import sys

# Aggiungi il parent directory al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.quiz_loader import QuizLoader, QuizLoadError
from app.models import TeamScore, GameState
import config

# Crea un blueprint per le rotte
bp = Blueprint("main", __name__)

# Istanza globale del quiz loader (inizializzata al primo caricamento)
_quiz_loader = None


def get_quiz_loader():
    """
    Ritorna l'istanza di QuizLoader, creandola se necessario.
    
    Questo pattern evita di creare il loader ogni richiesta.
    """
    global _quiz_loader
    if _quiz_loader is None:
        _quiz_loader = QuizLoader(
            quiz_file=config.QUIZ_DATA_FILE,
            media_dir=config.MEDIA_DIR
        )
    return _quiz_loader

def init_game_state():
    """
    Inizializza il game state nella sessione con i dati dei team dal quiz.
    Questa funzione viene chiamata UNA SOLA VOLTA all'inizio della partita.
    """
    try:
        loader = get_quiz_loader()
        quiz_data = loader.load()
        
        teams = quiz_data.teams or []
        teams_scores = [
            TeamScore(team_id=t["id"], team_name=t["name"], score=0).dict()
            for t in teams
        ]
        
        session['game_state'] = {
            'current_team_index': 0,
            'teams_scores': teams_scores,  # Punteggio globale di partita
            'points_assigned_for_current_question': False,
            'completed_rounds': {},  # Traccia quali round sono completati
            'completed_symbols': {},  # Traccia i simboli completati per round (globale per la partita)
            'symbol_points_history': {},  # Traccia i punti assegnati a ciascun simbolo
            'symbol_team_history': {}  # Traccia il team che ha giocato ogni simbolo
        }
        session.modified = True
    except Exception as e:
        print(f"Errore nell'inizializzazione del game state: {str(e)}")


def get_game_state():
    """
    Ritorna il game state dalla sessione, inizializzandolo se necessario.
    NON resetta il punteggio globale.
    """
    if 'game_state' not in session:
        init_game_state()
    return session.get('game_state', {})

@bp.route("/")
def home():
    """Home page dell'app."""
    # Ottieni il game state (con punteggio globale accumulato)
    # I simboli completati rimangono tracciati nella sessione di gioco
    game_state = get_game_state()
    teams_scores = game_state.get('teams_scores', [])
    completed_rounds = game_state.get('completed_rounds', {})
    
    return render_template(
        "home.html",
        teams_scores=teams_scores,
        completed_rounds=completed_rounds
    )


@bp.route("/round/<round_type>/choose-team")
def choose_team(round_type):
    """
    Pagina di scelta del team iniziale.
    Verifica se il round è già completato o già iniziato.
    
    Args:
        round_type: 'connections' o 'sequence'
    """
    if round_type not in ['connections', 'sequence']:
        return "Round non valido", 404
    
    try:
        loader = get_quiz_loader()
        quiz_data = loader.load()
        
        # Ottieni il game state
        game_state = get_game_state()
        completed_rounds = game_state.get('completed_rounds', {})
        completed_symbols = game_state.get('completed_symbols', {})
        
        # Controlla se il round è già completato
        if completed_rounds.get(round_type, False):
            return render_template(
                "round_completed.html",
                round_type=round_type,
                teams_scores=game_state.get('teams_scores', [])
            )
        
        # Controlla se il round è già iniziato (ha simboli completati)
        if round_type in completed_symbols and len(completed_symbols[round_type]) > 0:
            # Il round è già stato iniziato, vai direttamente alla griglia
            return redirect(f"/round/{round_type}/symbols")
        
        # Ottieni i team
        teams = quiz_data.teams or []
        
        return render_template(
            "choose_team.html",
            round_type=round_type,
            teams=teams
        )
    
    except QuizLoadError as e:
        return f"Errore nel caricamento del quiz: {str(e)}", 500


@bp.route("/round/<round_type>/start/<team_id>")
def start_round(round_type, team_id):
    """
    Inizia il round con il team scelto e reindirizza alla griglia dei simboli.
    NON resetta il game state se esiste già (preserva i simboli completati).
    
    Args:
        round_type: 'connections' o 'sequence'
        team_id: ID del team che inizia
    """
    if round_type not in ['connections', 'sequence']:
        return "Round non valido", 404
    
    try:
        loader = get_quiz_loader()
        quiz_data = loader.load()
        
        # Ottieni il game state (crea solo se non esiste)
        game_state = get_game_state()
        teams = quiz_data.teams or []
        
        # Imposta il team iniziale
        team_index = 0
        for i, team in enumerate(teams):
            if team['id'] == team_id:
                team_index = i
                break
        
        game_state['current_team_index'] = team_index
        session['game_state'] = game_state
        session.modified = True
        
        # Reindirizza alla griglia dei simboli
        return jsonify({
            "success": True,
            "redirect": f"/round/{round_type}/symbols"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/quiz")
def api_quiz():
    """
    Endpoint API che ritorna i dati del quiz.
    
    Se il quiz non è disponibile (file mancante o invalido),
    ritorna un errore JSON con messaggio diagnostico.
    """
    try:
        loader = get_quiz_loader()
        quiz_data = loader.load()
        
        # Converti Pydantic model a dict
        # Per il nuovo formato con simboli, ritorniamo la struttura completa
        return jsonify({
            "success": True,
            "data": {
                "connections": quiz_data.connections.dict() if quiz_data.connections else None,
                "sequence": quiz_data.sequence.dict() if quiz_data.sequence else None,
            }
        })
    
    except QuizLoadError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Errore inaspettato: {str(e)}"
        }), 500


@bp.route("/round/<round_type>/symbols")
def round_symbols(round_type):
    """
    Mostra la griglia di 6 simboli per scegliere la domanda.
    
    Args:
        round_type: 'connections' o 'sequence'
    """
    if round_type not in ['connections', 'sequence']:
        return "Round non valido", 404
    
    try:
        loader = get_quiz_loader()
        quiz_data = loader.load()
        
        # Ottieni il round richiesto
        round_data = getattr(quiz_data, round_type, None)
        
        if not round_data:
            return f"Round {round_type} non disponibile", 404
        
        # Prendi i simboli dal round
        symbols = [s.dict() for s in round_data.symbols]
        
        # Ottieni il game state
        game_state = get_game_state()
        
        # Inizializza la lista di simboli completati per questo round (se non esiste)
        if 'completed_symbols' not in game_state:
            game_state['completed_symbols'] = {}
        if round_type not in game_state['completed_symbols']:
            game_state['completed_symbols'][round_type] = []
        
        completed_symbol_ids = game_state['completed_symbols'][round_type]
        
        # Reset del flag per la nuova domanda
        game_state['points_assigned_for_current_question'] = False
        session['game_state'] = game_state
        session.modified = True
        
        # Ottieni il team in turno
        current_team_index = game_state.get('current_team_index', 0)
        teams_scores = game_state.get('teams_scores', [])
        current_team = teams_scores[current_team_index] if current_team_index < len(teams_scores) else None
        
        return render_template(
            "round_symbols.html",
            round_type=round_type,
            symbols=symbols,
            completed_symbol_ids=completed_symbol_ids,
            current_team=current_team,
            game_state=game_state
        )
    
    except QuizLoadError as e:
        return f"Errore nel caricamento del quiz: {str(e)}", 500


@bp.route("/round/<round_type>/<symbol_id>")
def round_question(round_type, symbol_id):
    """
    Mostra la domanda associata a un simbolo.
    
    Args:
        round_type: 'connections' o 'sequence'
        symbol_id: ID del simbolo scelto
    """
    if round_type not in ['connections', 'sequence']:
        return "Round non valido", 404
    
    try:
        loader = get_quiz_loader()
        quiz_data = loader.load()
        
        # Ottieni il round richiesto
        round_data = getattr(quiz_data, round_type, None)
        
        if not round_data:
            return f"Round {round_type} non disponibile", 404
        
        # Trova la domanda associata al simbolo
        if symbol_id not in round_data.questions:
            return "Simbolo non trovato", 404
        
        question = round_data.questions[symbol_id]
        
        # Per Pydantic v2, usiamo model_dump() al posto di dict()
        question_dict = question.dict() if hasattr(question, 'dict') else question.model_dump()
        
        # Ottieni il game state
        game_state = get_game_state()
        teams_scores = game_state.get('teams_scores', [])
        
        # Controlla se il simbolo è già stato giocato (è una modifica)
        is_modification = False
        modification_team = None
        completed_symbols = game_state.get('completed_symbols', {})
        if round_type in completed_symbols and symbol_id in completed_symbols[round_type]:
            is_modification = True
            # Estrai il team che ha giocato per primo da symbol_points_history
            symbol_points_history = game_state.get('symbol_points_history', {})
            if round_type in symbol_points_history and symbol_id in symbol_points_history[round_type]:
                original_team_id = symbol_points_history[round_type][symbol_id].get('original_team_id')
                # Trova il team con questo ID
                for team in teams_scores:
                    if team['team_id'] == original_team_id:
                        modification_team = team
                        break
        
        # Se è una modifica, usa il team originale; altrimenti usa il team alternato
        if is_modification:
            current_team = modification_team
        else:
            current_team_index = game_state.get('current_team_index', 0)
            current_team = teams_scores[current_team_index] if current_team_index < len(teams_scores) else None
        
        template = f"{round_type}.html"
        
        # Ottieni il tempo totale per questo round dal config
        total_time = config.DEFAULT_TIMERS.get(round_type, 45)
        
        return render_template(
            template,
            question=question_dict,
            symbol_id=symbol_id,
            round_type=round_type,
            current_team=current_team,
            game_state=game_state,
            teams_scores=teams_scores,
            total_time=total_time,
            is_modification=is_modification
        )
    
    except QuizLoadError as e:
        return f"Errore nel caricamento del quiz: {str(e)}", 500
    except Exception as e:
        return f"Errore: {str(e)}", 500


@bp.route("/api/mark-symbol-complete", methods=["POST"])
def mark_symbol_complete():
    """
    Segna un simbolo come completato.
    Permette la modifica retroattiva: se un simbolo era già completato,
    non alterna il team (solo salva i nuovi punti).
    
    Richiesta JSON:
        {
            "round_type": "connections",
            "symbol_id": "sym-001"
        }
    
    Ritorna errore 400 se i punti non sono stati ancora assegnati per questa domanda.
    """
    try:
        # Controlla se i punti sono stati assegnati
        game_state = get_game_state()
        if not game_state.get('points_assigned_for_current_question', False):
            return jsonify({
                "success": False, 
                "error": "Devi assegnare i punti prima di tornare ai simboli"
            }), 400
        
        data = request.get_json()
        round_type = data.get("round_type")
        symbol_id = data.get("symbol_id")
        
        if not round_type or not symbol_id:
            return jsonify({"success": False, "error": "Parametri mancanti"}), 400
        
        # Inizializza completed_symbols nel game_state se non esiste
        if 'completed_symbols' not in game_state:
            game_state['completed_symbols'] = {}
        if round_type not in game_state['completed_symbols']:
            game_state['completed_symbols'][round_type] = []
        
        # Controlla se il simbolo era già completato (è una modifica retroattiva)
        is_modification = symbol_id in game_state['completed_symbols'][round_type]
        
        if not is_modification:  # Nuovo simbolo
            game_state['completed_symbols'][round_type].append(symbol_id)
            
            # Alterna il team di turno solo se è la prima volta
            teams_scores = game_state.get('teams_scores', [])
            current_index = game_state.get('current_team_index', 0)
            next_index = (current_index + 1) % len(teams_scores)
            game_state['current_team_index'] = next_index
            
            # Controlla se il round è completato (tutti i 6 simboli)
            if len(game_state['completed_symbols'][round_type]) == 6:
                completed_rounds = game_state.get('completed_rounds', {})
                completed_rounds[round_type] = True
                game_state['completed_rounds'] = completed_rounds
        # Se è una modifica, NON alterniamo il team — solo salviamo i nuovi punti
        
        # Reset del flag per la prossima domanda
        game_state['points_assigned_for_current_question'] = False
        session['game_state'] = game_state
        session.modified = True
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/assign-points", methods=["POST"])
def assign_points():
    """
    Assegna punti a una squadra per la domanda corrente.
    Permette la modifica retroattiva: sottrae i vecchi punti e aggiunge i nuovi.
    
    Richiesta JSON:
        {
            "points": 5,  // 5, 3, 2, 1 per team in turno; 1 per bonus all'altra squadra; 0 per nessun punto
            "team_id": "team-1",  // ID della squadra a cui assegnare i punti (non necessario se points=0)
            "round_type": "connections",  // Tipo di round (per storico)
            "symbol_id": "sym-001"  // ID del simbolo (per storico)
        }
    """
    try:
        data = request.get_json()
        points = data.get("points")
        team_id = data.get("team_id")
        round_type = data.get("round_type")
        symbol_id = data.get("symbol_id")
        
        if points is None:
            return jsonify({"success": False, "error": "Parametri mancanti"}), 400
        
        # Valida i punti
        if points not in [0, 1, 2, 3, 5]:
            return jsonify({"success": False, "error": "Punti non validi"}), 400
        
        # Se points > 0, team_id è obbligatorio
        if points > 0 and not team_id:
            return jsonify({"success": False, "error": "Team ID mancante"}), 400
        
        # Ottieni il game state
        game_state = get_game_state()
        teams_scores = game_state.get('teams_scores', [])
        
        # Traccia la cronologia dei punteggi (per permettere modifiche retroattive)
        symbol_points_history = game_state.get('symbol_points_history', {})
        if round_type and symbol_id:
            if round_type not in symbol_points_history:
                symbol_points_history[round_type] = {}
            
            # Recupera i vecchi punti per questo simbolo (se esiste una modifica)
            old_points_data = symbol_points_history[round_type].get(symbol_id, {})
            old_points = old_points_data.get('points', 0)
            old_team_id = old_points_data.get('team_id', None)
            original_team_id = old_points_data.get('original_team_id', None)  # Team che ha giocato per primo
            
            # Se è una modifica, togli i vecchi punti
            if old_points > 0 and old_team_id:
                for team_score in teams_scores:
                    if team_score['team_id'] == old_team_id:
                        team_score['score'] -= old_points
                        break
            
            # Se è la prima volta, registra il team che ha giocato
            if not original_team_id:
                original_team_id = team_id
            
            # Traccia i nuovi punti
            symbol_points_history[round_type][symbol_id] = {
                'points': points,
                'team_id': team_id,
                'original_team_id': original_team_id  # Team che ha giocato per primo
            }
            game_state['symbol_points_history'] = symbol_points_history
        
        # Trova il team e assegna i nuovi punti
        if points > 0 and team_id:
            for team_score in teams_scores:
                if team_score['team_id'] == team_id:
                    team_score['score'] += points
                    break
        
        # Setta il flag
        game_state['points_assigned_for_current_question'] = True
        session['game_state'] = game_state
        session.modified = True
        
        return jsonify({
            "success": True,
            "teams_scores": teams_scores
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



