from marshmallow import Schema, fields, validate

class InscriptionSchema(Schema):
    """Validation données inscription"""
    
    id = fields.Integer(dump_only=True)
    eleve_id = fields.Integer(required=True)
    etablissement_id = fields.Integer(dump_only=True)
    annee_scolaire = fields.String(required=True, validate=validate.Length(equal=9))
    classe = fields.String(required=True, validate=validate.Length(min=2, max=50))
    frais_total = fields.Decimal(required=True, places=2, validate=validate.Range(min=1000))
    frais_inscription = fields.Decimal(places=2, allow_none=True)
    frais_payes = fields.Decimal(places=2, dump_only=True)
    statut = fields.String(dump_only=True)
    date_inscription = fields.DateTime(dump_only=True)
    date_confirmation = fields.DateTime(allow_none=True, dump_only=True)
    date_modification = fields.DateTime(dump_only=True)
    remarques = fields.String(allow_none=True)

inscription_schema = InscriptionSchema()
inscriptions_schema = InscriptionSchema(many=True)
