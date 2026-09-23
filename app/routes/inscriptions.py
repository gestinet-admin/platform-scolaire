from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Inscription, Utilisateur, Eleve
from app.schemas.inscription_schema import inscription_schema, inscriptions_schema
from marshmallow import ValidationError

bp = Blueprint('inscriptions', __name__, url_prefix='/api/inscriptions')

@bp.route('', methods=['POST'])
@jwt_required()
def create_inscription():
    """Créer une nouvelle inscription"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    if not user:
        return {'msg': 'Utilisateur non trouvé'}, 404
    
    try:
        data = inscription_schema.load(request.get_json())
    except ValidationError as err:
        return {'errors': err.messages}, 400
    
    # Vérifier que l'élève existe
    eleve = Eleve.query.filter_by(id=data['eleve_id'], etablissement_id=user.etablissement_id).first()
    if not eleve:
        return {'msg': 'Élève non trouvé'}, 404
    
    inscription = Inscription(
        etablissement_id=user.etablissement_id,
        eleve_id=data['eleve_id'],
        annee_scolaire=data['annee_scolaire'],
        frais_total=data['frais_total'],
        frais_incluent_inscription=True,
        statut='en_attente'
    )
    
    db.session.add(inscription)
    db.session.commit()
    
    return {
        'message': f'Inscription créée pour {eleve.nom_complet()}',
        'inscription': inscription_schema.dump(inscription)
    }, 201

@bp.route('', methods=['GET'])
@jwt_required()
def list_inscriptions():
    """Lister les inscriptions"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    annee = request.args.get('annee_scolaire')
    statut = request.args.get('statut')
    
    query = Inscription.query.filter_by(etablissement_id=user.etablissement_id)
    
    if annee:
        query = query.filter_by(annee_scolaire=annee)
    if statut:
        query = query.filter_by(statut=statut)
    
    inscriptions = query.paginate(page=page, per_page=limit)
    
    return {
        'total': inscriptions.total,
        'page': page,
        'pages': inscriptions.pages,
        'inscriptions': inscriptions_schema.dump(inscriptions.items)
    }, 200

@bp.route('/<int:inscription_id>', methods=['GET'])
@jwt_required()
def get_inscription(inscription_id):
    """Récupérer détails inscription"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    inscription = Inscription.query.filter_by(id=inscription_id, etablissement_id=user.etablissement_id).first()
    
    if not inscription:
        return {'msg': 'Inscription non trouvée'}, 404
    
    return {'inscription': inscription_schema.dump(inscription)}, 200

@bp.route('/<int:inscription_id>', methods=['PUT'])
@jwt_required()
def update_inscription(inscription_id):
    """Modifier inscription"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    inscription = Inscription.query.filter_by(id=inscription_id, etablissement_id=user.etablissement_id).first()
    
    if not inscription:
        return {'msg': 'Inscription non trouvée'}, 404
    
    try:
        data = inscription_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return {'errors': err.messages}, 400
    
    for key, value in data.items():
        if key != 'eleve_id':  # Ne pas changer l'élève
            setattr(inscription, key, value)
    
    db.session.commit()
    
    return {'message': 'Inscription modifiée', 'inscription': inscription_schema.dump(inscription)}, 200

@bp.route('/<int:inscription_id>', methods=['DELETE'])
@jwt_required()
def delete_inscription(inscription_id):
    """Annuler inscription (soft delete)"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    inscription = Inscription.query.filter_by(id=inscription_id, etablissement_id=user.etablissement_id).first()
    
    if not inscription:
        return {'msg': 'Inscription non trouvée'}, 404
    
    inscription.statut = 'annulee'
    db.session.commit()
    
    return {'message': 'Inscription annulée'}, 200
