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
    
    def test_contract_create_failure(self, monkeypatch):
        runner = CliRunner()

        def mock_create_contract(self, **kwargs):
            return False, "Erreur lors de la création du contrat"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        monkeypatch.setattr("services.contract_services.ContractService.create_contract", mock_create_contract)

        input_data = 'Contrat Test\n1\n1000.50\n'
        result = runner.invoke(contract, ['create'], input=input_data)
        assert "Erreur lors de la création du contrat" in result.output
    
    def test_contract_update_success(self, monkeypatch):
        runner = CliRunner()

        def mock_update_contract(self, **kwargs):
            return True, "Le contrat a été mis à jour"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        monkeypatch.setattr("services.contract_services.ContractService.update_contract", mock_update_contract)

        # Test de mise à jour avec signature
        result = runner.invoke(contract, ['update', '--contract-id', '1', '--sign'])
        assert "Le contrat a été mis à jour" in result.output
    
    def test_contract_update_failure(self, monkeypatch):
        runner = CliRunner()

        def mock_update_contract(self, **kwargs):
            return False, "Erreur lors de la mise à jour du contrat"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        monkeypatch.setattr("services.contract_services.ContractService.update_contract", mock_update_contract)

        result = runner.invoke(contract, ['update', '--contract-id', '1', '--sign'])
        assert "Erreur lors de la mise à jour du contrat" in result.output
    
    def test_contract_update_with_paid_amount(self, monkeypatch):
        runner = CliRunner()

        def mock_update_contract(self, **kwargs):
            return True, "Le contrat a été mis à jour"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        monkeypatch.setattr("services.contract_services.ContractService.update_contract", mock_update_contract)

        # Test de mise à jour avec montant payé
        result = runner.invoke(contract, ['update', '--contract-id', '1', '--paid-amount', '500.00'])
        assert "Le contrat a été mis à jour" in result.output
    
    def test_contract_update_no_auth(self, monkeypatch):
        runner = CliRunner()
        
        def mock_get_current_user_info():
            return None
        
        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user_info)
        
        result = runner.invoke(contract, ['update', '--contract-id', '1'])
        assert "connecté" in result.output.lower()  # Message d'erreur d'authentification
    
    def test_contract_list_success(self, monkeypatch):
        runner = CliRunner()

        # Mock des contrats
        fake_contracts = [
            type('Contract', (), {
                'id': 1,
                'fullname': 'Client Test',
                'title': 'Contrat Test',
                'created_at': type('datetime', (), {'strftime': lambda self, fmt: '2024-01-01'})(),
                'status': True,
                'amount': 1000.0,
                'paid_amount': 500.0
            })()
        ]

        def mock_get_contract_list(self):
            return True, fake_contracts, "Contrats récupérés"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        monkeypatch.setattr("services.contract_services.ContractService.get_contract_list", mock_get_contract_list)

        result = runner.invoke(contract, ['list'])
        assert "Client Test" in result.output
        assert "Contrat Test" in result.output
        assert "Contrats récupérés" in result.output
    
    def test_contract_list_empty(self, monkeypatch):
        runner = CliRunner()

        def mock_get_contract_list(self):
            return False, [], "Aucun contrat trouvé"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        monkeypatch.setattr("services.contract_services.ContractService.get_contract_list", mock_get_contract_list)

        result = runner.invoke(contract, ['list'])
        assert "Aucun contrat trouvé" in result.output
    
    def test_contracts_not_sign_success(self, monkeypatch):
        runner = CliRunner()

        # Mock des contrats non signés
        fake_contracts = [
            type('Contract', (), {
                'id': 2,
                'fullname': 'Client Non Signé',
                'title': 'Contrat Non Signé',
                'created_at': type('datetime', (), {'strftime': lambda self, fmt: '2024-01-01'})(),
                'status': False,
                'amount': 2000.0,
                'paid_amount': 0.0
            })()
        ]

        def mock_get_contract_list_not_sign(self):
            return True, fake_contracts, "Contrats non signés récupérés"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        monkeypatch.setattr("services.contract_services.ContractService.get_contract_list_not_sign", mock_get_contract_list_not_sign)

        result = runner.invoke(contract, ['contracts-not-sign'])
        assert "Client Non Signé" in result.output
        assert "Contrats non signés récupérés" in result.output
    
    def test_contracts_not_sign_empty(self, monkeypatch):
        runner = CliRunner()

        def mock_get_contract_list_not_sign(self):
            return False, [], "Aucun contrat non signé"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        monkeypatch.setattr("services.contract_services.ContractService.get_contract_list_not_sign", mock_get_contract_list_not_sign)

        result = runner.invoke(contract, ['contracts-not-sign'])
        assert "Aucun contrat non signé" in result.output
    
    def test_contracts_not_paid_success(self, monkeypatch):
        runner = CliRunner()

        # Mock des contrats non entièrement payés
        fake_contracts = [
            type('Contract', (), {
                'id': 3,
                'fullname': 'Client Impayé',
                'title': 'Contrat Impayé',
                'created_at': type('datetime', (), {'strftime': lambda self, fmt: '2024-01-01'})(),
                'status': True,
                'amount': 1500.0,
                'paid_amount': 750.0
            })()
        ]

        def mock_get_contract_list_not_fully_paid(self):
            return True, fake_contracts, "Contrats non entièrement payés récupérés"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        monkeypatch.setattr("services.contract_services.ContractService.get_contract_list_not_fully_paid", mock_get_contract_list_not_fully_paid)

        result = runner.invoke(contract, ['contracts-not-paid'])
        assert "Client Impayé" in result.output
        assert "Contrats non entièrement payés récupérés" in result.output
    
    def test_contracts_not_paid_empty(self, monkeypatch):
        runner = CliRunner()

        def mock_get_contract_list_not_fully_paid(self):
            return False, [], "Aucun contrat impayé"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        monkeypatch.setattr("services.contract_services.ContractService.get_contract_list_not_fully_paid", mock_get_contract_list_not_fully_paid)

        result = runner.invoke(contract, ['contracts-not-paid'])
        assert "Aucun contrat impayé" in result.output
    
    def test_contract_update_prompt_for_id(self, monkeypatch):
        runner = CliRunner()

        def mock_update_contract(self, **kwargs):
            return True, "Le contrat a été mis à jour"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        monkeypatch.setattr("services.contract_services.ContractService.update_contract", mock_update_contract)

        # Test sans spécifier l'ID (sera demandé en prompt)
        result = runner.invoke(contract, ['update'], input='1\n')
        assert "Le contrat a été mis à jour" in result.output

    def test_contract_commands_import(self):
        """Test pour forcer l'import du module contract_commands pour la couverture"""
        from cli.commands.contract_commands import contract
        assert contract is not None
        
        # Vérifier que les commandes existent
        commands = contract.commands
        command_names = [cmd.name for cmd in commands.values()]
        
        expected_commands = ['create', 'update', 'list', 'contracts-not-sign', 'contracts-not-paid']
        for cmd in expected_commands:
            assert cmd in command_names, f"Commande {cmd} manquante"

    def test_contract_list_with_no_created_at(self, monkeypatch):
        runner = CliRunner()

        # Mock des contrats avec created_at = None
        fake_contracts = [
            type('Contract', (), {
                'id': 1,
                'fullname': 'Client Test',
                'title': 'Contrat Test',
                'created_at': None,  # Test du cas où created_at est None
                'status': True,
                'amount': 1000.0,
                'paid_amount': 500.0
            })()
        ]

        def mock_get_contract_list(self):
            return True, fake_contracts, "Contrats récupérés"

        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        monkeypatch.setattr("services.contract_services.ContractService.get_contract_list", mock_get_contract_list)

        result = runner.invoke(contract, ['list'])
        assert "N/A" in result.output  # Devrait afficher N/A pour la date
    
    def test_contract_access_denied_wrong_department(self, monkeypatch):
        runner = CliRunner()
        
        # Mock authentification avec département non autorisé
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Support"})
        
        result = runner.invoke(contract, ['create'])
        assert "Accès refusé" in result.output or "access" in result.output.lower()


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


