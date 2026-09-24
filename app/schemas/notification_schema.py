from marshmallow import Schema, fields, validate

class NotificationConfigSchema(Schema):
    """Validation configuration notifications"""
    
    id = fields.Integer(dump_only=True)
    etablissement_id = fields.Integer(dump_only=True)
    
    # SMS
    sms_actif = fields.Boolean()
    sms_operateur = fields.String(validate=validate.OneOf(['orange', 'airtel', 'maroc_telecom', 'zain']))
    sms_api_key = fields.String(load_only=True)  # Ne pas retourner en réponse
    sms_sender_id = fields.String()
    
    # WhatsApp
    whatsapp_actif = fields.Boolean()
    whatsapp_api_key = fields.String(load_only=True)
    whatsapp_phone_id = fields.String()
    
    # Email
    email_actif = fields.Boolean()
    email_smtp_server = fields.String()
    email_smtp_port = fields.Integer()
    email_address = fields.Email()
    email_password = fields.String(load_only=True)
    
    # Préférences
    alertes_impayés_actif = fields.Boolean()
    relances_sms_groupes = fields.Boolean()
    confirmations_inscription = fields.Boolean()
    
    date_creation = fields.DateTime(dump_only=True)
    date_modification = fields.DateTime(dump_only=True)

notif_config_schema = NotificationConfigSchema()
