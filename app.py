"""
Entry point dell'applicazione Flask.

Questo script avvia il server Flask.
Esegui con: python app.py
"""

from app import create_app
import config

if __name__ == "__main__":
    app = create_app(config)
    
    # Debug mode se FLASK_ENV=development
    debug = config.DEBUG
    
    # Avvia il server
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=debug
    )