class TestEventCommands:
    """Tests unitaires pour les commandes d'événements CLI"""

    @pytest.fixture
    def mock_auth_success(self, monkeypatch):
        """Mock pour une authentification réussie avec département Gestion"""
        def mock_get_current_user():
            return {"user_id": 1, "username": "admin", "departement": "Gestion"}
        
        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user)

    @pytest.fixture
    def mock_auth_support(self, monkeypatch):
        """Mock pour une authentification réussie avec département Support"""
        def mock_get_current_user():
            return {"user_id": 2, "username": "support_user", "departement": "Support"}
        
        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user)

    def test_event_create_success(self, monkeypatch, mock_auth_success):
        """Test de création d'événement avec succès"""
        # Mock du service
        def mock_create_event(self, contract_id, start_date, attendees, location, notes, support_id):
            return True, "L'évènement a été crée"
        
        monkeypatch.setattr("services.event_services.EventService.create_event", mock_create_event)

        # Test de la commande
        runner = CliRunner()
        result = runner.invoke(event, [
            'create',
            '--contract-id', '1',
            '--start', '2024-12-25 10:00:00',
            '--attendees', '50',
            '--location', 'Salle de conférence',
            '--notes', 'Événement important',
            '--support-id', '2'
        ])

        assert result.exit_code == 0
        assert "L'évènement a été crée" in result.output

    def test_event_create_failure(self, monkeypatch, mock_auth_success):
        """Test de création d'événement avec échec"""
        # Mock du service retournant une erreur
        def mock_create_event(self, contract_id, start_date, attendees, location, notes, support_id):
            return False, "le contrat n'existe pas"
        
        monkeypatch.setattr("services.event_services.EventService.create_event", mock_create_event)

        runner = CliRunner()
        result = runner.invoke(event, [
            'create',
            '--contract-id', '999',
            '--start', '2024-12-25 10:00:00',
            '--attendees', '50',
            '--location', 'Salle de conférence',
            '--notes', '',
            '--support-id', ''
        ])

        assert result.exit_code == 0
        assert "le contrat n'existe pas" in result.output

    def test_event_create_invalid_support_id(self, monkeypatch, mock_auth_success):
        """Test de création d'événement avec ID support invalide"""
        def mock_create_event(self, contract_id, start_date, attendees, location, notes, support_id):
            return False, "ID du support n'est pas unmembre de l'équipe support"
        
        monkeypatch.setattr("services.event_services.EventService.create_event", mock_create_event)

        runner = CliRunner()
        result = runner.invoke(event, [
            'create',
            '--contract-id', '1',
            '--start', '2024-12-25 10:00:00',
            '--attendees', '50',
            '--location', 'Salle de conférence',
            '--notes', '',
            '--support-id', '999'
        ])

        assert result.exit_code == 0
        assert "membre de l'équipe support" in result.output

    def test_event_update_success_gestion(self, monkeypatch, mock_auth_success):
        """Test de mise à jour d'événement par département Gestion"""
        def mock_update_event(self, event_id, **kwargs):
            return True, "L'événement a été mis à jour avec succès"
        
        monkeypatch.setattr("services.event_services.EventService.update_event", mock_update_event)

        runner = CliRunner()
        result = runner.invoke(event, [
            'update',
            '--event-id', '1'
        ], input='\n\n\nNouveau lieu\nNouveaux notes\n3\n')

        assert result.exit_code == 0
        assert "L'événement a été mis à jour avec succès" in result.output

    def test_event_update_success_support(self, monkeypatch, mock_auth_support):
        """Test de mise à jour d'événement par département Support"""
        def mock_update_event(self, event_id, **kwargs):
            return True, "L'événement a été mis à jour avec succès"
        
        monkeypatch.setattr("services.event_services.EventService.update_event", mock_update_event)

        runner = CliRunner()
        result = runner.invoke(event, [
            'update',
            '--event-id', '1'
        ], input='\n\n\n\nNouveau lieu\n\n\n')

        assert result.exit_code == 0
        assert "L'événement a été mis à jour avec succès" in result.output

    def test_event_update_not_found(self, monkeypatch, mock_auth_success):
        """Test de mise à jour d'événement inexistant"""
        def mock_update_event(self, event_id, **kwargs):
            return False, "Evenement introuvable"
        
        monkeypatch.setattr("services.event_services.EventService.update_event", mock_update_event)

        runner = CliRunner()
        result = runner.invoke(event, [
            'update',
            '--event-id', '999'
        ], input='\n\n\n\n\n\n\n')

        assert result.exit_code == 0
        assert "Evenement introuvable" in result.output

    def test_event_update_access_denied(self, monkeypatch, mock_auth_support):
        """Test de mise à jour refusée pour Support"""
        def mock_update_event(self, event_id, **kwargs):
            return False, "Vous ne pouvez mettre à jour que les événements qui vous sont attribués"
        
        monkeypatch.setattr("services.event_services.EventService.update_event", mock_update_event)

        runner = CliRunner()
        result = runner.invoke(event, [
            'update',
            '--event-id', '1'
        ], input='\n\n\n\n\n\n\n')

        assert result.exit_code == 0
        assert "qui vous sont attribués" in result.output

    def test_event_update_invalid_date_format(self, monkeypatch, mock_auth_success):
        """Test de mise à jour avec format de date invalide"""
        def mock_update_event(self, event_id, **kwargs):
            return True, "L'événement a été mis à jour avec succès"
        
        monkeypatch.setattr("services.event_services.EventService.update_event", mock_update_event)

        runner = CliRunner()
        # Saisir d'abord une date invalide, puis une date valide
        result = runner.invoke(event, [
            'update',
            '--event-id', '1'
        ], input='invalid-date\n2024-12-25\n\n\n\n\n\n\n')

        assert result.exit_code == 0
        assert "Format de date invalide" in result.output

    def test_event_update_invalid_attendees(self, monkeypatch, mock_auth_success):
        """Test de mise à jour avec nombre de participants invalide"""
        def mock_update_event(self, event_id, **kwargs):
            return True, "L'événement a été mis à jour avec succès"
        
        monkeypatch.setattr("services.event_services.EventService.update_event", mock_update_event)

        runner = CliRunner()
        # Saisir d'abord un nombre invalide, puis un nombre valide
        result = runner.invoke(event, [
            'update',
            '--event-id', '1'
        ], input='\n\ninvalid\n50\n\n\n\n')

        assert result.exit_code == 0
        assert "nombre entier" in result.output

    def test_event_update_negative_attendees(self, monkeypatch, mock_auth_success):
        """Test de mise à jour avec nombre de participants négatif"""
        def mock_update_event(self, event_id, **kwargs):
            return True, "L'événement a été mis à jour avec succès"
        
        monkeypatch.setattr("services.event_services.EventService.update_event", mock_update_event)

        runner = CliRunner()
        # Saisir d'abord un nombre négatif, puis un nombre valide
        result = runner.invoke(event, [
            'update',
            '--event-id', '1'
        ], input='\n\n-5\n50\n\n\n\n')

        assert result.exit_code == 0
        assert "entier positif" in result.output

    def test_event_update_invalid_support_id(self, monkeypatch, mock_auth_success):
        """Test de mise à jour avec ID support invalide"""
        def mock_update_event(self, event_id, **kwargs):
            return True, "L'événement a été mis à jour avec succès"
        
        monkeypatch.setattr("services.event_services.EventService.update_event", mock_update_event)

        runner = CliRunner()
        result = runner.invoke(event, [
            'update',
            '--event-id', '1'
        ], input='\n\n\n\n\ninvalid_id\n')

        assert result.exit_code == 0
        assert "nombre entier" in result.output

    def test_event_update_end_date_before_start(self, monkeypatch, mock_auth_success):
        """Test de mise à jour avec date de fin antérieure à date de début"""
        def mock_update_event(self, event_id, **kwargs):
            return True, "L'événement a été mis à jour avec succès"
        
        monkeypatch.setattr("services.event_services.EventService.update_event", mock_update_event)

        runner = CliRunner()
        # Date de début puis date de fin antérieure, puis date de fin correcte pour corriger
        result = runner.invoke(event, [
            'update',
            '--event-id', '1'
        ], input='2024-12-25\n2024-12-24\n2024-12-26\n\n\n\n\n')

        assert result.exit_code == 0
        assert "postérieure à la date de début" in result.output

    def test_assigned_events_with_events(self, monkeypatch, mock_auth_success):
        """Test de récupération d'événements assignés avec des événements"""
        class MockEvent:
            def __init__(self, id, start_date, end_date, attendees, location):
                self.id = id
                self.start_date = start_date
                self.end_date = end_date
                self.attendees = attendees
                self.location = location

        mock_events = [
            MockEvent(1, "2024-12-25 10:00:00", "2024-12-25 18:00:00", 50, "Salle A"),
            MockEvent(2, "2024-12-26 14:00:00", "2024-12-26 17:00:00", 30, "Salle B")
        ]

        def mock_get_events(self):
            return True, mock_events, "2 événement(s) attribué(s)"
        
        monkeypatch.setattr("services.event_services.EventService.get_events_by_support_contact_id", 
                          mock_get_events)

        runner = CliRunner()
        result = runner.invoke(event, ['assigned-events'])

        assert result.exit_code == 0
        assert "Evenement ID: 1" in result.output
        assert "Evenement ID: 2" in result.output
        assert "Salle A" in result.output
        assert "Salle B" in result.output

    def test_assigned_events_no_events(self, monkeypatch, mock_auth_success):
        """Test de récupération d'événements assignés sans événements"""
        def mock_get_events(self):
            return True, [], "Aucun événement attribué"
        
        monkeypatch.setattr("services.event_services.EventService.get_events_by_support_contact_id", 
                          mock_get_events)

        runner = CliRunner()
        result = runner.invoke(event, ['assigned-events'])

        assert result.exit_code == 0
        assert "Aucun événément affecté" in result.output

    def test_assigned_events_error(self, monkeypatch, mock_auth_success):
        """Test de récupération d'événements assignés avec erreur"""
        def mock_get_events(self):
            return False, [], "Accès réservé au département Support"
        
        monkeypatch.setattr("services.event_services.EventService.get_events_by_support_contact_id", 
                          mock_get_events)

        runner = CliRunner()
        result = runner.invoke(event, ['assigned-events'])

        assert result.exit_code == 0
        assert "Accès réservé au département Support" in result.output

    def test_event_create_unauthorized_commercial(self, monkeypatch):
        """Test de création d'événement par département Commercial (non autorisé)"""
        def mock_get_current_user():
            return {"user_id": 3, "username": "commercial", "departement": "Commercial"}
        
        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user)

        runner = CliRunner()
        result = runner.invoke(event, [
            'create',
            '--contract-id', '1',
            '--start', '2024-12-25 10:00:00',
            '--attendees', '50',
            '--location', 'Salle de conférence',
            '--notes', '',
            '--support-id', ''
        ])

        assert result.exit_code == 0  # Le décorateur ne fait que echo et return
        assert "Accès refusé" in result.output
        assert "departement(s) ('Gestion',)" in result.output

    def test_event_update_unauthorized_commercial(self, monkeypatch):
        """Test de mise à jour d'événement par département Commercial (non autorisé)"""
        def mock_get_current_user():
            return {"user_id": 3, "username": "commercial", "departement": "Commercial"}
        
        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user)

        runner = CliRunner()
        result = runner.invoke(event, [
            'update',
            '--event-id', '1'
        ])

        assert result.exit_code == 0  # Le décorateur ne fait que echo et return
        assert "Accès refusé" in result.output
        assert "departement(s) ('Gestion', 'Support')" in result.output

    def test_assigned_events_unauthorized_commercial(self, monkeypatch):
        """Test de récupération d'événements par département Commercial (non autorisé)"""
        def mock_get_current_user():
            return {"user_id": 3, "username": "commercial", "departement": "Commercial"}
        
        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user)

        runner = CliRunner()
        result = runner.invoke(event, ['assigned-events'])

        assert result.exit_code == 0  # Le décorateur ne fait que echo et return
        assert "Accès refusé" in result.output
        assert "departement(s) ('Gestion', 'Support')" in result.output

    def test_event_commands_import(self):
        """Test d'import du module event_commands"""
        from cli.commands.event_commands import event, create, event_update, get_assign_events_by_support_contact_id
        
        assert event is not None
        assert create is not None
        assert event_update is not None
        assert get_assign_events_by_support_contact_id is not None


