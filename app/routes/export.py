from flask import Blueprint, send_file, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Utilisateur, Eleve, Inscription, PaiementFrais
from app.services.pdf_service import PDFService
from app.services.excel_service import ExcelService
from datetime import datetime

bp = Blueprint('export', __name__, url_prefix='/api/export')

@bp.route('/liste-classe/<classe>', methods=['GET'])
@jwt_required()
def export_liste_classe(classe):
    """Exporter liste classe PDF"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    eleves = Eleve.query.filter_by(
        etablissement_id=user.etablissement_id,
        classe_actuelle=classe,
        actif=True
    ).all()
    
    if not eleves:
        return {'msg': 'Aucun élève trouvé'}, 404
    
    pdf = PDFService.generer_liste_classe(
        user.etablissement.nom,
        classe,
        eleves
    )
    
    return send_file(
        pdf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'liste_classe_{classe}_{datetime.now().strftime("%Y%m%d")}.pdf'
    )

@bp.route('/bulletin/<int:eleve_id>', methods=['GET'])
@jwt_required()
def export_bulletin(eleve_id):
    """Exporter bulletin élève PDF"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    eleve = Eleve.query.filter_by(id=eleve_id, etablissement_id=user.etablissement_id).first()
    
    if not eleve:
        return {'msg': 'Élève non trouvé'}, 404
    
    inscription = Inscription.query.filter_by(eleve_id=eleve_id).first()
    
    if not inscription:
        return {'msg': 'Aucune inscription trouvée'}, 404
    
    pdf = PDFService.generer_bulletin(eleve, inscription)
    
    return send_file(
        pdf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'bulletin_{eleve.nom}_{datetime.now().strftime("%Y%m%d")}.pdf'
    )

@bp.route('/recu-paiement/<int:paiement_id>', methods=['GET'])
@jwt_required()
def export_recu_paiement(paiement_id):
    """Exporter reçu paiement PDF"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    paiement = PaiementFrais.query.get(paiement_id)
    
    if not paiement:
        return {'msg': 'Paiement non trouvé'}, 404
    
    inscription = paiement.inscription
    eleve = inscription.eleve
    
    pdf = PDFService.generer_recu_paiement(paiement, inscription, eleve)
    
    return send_file(
        pdf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'recu_{paiement.id}_{datetime.now().strftime("%Y%m%d")}.pdf'
    )

@bp.route('/rapport-frais', methods=['GET'])
@jwt_required()
def export_rapport_frais():
    """Exporter rapport frais Excel"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    inscriptions = Inscription.query.filter_by(etablissement_id=user.etablissement_id).all()
    
    if not inscriptions:
        return {'msg': 'Aucune inscription trouvée'}, 404
    
    excel = ExcelService.generer_rapport_frais(
        user.etablissement.nom,
        inscriptions
    )
    
    return send_file(
        excel,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'rapport_frais_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

@bp.route('/liste-eleves', methods=['GET'])
@jwt_required()
def export_liste_eleves():
    """Exporter liste élèves Excel"""
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    
    eleves = Eleve.query.filter_by(
        etablissement_id=user.etablissement_id,
        actif=True
    ).all()
    
    if not eleves:
        return {'msg': 'Aucun élève trouvé'}, 404
    
    excel = ExcelService.generer_liste_eleves(
        user.etablissement.nom,
        eleves
    )
    
    return send_file(
        excel,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'liste_eleves_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )
