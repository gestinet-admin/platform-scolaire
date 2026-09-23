"""
Service d'authentification
"""
import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from app import db
from app.models import Utilisateur, Etablissement


class AuthService:
    """Gestion authentification (hash, JWT, login)"""
    
    @staticmethod
    def hash_password(password):
        """Hasher un mot de passe avec bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    @staticmethod
    def verify_password(password, password_hash):
        """Vérifier un mot de passe"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash)
    
    @staticmethod
    def create_user(
        etablissement_id,
        nom,
        prenom,
        email,
        password,
        role,
        telephone=None
    ):
        """
        Créer un nouvel utilisateur
        
        Args:
            etablissement_id: ID de l'établissement
            nom: Nom de l'utilisateur
            prenom: Prénom
            email: Email unique
            password: Mot de passe (sera hashé)
            role: 'directeur', 'secretaire', 'professeur', 'parent', 'admin'
            telephone: Numéro de téléphone (optionnel)
        
        Returns:
            Utilisateur créé ou None si erreur
        """
        try:
            # Vérifier que l'établissement existe
            etablissement = Etablissement.query.get(etablissement_id)
            if not etablissement:
                raise ValueError(f"Établissement {etablissement_id} non trouvé")
            
            # Vérifier que l'email n'existe pas déjà pour cet établissement
            existing = Utilisateur.query.filter_by(
                etablissement_id=etablissement_id,
                email=email
            ).first()
            if existing:
                raise ValueError(f"Email {email} déjà utilisé dans cet établissement")
            
            # Créer l'utilisateur
            user = Utilisateur(
                etablissement_id=etablissement_id,
                nom=nom,
                prenom=prenom,
                email=email,
                mot_de_passe_hash=AuthService.hash_password(password),
                role=role,
                telephone=telephone,
                actif=True
            )
            
            db.session.add(user)
            db.session.commit()
            
            return user
        
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def login(email, password, etablissement_id=None):
        """
        Authentifier un utilisateur
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe
            etablissement_id: ID établissement (optionnel, pour multi-tenant)
        
        Returns:
            dict avec access_token, refresh_token, user_data
            ou None si authentification échouée
        """
        try:
            # Trouver l'utilisateur
            query = Utilisateur.query.filter_by(email=email)
            
            if etablissement_id:
                query = query.filter_by(etablissement_id=etablissement_id)
            
            user = query.first()
            
            if not user:
                return None  # Utilisateur non trouvé
            
            if not user.actif:
                return None  # Utilisateur désactivé
            
            # Vérifier le mot de passe
            if not AuthService.verify_password(password, user.mot_de_passe_hash):
                return None  # Mot de passe incorrect
            
            # Créer les tokens JWT
            access_token = create_access_token(
                identity=user.id,
                additional_claims={
                    'role': user.role,
                    'etablissement_id': user.etablissement_id,
                }
            )
            
            refresh_token = create_refresh_token(
                identity=user.id,
                additional_claims={
                    'role': user.role,
                    'etablissement_id': user.etablissement_id,
                }
            )
            
            # Mettre à jour la date du dernier login
            user.date_dernier_login = db.func.now()
            db.session.commit()
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }
        
        except Exception as e:
            raise e
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        Changer le mot de passe d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            old_password: Ancien mot de passe
            new_password: Nouveau mot de passe
        
        Returns:
            True si succès, False sinon
        """
        try:
            user = Utilisateur.query.get(user_id)
            if not user:
                return False
            
            # Vérifier l'ancien mot de passe
            if not AuthService.verify_password(old_password, user.mot_de_passe_hash):
                return False
            
            # Changer le mot de passe
            user.mot_de_passe_hash = AuthService.hash_password(new_password)
            db.session.commit()
            
            return True
        
        except Exception as e:
            db.session.rollback()
            raise e