class TestInitDB:
    """Tests pour l'initialisation de la base de données"""
    
    def test_init_db_import(self):
        """Test d'import du module init_db"""
        from database.init_db import init_db
        assert init_db is not None
        assert callable(init_db)
    
    def test_init_db_success_first_time(self, monkeypatch, capfd):
        """Test d'initialisation DB avec insertion des départements (première fois)"""
        from database.init_db import init_db
        
        # Mock pour simuler une base vide (aucun département existant)
        mock_existing_departments = set()
        
        class MockConnection:
            def execute(self, query, values=None):
                if values is None:  # SELECT query
                    # Retourner un résultat vide pour simuler aucun département existant
                    return MockResult([])
                else:  # INSERT query
                    return MockResult([])
        
        class MockResult:
            def __init__(self, rows):
                self.rows = rows
            
            def __iter__(self):
                return iter(self.rows)
        
        class MockEngine:
            def begin(self):
                return MockConnectionContext()
        
        class MockConnectionContext:
            def __enter__(self):
                return MockConnection()
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
        
        class MockMeta:
            def create_all(self, engine):
                pass  # Simuler la création des tables
        
        # Mock des objets de base de données
        monkeypatch.setattr("database.init_db.engine", MockEngine())
        monkeypatch.setattr("database.init_db.meta", MockMeta())
        
        # Mock du schéma departement
        class MockDepartement:
            class c:
                name = "name"
        
        monkeypatch.setattr("database.init_db.departement", MockDepartement())
        
        # Mock des fonctions SQL
        def mock_select(column):
            return "SELECT_QUERY"
        
        def mock_insert(table):
            return "INSERT_QUERY"
        
        monkeypatch.setattr("database.init_db.select", mock_select)
        monkeypatch.setattr("database.init_db.insert", mock_insert)
        
        # Exécuter la fonction
        init_db()
        
        # Vérifier la sortie
        captured = capfd.readouterr()
        assert "Départements ajoutés" in captured.out
        assert "Gestion" in captured.out or "Commercial" in captured.out or "Support" in captured.out
    
    def test_init_db_departments_already_exist(self, monkeypatch, capfd):
        """Test d'initialisation DB quand les départements existent déjà"""
        from database.init_db import init_db
        
        class MockConnection:
            def execute(self, query, values=None):
                if values is None:  # SELECT query
                    # Retourner tous les départements existants
                    return MockResult([("Gestion",), ("Commercial",), ("Support",)])
                else:  # INSERT query - ne devrait pas être appelé
                    raise AssertionError("INSERT ne devrait pas être appelé quand tous les départements existent")
        
        class MockResult:
            def __init__(self, rows):
                self.rows = rows
            
            def __iter__(self):
                return iter(self.rows)
        
        class MockEngine:
            def begin(self):
                return MockConnectionContext()
        
        class MockConnectionContext:
            def __enter__(self):
                return MockConnection()
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
        
        class MockMeta:
            def create_all(self, engine):
                pass
        
        # Mock des objets
        monkeypatch.setattr("database.init_db.engine", MockEngine())
        monkeypatch.setattr("database.init_db.meta", MockMeta())
        
        class MockDepartement:
            class c:
                name = "name"
        
        monkeypatch.setattr("database.init_db.departement", MockDepartement())
        
        def mock_select(column):
            return "SELECT_QUERY"
        
        def mock_insert(table):
            return "INSERT_QUERY"
        
        monkeypatch.setattr("database.init_db.select", mock_select)
        monkeypatch.setattr("database.init_db.insert", mock_insert)
        
        # Exécuter la fonction
        init_db()
        
        # Vérifier la sortie
        captured = capfd.readouterr()
        assert "Tous les départements existent déjà" in captured.out
    
    def test_init_db_partial_departments_exist(self, monkeypatch, capfd):
        """Test d'initialisation DB quand certains départements existent déjà"""
        from database.init_db import init_db
        
        class MockConnection:
            def execute(self, query, values=None):
                if values is None:  # SELECT query
                    # Seulement "Gestion" existe
                    return MockResult([("Gestion",)])
                else:  # INSERT query
                    return MockResult([])
        
        class MockResult:
            def __init__(self, rows):
                self.rows = rows
            
            def __iter__(self):
                return iter(self.rows)
        
        class MockEngine:
            def begin(self):
                return MockConnectionContext()
        
        class MockConnectionContext:
            def __enter__(self):
                return MockConnection()
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
        
        class MockMeta:
            def create_all(self, engine):
                pass
        
        # Mock des objets
        monkeypatch.setattr("database.init_db.engine", MockEngine())
        monkeypatch.setattr("database.init_db.meta", MockMeta())
        
        class MockDepartement:
            class c:
                name = "name"
        
        monkeypatch.setattr("database.init_db.departement", MockDepartement())
        
        def mock_select(column):
            return "SELECT_QUERY"
        
        def mock_insert(table):
            return "INSERT_QUERY"
        
        monkeypatch.setattr("database.init_db.select", mock_select)
        monkeypatch.setattr("database.init_db.insert", mock_insert)
        
        # Exécuter la fonction
        init_db()
        
        # Vérifier la sortie
        captured = capfd.readouterr()
        assert "Départements ajoutés" in captured.out
        # Devrait ajouter Commercial et Support (mais pas Gestion qui existe déjà)
        assert "Commercial" in captured.out or "Support" in captured.out
    
    def test_init_db_database_error(self, monkeypatch):
        """Test de gestion d'erreur lors de l'initialisation DB"""
        from database.init_db import init_db
        
        class MockEngine:
            def begin(self):
                raise Exception("Erreur de connexion à la base de données")
        
        class MockMeta:
            def create_all(self, engine):
                pass
        
        # Mock des objets pour lever une exception
        monkeypatch.setattr("database.init_db.engine", MockEngine())
        monkeypatch.setattr("database.init_db.meta", MockMeta())
        
        # La fonction devrait lever une exception
        with pytest.raises(Exception) as exc_info:
            init_db()
        
        assert "Erreur de connexion à la base de données" in str(exc_info.value)
    
    def test_init_db_meta_create_tables_error(self, monkeypatch):
        """Test de gestion d'erreur lors de la création des tables"""
        from database.init_db import init_db
        
        class MockMeta:
            def create_all(self, engine):
                raise Exception("Erreur lors de la création des tables")
        
        # Mock pour lever une exception lors de la création des tables
        monkeypatch.setattr("database.init_db.meta", MockMeta())
        
        # La fonction devrait lever une exception
        with pytest.raises(Exception) as exc_info:
            init_db()
        
        assert "Erreur lors de la création des tables" in str(exc_info.value)
    
    def test_init_db_module_execution(self, monkeypatch, capfd):
        """Test d'exécution du module init_db directement"""
        # Mock de la fonction init_db pour éviter les effets de bord
        mock_called = False
        
        def mock_init_db():
            nonlocal mock_called
            mock_called = True
            print("init_db() appelée depuis __main__")
        
        monkeypatch.setattr("database.init_db.init_db", mock_init_db)
        
        # Simuler l'exécution du module
        import database.init_db
        
        # Le module contient `if __name__ == "__main__": init_db`
        # Mais comme nous l'importons, __name__ sera le nom du module, pas "__main__"
        # Donc nous devons simuler l'exécution directe
        exec("""
if "__main__" == "__main__":
    from database.init_db import init_db
    init_db()
""")
        
        captured = capfd.readouterr()
        assert "init_db() appelée depuis __main__" in captured.out
    
    def test_init_db_integration_with_real_objects(self, monkeypatch):
        """Test d'intégration avec de vrais objets (sans connexion DB réelle)"""
        from database.init_db import init_db
        
        # Mock seulement engine.begin() pour éviter la vraie connexion DB
        class MockTransaction:
            def __enter__(self):
                return MockConnection()
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
        
        class MockConnection:
            def execute(self, query, values=None):
                if values is None:  # SELECT
                    return MockResult([])
                else:  # INSERT
                    return MockResult([])
        
        class MockResult:
            def __init__(self, rows):
                self.rows = rows
            
            def __iter__(self):
                return iter(self.rows)
        
        def mock_begin():
            return MockTransaction()
        
        # Mock seulement la connexion, pas les autres objets
        monkeypatch.setattr("database.init_db.engine.begin", mock_begin)
        
        # Cette fonction devrait s'exécuter sans erreur
        try:
            init_db()
        except Exception as e:
            # Si il y a une erreur, ce devrait être liée à la DB, pas au code
            assert "database" in str(e).lower() or "connection" in str(e).lower()

