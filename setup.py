#!/usr/bin/env python
"""
Script d'initialisation de la plateforme

Usage:
    python setup.py
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import Etablissement, Utilisateur
from app.services.auth_service import AuthService


def init_db():
    """Initialiser la base de données"""
    print("\n✅ Initialisation de la base de données...")
    
    app = create_app()
    
    with app.app_context():
        # Créer toutes les tables
        print("  → Création des tables...")
        db.create_all()
        print("  ✓ Tables créées")
        
        # Vérifier si l'établissement par défaut existe
        etablissement = Etablissement.query.filter_by(
            nom='Écol​e Par Défaut'
        ).first()
        
        if not etablissement:
            print("  → Création établissement par défaut...")
            etablissement = Etablissement(
                nom='École Par Défaut',
                localite='Maradi',
                region='Maradi',
                contact_principal='Directeur',
                email='directeur@ecole.local',
                telephone='+227 XX XX XX XX',
                couleur_primaire='#1F4E78',
                couleur_secondaire='#4472C4',
                cle_api='api_key_dev_12345'
            )
            db.session.add(etablissement)
            db.session.commit()
            print(f"  ✓ Établissement créé (ID: {etablissement.id})")
        else:
            print(f"  ✓ Établissement existe déjà (ID: {etablissement.id})")
        
        # Créer utilisateur admin par défaut
        admin_user = Utilisateur.query.filter_by(
            email='admin@ecole.local'
        ).first()
        
        if not admin_user:
            print("  → Création utilisateur admin...")
            try:
                admin = AuthService.create_user(
                    etablissement_id=etablissement.id,
                    nom='Admin',
                    prenom='Directeur',
                    email='admin@ecole.local',
                    password='password123',  # À changer absolument en production!
                    role='directeur',
                    telephone='+227 XX XX XX XX'
                )
                print(f"  ✓ Admin créé (ID: {admin.id})")
                print(f"\n  ⚠️  EMAIL: admin@ecole.local")
                print(f"  ⚠️  PASSWORD: password123")
                print(f"  ⚠️  À CHANGER ABSOLUMENT EN PRODUCTION!")
            except Exception as e:
                print(f"  ✗ Erreur création admin: {e}")
        else:
            print("  ✓ Admin existe déjà")
        
        print("\n✅ Initialisation terminée!\n")


def main():
    """Fonction principale"""
    print("""
╔════════════════════════════════════════════════════════════╗
║     PlatformScolaire - Initialisation Développement       ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        init_db()
        
        print("🚀 Prochaines étapes:")
        print("   1. Copier .env.example → .env")
        print("   2. Configurer DATABASE_URL dans .env")
        print("   3. Lancer: python wsgi.py")
        print("   4. Accéder: http://localhost:5000")
        print("\n✅ Prêt à démarrer!\n")
        
    except Exception as e:
        print(f"\n✗ Erreur: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
