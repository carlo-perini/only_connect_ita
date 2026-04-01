"""
Servizio di caricamento del file quiz_data.json.

Responsabilità:
1. Leggere il JSON da file
2. Validare la struttura con Pydantic
3. Verificare che i file media referenziati esistano
4. Sollevare errori chiari se qualcosa non va
5. Mettere in cache i dati caricati per non rileggere da disco ogni richiesta
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from app.models import QuizData, Clue


class QuizLoadError(Exception):
    """Eccezione personalizzata per errori nel caricamento del quiz."""
    pass


class QuizLoader:
    """Carica e valida i dati del quiz da file JSON."""
    
    def __init__(self, quiz_file: Path, media_dir: Path):
        """
        Inizializza il loader.
        
        Args:
            quiz_file: Path al file quiz_data.json
            media_dir: Path alla cartella dei media
        """
        self.quiz_file = Path(quiz_file)
        self.media_dir = Path(media_dir)
        self._cache: Optional[QuizData] = None
    
    def load(self, force_reload: bool = False) -> QuizData:
        """
        Carica i dati del quiz da file.
        
        Args:
            force_reload: Se True, ri-carica da file anche se in cache
        
        Returns:
            QuizData validato e con file media verificati
        
        Raises:
            QuizLoadError: Se il file non esiste, non è valido JSON, o la struttura non è valida
        """
        # Se già in cache, ritorna quello (a meno che non si richieda reload)
        if self._cache is not None and not force_reload:
            return self._cache
        
        # Verifica che il file esista
        if not self.quiz_file.exists():
            raise QuizLoadError(
                f"File quiz non trovato: {self.quiz_file}\n"
                f"Assicurati di creare quiz_data.json nella cartella radice."
            )
        
        # Leggi il file JSON
        try:
            with open(self.quiz_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except json.JSONDecodeError as e:
            raise QuizLoadError(
                f"quiz_data.json non è un JSON valido.\n"
                f"Errore: {e}"
            )
        except Exception as e:
            raise QuizLoadError(
                f"Errore nella lettura di quiz_data.json: {e}"
            )
        
        # Valida con Pydantic
        try:
            quiz_data = QuizData(**raw_data)
        except Exception as e:
            raise QuizLoadError(
                f"Struttura di quiz_data.json non valida.\n"
                f"Errore: {e}"
            )
        
        # Verifica che tutti i file media referenziati esistano
        self._validate_media_files(quiz_data)
        
        # Metti in cache e ritorna
        self._cache = quiz_data
        return quiz_data
    
    def _validate_media_files(self, quiz_data: QuizData) -> None:
        """
        Verifica che tutti i clue di tipo 'image' e 'audio' referenzino file che esistono.
        
        Args:
            quiz_data: I dati del quiz da verificare
        
        Raises:
            QuizLoadError: Se un file media non esiste
        """
        all_questions = []
        if quiz_data.connections:
            all_questions.extend(quiz_data.connections.questions.values())
        if quiz_data.sequence:
            all_questions.extend(quiz_data.sequence.questions.values())
        
        missing_files = []
        for question in all_questions:
            for i, clue in enumerate(question.clues):
                if clue.type in {"image", "audio"}:
                    file_path = self.media_dir / clue.value
                    if not file_path.exists():
                        missing_files.append({
                            "question_id": question.id,
                            "clue_index": i,
                            "clue_type": clue.type,
                            "expected_path": str(file_path)
                        })
        
        if missing_files:
            error_lines = ["I seguenti file media non sono stati trovati:"]
            for item in missing_files:
                error_lines.append(
                    f"  - Domanda {item['question_id']}, clue {item['clue_index']}: "
                    f"{item['expected_path']}"
                )
            error_lines.append(f"\nAssicurati che i file siano in {self.media_dir}")
            raise QuizLoadError("\n".join(error_lines))
    
    def reload(self) -> QuizData:
        """Forza il ricaricamento del quiz da file."""
        return self.load(force_reload=True)
