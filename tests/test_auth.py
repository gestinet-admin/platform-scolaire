"""
Tests pour authentification
"""
import pytest
from app import create_app, db
from app.models import Etablissement, Utilisateur
from app.services.auth_service import AuthService


@pytest.fixture
def app():
    """Créer une app de test"""
    app = create_app('test')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Créer un client de test"""
    return app.test_client()


@pytest.fixture
def etablissement(app):
    """Créer un établissement de test"""
    with app.app_context():
        etab = Etablissement(
            nom='École Test',
            localite='Maradi',
            email='test@ecole.local'
        )
        db.session.add(etab)
        db.session.commit()
        return etab


@pytest.fixture
def admin_user(app, etablissement):
    """Créer un utilisateur admin de test"""
    with app.app_context():
        user = AuthService.create_user(
            etablissement_id=etablissement.id,
            nom='Test',
            prenom='Admin',
            email='admin@test.local',
            password='password123',
            role='directeur'
        )
        return user


class TestAuthService:
    """Tests du service d'authentification"""
    
    def test_hash_password(self):
        """Test hashage password"""
        password = 'password123'
        hashed = AuthService.hash_password(password)
        
        assert hashed != password.encode()
        assert AuthService.verify_password(password, hashed)
    
    def test_verify_password_invalid(self):
        """Test vérification password invalide"""
        password = 'password123'
        wrong_password = 'wrongpassword'
        hashed = AuthService.hash_password(password)
        
        assert not AuthService.verify_password(wrong_password, hashed)
    
    def test_create_user_success(self, app, etablissement):
        """Test création utilisateur réussie"""
        with app.app_context():
            user = AuthService.create_user(
                etablissement_id=etablissement.id,
                nom='Dupont',
                prenom='Jean',
                email='jean@test.local',
                password='secure123',
                role='professeur'
            )
            
            assert user.id is not None
            assert user.email == 'jean@test.local'
            assert user.role == 'professeur'
            assert user.actif is True
    
    def test_create_user_duplicate_email(self, app, establecimiento, admin_user):
        """Test création user avec email déjà existant"""
        with app.app_context():
            with pytest.raises(ValueError):
                AuthService.create_user(
                    etablissement_id=etablissement.id,
                    nom='Autre',
                    prenom='User',
                    email='admin@test.local',  # Déjà utilisé
                    password='pass123',
                    role='secretaire'
                )
    
    def test_login_success(self, app, admin_user):
        """Test login réussi"""
        with app.app_context():
            result = AuthService.login('admin@test.local', 'password123')
            
            assert result is not None
            assert 'access_token' in result
            assert 'refresh_token' in result
            assert result['user']['email'] == 'admin@test.local'
    
    def test_login_wrong_password(self, app, admin_user):
        """Test login avec mauvais mot de passe"""
        with app.app_context():
            result = AuthService.login('admin@test.local', 'wrongpassword')
            assert result is None
    
    def test_login_non_existent_user(self, app):
        """Test login avec utilisateur inexistant"""
        with app.app_context():
            result = AuthService.login('nonexistent@test.local', 'password123')
            assert result is None
    
    def test_change_password_success(self, app, admin_user):
        """Test changement password réussi"""
        with app.app_context():
            success = AuthService.change_password(
                admin_user.id,
                'password123',
                'newpassword123'
            )
            
            assert success is True
            
            # Vérifier que le nouveau password fonctionne
            result = AuthService.login('admin@test.local', 'newpassword123')
            assert result is not None


class TestAuthRoutes:
    """Tests des routes d'authentification"""
    
    def test_login_endpoint_success(self, client, admin_user):
        """Test endpoint /api/auth/login réussi"""
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.local',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'admin@test.local'
    
    def test_login_endpoint_wrong_credentials(self, client, admin_user):
        """Test endpoint login avec mauvaises credentials"""
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.local',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'erreur' in data
    
    def test_login_endpoint_missing_data(self, client):
        """Test endpoint login sans données"""
        response = client.post('/api/auth/login', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'erreur' in data
    
    def test_current_user_endpoint(self, client, admin_user):
        """Test endpoint /api/auth/me"""
        # D'abord login pour obtenir token
        login_response = client.post('/api/auth/login', json={
            'email': 'admin@test.local',
            'password': 'password123'
        })
        token = login_response.get_json()['access_token']
        
        # Utiliser le token pour accéder /me
        response = client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {token}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['email'] == 'admin@test.local'
    
    def test_current_user_without_token(self, client):
        """Test /api/auth/me sans token"""
        response = client.get('/api/auth/me')
        assert response.status_code == 401
    
    def test_change_password_endpoint(self, client, admin_user):
        """Test endpoint /api/auth/change-password"""
        # Login
        login_response = client.post('/api/auth/login', json={
            'email': 'admin@test.local',
            'password': 'password123'
        })
        token = login_response.get_json()['access_token']
        
        # Changer password
        response = client.post('/api/auth/change-password',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'old_password': 'password123',
                'new_password': 'newpassword123'
            }
        )
        
        assert response.status_code == 200
        
        # Vérifier que nouveau password fonctionne
        login_response = client.post('/api/auth/login', json={
            'email': 'admin@test.local',
            'password': 'newpassword123'
        })
        assert login_response.status_code == 200
    
    def test_logout_endpoint(self, client, admin_user):
        """Test endpoint /api/auth/logout"""
        # Login
        login_response = client.post('/api/auth/login', json={
            'email': 'admin@test.local',
            'password': 'password123'
        })
        token = login_response.get_json()['access_token']
        
        # Logout
        response = client.post('/api/auth/logout',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        assert response.get_json()['message'] == 'Déconnexion réussie'
