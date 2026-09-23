from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import PaiementFrais, Inscription, Utilisateur
from app.schemas.frais_schema import paiement_schema, paiements_schema
from marshmallow import ValidationError
from datetime import datetime

bp = Blueprint('frais', __name__, url_prefix='/api/frais')

@bp.route('/paiement', methods=['POST'])
@jwt_required()
def create_paiement():
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    if not user:
        return {'msg': 'Utilisateur non trouvé'}, 404
    try:
        data = paiement_schema.load(request.get_json())
    except ValidationError as err:
        return {'errors': err.messages}, 400
    inscription = Inscription.query.filter_by(id=data['inscription_id'], etablissement_id=user.etablissement_id).first()
    if not inscription:
        return {'msg': 'Inscription non trouvée'}, 404
    paiement = PaiementFrais(inscription_id=data['inscription_id'], montant=data['montant'], methode=data['methode'], reference=data.get('reference'), remarques=data.get('remarques'), enregistre_par_id=user_id, date_paiement=datetime.utcnow())
    db.session.add(paiement)
    inscription.frais_payes = (inscription.frais_payes or 0) + data['montant']
    db.session.commit()
    return {'message': 'Paiement enregistré', 'paiement': paiement_schema.dump(paiement)}, 201

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard_frais():
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    inscriptions = Inscription.query.filter_by(etablissement_id=user.etablissement_id).all()
    total_frais = sum(float(i.frais_total or 0) for i in inscriptions)
    total_payes = sum(float(i.frais_payes or 0) for i in inscriptions)
    total_restants = total_frais - total_payes
    en_retard = [i for i in inscriptions if (i.frais_total or 0) - (i.frais_payes or 0) > 0]
    return {'total_frais': total_frais, 'total_payes': total_payes, 'total_restants': total_restants, 'taux_recouvrement': round((total_payes / total_frais * 100) if total_frais > 0 else 0, 2), 'inscriptions_total': len(inscriptions), 'en_retard': len(en_retard)}, 200
