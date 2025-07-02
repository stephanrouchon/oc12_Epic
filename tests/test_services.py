import pytest
from unittest.mock import Mock, patch
from services.user_services import UserService
from services.client_services import ClientService
from services.contract_services import ContractService
from services.event_services import EventService


class TestUserService:
    """Tests unitaires pour UserService"""
    
    def test_create_user_success(self, monkeypatch):
        # Mock des dépendances
        mock_user_dao = Mock()
        mock_user_dao.create_user.return_value = 1
        
        # Mock des DAOs pour Sentry
        mock_dept_dao = Mock()
        mock_dept_dao.get_departement_name_by_id.return_value = "Gestion"
        
        def mock_is_valid_email(email):
            return "@" in email
        
        def mock_get_current_user_info():
            return {"username": "admin"}
        
        def mock_log_user_creation(*args, **kwargs):
            pass  # Mock Sentry logging
        
        monkeypatch.setattr("services.user_services.utils.is_valid_email", mock_is_valid_email)
        monkeypatch.setattr("services.user_services.get_current_user_info", mock_get_current_user_info)
        monkeypatch.setattr("services.user_services.log_user_creation", mock_log_user_creation)
        
        # Test
        user_service = UserService()
        user_service.user_dao = mock_user_dao
        
        # Mock de l'import dynamique de DepartementDAO
        with patch("database.dao.departement_dao.DepartementDAO") as mock_dept_dao_class:
            mock_dept_dao_class.return_value = mock_dept_dao
            
            success, message = user_service.create_user(
                username="test",
                employee_number=123,
                email="test@test.com",
                first_name="Test",
                last_name="User",
                password="password",
                departement_id=1
            )
        
        assert success is True
        assert "succès" in message
        mock_user_dao.create_user.assert_called_once()
    
    def test_create_user_invalid_email(self, monkeypatch):
        def mock_is_valid_email(email):
            return False
        
        monkeypatch.setattr("services.user_services.utils.is_valid_email", mock_is_valid_email)
        
        user_service = UserService()
        
        success, message = user_service.create_user(
            username="test",
            employee_number=123,
            email="invalid_email",
            first_name="Test",
            last_name="User",
            password="password",
            departement_id=1
        )
        
        assert success is False
        assert "Email invalide" in message


class TestClientService:
    """Tests unitaires pour ClientService"""
    
    def test_create_client_success(self):
        # Mock des DAOs
        mock_client_dao = Mock()
        mock_user_dao = Mock()
        mock_user_dao.is_commercial.return_value = True
        
        def mock_is_valid_email(email):
            return "@" in email
        
        client_service = ClientService()
        client_service.client_dao = mock_client_dao
        client_service.user_dao = mock_user_dao
        
        with patch("services.client_services.utils.is_valid_email", mock_is_valid_email):
            success, message = client_service.create_client(
                fullname="Test Client",
                contact="Contact",
                email="client@test.com",
                phone_number="0123456789",
                commercial_id=1
            )
        
        assert success is True
        assert "crée" in message
        mock_client_dao.create_client.assert_called_once()
    
    def test_create_client_invalid_commercial(self):
        mock_client_dao = Mock()
        mock_user_dao = Mock()
        mock_user_dao.is_commercial.return_value = False
        
        def mock_is_valid_email(email):
            return True
        
        client_service = ClientService()
        client_service.client_dao = mock_client_dao
        client_service.user_dao = mock_user_dao
        
        with patch("services.client_services.utils.is_valid_email", mock_is_valid_email):
            success, message = client_service.create_client(
                fullname="Test Client",
                contact="Contact",
                email="client@test.com",
                phone_number="0123456789",
                commercial_id=999
            )
        
        assert success is False
        assert "commercial" in message


class TestContractService:
    """Tests unitaires pour ContractService"""
    
    def test_create_contract_success(self):
        mock_contract_dao = Mock()
        mock_client_dao = Mock()
        mock_client_dao.exists.return_value = True
        
        contract_service = ContractService()
        contract_service.contract_dao = mock_contract_dao
        contract_service.client_dao = mock_client_dao
        
        success, message = contract_service.create_contract(
            title="Test Contract",
            client_id=1,
            amount=1000.0
        )
        
        assert success is True
        assert "crée" in message
        mock_contract_dao.create_contract.assert_called_once()
    
    def test_create_contract_client_not_exists(self):
        mock_contract_dao = Mock()
        mock_client_dao = Mock()
        mock_client_dao.exists.return_value = False
        
        contract_service = ContractService()
        contract_service.contract_dao = mock_contract_dao
        contract_service.client_dao = mock_client_dao
        
        success, message = contract_service.create_contract(
            title="Test Contract",
            client_id=999,
            amount=1000.0
        )
        
        assert success is False
        assert "introuvable" in message


