import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models import NotificationConfig

class EmailService:
    """Service d'envoi Email"""
    
    @staticmethod
    def envoyer_email(etablissement_id, destinataire, sujet, message):
        """Envoyer email"""
        config = NotificationConfig.query.filter_by(etablissement_id=etablissement_id).first()
        
        if not config or not config.email_actif:
            return {'success': False, 'msg': 'Email non configuré'}
        
        try:
            # Créer message
            msg = MIMEMultipart()
            msg['From'] = config.email_address
            msg['To'] = destinataire
            msg['Subject'] = sujet
            
            msg.attach(MIMEText(message, 'html'))
            
            # Envoyer via SMTP
            with smtplib.SMTP(config.email_smtp_server, config.email_smtp_port) as server:
                server.starttls()
                server.login(config.email_address, config.email_password)
                server.send_message(msg)
            
            return {'success': True, 'msg': 'Email envoyé'}
        
        except Exception as e:
            return {'success': False, 'msg': str(e)}
    
    @staticmethod
    def envoyer_email_groupe(etablissement_id, destinataires_list, sujet, message):
        """Envoyer email à plusieurs destinataires"""
        resultats = []
        for email in destinataires_list:
            resultat = EmailService.envoyer_email(etablissement_id, email, sujet, message)
            resultats.append(resultat)
        
        return {
            'total': len(destinataires_list),
            'reussis': sum(1 for r in resultats if r['success']),
            'details': resultats
        }
