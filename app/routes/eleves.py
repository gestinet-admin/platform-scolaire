from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Eleve, Utilisateur
from app.schemas.eleve_schema import eleve_schema, eleves_schema
from marshmallow import ValidationError

bp = Blueprint('eleves', __name__, url_prefix='/api/eleves')

@bp.route('', methods=['POST'])
@jwt_required()
def create_eleve():
    """Créer un nouvel élève"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    if not user:
        return {'msg': 'Utilisateur non trouvé'}, 404
    
    try:
        data = eleve_schema.load(request.get_json())
    except ValidationError as err:
        return {'errors': err.messages}, 400
    
    eleve = Eleve(
        etablissement_id=user.etablissement_id,
        nom=data['nom'],
        prenom=data['prenom'],
        date_naissance=data.get('date_naissance'),
        numero_matricule=data.get('numero_matricule'),
        classe_actuelle=data.get('classe_actuelle'),
        frais_scolarite_annuels=data.get('frais_scolarite_annuels'),
        parent_id=data.get('parent_id'),
    )
    
    db.session.add(eleve)
    db.session.commit()
    
    return {
        'message': f'Élève {eleve.prenom} {eleve.nom} créé',
        'eleve': eleve_schema.dump(eleve)
    }, 201

@bp.route('', methods=['GET'])
@jwt_required()
def list_eleves():
    """Lister tous les élèves de l'établissement"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    classe = request.args.get('classe')
    
    query = Eleve.query.filter_by(etablissement_id=user.etablissement_id, actif=True)
    
    if classe:
        query = query.filter_by(classe_actuelle=classe)
    
    eleves = query.paginate(page=page, per_page=limit)
    
    return {
        'total': eleves.total,
        'page': page,
        'pages': eleves.pages,
        'eleves': eleves_schema.dump(eleves.items)
    }, 200

@bp.route('/<int:eleve_id>', methods=['GET'])
@jwt_required()
def get_eleve(eleve_id):
    """Récupérer détails d'un élève"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    eleve = Eleve.query.filter_by(id=eleve_id, etablissement_id=user.etablissement_id).first()
    
    if not eleve:
        return {'msg': 'Élève non trouvé'}, 404
    
    return {'eleve': eleve_schema.dump(eleve)}, 200

@bp.route('/<int:eleve_id>', methods=['PUT'])
@jwt_required()
def update_eleve(eleve_id):
    """Modifier un élève"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    eleve = Eleve.query.filter_by(id=eleve_id, etablissement_id=user.etablissement_id).first()
    
    if not eleve:
        return {'msg': 'Élève non trouvé'}, 404
    
    try:
        data = eleve_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return {'errors': err.messages}, 400
    
    for key, value in data.items():
        setattr(eleve, key, value)
    
    db.session.commit()
    
    return {'message': 'Élève modifié', 'eleve': eleve_schema.dump(eleve)}, 200

@bp.route('/<int:eleve_id>', methods=['DELETE'])
@jwt_required()
def delete_eleve(eleve_id):
    """Supprimer un élève (soft delete)"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    eleve = Eleve.query.filter_by(id=eleve_id, etablissement_id=user.etablissement_id).first()
    
    if not eleve:
        return {'msg': 'Élève non trouvé'}, 404
    
    eleve.actif = False
    db.session.commit()
    
    return {'message': 'Élève supprimé'}, 200
