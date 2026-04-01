"""
Utilità per il matching di risposte.

Gestisce il confronto case-insensitive tra le risposte dell'utente e quelle corrette,
ignorando spazi superflui e punteggiatura semplice.
"""

import string
import re
from typing import List


def normalize_answer(text: str) -> str:
    """
    Normalizza una risposta per il confronto.
    
    - Converte a minuscolo
    - Rimuove spazi all'inizio e fine
    - Riduce spazi multipli a un singolo spazio
    - Rimuove punteggiatura semplice
    
    Args:
        text: Testo da normalizzare
    
    Returns:
        Testo normalizzato
    
    Esempio:
        normalize_answer("  Ciao, Mondo!  ") -> "ciao mondo"
    """
    # Minuscolo
    text = text.lower()
    
    # Rimuovi spazi superflui
    text = " ".join(text.split())
    
    # Rimuovi punteggiatura semplice (non accenti)
    # Mantieni lettere, numeri, spazi e punteggiatura preservata
    text = text.translate(str.maketrans("", "", string.punctuation))
    
    return text


def is_answer_correct(
    user_answer: str,
    correct_answer: str,
    accepted_variants: List[str] = None
) -> bool:
    """
    Controlla se la risposta dell'utente è corretta.
    
    Compara la risposta normalizzata con quella corretta e le varianti accettate.
    
    Args:
        user_answer: La risposta data dall'utente
        correct_answer: La risposta corretta
        accepted_variants: Lista di altre risposte accettate (default: [])
    
    Returns:
        True se la risposta è corretta, False altrimenti
    
    Esempio:
        is_answer_correct("Ciao!", "ciao") -> True
        is_answer_correct("Hello", "ciao") -> False
    """
    if accepted_variants is None:
        accepted_variants = []
    
    # Normalizza tutte le risposte
    normalized_user = normalize_answer(user_answer)
    normalized_correct = normalize_answer(correct_answer)
    normalized_variants = [normalize_answer(v) for v in accepted_variants]
    
    # Confronta
    all_acceptable = [normalized_correct] + normalized_variants
    return normalized_user in all_acceptable
