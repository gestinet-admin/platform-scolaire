import requests
from app.models import NotificationConfig

class SMSService:
    """Service d'envoi SMS multi-opérateur"""
    
    # URLs API des opérateurs Niger (exemples)
    OPERATEURS = {
        'orange': 'https://api.orange.ne/sms/send',
        'airtel': 'https://api.airtel.ne/sms/send',
        'maroc_telecom': 'https://api.maroctelcom.ne/sms/send',
        'zain': 'https://api.zain.ne/sms/send'
    }
    
    @staticmethod
    def envoyer_sms(etablissement_id, numero, message):
        """Envoyer SMS via opérateur configuré"""
        config = NotificationConfig.query.filter_by(etablissement_id=etablissement_id).first()
        
        if not config or not config.sms_actif:
            return {'success': False, 'msg': 'SMS non configuré'}
        
        operateur = config.sms_operateur
        api_url = SMSService.OPERATEURS.get(operateur)
        
        if not api_url:
            return {'success': False, 'msg': f'Opérateur {operateur} non supporté'}
        
        # Préparer payload
        payload = {
            'api_key': config.sms_api_key,
            'sender_id': config.sms_sender_id,
            'phone': numero,
            'message': message
        }
        
        try:
            # Appel API opérateur (À IMPLÉMENTER avec vraies credentials)
            response = requests.post(api_url, json=payload, timeout=5)
            
            if response.status_code == 200:
                return {'success': True, 'msg': 'SMS envoyé'}
            else:
                return {'success': False, 'msg': f'Erreur {response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'msg': str(e)}
    
    @staticmethod
    def envoyer_sms_groupe(etablissement_id, numeros_list, message):
        """Envoyer SMS à plusieurs numéros"""
        resultats = []
        for numero in numeros_list:
            resultat = SMSService.envoyer_sms(etablissement_id, numero, message)
            resultats.append(resultat)
        
        return {
            'total': len(numeros_list),
            'reussis': sum(1 for r in resultats if r['success']),
            'details': resultats
        }
