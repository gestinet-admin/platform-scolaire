from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import NotificationConfig, Utilisateur, Inscription
from app.schemas.notification_schema import notif_config_schema
from app.services.sms_service import SMSService
from app.services.whatsapp_service import WhatsAppService
from app.services.email_service import EmailService
from marshmallow import ValidationError

bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@bp.route('/config', methods=['GET'])
@jwt_required()
def get_config():
    """Récupérer config notifications"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    config = NotificationConfig.query.filter_by(etablissement_id=user.etablissement_id).first()
    
    if not config:
        return {'msg': 'Configuration non trouvée'}, 404
    
    return {'config': notif_config_schema.dump(config)}, 200

@bp.route('/config', methods=['PUT'])
@jwt_required()
def update_config():
    """Mettre à jour config notifications"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    config = NotificationConfig.query.filter_by(etablissement_id=user.etablissement_id).first()
    
    if not config:
        config = NotificationConfig(etablissement_id=user.etablissement_id)
        db.session.add(config)
    
    try:
        data = notif_config_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return {'errors': err.messages}, 400
    
    for key, value in data.items():
        setattr(config, key, value)
    
    db.session.commit()
    
    return {'message': 'Configuration mise à jour', 'config': notif_config_schema.dump(config)}, 200

@bp.route('/send-sms', methods=['POST'])
@jwt_required()
def send_sms():
    """Envoyer SMS"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    data = request.get_json()
    numero = data.get('numero')
    message = data.get('message')
    
    if not numero or not message:
        return {'msg': 'Numéro et message requis'}, 400
    
    resultat = SMSService.envoyer_sms(user.etablissement_id, numero, message)
    
    return resultat, 200 if resultat['success'] else 400

@bp.route('/send-sms-groupe', methods=['POST'])
@jwt_required()
def send_sms_groupe():
    """Envoyer SMS groupe"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    data = request.get_json()
    numeros = data.get('numeros', [])
    message = data.get('message')
    
    if not numeros or not message:
        return {'msg': 'Numéros et message requis'}, 400
    
    resultat = SMSService.envoyer_sms_groupe(user.etablissement_id, numeros, message)
    
    return resultat, 200

@bp.route('/send-whatsapp', methods=['POST'])
@jwt_required()
def send_whatsapp():
    """Envoyer WhatsApp"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    data = request.get_json()
    numero = data.get('numero')
    message = data.get('message')
    
    resultat = WhatsAppService.envoyer_message(user.etablissement_id, numero, message)
    
    return resultat, 200 if resultat['success'] else 400

@bp.route('/send-email', methods=['POST'])
@jwt_required()
def send_email():
    """Envoyer Email"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    data = request.get_json()
    destinataire = data.get('destinataire')
    sujet = data.get('sujet')
    message = data.get('message')
    
    resultat = EmailService.envoyer_email(user.etablissement_id, destinataire, sujet, message)
    
    return resultat, 200 if resultat['success'] else 400

@bp.route('/relance-impayés', methods=['POST'])
@jwt_required()
def relance_impayés():
    """Relancer élèves en retard (SMS/Email/WhatsApp)"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    # Récupérer inscriptions avec retards
    inscriptions = Inscription.query.filter_by(etablissement_id=user.etablissement_id).all()
    en_retard = [i for i in inscriptions if (i.frais_total or 0) - (i.frais_payes or 0) > 0]
    
    channel = request.get_json().get('channel', 'sms')  # sms, whatsapp, email
    
    numeros = []
    for inscription in en_retard:
        if channel == 'sms':
            numeros.append(inscription.eleve.parent.telephone if hasattr(inscription.eleve.parent, 'telephone') else None)
    
    message = f"Rappel: Frais de scolarité en retard pour {inscription.eleve.nom_complet()}"
    
    resultat = SMSService.envoyer_sms_groupe(user.etablissement_id, [n for n in numeros if n], message)
    
    return resultat, 200