class TestEventService:
    """Tests unitaires pour EventService"""
    
    def test_create_event_success(self):
        mock_event_dao = Mock()
        mock_contract_dao = Mock()
        mock_user_dao = Mock()
        
        # Mock contract exists et est signé
        mock_contract_dao.exists.return_value = True
        mock_contract = Mock()
        mock_contract.status = True
        mock_contract_dao.get_contract_by_id.return_value = mock_contract
        
        # Mock support user
        mock_user_dao.is_support.return_value = True
        
        event_service = EventService()
        event_service.event_dao = mock_event_dao
        event_service.contract_dao = mock_contract_dao
        event_service.user_dao = mock_user_dao
        
        from datetime import datetime
        
        success, message = event_service.create_event(
            contract_id=1,
            start_date=datetime.now(),
            attendees=50,
            location="Paris",
            notes="Test event",
            support_id=1
        )
        
        assert success is True
        assert "crée" in message
        mock_event_dao.create_event.assert_called_once()
    
    def test_create_event_contract_not_signed(self):
        mock_event_dao = Mock()
        mock_contract_dao = Mock()
        mock_user_dao = Mock()
        
        # Mock contract exists mais pas signé
        mock_contract_dao.exists.return_value = True
        mock_contract = Mock()
        mock_contract.status = False  # Pas signé
        mock_contract_dao.get_contract_by_id.return_value = mock_contract
        
        event_service = EventService()
        event_service.event_dao = mock_event_dao
        event_service.contract_dao = mock_contract_dao
        event_service.user_dao = mock_user_dao
        
        from datetime import datetime
        
        success, message = event_service.create_event(
            contract_id=1,
            start_date=datetime.now(),
            attendees=50,
            location="Paris",
            notes="Test event",
            support_id=1
        )
        
        assert success is False
        assert "non signé" in message


class TestDepartementService:
    """Tests pour le service département"""
    
    def test_get_departement_id_case_insensitive(self, monkeypatch):
        from services.departement_services import get_departement_id_by_name
        from unittest.mock import Mock
        
        # Mock des données de départements
        mock_departements = [(1, "Gestion"), (2, "Commercial"), (3, "Support")]
        
        def mock_get_all_departements():
            return mock_departements
        
        monkeypatch.setattr("services.departement_services.departement_dao.get_all_departements", mock_get_all_departements)
        
        # Test avec différentes casses
        result = get_departement_id_by_name("GESTION")
        assert result == 1
        
        result = get_departement_id_by_name("gestion")
        assert result == 1
        
        result = get_departement_id_by_name("Gestion")
        assert result == 1


class TestAuthService:
    """Tests supplémentaires pour le service d'authentification"""
    
    def test_password_verification(self):
        from services.auth_service import AuthService
        from unittest.mock import Mock
        
        mock_dao = Mock()
        service = AuthService()
        service.user_dao = mock_dao
        
        # Mock d'un utilisateur avec mot de passe hashé
        mock_user = Mock()
        mock_user.password = "$argon2id$v=19$m=65536,t=3,p=4$test"  # Mock hash
        mock_dao.get_user_by_username.return_value = mock_user
        
        # Test avec mauvais mot de passe
        with patch("argon2.PasswordHasher.verify") as mock_verify:
            mock_verify.side_effect = Exception("Invalid password")
            
            success, token, message = service.login(Mock(), "testuser", "wrongpass")
            assert success is False
            assert "Mot de passe incorect" in message


class TestSentryIntegration:
    """Tests pour l'intégration Sentry"""
    
    def test_sentry_logging_user_creation(self, monkeypatch):
        from services.sentry_service import log_user_creation
        
        # Mock Sentry
        mock_sentry_capture_message = Mock()
        monkeypatch.setattr("sentry_sdk.capture_message", mock_sentry_capture_message)
        
        # Test log avec tous les arguments requis
        log_user_creation("1", "testuser", "Gestion", "admin")
        
        # Vérifier que Sentry a été appelé
        mock_sentry_capture_message.assert_called()
    
    def test_sentry_exception_handler(self, monkeypatch):
        from services.sentry_service import sentry_exception_handler
        
        mock_sentry_capture = Mock()
        monkeypatch.setattr("sentry_sdk.capture_exception", mock_sentry_capture)
        
        @sentry_exception_handler()
        def test_function():
            raise ValueError("Test error")
        
        try:
            test_function()
        except ValueError:
            pass
        
        # Vérifier que l'exception a été capturée par Sentry
        mock_sentry_capture.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
