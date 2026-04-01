"""
Factory per l'app Flask.

Questo modulo crea un'istanza di Flask app in modo modulare.
Separa la creazione dell'app dalla sua configurazione, utile per testing.
"""

from flask import Flask
import sys
from pathlib import Path

# Aggiungi la cartella radice al path per importare moduli
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_app(config_object=None):
    """
    Crea e configura l'app Flask.
    
    Args:
        config_object: Modulo o dict di configurazione (di default user config.py)
    
    Returns:
        Flask app ready to run
    """
    app = Flask(__name__)
    
    # Carica configurazioni
    if config_object is None:
        import config
        app.config.from_object(config)
    else:
        app.config.from_object(config_object)
    
    # Registra i blueprint delle rotte
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app