class TestUserCommands:
    """Tests unitaires complets pour les commandes utilisateur CLI"""
    
    def test_user_commands_import(self):
        """Test d'import du module user_commands"""
        from cli.commands.user_commands import user, create, update, list
        
        assert user is not None
        assert create is not None
        assert update is not None
        assert list is not None

        # Vérifier que les commandes sont bien attachées au groupe
        commands = user.commands
        command_names = [cmd.name for cmd in commands.values()]
        
        expected_commands = ['create', 'update', 'list']
        for cmd in expected_commands:
            assert cmd in command_names, f"Commande {cmd} manquante"

    def test_user_create_success(self, monkeypatch):
        """Test création d'utilisateur réussie"""
        # Mock authentification
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        # Mock des services
        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]
        
        def mock_get_departement_id_by_name(name):
            return 1
            
        def mock_create_user(self, **kwargs):
            return True, "✅ Utilisateur créé avec succès"
        
        monkeypatch.setattr("cli.commands.user_commands.get_departement_choice", mock_get_departement_choice)
        monkeypatch.setattr("cli.commands.user_commands.get_departement_id_by_name", mock_get_departement_id_by_name)
        monkeypatch.setattr("services.user_services.UserService.create_user", mock_create_user)
        
        runner = CliRunner()
        
        # Simulation des entrées utilisateur
        inputs = [
            "john_doe",      # username
            "12345",         # employee_number
            "john@epic.com", # email
            "John",          # first_name
            "Doe",           # last_name
            "password123",   # password
            "password123",   # confirmation password
            "Gestion"        # departement
        ]
        
        result = runner.invoke(user, ['create'], input='\n'.join(inputs))
        
        assert result.exit_code == 0
        assert "✅ Utilisateur créé avec succès" in result.output

    def test_user_create_invalid_employee_number(self, monkeypatch):
        """Test création d'utilisateur avec matricule invalide"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]
        
        def mock_get_departement_id_by_name(name):
            return 1
        
        monkeypatch.setattr("cli.commands.user_commands.get_departement_choice", mock_get_departement_choice)
        monkeypatch.setattr("cli.commands.user_commands.get_departement_id_by_name", mock_get_departement_id_by_name)
        
        runner = CliRunner()
        
        # Simulation: matricule invalide puis valide
        inputs = [
            "john_doe",      # username
            "abc",           # employee_number invalide
            "12345",         # employee_number valide
            "john@epic.com", # email
            "John",          # first_name
            "Doe",           # last_name
            "password123",   # password
            "password123",   # confirmation password
            "Gestion"        # departement
        ]
        
        result = runner.invoke(user, ['create'], input='\n'.join(inputs))
        
        assert "Le matricule doit être un nombre entier valide" in result.output

    def test_user_create_invalid_email(self, monkeypatch):
        """Test création d'utilisateur avec email invalide"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]
        
        def mock_get_departement_id_by_name(name):
            return 1
        
        monkeypatch.setattr("cli.commands.user_commands.get_departement_choice", mock_get_departement_choice)
        monkeypatch.setattr("cli.commands.user_commands.get_departement_id_by_name", mock_get_departement_id_by_name)
        
        runner = CliRunner()
        
        # Simulation: email invalide puis valide
        inputs = [
            "john_doe",      # username
            "12345",         # employee_number
            "invalid-email", # email invalide
            "john@epic.com", # email valide
            "John",          # first_name
            "Doe",           # last_name
            "password123",   # password
            "password123",   # confirmation password
            "Gestion"        # departement
        ]
        
        result = runner.invoke(user, ['create'], input='\n'.join(inputs))
        
        assert "Format d'email invalide" in result.output

    def test_user_create_department_not_found(self, monkeypatch):
        """Test création d'utilisateur avec département non trouvé"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]
        
        def mock_get_departement_id_by_name(name):
            return None  # Département non trouvé
        
        monkeypatch.setattr("cli.commands.user_commands.get_departement_choice", mock_get_departement_choice)
        monkeypatch.setattr("cli.commands.user_commands.get_departement_id_by_name", mock_get_departement_id_by_name)
        
        runner = CliRunner()
        
        inputs = [
            "john_doe",      # username
            "12345",         # employee_number
            "john@epic.com", # email
            "John",          # first_name
            "Doe",           # last_name
            "password123",   # password
            "password123",   # confirmation password
            "Gestion"        # departement
        ]
        
        result = runner.invoke(user, ['create'], input='\n'.join(inputs))
        
        assert result.exit_code == 0
        assert "❌ Erreur : Le département 'Gestion' n'a pas été trouvé." in result.output

    def test_user_create_access_denied(self, monkeypatch):
        """Test accès refusé pour création d'utilisateur"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        
        runner = CliRunner()
        result = runner.invoke(user, ['create'])
        
        assert result.exit_code == 0
        assert "Accès refusé" in result.output

    def test_user_update_success(self, monkeypatch):
        """Test mise à jour d'utilisateur réussie"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]
        
        def mock_get_departement_id_by_name(name):
            return 2
            
        def mock_is_valid_email(email):
            return True
            
        def mock_update_user(self, user_id, **kwargs):
            return True, "✅ Utilisateur mis à jour avec succès"
        
        monkeypatch.setattr("cli.commands.user_commands.get_departement_choice", mock_get_departement_choice)
        monkeypatch.setattr("cli.commands.user_commands.get_departement_id_by_name", mock_get_departement_id_by_name)
        monkeypatch.setattr("services.utils.is_valid_email", mock_is_valid_email)
        monkeypatch.setattr("services.user_services.UserService.update_user", mock_update_user)
        
        runner = CliRunner()
        
        inputs = [
            "1",             # user_id
            "new_username",  # nouveau username
            "54321",         # nouveau matricule
            "new@epic.com",  # nouvel email
            "NewFirstName",  # nouveau prénom
            "NewLastName",   # nouveau nom
            "y",             # changer mot de passe
            "newpass123",    # nouveau mot de passe
            "newpass123",    # confirmation
            "y",             # changer département
            "Commercial"     # nouveau département
        ]
        
        result = runner.invoke(user, ['update'], input='\n'.join(inputs))
        
        assert result.exit_code == 0
        assert "✅ Utilisateur mis à jour avec succès" in result.output

    def test_user_update_invalid_email(self, monkeypatch):
        """Test mise à jour avec email invalide"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        call_count = 0
        def mock_is_valid_email(email):
            nonlocal call_count
            call_count += 1
            return call_count > 1  # Premier appel False, deuxième True
        
        monkeypatch.setattr("services.utils.is_valid_email", mock_is_valid_email)
        
        runner = CliRunner()
        
        inputs = [
            "1",                 # user_id
            "",                  # username (vide)
            "",                  # matricule (vide)
            "invalid-email",     # email invalide
            "valid@epic.com",    # email valide
            "",                  # prénom (vide)
            "",                  # nom (vide)
            "n",                 # pas de changement de mot de passe
            "n"                  # pas de changement de département
        ]
        
        result = runner.invoke(user, ['update'], input='\n'.join(inputs))
        
        assert "Format d'email invalide" in result.output

    def test_user_update_invalid_employee_number(self, monkeypatch):
        """Test mise à jour avec matricule invalide"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        runner = CliRunner()
        
        inputs = [
            "1",             # user_id
            "",              # username (vide)
            "abc",           # matricule invalide
            "12345",         # matricule valide
            "",              # email (vide)
            "",              # prénom (vide)
            "",              # nom (vide)
            "n",             # pas de changement de mot de passe
            "n"              # pas de changement de département
        ]
        
        result = runner.invoke(user, ['update'], input='\n'.join(inputs))
        
        assert "Le matricule doit être un nombre entier valide" in result.output

    def test_user_update_access_denied(self, monkeypatch):
        """Test accès refusé pour mise à jour d'utilisateur"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Support"})
        
        runner = CliRunner()
        result = runner.invoke(user, ['update'], input="1\n")
        
        assert result.exit_code == 0
        assert "Accès refusé" in result.output

    def test_user_list_success(self, monkeypatch):
        """Test listing des utilisateurs réussi"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        # Mock des utilisateurs
        class MockUser:
            def __init__(self, id, employee_number, username, email, first_name, last_name):
                self.id = id
                self.employee_number = employee_number
                self.username = username
                self.email = email
                self.first_name = first_name
                self.last_name = last_name
        
        def mock_get_users(self):
            return [
                MockUser(1, 12345, "john_doe", "john@epic.com", "John", "Doe"),
                MockUser(2, 67890, "jane_smith", "jane@epic.com", "Jane", "Smith")
            ]
        
        monkeypatch.setattr("services.user_services.UserService.get_users", mock_get_users)
        
        runner = CliRunner()
        result = runner.invoke(user, ['list'])
        
        assert result.exit_code == 0
        assert "Liste des utilisateurs :" in result.output
        assert "john_doe" in result.output
        assert "jane_smith" in result.output
        assert "john@epic.com" in result.output
        assert "Jane Smith" in result.output

    def test_user_list_empty(self, monkeypatch):
        """Test listing des utilisateurs vide"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        def mock_get_users(self):
            return []
        
        monkeypatch.setattr("services.user_services.UserService.get_users", mock_get_users)
        
        runner = CliRunner()
        result = runner.invoke(user, ['list'])
        
        assert result.exit_code == 0
        assert "Aucun utilisateur trouvé." in result.output

    def test_user_list_access_denied(self, monkeypatch):
        """Test accès refusé pour listing des utilisateurs"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        
        runner = CliRunner()
        result = runner.invoke(user, ['list'])
        
        assert result.exit_code == 0
        assert "Accès refusé" in result.output

    def test_user_update_partial_update(self, monkeypatch):
        """Test mise à jour partielle d'utilisateur"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        captured_args = {}
        def mock_update_user(self, user_id, **kwargs):
            captured_args.update(kwargs)
            return True, "✅ Utilisateur mis à jour avec succès"
        
        monkeypatch.setattr("services.user_services.UserService.update_user", mock_update_user)
        
        runner = CliRunner()
        
        # Mise à jour uniquement du prénom et nom
        inputs = [
            "1",             # user_id
            "",              # username (vide)
            "",              # matricule (vide)
            "",              # email (vide)
            "UpdatedFirst",  # nouveau prénom
            "UpdatedLast",   # nouveau nom
            "n",             # pas de changement de mot de passe
            "n"              # pas de changement de département
        ]
        
        result = runner.invoke(user, ['update'], input='\n'.join(inputs))
        
        assert result.exit_code == 0
        # Vérifier que seuls les champs non vides sont passés
        assert "first_name" in captured_args
        assert "last_name" in captured_args
        assert "username" not in captured_args
        assert "email" not in captured_args
        assert captured_args["first_name"] == "UpdatedFirst"
        assert captured_args["last_name"] == "UpdatedLast"

    def test_user_create_negative_employee_number(self, monkeypatch):
        """Test création avec matricule négatif"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]
        
        def mock_get_departement_id_by_name(name):
            return 1
        
        monkeypatch.setattr("cli.commands.user_commands.get_departement_choice", mock_get_departement_choice)
        monkeypatch.setattr("cli.commands.user_commands.get_departement_id_by_name", mock_get_departement_id_by_name)
        
        runner = CliRunner()
        
        inputs = [
            "john_doe",      # username
            "-123",          # employee_number négatif
            "12345",         # employee_number valide
            "john@epic.com", # email
            "John",          # first_name
            "Doe",           # last_name
            "password123",   # password
            "password123",   # confirmation password
            "Gestion"        # departement
        ]
        
        result = runner.invoke(user, ['create'], input='\n'.join(inputs))
        
        assert "Le matricule doit être un entier positif" in result.output

    def test_user_update_zero_employee_number(self, monkeypatch):
        """Test mise à jour avec matricule zéro"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        runner = CliRunner()
        
        inputs = [
            "1",             # user_id
            "",              # username (vide)
            "0",             # matricule zéro
            "12345",         # matricule valide
            "",              # email (vide)
            "",              # prénom (vide)
            "",              # nom (vide)
            "n",             # pas de changement de mot de passe
            "n"              # pas de changement de département
        ]
        
        result = runner.invoke(user, ['update'], input='\n'.join(inputs))
        
        assert "Le matricule doit être un entier positif" in result.output

    def test_user_create_service_error(self, monkeypatch):
        """Test gestion d'erreur du service lors de la création"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]
        
        def mock_get_departement_id_by_name(name):
            return 1
            
        def mock_create_user(self, **kwargs):
            return False, "❌ Erreur : Matricule déjà utilisé"
        
        monkeypatch.setattr("cli.commands.user_commands.get_departement_choice", mock_get_departement_choice)
        monkeypatch.setattr("cli.commands.user_commands.get_departement_id_by_name", mock_get_departement_id_by_name)
        monkeypatch.setattr("services.user_services.UserService.create_user", mock_create_user)
        
        runner = CliRunner()
        
        inputs = [
            "john_doe",      # username
            "12345",         # employee_number
            "john@epic.com", # email
            "John",          # first_name
            "Doe",           # last_name
            "password123",   # password
            "password123",   # confirmation password
            "Gestion"        # departement
        ]
        
        result = runner.invoke(user, ['create'], input='\n'.join(inputs))
        
        assert result.exit_code == 0
        assert "❌ Erreur : Matricule déjà utilisé" in result.output

    def test_user_update_service_error(self, monkeypatch):
        """Test gestion d'erreur du service lors de la mise à jour"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        def mock_update_user(self, user_id, **kwargs):
            return False, "❌ Erreur : Utilisateur non trouvé"
        
        monkeypatch.setattr("services.user_services.UserService.update_user", mock_update_user)
        
        runner = CliRunner()
        
        inputs = [
            "999",           # user_id inexistant
            "new_username",  # nouveau username
            "",              # matricule (vide)
            "",              # email (vide)
            "",              # prénom (vide)
            "",              # nom (vide)
            "n",             # pas de changement de mot de passe
            "n"              # pas de changement de département
        ]
        
        result = runner.invoke(user, ['update'], input='\n'.join(inputs))
        
        assert result.exit_code == 0
        assert "❌ Erreur : Utilisateur non trouvé" in result.output

    def test_user_create_with_option_flags(self, monkeypatch):
        """Test création d'utilisateur avec flags d'option"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]
        
        def mock_get_departement_id_by_name(name):
            return 1
            
        def mock_create_user(self, **kwargs):
            return True, "✅ Utilisateur créé avec succès"
        
        monkeypatch.setattr("cli.commands.user_commands.get_departement_choice", mock_get_departement_choice)
        monkeypatch.setattr("cli.commands.user_commands.get_departement_id_by_name", mock_get_departement_id_by_name)
        monkeypatch.setattr("services.user_services.UserService.create_user", mock_create_user)
        
        runner = CliRunner()
        
        # Test avec des caractères spéciaux dans les inputs
        inputs = [
            "test_user-123",     # username avec caractères spéciaux
            "99999",             # employee_number grand
            "test.user@epic.com", # email avec point
            "Jean-Marc",         # first_name avec tiret
            "Dupont-Martin",     # last_name avec tiret
            "P@ssw0rd!",         # password complexe
            "P@ssw0rd!",         # confirmation password
            "Support"            # departement
        ]
        
        result = runner.invoke(user, ['create'], input='\n'.join(inputs))
        
        assert result.exit_code == 0
        assert "✅ Utilisateur créé avec succès" in result.output

    def test_user_update_with_all_fields_changed(self, monkeypatch):
        """Test mise à jour avec tous les champs modifiés"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]
        
        def mock_get_departement_id_by_name(name):
            return 3
            
        def mock_is_valid_email(email):
            return True
            
        captured_args = {}
        def mock_update_user(self, user_id, **kwargs):
            captured_args.update(kwargs)
            return True, "✅ Tous les champs mis à jour avec succès"
        
        monkeypatch.setattr("cli.commands.user_commands.get_departement_choice", mock_get_departement_choice)
        monkeypatch.setattr("cli.commands.user_commands.get_departement_id_by_name", mock_get_departement_id_by_name)
        monkeypatch.setattr("services.utils.is_valid_email", mock_is_valid_email)
        monkeypatch.setattr("services.user_services.UserService.update_user", mock_update_user)
        
        runner = CliRunner()
        
        inputs = [
            "1",                    # user_id
            "updated_username",     # nouveau username
            "77777",               # nouveau matricule
            "updated@epic.com",    # nouvel email
            "Updated",             # nouveau prénom
            "Name",                # nouveau nom
            "y",                   # changer mot de passe
            "newpassword",         # nouveau mot de passe
            "newpassword",         # confirmation
            "y",                   # changer département
            "Support"              # nouveau département
        ]
        
        result = runner.invoke(user, ['update'], input='\n'.join(inputs))
        
        assert result.exit_code == 0
        assert "✅ Tous les champs mis à jour avec succès" in result.output
        
        # Vérifier que tous les champs ont été transmis
        assert "username" in captured_args
        assert "employee_number" in captured_args  
        assert "email" in captured_args
        assert "first_name" in captured_args
        assert "last_name" in captured_args
        assert "password" in captured_args
        assert "departement_id" in captured_args
        
        assert captured_args["username"] == "updated_username"
        assert captured_args["employee_number"] == 77777
        assert captured_args["email"] == "updated@epic.com"
        assert captured_args["first_name"] == "Updated"
        assert captured_args["last_name"] == "Name"
        assert captured_args["departement_id"] == 3

    def test_user_update_with_invalid_user_id_type(self, monkeypatch):
        """Test mise à jour avec ID utilisateur invalide"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        runner = CliRunner()
        
        # Test avec un ID non numérique - Click devrait gérer cela
        result = runner.invoke(user, ['update', '--user-id', 'abc'])
        
        assert result.exit_code == 2  # Error code pour bad parameter
        assert "Invalid value for '--user-id'" in result.output

    def test_user_create_edge_cases(self, monkeypatch):
        """Test des cas limites pour la création d'utilisateur"""
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]
        
        def mock_get_departement_id_by_name(name):
            return 1
            
        def mock_create_user(self, **kwargs):
            return True, "✅ Utilisateur créé avec succès"
        
        monkeypatch.setattr("cli.commands.user_commands.get_departement_choice", mock_get_departement_choice)
        monkeypatch.setattr("cli.commands.user_commands.get_departement_id_by_name", mock_get_departement_id_by_name)
        monkeypatch.setattr("services.user_services.UserService.create_user", mock_create_user)
        
        runner = CliRunner()
        
        # Test avec des valeurs à la limite
        inputs = [
            "a",                    # username très court
            "1",                    # employee_number minimal
            "a@b.c",               # email minimal valide
            "A",                   # prénom très court
            "B",                   # nom très court
            "1234567890",          # password numérique
            "1234567890",          # confirmation password
            "Gestion"              # departement
        ]
        
        result = runner.invoke(user, ['create'], input='\n'.join(inputs))
        
        assert result.exit_code == 0
        assert "✅ Utilisateur créé avec succès" in result.output


