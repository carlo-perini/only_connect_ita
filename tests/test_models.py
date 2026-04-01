"""
Test minimo - Validazione dei modelli Pydantic

Esegui con: pytest tests/test_models.py -v
"""

import pytest
from app.models import Clue, ConnectionQuestion, SequenceQuestion, QuizData


def test_clue_text():
    """Un clue di testo è valido."""
    clue = Clue(type="text", value="Un indizio di testo")
    assert clue.type == "text"
    assert clue.value == "Un indizio di testo"


def test_clue_image():
    """Un clue di immagine è valido."""
    clue = Clue(type="image", value="images/photo.jpg", label="Una foto")
    assert clue.type == "image"
    assert clue.label == "Una foto"


def test_clue_audio():
    """Un clue di audio è valido."""
    clue = Clue(type="audio", value="audio/song.mp3")
    assert clue.type == "audio"


def test_clue_invalid_type():
    """Un clue con type invalido solleva errore."""
    with pytest.raises(ValueError):
        Clue(type="video", value="test")


def test_connection_question_valid():
    """Una ConnectionQuestion con 4 clue è valida."""
    clues = [
        Clue(type="text", value=f"Indizio {i+1}")
        for i in range(4)
    ]
    question = ConnectionQuestion(
        id="conn-001",
        clues=clues,
        answer="La risposta",
        explanation="Spiegazione"
    )
    assert len(question.clues) == 4
    assert question.id == "conn-001"


def test_connection_question_wrong_clue_count():
    """Una ConnectionQuestion con numero sbagliato di clue solleva errore."""
    clues = [Clue(type="text", value=f"Indizio {i+1}") for i in range(3)]
    with pytest.raises(ValueError):
        ConnectionQuestion(
            id="conn-001",
            clues=clues,
            answer="La risposta",
            explanation="Spiegazione"
        )


def test_sequence_question_valid():
    """Una SequenceQuestion con 3 clue è valida."""
    clues = [
        Clue(type="text", value=f"Elemento {i+1}")
        for i in range(3)
    ]
    question = SequenceQuestion(
        id="seq-001",
        clues=clues,
        answer="Quarto elemento",
        sequence_rule="La regola della sequenza",
        explanation="Spiegazione"
    )
    assert len(question.clues) == 3


def test_quiz_data_mixed():
    """QuizData può contenere sia connessioni che sequenze."""
    conn_clues = [Clue(type="text", value=f"C{i}") for i in range(4)]
    seq_clues = [Clue(type="text", value=f"S{i}") for i in range(3)]
    
    conn = ConnectionQuestion(
        id="c1", clues=conn_clues, answer="Ans", explanation="Exp"
    )
    seq = SequenceQuestion(
        id="s1", clues=seq_clues, answer="Ans",
        sequence_rule="Rule", explanation="Exp"
    )
    
    quiz = QuizData(connections=[conn], sequence=[seq])
    assert len(quiz.connections) == 1
    assert len(quiz.sequence) == 1
