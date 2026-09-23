"""
Initialisation de l'application Flask
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import get_config

# Initialiser extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name=None):
    """Factory pour créer l'app Flask"""
    
    app = Flask(__name__)
    
    # Configuration
    if config_name is None:
        config = get_config()
    else:
        from config import config as config_dict
        config = config_dict.get(config_name, get_config())
    
    app.config.from_object(config)
    
    # Initialiser extensions avec app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Importer models (pour que SQLAlchemy les connaisse)
    from app.models import Etablissement, Utilisateur, Eleve, Inscription
    
    # Enregistrer blueprints (routes)
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Context CLI commands
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'Etablissement': Etablissement,
            'Utilisateur': Utilisateur,
            'Eleve': Eleve,
            'Inscription': Inscription,
        }
    
    # Erreurs handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'erreur': 'Ressource non trouvée'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'erreur': 'Erreur serveur interne'}, 500
    
    return app

# Élèves routes
from app.routes.eleves import bp as eleves_bp
app.register_blueprint(eleves_bp)
