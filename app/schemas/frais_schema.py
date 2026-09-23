from marshmallow import Schema, fields, validate

class PaiementSchema(Schema):
    """Validation données paiement frais"""
    
    id = fields.Integer(dump_only=True)
    inscription_id = fields.Integer(required=True)
    montant = fields.Decimal(required=True, places=2, validate=validate.Range(min=100))
    date_paiement = fields.DateTime(dump_only=True)
    methode = fields.String(required=True, validate=validate.OneOf(['especes', 'virement', 'mobile_money']))
    reference = fields.String(allow_none=True)
    remarques = fields.String(allow_none=True)
    enregistre_par_id = fields.Integer(dump_only=True)
    date_creation = fields.DateTime(dump_only=True)

paiement_schema = PaiementSchema()
paiements_schema = PaiementSchema(many=True)
