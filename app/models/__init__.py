"""
Modèles SQLAlchemy
"""
from datetime import datetime
from app import db


class Etablissement(db.Model):
    """Modèle pour un établissement scolaire"""
    __tablename__ = 'etablissements'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False, unique=True)
    localite = db.Column(db.String(255))
    region = db.Column(db.String(100))
    contact_principal = db.Column(db.String(100))
    email = db.Column(db.String(255))
    telephone = db.Column(db.String(20))
    
    # Branding
    couleur_primaire = db.Column(db.String(7), default='#1F4E78')
    couleur_secondaire = db.Column(db.String(7), default='#4472C4')
    logo_url = db.Column(db.String(500))
    domaine_custom = db.Column(db.String(255))
    
    # Config
    devise_locale = db.Column(db.String(3), default='XOF')
    fuseau_horaire = db.Column(db.String(50), default='Africa/Niamey')
    
    # API
    cle_api = db.Column(db.String(255), unique=True)
    
    # Status
    statut = db.Column(db.String(50), default='actif')
    
    # Timestamps
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    utilisateurs = db.relationship('Utilisateur', backref='etablissement', lazy=True)
    eleves = db.relationship('Eleve', backref='etablissement', lazy=True)
    inscriptions = db.relationship('Inscription', backref='etablissement', lazy=True)
    
    def __repr__(self):
        return f'<Etablissement {self.nom}>'


class Utilisateur(db.Model):
    """Modèle pour un utilisateur (directeur, secrétaire, prof, parent)"""
    __tablename__ = 'utilisateurs'
    
    id = db.Column(db.Integer, primary_key=True)
    etablissement_id = db.Column(db.Integer, db.ForeignKey('etablissements.id'), nullable=False)
    
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(20))
    
    # Auth
    mot_de_passe_hash = db.Column(db.String(255), nullable=False)
    
    # Rôle
    role = db.Column(db.String(50), nullable=False)  # 'directeur', 'secretaire', 'professeur', 'parent', 'admin'
    
    # Accès
    actif = db.Column(db.Boolean, default=True)
    date_dernier_login = db.Column(db.DateTime)
    
    # Timestamps
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique par établissement
    __table_args__ = (
        db.UniqueConstraint('etablissement_id', 'email', name='uq_etablissement_email'),
    )
    
    def __repr__(self):
        return f'<Utilisateur {self.prenom} {self.nom} ({self.role})>'
    
    def to_dict(self):
        """Convertir en dictionnaire (pour JSON)"""
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'role': self.role,
            'etablissement_id': self.etablissement_id,
        }


class Eleve(db.Model):
    """Modèle pour un élève"""
    __tablename__ = 'eleves'
    
    id = db.Column(db.Integer, primary_key=True)
    etablissement_id = db.Column(db.Integer, db.ForeignKey('etablissements.id'), nullable=False)
    
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date)
    numero_matricule = db.Column(db.String(50), unique=True)
    
    # Parent/Tuteur
    parent_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    
    # Classe
    classe_actuelle = db.Column(db.String(50))
    
    # Frais
    frais_scolarite_annuels = db.Column(db.Numeric(10, 2))
    frais_payes = db.Column(db.Numeric(10, 2), default=0)
    
    # Status
    actif = db.Column(db.Boolean, default=True)
    date_inscription = db.Column(db.Date)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    parent = db.relationship('Utilisateur', backref='enfants')
    inscriptions = db.relationship('Inscription', backref='eleve', lazy=True)
    
    def __repr__(self):
        return f'<Eleve {self.prenom} {self.nom}>'
    
    def nom_complet(self):
        return f'{self.prenom} {self.nom}'


class Inscription(db.Model):
    """Modèle pour une inscription (élève à une année scolaire)"""
    __tablename__ = 'inscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    etablissement_id = db.Column(db.Integer, db.ForeignKey('etablissements.id'), nullable=False)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleves.id'), nullable=False)
    
    # Année scolaire
    annee_scolaire = db.Column(db.String(10), nullable=False)  # Ex: "2026-2027"
    
    # Frais
    frais_total = db.Column(db.Numeric(10, 2))
    frais_incluent_inscription = db.Column(db.Boolean, default=True)
    
    # Status
    statut = db.Column(db.String(50), default='en_attente')  # 'en_attente', 'confirmee', 'payee', 'annulee'
    
    # Timestamps
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    date_confirmation = db.Column(db.DateTime)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Meta
    remarques = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Inscription {self.eleve.nom_complet()} {self.annee_scolaire}>'
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'eleve_id': self.eleve_id,
            'eleve_nom': self.eleve.nom_complet(),
            'annee_scolaire': self.annee_scolaire,
            'frais_total': str(self.frais_total),
            'statut': self.statut,
            'date_inscription': self.date_inscription.isoformat(),
        }


class PaiementFrais(db.Model):
    """Enregistrement des paiements de frais scolaires"""
    __tablename__ = 'paiements_frais'
    
    id = db.Column(db.Integer, primary_key=True)
    inscription_id = db.Column(db.Integer, db.ForeignKey('inscriptions.id'), nullable=False)
    enregistre_par_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    date_paiement = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    methode = db.Column(db.String(50))
    reference = db.Column(db.String(100))
    remarques = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    inscription = db.relationship('Inscription', backref='paiements')
    enregistre_par = db.relationship('Utilisateur', backref='paiements_enregistres')
    
    def __repr__(self):
        return f'<PaiementFrais {self.id}: {self.montant} CFA>'


class NotificationConfig(db.Model):
    """Configuration des notifications pour une école"""
    __tablename__ = 'notification_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    etablissement_id = db.Column(db.Integer, db.ForeignKey('etablissements.id'), nullable=False)
    
    # SMS
    sms_actif = db.Column(db.Boolean, default=True)
    sms_operateur = db.Column(db.String(50))  # orange, airtel, maroc_telecom, zain
    sms_api_key = db.Column(db.String(255))  # Clé API chiffrée
    sms_sender_id = db.Column(db.String(20))  # ID du sender
    
    # WhatsApp
    whatsapp_actif = db.Column(db.Boolean, default=False)
    whatsapp_api_key = db.Column(db.String(255))  # Clé API chiffrée
    whatsapp_phone_id = db.Column(db.String(50))  # Numéro WhatsApp Business
    
    # Email
    email_actif = db.Column(db.Boolean, default=False)
    email_smtp_server = db.Column(db.String(100))
    email_smtp_port = db.Column(db.Integer)
    email_address = db.Column(db.String(100))
    email_password = db.Column(db.String(255))  # Chiffrée
    
    # Préférences
    alertes_impayés_actif = db.Column(db.Boolean, default=True)
    relances_sms_groupes = db.Column(db.Boolean, default=True)
    confirmations_inscription = db.Column(db.Boolean, default=True)
    
    # Audit
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    etablissement = db.relationship('Etablissement', backref='notification_config')
    
    def __repr__(self):
        return f'<NotificationConfig {self.id}: {self.sms_operateur}>'
