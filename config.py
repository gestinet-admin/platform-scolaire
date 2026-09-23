import os
from datetime import timedelta

class Config:
    """Configuration de base"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')
    DEBUG = False
    TESTING = False
    
    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-prod')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS
    CORS_ORIGINS = ['*']
    
    # Établissement
    ETABLISSEMENT_ID = os.getenv('ETABLISSEMENT_ID', 1)
    ETABLISSEMENT_NOM = os.getenv('ETABLISSEMENT_NOM', 'Établissement Par Défaut')


class DevelopmentConfig(Config):
    """Configuration développement"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/platform_scolaire_dev'
    )
    
    # JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Plus long en dev


class TestConfig(Config):
    """Configuration test"""
    TESTING = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(Config):
    """Configuration production"""
    DEBUG = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/platform_scolaire'
    )
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    if not SECRET_KEY or not JWT_SECRET_KEY:
        raise ValueError("SECRET_KEY et JWT_SECRET_KEY doivent être définis en production")


# Sélectionner config selon environnement
config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Récupère la config selon FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
