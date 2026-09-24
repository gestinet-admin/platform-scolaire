import requests
from app.models import NotificationConfig

class WhatsAppService:
    """Service d'envoi WhatsApp Business"""
    
    WHATSAPP_API_URL = 'https://graph.instagram.com/v18.0/me/messages'
    
    @staticmethod
    def envoyer_message(etablissement_id, numero_whatsapp, message):
        """Envoyer message WhatsApp"""
        config = NotificationConfig.query.filter_by(etablissement_id=etablissement_id).first()
        
        if not config or not config.whatsapp_actif:
            return {'success': False, 'msg': 'WhatsApp non configuré'}
        
        # Préparer payload WhatsApp API
        payload = {
            'messaging_product': 'whatsapp',
            'to': numero_whatsapp,
            'type': 'text',
            'text': {'body': message}
        }
        
        headers = {
            'Authorization': f"Bearer {config.whatsapp_api_key}",
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                WhatsAppService.WHATSAPP_API_URL,
                json=payload,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return {'success': True, 'msg': 'Message WhatsApp envoyé'}
            else:
                return {'success': False, 'msg': f'Erreur {response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'msg': str(e)}
    
    @staticmethod
    def envoyer_groupe_whatsapp(etablissement_id, numeros_list, message):
        """Envoyer message à plusieurs numéros WhatsApp"""
        resultats = []
        for numero in numeros_list:
            resultat = WhatsAppService.envoyer_message(etablissement_id, numero, message)
            resultats.append(resultat)
        
        return {
            'total': len(numeros_list),
            'reussis': sum(1 for r in resultats if r['success']),
            'details': resultats
        }
