"""
Entry point WSGI pour production

Usage:
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""
import os
from dotenv import load_dotenv

# Charger les variables .env
load_dotenv()

from app import create_app, db

# Créer l'app
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Contexte pour flask shell"""
    return {'db': db}


if __name__ == '__main__':
    # Pour développement local
    # Pour production, utiliser gunicorn
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
