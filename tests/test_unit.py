import pytest
from click.testing import CliRunner
from cli.epic import epic
from cli.commands.auth_commands import auth
from cli.commands.user_commands import user
from cli.commands.client_commands import client
from cli.commands.contract_commands import contract
from cli.commands.event_commands import event


# Helper pour mocker l'authentification
def mock_authenticated_user(monkeypatch, user_data=None):
    """Helper pour mocker un utilisateur authentifié"""
    if user_data is None:
        user_data = {"user_id": 1, "departement": "Gestion"}
    
    def mock_get_token():
        return "fake_token"
    
    def mock_get_current_user_info():
        return user_data
    
    def mock_jwt_decode(token, key, algorithms):
        return user_data
    
    monkeypatch.setattr("services.auth_service.get_token", mock_get_token)
    monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user_info)
    monkeypatch.setattr("services.auth_service.jwt.decode", mock_jwt_decode)


class TestAuth:
    """Tests pour les commandes d'authentification"""
    
    def test_login_success(self, monkeypatch):
        runner = CliRunner()

        def mock_auth_service_login(self, session, username, password):
            return True, "fake_token", "Connexion réussie"

        monkeypatch.setattr("services.auth_service.AuthService.login", mock_auth_service_login)

        result = runner.invoke(auth, ['login'], input='user\npass\n')
        assert "Connexion réussie" in result.output
        assert result.exit_code == 0

    def test_login_fail(self, monkeypatch):
        runner = CliRunner()

        def mock_auth_service_login(self, session, username, password):
            return False, None, "Utilisateur non trouvé"

        monkeypatch.setattr("services.auth_service.AuthService.login", mock_auth_service_login)

        result = runner.invoke(auth, ['login'], input='user\npass\n')
        assert "Utilisateur non trouvé" in result.output

    def test_logout_success(self, monkeypatch):
        runner = CliRunner()

        def mock_auth_service_logout(self):
            return True, "Déconnexion réussie"

        monkeypatch.setattr("services.auth_service.AuthService.logout", mock_auth_service_logout)

        result = runner.invoke(auth, ['logout'])
        assert "Déconnexion réussie" in result.output


class TestUser:
    """Tests pour les commandes utilisateur"""
    
    def test_user_list(self, monkeypatch):
        runner = CliRunner()

        fake_users = [
            type('User', (), {
                'id': 1,
                'username': 'alice',
                'employee_number': 101,
                'email': 'alice@test.com',
                'first_name': 'Alice',
                'last_name': 'Wright'
            })(),
            type('User', (), {
                'id': 2,
                'username': 'bob',
                'employee_number': 102,
                'email': 'bob@test.com',
                'first_name': 'Bob',
                'last_name': 'Leponge'
            })()
        ]

        def mock_get_users(self):
            return fake_users

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        monkeypatch.setattr("services.user_services.UserService.get_users", mock_get_users)

        result = runner.invoke(user, ['list'])
        assert "alice" in result.output
        assert "bob" in result.output
        assert result.exit_code == 0

    def test_user_create_success(self, monkeypatch):
        runner = CliRunner()

        def mock_create_user(self, **kwargs):
            return True, "L'utilisateur a été créé avec succès"

        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]

        def mock_get_departement_id_by_name(name):
            dept_map = {"Gestion": 1, "Commercial": 2, "Support": 3}
            return dept_map.get(name)

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        monkeypatch.setattr("services.user_services.UserService.create_user", mock_create_user)
        monkeypatch.setattr("services.departement_services.get_departement_choice", mock_get_departement_choice)
        monkeypatch.setattr("services.departement_services.get_departement_id_by_name", mock_get_departement_id_by_name)

        input_data = 'test_user\n123\ntest@test.com\nTest\nUser\npassword\npassword\nGestion\n'
        result = runner.invoke(user, ['create'], input=input_data)
        assert "L'utilisateur a été créé avec succès" in result.output

    def test_user_create_invalid_email(self, monkeypatch):
        runner = CliRunner()

        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        monkeypatch.setattr("services.departement_services.get_departement_choice", mock_get_departement_choice)

        # Email invalide puis valide
        input_data = 'test_user\n123\ninvalid_email\ntest@test.com\nTest\nUser\npassword\npassword\nGestion\n'
        result = runner.invoke(user, ['create'], input=input_data)
        assert "Format d'email invalide" in result.output