class TestContractUpdate:
    """Tests pour la mise à jour de contrats"""
    
    def test_contract_update_success_commercial_own_client(self, monkeypatch):
        """Test réussi: commercial met à jour un contrat de son client"""
        runner = CliRunner()
        
        # Mock user authentifié comme commercial
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        
        # Mock contract service
        def mock_update_contract(self, contract_id, user_id, user_departement, sign=None, paid_amount=None):
            return True, "Le contrat a été mis à jour"
        
        monkeypatch.setattr("services.contract_services.ContractService.update_contract", mock_update_contract)
        
        result = runner.invoke(contract, ['update', '--contract-id', '1', '--sign'])
        
        assert result.exit_code == 0
        assert "Le contrat a été mis à jour" in result.output
    
    def test_contract_update_success_commercial_unassigned_client(self, monkeypatch):
        """Test réussi: commercial met à jour un contrat d'un client non assigné"""
        runner = CliRunner()
        
        # Mock user authentifié comme commercial
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        
        # Mock contract service - contrat avec client non assigné
        def mock_update_contract(self, contract_id, user_id, user_departement, sign=None, paid_amount=None):
            return True, "Le contrat a été mis à jour"
        
        monkeypatch.setattr("services.contract_services.ContractService.update_contract", mock_update_contract)
        
        result = runner.invoke(contract, ['update', '--contract-id', '1', '--sign'])
        
        assert result.exit_code == 0
        assert "Le contrat a été mis à jour" in result.output
    
    def test_contract_update_fail_commercial_other_client(self, monkeypatch):
        """Test échec: commercial tente de mettre à jour un contrat d'un autre commercial"""
        runner = CliRunner()
        
        # Mock user authentifié comme commercial
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        
        # Mock contract service - contrat appartenant à un autre commercial
        def mock_update_contract(self, contract_id, user_id, user_departement, sign=None, paid_amount=None):
            return False, "Vous ne pouvez mettre à jour que les contrats de vos clients. Ce contrat appartient à un client assigné à un autre commercial (ID: 2)"
        
        monkeypatch.setattr("services.contract_services.ContractService.update_contract", mock_update_contract)
        
        result = runner.invoke(contract, ['update', '--contract-id', '1', '--sign'])
        
        assert result.exit_code == 0
        assert "Ce contrat appartient à un client assigné à un autre commercial" in result.output
    
    def test_contract_update_fail_contract_not_found(self, monkeypatch):
        """Test échec: contrat inexistant"""
        runner = CliRunner()
        
        # Mock user authentifié comme commercial
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        
        # Mock contract service - contrat introuvable
        def mock_update_contract(self, contract_id, user_id, user_departement, sign=None, paid_amount=None):
            return False, "Contrat avec l'ID 999 introuvable"
        
        monkeypatch.setattr("services.contract_services.ContractService.update_contract", mock_update_contract)
        
        result = runner.invoke(contract, ['update', '--contract-id', '999', '--sign'])
        
        assert result.exit_code == 0
        assert "Contrat avec l'ID 999 introuvable" in result.output
    
    def test_contract_update_gestion_user_paid_amount(self, monkeypatch):
        """Test réussi: utilisateur gestion met à jour le montant payé"""
        runner = CliRunner()
        
        # Mock user authentifié comme gestion
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        # Mock contract service
        def mock_update_contract(self, contract_id, user_id, user_departement, sign=None, paid_amount=None):
            return True, "Le contrat a été mis à jour"
        
        monkeypatch.setattr("services.contract_services.ContractService.update_contract", mock_update_contract)
        
        result = runner.invoke(contract, ['update', '--contract-id', '1', '--paid-amount', '1000.50'])
        
        assert result.exit_code == 0
        assert "Le contrat a été mis à jour" in result.output
    
    def test_contract_update_fail_paid_amount_too_high(self, monkeypatch):
        """Test échec: montant payé supérieur au montant du contrat"""
        runner = CliRunner()
        
        # Mock user authentifié comme gestion
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        # Mock contract service
        def mock_update_contract(self, contract_id, user_id, user_departement, sign=None, paid_amount=None):
            return False, "Le montant payé (5000€) ne doit pas être supérieur au montant du contrat (2000€)"
        
        monkeypatch.setattr("services.contract_services.ContractService.update_contract", mock_update_contract)
        
        result = runner.invoke(contract, ['update', '--contract-id', '1', '--paid-amount', '5000'])
        
        assert result.exit_code == 0
        assert "ne doit pas être supérieur au montant du contrat" in result.output
    
    def test_contract_update_fail_no_user_logged_in(self, monkeypatch):
        """Test échec: aucun utilisateur connecté"""
        runner = CliRunner()
        
        # Mock pas d'utilisateur connecté
        def mock_get_current_user_info():
            return None
        
        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user_info)
        
        result = runner.invoke(contract, ['update', '--contract-id', '1', '--sign'])
        
        assert result.exit_code == 0
        assert "Vous n'etes pas connectés" in result.output
    
    def test_contract_update_fail_no_data_to_update(self, monkeypatch):
        """Test échec: aucune donnée à mettre à jour"""
        runner = CliRunner()
        
        # Mock user authentifié
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Commercial"})
        
        # Mock contract service
        def mock_update_contract(self, contract_id, user_id, user_departement, sign=None, paid_amount=None):
            return False, "Aucune donnée à mettre à jour"
        
        monkeypatch.setattr("services.contract_services.ContractService.update_contract", mock_update_contract)
        
        result = runner.invoke(contract, ['update', '--contract-id', '1'])
        
        assert result.exit_code == 0
        assert "Aucune donnée à mettre à jour" in result.output
    
    def test_contract_update_with_both_sign_and_paid_amount(self, monkeypatch):
        """Test réussi: mise à jour avec signature et montant payé"""
        runner = CliRunner()
        
        # Mock user authentifié comme gestion
        mock_authenticated_user(monkeypatch, {"user_id": 1, "departement": "Gestion"})
        
        # Mock contract service
        def mock_update_contract(self, contract_id, user_id, user_departement, sign=None, paid_amount=None):
            return True, "Le contrat a été mis à jour"
        
        monkeypatch.setattr("services.contract_services.ContractService.update_contract", mock_update_contract)
        
        result = runner.invoke(contract, ['update', '--contract-id', '1', '--sign', '--paid-amount', '1500'])
        
        assert result.exit_code == 0
        assert "Le contrat a été mis à jour" in result.output


