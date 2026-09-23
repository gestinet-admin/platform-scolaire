from marshmallow import Schema, fields, validate

class EleveSchema(Schema):
    """Validation données élève"""
    
    id = fields.Integer(dump_only=True)
    nom = fields.String(required=True, validate=validate.Length(min=2, max=100))
    prenom = fields.String(required=True, validate=validate.Length(min=2, max=100))
    date_naissance = fields.Date(allow_none=True)
    numero_matricule = fields.String(allow_none=True, validate=validate.Length(max=50))
    classe_actuelle = fields.String(allow_none=True, validate=validate.Length(max=50))
    frais_scolarite_annuels = fields.Decimal(places=2, allow_none=True)
    frais_payes = fields.Decimal(places=2, dump_only=True)
    parent_id = fields.Integer(allow_none=True)
    actif = fields.Boolean(missing=True)
    date_inscription = fields.Date(allow_none=True)
    date_creation = fields.DateTime(dump_only=True)
    date_modification = fields.DateTime(dump_only=True)

eleve_schema = EleveSchema()
eleves_schema = EleveSchema(many=True)