class TestClient:
    """Tests pour les commandes client"""
    
    def test_client_create_success(self, monkeypatch):
        runner = CliRunner()

        def mock_create_client(self, **kwargs):
            return True, "Le client a été créé"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        monkeypatch.setattr("services.client_services.ClientService.create_client", mock_create_client)

        input_data = 'Test Client\nContact Info\ntest@client.com\n0123456789\n'
        result = runner.invoke(client, ['create'], input=input_data)
        assert "Le client a été créé" in result.output

    def test_get_clients(self, monkeypatch):
        runner = CliRunner()

        fake_clients = [
            type('Client', (), {
                'id': 1,
                'fullname': 'Client Test',
                'email': 'client@test.com',
                'phone_number': '0123456789',
                'commercial_id': 1,
                'commercial_first_name': 'John',
                'commercial_last_name': 'Doe'
            })()
        ]

        def mock_get_clients(self):
            return True, fake_clients, "Clients récupérés"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        monkeypatch.setattr("services.client_services.ClientService.get_clients", mock_get_clients)

        result = runner.invoke(client, ['get-clients'])
        assert "Client Test" in result.output


class TestContract:
    """Tests pour les commandes contrat"""
    
    def test_contract_create_success(self, monkeypatch):
        runner = CliRunner()

        def mock_create_contract(self, **kwargs):
            return True, "Le contrat a été créé"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        monkeypatch.setattr("services.contract_services.ContractService.create_contract", mock_create_contract)

        input_data = 'Contrat Test\n1\n1000.50\n'
        result = runner.invoke(contract, ['create'], input=input_data)
        assert "Le contrat a été créé" in result.output


class TestEvent:
    """Tests pour les commandes événement"""
    
    def test_event_create_success(self, monkeypatch):
        runner = CliRunner()

        def mock_create_event(self, **kwargs):
            return True, "L'évènement a été créé"

        def mock_get_current_user_info():
            return {"user_id": 1, "departement": "Gestion"}

        monkeypatch.setattr("services.event_services.EventService.create_event", mock_create_event)
        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user_info)

        input_data = '1\n2024-12-25 10:00:00\n50\nParis\nTest event\n1\n'
        result = runner.invoke(event, ['create'], input=input_data)
        assert "L'évènement a été créé" in result.output


class TestAuthDecorators:
    """Tests pour les décorateurs d'authentification"""
    
    def test_require_auth_without_login(self, monkeypatch):
        runner = CliRunner()

        def mock_get_current_user_info():
            return None

        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user_info)

        result = runner.invoke(client, ['get-clients'])
        assert "Vous devez être connecté" in result.output or "Vous n'êtes pas connecté" in result.output

    def test_require_departement_wrong_dept(self, monkeypatch):
        runner = CliRunner()

        def mock_get_current_user_info():
            return {"user_id": 1, "departement": "Support"}

        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user_info)

        # Un utilisateur Support ne peut pas créer d'utilisateur (réservé à Gestion)
        result = runner.invoke(user, ['create'])
        assert "Accès refusé" in result.output


class TestInputValidation:
    """Tests pour la validation des entrées"""
    
    def test_invalid_email_format(self, monkeypatch):
        runner = CliRunner()
        
        def mock_create_user(self, **kwargs):
            return False, "Format d'email invalide"
        
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        monkeypatch.setattr("services.user_services.UserService.create_user", mock_create_user)
        
        # Test avec email invalide
        input_data = 'testuser\n123\nemail_invalide\nTest\nUser\npassword\n1\n'
        result = runner.invoke(user, ['create'], input=input_data)
        assert "Format d'email invalide" in result.output
    
    def test_invalid_date_format(self, monkeypatch):
        runner = CliRunner()
        
        def mock_get_current_user_info():
            return {"user_id": 1, "departement": "Support"}
        
        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user_info)
        
        # Test avec format de date invalide dans event update
        input_data = '1\ndate_invalide\n'
        result = runner.invoke(event, ['update', '1'], input=input_data)
        assert result.exit_code != 0  # Devrait échouer avec une date invalide


class TestErrorMessages:
    """Tests pour les messages d'erreur"""
    
    def test_authentication_error_message(self, monkeypatch):
        runner = CliRunner()
        
        def mock_get_current_user_info():
            return None
        
        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user_info)
        
        # Test d'accès sans authentification
        result = runner.invoke(user, ['create'])
        assert "connecté" in result.output.lower()  # Message d'erreur d'authentification