class TestContractServiceUpdate:
    """Tests pour les services de mise à jour de contrats"""
    
    def test_contract_service_update_assigns_commercial_to_unassigned_client(self, monkeypatch):
        """Test: assignation automatique d'un commercial à un client non assigné lors de la signature"""
        from services.contract_services import ContractService
        
        # Mock contract avec client non assigné
        class MockContract:
            def __init__(self):
                self.id = 1
                self.client_id = 1
                self.commercial_id = None  # Client non assigné
                self.status = False
                self.amount = 1000.0
                self.paid_amount = 0.0
        
        # Mock client
        class MockClient:
            def __init__(self):
                self.id = 1
                self.fullname = "Test Client"
        
        # Mock DAOs
        def mock_get_contract_by_id(self, contract_id):
            return MockContract()
        
        def mock_get_client_by_id(self, client_id):
            return MockClient()
        
        def mock_update_contract(self, contract_id, update_data):
            return 1  # 1 row affected
        
        def mock_update_client(self, client_id, update_data):
            return 1  # 1 row affected
        
        # Mock Sentry logging
        def mock_log_contract_signature(*args, **kwargs):
            pass
        
        def mock_get_current_user_info():
            return {"user_id": 1, "username": "test_commercial"}
        
        monkeypatch.setattr("database.dao.contract_dao.ContractDAO.get_contract_by_id", mock_get_contract_by_id)
        monkeypatch.setattr("database.dao.client_dao.ClientDAO.get_client_by_id", mock_get_client_by_id)
        monkeypatch.setattr("database.dao.contract_dao.ContractDAO.update_contract", mock_update_contract)
        monkeypatch.setattr("database.dao.client_dao.ClientDAO.update_client", mock_update_client)
        monkeypatch.setattr("services.sentry_service.log_contract_signature", mock_log_contract_signature)
        monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user_info)
        
        service = ContractService()
        success, message = service.update_contract(
            contract_id=1,
            user_id=1,
            user_departement="Commercial",
            sign=True,
            paid_amount=None
        )
        
        assert success == True
        assert message == "Le contrat a été mis à jour"
    
    def test_contract_service_update_permission_denied_wrong_commercial(self, monkeypatch):
        """Test: refus d'accès pour un commercial qui n'est pas assigné au client"""
        from services.contract_services import ContractService
        
        # Mock contract avec client assigné à un autre commercial
        class MockContract:
            def __init__(self):
                self.id = 1
                self.client_id = 1
                self.commercial_id = 2  # Assigné à un autre commercial
                self.status = False
                self.amount = 1000.0
                self.paid_amount = 0.0
        
        # Mock DAOs
        def mock_get_contract_by_id(self, contract_id):
            return MockContract()
        
        monkeypatch.setattr("database.dao.contract_dao.ContractDAO.get_contract_by_id", mock_get_contract_by_id)
        
        service = ContractService()
        success, message = service.update_contract(
            contract_id=1,
            user_id=1,  # Commercial ID 1 tente d'accéder au contrat du commercial ID 2
            user_departement="Commercial",
            sign=True,
            paid_amount=None
        )
        
        assert success == False
        assert "Ce contrat appartient à un client assigné à un autre commercial" in message
    
    def test_contract_service_update_paid_amount_validation(self, monkeypatch):
        """Test: validation du montant payé"""
        from services.contract_services import ContractService
        
        # Mock contract
        class MockContract:
            def __init__(self):
                self.id = 1
                self.client_id = 1
                self.commercial_id = 1
                self.status = False
                self.amount = 1000.0
                self.paid_amount = 0.0
        
        # Mock DAOs
        def mock_get_contract_by_id(self, contract_id):
            return MockContract()
        
        monkeypatch.setattr("database.dao.contract_dao.ContractDAO.get_contract_by_id", mock_get_contract_by_id)
        
        service = ContractService()
        success, message = service.update_contract(
            contract_id=1,
            user_id=1,
            user_departement="Gestion",
            sign=False,
            paid_amount=1500.0  # Montant supérieur au montant du contrat
        )
        
        assert success == False
        assert "ne doit pas être supérieur au montant du contrat" in message
