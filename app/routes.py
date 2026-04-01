"""
Rotte principali dell'app Flask.

Le rotte Flask gestiscono:
1. Home page
2. Caricamento del quiz
3. Le schermate dei round
4. La griglia di simboli (per Connessioni e Sequenza)
5. La logica di navigazione
"""

from flask import Blueprint, render_template, request, jsonify, session
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
            'teams_scores': teams_scores,
            'points_assigned_for_current_question': False
        }
        session.modified = True
    except Exception as e:
        print(f"Errore nell'inizializzazione del game state: {str(e)}")


def get_game_state():
    """
    Ritorna il game state dalla sessione, inizializzandolo se necessario.
    """
    if 'game_state' not in session:
        init_game_state()
    return session.get('game_state', {})

@bp.route("/")
def home():
    """Home page dell'app."""
    # Pulisci la sessione dalle domande precedenti e reset game state
    session.pop('completed_symbols', None)
    session.pop('game_state', None)
    
    return render_template("home.html")


@bp.route("/round/<round_type>/choose-team")
def choose_team(round_type):
    """
    Pagina di scelta del team iniziale.
    
    Args:
        round_type: 'connections' o 'sequence'
    """
    if round_type not in ['connections', 'sequence']:
        return "Round non valido", 404
    
    try:
        loader = get_quiz_loader()
        quiz_data = loader.load()
        
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
    
    Args:
        round_type: 'connections' o 'sequence'
        team_id: ID del team che inizia
    """
    if round_type not in ['connections', 'sequence']:
        return "Round non valido", 404
    
    try:
        loader = get_quiz_loader()
        quiz_data = loader.load()
        
        # Inizializza il game state
        init_game_state()
        
        # Imposta il team iniziale
        game_state = get_game_state()
        teams = quiz_data.teams or []
        
        # Trova l'indice del team scelto
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
        
        # Inizializza la sessione con i simboli completati
        if 'completed_symbols' not in session:
            session['completed_symbols'] = {}
        if round_type not in session['completed_symbols']:
            session['completed_symbols'][round_type] = []
        
        # Ottieni il game state
        game_state = get_game_state()
        
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
            completed_symbol_ids=session['completed_symbols'][round_type],
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
        current_team_index = game_state.get('current_team_index', 0)
        teams_scores = game_state.get('teams_scores', [])
        current_team = teams_scores[current_team_index] if current_team_index < len(teams_scores) else None
        
        template = f"{round_type}.html"
        
        return render_template(
            template,
            question=question_dict,
            symbol_id=symbol_id,
            round_type=round_type,
            current_team=current_team,
            game_state=game_state,
            teams_scores=teams_scores
        )
    
    except QuizLoadError as e:
        return f"Errore nel caricamento del quiz: {str(e)}", 500
    except Exception as e:
        return f"Errore: {str(e)}", 500


@bp.route("/api/mark-symbol-complete", methods=["POST"])
def mark_symbol_complete():
    """
    Segna un simbolo come completato.
    
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
        
        if 'completed_symbols' not in session:
            session['completed_symbols'] = {}
        if round_type not in session['completed_symbols']:
            session['completed_symbols'][round_type] = []
        
        if symbol_id not in session['completed_symbols'][round_type]:
            session['completed_symbols'][round_type].append(symbol_id)
            
            # Alterna il team di turno
            teams_scores = game_state.get('teams_scores', [])
            current_index = game_state.get('current_team_index', 0)
            next_index = (current_index + 1) % len(teams_scores)
            game_state['current_team_index'] = next_index
            
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
    
    Richiesta JSON:
        {
            "points": 5,  // 5, 3, 2, 1 per team in turno; 1 per bonus all'altra squadra
            "team_id": "team-1"  // ID della squadra a cui assegnare i punti
        }
    """
    try:
        data = request.get_json()
        points = data.get("points")
        team_id = data.get("team_id")
        
        if points is None or not team_id:
            return jsonify({"success": False, "error": "Parametri mancanti"}), 400
        
        # Valida i punti
        if points not in [0, 1, 2, 3, 5]:
            return jsonify({"success": False, "error": "Punti non validi"}), 400
        
        # Ottieni il game state
        game_state = get_game_state()
        teams_scores = game_state.get('teams_scores', [])
        
        # Trova il team e assegna i punti
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



