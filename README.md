# PlatformScolaire — Gestion Scolaire Niger

**Version**: 1.0 Sprint 1  
**Status**: Backend Authentification ✅ | Frontend: À venir Phase 2

---

## 🎯 Qu'est-ce que c'est?

Plateforme Web **auto-hébergée** pour gestion administrative d'établissements scolaires:
- Inscriptions digitales
- Gestion des frais de scolarité
- Bulletins scolaires sécurisés
- Notifications SMS aux parents
- Dashboard directeur

Chaque école reçoit sa **propre instance** (base de données + serveur) après formation.

---

## 📁 Structure du Projet

```
platform_scolaire/
├── app/
│   ├── models/           # Modèles SQLAlchemy
│   ├── routes/           # API endpoints (blueprints)
│   ├── services/         # Business logic
│   ├── utils/            # Helpers, validators
│   └── __init__.py       # Initialisation Flask
│
├── migrations/           # Migrations DB (Alembic)
├── tests/                # Tests unitaires
├── requirements.txt      # Dépendances Python
├── config.py             # Configuration (dev/prod/test)
├── wsgi.py               # Entry point Gunicorn
├── setup.py              # Script initialisation
└── README.md             # Ce fichier
```

---

## 🚀 Démarrage Rapide

### 1️⃣ Prérequis

- Python 3.8+
- PostgreSQL 12+ (installation locale recommandée)
- pip

### 2️⃣ Installation

```bash
# Cloner/télécharger le projet
cd platform_scolaire

# Créer environnement virtuel Python
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate     # Windows

# Installer dépendances
pip install -r requirements.txt

# Copier config exemple
cp .env.example .env
```

### 3️⃣ Configurer la Base de Données

**Option A: PostgreSQL local**

```bash
# Créer la base de données
createdb platform_scolaire_dev

# Éditer .env
# DATABASE_URL=postgresql://user:password@localhost:5432/platform_scolaire_dev
```

**Option B: SQLite pour développement rapide**

```bash
# Dans .env, remplacer DATABASE_URL par:
# DATABASE_URL=sqlite:///platform_scolaire.db
```

### 4️⃣ Initialiser la Base

```bash
python setup.py
```

Output:
```
✅ Initialisation de la base de données...
  → Création des tables...
  ✓ Tables créées
  → Création établissement par défaut...
  ✓ Établissement créé (ID: 1)
  → Création utilisateur admin...
  ✓ Admin créé (ID: 1)

  ⚠️  EMAIL: admin@ecole.local
  ⚠️  PASSWORD: password123
  ⚠️  À CHANGER ABSOLUMENT EN PRODUCTION!

✅ Initialisation terminée!
```

### 5️⃣ Lancer le Serveur

```bash
python wsgi.py
```

Serveur accessible à `http://localhost:5000`

---

## 🔌 API Endpoints (Sprint 1)

### Authentification

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@ecole.local",
    "password": "password123"
  }'

# Response:
{
  "message": "Connexion réussie",
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": 1,
    "nom": "Admin",
    "prenom": "Directeur",
    "email": "admin@ecole.local",
    "role": "directeur",
    "etablissement_id": 1
  }
}
```

```bash
# Récupérer utilisateur connecté
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer <access_token>"

# Changer mot de passe
curl -X POST http://localhost:5000/api/auth/change-password \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "password123",
    "new_password": "nouveau_mdp_secure"
  }'

# Refresh token
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"

# Logout
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer <access_token>"
```

---

## 🗄️ Base de Données

### Schéma Sprint 1

Tables créées:
- `etablissements` — Établissements scolaires
- `utilisateurs` — Directeur, secrétaire, profs, parents
- `eleves` — Élèves
- `inscriptions` — Inscriptions (élève + année scolaire)

### Exemple: Créer un élève

```python
from app import create_app, db
from app.models import Eleve, Utilisateur

app = create_app()

with app.app_context():
    # Créer un élève
    eleve = Eleve(
        etablissement_id=1,
        nom='Issoufou',
        prenom='Mamadou',
        date_naissance='2015-03-15',
        numero_matricule='MAT2026001',
        classe_actuelle='6eme',
        frais_scolarite_annuels=150000,
    )
    db.session.add(eleve)
    db.session.commit()
    print(f"Élève créé: {eleve.id}")
```

---

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=app

# Test spécifique
pytest tests/test_auth.py
```

---

## 🔒 Sécurité

### En Développement
- ✅ Passwords hashés (bcrypt)
- ✅ JWT tokens (access + refresh)
- ✅ Validation données

### En Production (TODO)
- [ ] HTTPS/SSL obligatoire
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Audit logs complets
- [ ] 2FA (optionnel)

---

## 📦 Déploiement

### Production avec Gunicorn

```bash
# Installer Gunicorn (dans requirements.txt déjà)
pip install gunicorn

# Lancer
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### Avec Nginx (reverse proxy)

```nginx
server {
    listen 80;
    server_name monecole.ne;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📋 Prochaines Étapes (Phase 2)

- [ ] CRUD Élèves complet
- [ ] CRUD Inscriptions
- [ ] Gestion Paiements frais
- [ ] SMS Orange intégration
- [ ] Frontend (HTML/CSS/JS)
- [ ] Dashboard Directeur
- [ ] Offline queue local
- [ ] Tests complets

---

## 🤝 Support / Questions

Pour questions ou issues:
1. Consulter la documentation `/docs` (à venir)
2. Vérifier les logs: `app.log`
3. Contactez support@platformscolaire.ne

---

## 📄 License

Propriétaire - Tous droits réservés

---

## ✅ Checklist Démarrage

- [ ] Python 3.8+ installé
- [ ] PostgreSQL ou SQLite configuré
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] `.env` configuré
- [ ] `python setup.py` exécuté
- [ ] `python wsgi.py` démarré
- [ ] Login testé avec admin@ecole.local / password123

🚀 **Prêt à développer!**
