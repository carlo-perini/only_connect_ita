"""
Modelli dati per il quiz usando Pydantic.

Pydantic valida i dati JSON e assicura che abbiano la struttura corretta.
Se i dati sono invalidi, genera errori chiari.

Struttura:
- Clue: un singolo indizio (testo, immagine o audio)
- ConnectionQuestion: domanda del round Connessioni
- SequenceQuestion: domanda del round Sequenza
- Symbol: simbolo con ID e visualizzazione
- RoundSymbols: mapping tra simboli e domande per un round
- QuizData: contenitore principale con tutte le domande
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from pathlib import Path


class Clue(BaseModel):
    """
    Un singolo indizio che può essere di tre tipi:
    - text: solo testo
    - image: immagine (jpg, png, webp)
    - audio: file audio (mp3, wav, ogg)
    """
    type: str = Field(..., description="Tipo: 'text', 'image' o 'audio'")
    value: str = Field(..., description="Testo o percorso del file")
    label: Optional[str] = Field(None, description="Descrizione breve per accessibilità")
    credit: Optional[str] = Field(None, description="Credito o attribuzione")
    
    @validator("type")
    def validate_type(cls, v):
        """Assicura che il type sia uno dei tre supportati."""
        allowed = {"text", "image", "audio"}
        if v not in allowed:
            raise ValueError(f"Type deve essere uno tra {allowed}, ricevuto '{v}'")
        return v


class Symbol(BaseModel):
    """Un simbolo nella griglia del round."""
    id: str = Field(..., description="ID unico del simbolo")
    display: str = Field(..., description="Carattere/emoji del simbolo (1 char)")
    label: Optional[str] = Field(None, description="Descrizione del simbolo")
    
    @validator("display")
    def validate_display_length(cls, v):
        """Assicura che il display sia un singolo carattere."""
        if len(v) != 1:
            raise ValueError(f"display deve essere un singolo carattere, ricevuto '{v}'")
        return v


class ConnectionQuestion(BaseModel):
    """Domanda del round Connessioni."""
    id: str = Field(..., description="ID unico della domanda")
    clues: List[Clue] = Field(..., description="Lista di 4 clue progressivi")
    answer: str = Field(..., description="Risposta corretta")
    explanation: str = Field(..., description="Spiegazione della risposta")
    
    @validator("clues")
    def validate_clues_count(cls, v):
        """Connessioni devono avere esattamente 4 clue."""
        if len(v) != 4:
            raise ValueError(f"Connessioni devono avere 4 clue, ricevuti {len(v)}")
        return v


class SequenceQuestion(BaseModel):
    """Domanda del round Sequenza."""
    id: str = Field(..., description="ID unico della domanda")
    clues: List[Clue] = Field(..., description="Lista di 3 clue della sequenza")
    answer: str = Field(..., description="Quarto elemento (risposta corretta)")
    sequence_rule: str = Field(..., description="Descrizione della regola della sequenza")
    explanation: str = Field(..., description="Spiegazione della sequenza")
    
    @validator("clues")
    def validate_clues_count(cls, v):
        """Sequenze devono avere esattamente 3 clue."""
        if len(v) != 3:
            raise ValueError(f"Sequenze devono avere 3 clue, ricevuti {len(v)}")
        return v


class RoundSymbols(BaseModel):
    """Mapping tra simboli e domande per un round."""
    symbols: List[Symbol] = Field(..., description="Lista di 6 simboli")
    questions: Dict[str, ConnectionQuestion | SequenceQuestion] = Field(
        ..., 
        description="Mapping symbol_id -> question"
    )
    
    @validator("symbols")
    def validate_symbols_count(cls, v):
        """Ci devono essere esattamente 6 simboli."""
        if len(v) != 6:
            raise ValueError(f"Devono esserci 6 simboli, ricevuti {len(v)}")
        return v
    
    @validator("questions")
    def validate_questions_mapping(cls, v):
        """Tutti i symbol_id devono avere una domanda."""
        if len(v) != 6:
            raise ValueError(f"Devono esserci 6 domande (una per simbolo), ricevute {len(v)}")
        return v


class MissingVowelsWord(BaseModel):
    """Una parola nel round Vocali Mancanti."""
    answer: str = Field(..., description="La parola/frase corretta con le vocali")
    display: str = Field(..., description="La versione senza vocali con spaziature modificate")


class MissingVowelsCategory(BaseModel):
    """Una categoria del round Vocali Mancanti con 4 parole."""
    id: str = Field(..., description="ID unico della categoria")
    category_name: str = Field(..., description="Nome della categoria (mostrato ai concorrenti)")
    words: List[MissingVowelsWord] = Field(..., description="Lista di 4 parole")
    
    @validator("words")
    def validate_words_count(cls, v):
        """Ogni categoria deve avere esattamente 4 parole."""
        if len(v) != 4:
            raise ValueError(f"Vocali Mancanti: ogni categoria deve avere 4 parole, ricevute {len(v)}")
        return v


class MissingVowelsRound(BaseModel):
    """Round Vocali Mancanti con 4 categorie."""
    categories: List[MissingVowelsCategory] = Field(..., description="Lista di 4 categorie")
    
    @validator("categories")
    def validate_categories_count(cls, v):
        """Devono esserci esattamente 4 categorie."""
        if len(v) != 4:
            raise ValueError(f"Vocali Mancanti: devono esserci 4 categorie, ricevute {len(v)}")
        return v


class WallGroup(BaseModel):
    """Un gruppo di 4 elementi nel Muro delle Connessioni."""
    connection: str = Field(..., description="La connessione nascosta tra i 4 elementi")
    items: List[str] = Field(..., description="Lista di 4 elementi")
    
    @validator("items")
    def validate_items_count(cls, v):
        if len(v) != 4:
            raise ValueError(f"Ogni gruppo del muro deve avere 4 elementi, ricevuti {len(v)}")
        return v


class WallQuestion(BaseModel):
    """Una griglia del Muro delle Connessioni con 4 gruppi da 4 elementi."""
    groups: List[WallGroup] = Field(..., description="Lista di 4 gruppi da 4 elementi")
    
    @validator("groups")
    def validate_groups_count(cls, v):
        if len(v) != 4:
            raise ValueError(f"Il muro deve avere 4 gruppi, ricevuti {len(v)}")
        return v


class WallRound(BaseModel):
    """Round Muro delle Connessioni con 2 simboli e 2 griglie diverse."""
    symbols: List[Symbol] = Field(..., description="Lista di 2 simboli")
    questions: Dict[str, WallQuestion] = Field(
        ..., 
        description="Mapping symbol_id -> wall_question"
    )
    
    @validator("symbols")
    def validate_symbols_count(cls, v):
        """Ci devono essere esattamente 2 simboli nel muro."""
        if len(v) != 2:
            raise ValueError(f"Il muro deve avere 2 simboli, ricevuti {len(v)}")
        return v
    
    @validator("questions")
    def validate_questions_mapping(cls, v):
        """Tutti i symbol_id devono avere una griglia."""
        if len(v) != 2:
            raise ValueError(f"Il muro deve avere 2 griglie (una per simbolo), ricevute {len(v)}")
        return v


class QuizData(BaseModel):
    """Contenitore principale del file quiz_data.json."""
    connections: Optional[RoundSymbols] = Field(
        None,
        description="Round Connessioni con 6 simboli"
    )
    sequence: Optional[RoundSymbols] = Field(
        None,
        description="Round Sequenza con 6 simboli"
    )
    missing_vowels: Optional[MissingVowelsRound] = Field(
        None,
        description="Round Vocali Mancanti con 4 categorie da 4 parole"
    )
    wall: Optional[WallRound] = Field(
        None,
        description="Round Muro delle Connessioni con 4 gruppi da 4 elementi"
    )
    teams: Optional[List[Dict]] = Field(
        None,
        description="Liste delle squadre con nome e colore"
    )
    
    class Config:
        # Pydantic: consenti assegnazione di attributi dopo creazione
        validate_assignment = True


class Team(BaseModel):
    """Definizione di una squadra."""
    id: str = Field(..., description="ID unico della squadra")
    name: str = Field(..., description="Nome della squadra")
    color: str = Field(..., description="Colore esadecimale della squadra (es: #FF8C42)")


class TeamScore(BaseModel):
    """Punteggio di una squadra durante il gioco."""
    team_id: str = Field(..., description="ID della squadra")
    team_name: str = Field(..., description="Nome della squadra")
    score: int = Field(default=0, description="Punteggio attuale")


class GameState(BaseModel):
    """Stato della partita in corso."""
    current_round: Optional[str] = Field(None, description="Round attuale (connections, sequence, wall, missing_vowels)")
    current_team_index: int = Field(default=0, description="Indice del team attuale (0 o 1)")
    teams_scores: List[TeamScore] = Field(default=[], description="Punteggi delle squadre")
    points_assigned_for_current_question: bool = Field(default=False, description="Se i punti sono già stati assegnati per la domanda corrente")
