"""
Routes d'authentification
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.auth_service import AuthService
from app.models import Utilisateur

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Route de login
    
    Payload JSON:
    {
        "email": "directeur@ecole.ne",
        "password": "password123",
        "etablissement_id": 1  (optionnel)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'erreur': 'Données JSON manquantes'}), 400
        
        email = data.get('email')
        password = data.get('password')
        etablissement_id = data.get('etablissement_id')
        
        if not email or not password:
            return jsonify({'erreur': 'Email et mot de passe requis'}), 400
        
        # Authentifier
        result = AuthService.login(email, password, etablissement_id)
        
        if not result:
            return jsonify({'erreur': 'Email ou mot de passe incorrect'}), 401
        
        return jsonify({
            'message': 'Connexion réussie',
            'access_token': result['access_token'],
            'refresh_token': result['refresh_token'],
            'user': result['user']
        }), 200
    
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh l'access token avec le refresh token
    
    Header:
    Authorization: Bearer <refresh_token>
    """
    try:
        user_id = get_jwt_identity()
        user = Utilisateur.query.get(user_id)
        
        if not user or not user.actif:
            return jsonify({'erreur': 'Utilisateur introuvable ou inactif'}), 401
        
        from flask_jwt_extended import create_access_token
        
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'role': user.role,
                'etablissement_id': user.etablissement_id,
            }
        )
        
        return jsonify({
            'message': 'Token rafraîchi',
            'access_token': access_token
        }), 200
    
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def current_user():
    """
    Récupère l'utilisateur actuellement connecté
    
    Header:
    Authorization: Bearer <access_token>
    """
    try:
        user_id = get_jwt_identity()
        user = Utilisateur.query.get(user_id)
        
        if not user:
            return jsonify({'erreur': 'Utilisateur non trouvé'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Changer le mot de passe de l'utilisateur connecté
    
    Payload JSON:
    {
        "old_password": "ancien_mdp",
        "new_password": "nouveau_mdp"
    }
    
    Header:
    Authorization: Bearer <access_token>
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'erreur': 'Données JSON manquantes'}), 400
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'erreur': 'Anciens et nouveau mot de passe requis'}), 400
        
        if len(new_password) < 6:
            return jsonify({'erreur': 'Le mot de passe doit faire au moins 6 caractères'}), 400
        
        success = AuthService.change_password(user_id, old_password, new_password)
        
        if not success:
            return jsonify({'erreur': 'Ancien mot de passe incorrect'}), 401
        
        return jsonify({
            'message': 'Mot de passe changé avec succès'
        }), 200
    
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout (simple, JWT n'a pas besoin de backend pour se disconnecter)
    
    Header:
    Authorization: Bearer <access_token>
    """
    # En JWT, il suffit que le client supprime le token
    # On peut logger l'action ici si besoin
    return jsonify({
        'message': 'Déconnexion réussie'
    }), 200
