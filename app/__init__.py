from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name='production'):
    app = Flask(__name__)
    
    # Configuration
    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    else:
        # Production (Heroku)
        database_url = os.getenv('DATABASE_URL', 'sqlite:///platform_scolaire.db')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-me-in-production')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Models
    from app.models import Etablissement, Utilisateur, Eleve, Inscription, PaiementFrais, NotificationConfig
    
    # Auth routes
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    # Élèves routes
    from app.routes.eleves import bp as eleves_bp
    app.register_blueprint(eleves_bp)
    
    # Inscriptions routes
    from app.routes.inscriptions import bp as inscriptions_bp
    app.register_blueprint(inscriptions_bp)
    
    # Frais routes
    from app.routes.frais import bp as frais_bp
    app.register_blueprint(frais_bp)
    
    # Notifications routes
    from app.routes.notifications import bp as notifications_bp
    app.register_blueprint(notifications_bp)
    
    # Export routes
    from app.routes.export import bp as export_bp
    app.register_blueprint(export_bp)
    
    # Views routes
    from app.routes.views import bp as views_bp
    app.register_blueprint(views_bp)
    
    return app
