import pytest
from click.testing import CliRunner
from cli.epic import epic
import tempfile
import os


@pytest.mark.integration
class TestIntegration:
    """Tests d'intégration end-to-end"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.runner = CliRunner()
        # Créer un token temporaire pour les tests
        self.temp_token = tempfile.NamedTemporaryFile(delete=False)
        self.temp_token.write(b"fake_token_for_testing")
        self.temp_token.close()

    def teardown_method(self):
        """Nettoyage après chaque test"""
        if os.path.exists(self.temp_token.name):
            os.unlink(self.temp_token.name)

    def test_full_user_workflow(self, monkeypatch):
        """Test du workflow complet de gestion d'utilisateur"""

        def mock_get_current_user_info():
            return {"user_id": 1, "departement": "Gestion"}

        def mock_create_user(self, **kwargs):
            return True, "L'utilisateur a été créé avec succès"

        def mock_get_departement_choice():
            return ["Gestion", "Commercial", "Support"]

        def mock_get_departement_id_by_name(name):
            return 1

        monkeypatch.setattr(
            "services.auth_service.get_current_user_info",
            mock_get_current_user_info)
        monkeypatch.setattr(
            "services.user_services.UserService.create_user",
            mock_create_user)
        monkeypatch.setattr(
            "services.departement_services.get_departement_choice",
            mock_get_departement_choice)
        monkeypatch.setattr(
            "services.departement_services.get_departement_id_by_name",
            mock_get_departement_id_by_name)

        # Test création utilisateur
        input_data = 'testuser\n123\ntest@test.com\nTest\nUser \
            \npassword\npassword\nGestion\n'
        result = self.runner.invoke(epic, ['user', 'create'],
                                    input=input_data)

        assert result.exit_code == 0
        assert "succès" in result.output

    def test_full_client_workflow(self, monkeypatch):
        """Test du workflow complet de gestion de client"""

        def mock_get_current_user_info():
            return {"user_id": 1, "departement": "Commercial"}

        def mock_get_token():
            return "fake_token"

        def mock_jwt_decode(token, key, algorithms):
            return {"user_id": 1, "departement": "Commercial"}

        def mock_create_client(self, **kwargs):
            return True, "Le client a été créé"

        def mock_get_clients(self):
            return True, [], "Aucun client trouvé"

        monkeypatch.setattr(
            "services.auth_service.get_current_user_info",
            mock_get_current_user_info)
        monkeypatch.setattr("services.auth_service.get_token",
                            mock_get_token)
        monkeypatch.setattr(
            "services.auth_service.jwt.decode",
            mock_jwt_decode)
        monkeypatch.setattr(
            "services.client_services.ClientService.create_client",
            mock_create_client)
        monkeypatch.setattr(
            "services.client_services.ClientService.get_clients",
            mock_get_clients)

        # Test création client
        input_data = 'Test Client\nContact\nclient@test.com\n0123456789\n'
        result = self.runner.invoke(
            epic, ['client', 'create'], input=input_data)

        assert result.exit_code == 0
        assert "créé" in result.output

        # Test liste clients
        result = self.runner.invoke(epic, ['client', 'get-clients'])
        assert result.exit_code == 0

    def test_authentication_workflow(self, monkeypatch):
        """Test du workflow d'authentification"""

        def mock_auth_login(self, session, username, password):
            return True, "fake_token", "Connexion réussie"

        def mock_auth_logout(self):
            return True, "Déconnexion réussie"

        monkeypatch.setattr(
            "services.auth_service.AuthService.login", mock_auth_login)
        monkeypatch.setattr(
            "services.auth_service.AuthService.logout", mock_auth_logout)

        # Test login
        result = self.runner.invoke(
            epic, ['auth', 'login'], input='testuser\npassword\n')
        assert result.exit_code == 0
        assert "Connexion réussie" in result.output

        # Test logout
        result = self.runner.invoke(epic, ['auth', 'logout'])
        assert result.exit_code == 0
        assert "Déconnexion réussie" in result.output

    @pytest.mark.slow
    def test_permission_system(self, monkeypatch):
        """Test du système de permissions"""

        # Test utilisateur non connecté
        def mock_get_current_user_info_none():
            return None

        monkeypatch.setattr(
            "services.auth_service.get_current_user_info",
            mock_get_current_user_info_none)

        result = self.runner.invoke(epic, ['user', 'list'])
        assert "connecté" in result.output.lower()

        # Test utilisateur avec mauvais département
        def mock_get_current_user_info_wrong_dept():
            return {"user_id": 1, "departement": "Support"}

        monkeypatch.setattr("services.auth_service.get_current_user_info",
                            mock_get_current_user_info_wrong_dept)

        result = self.runner.invoke(epic, ['user', 'create'])
        assert "Accès refusé" in result.output or "réservé" in result.output


@pytest.mark.integration
class TestErrorHandling:
    """Tests de gestion d'erreur"""

    def test_invalid_command(self):
        """Test commande invalide"""
        runner = CliRunner()
        result = runner.invoke(epic, ['invalid_command'])
        assert result.exit_code != 0

    def test_missing_required_option(self, monkeypatch):
        """Test option obligatoire manquante"""
        runner = CliRunner()

        def mock_get_current_user_info():
            return {"user_id": 1, "departement": "Gestion"}

        monkeypatch.setattr(
            "services.auth_service.get_current_user_info",
            mock_get_current_user_info)

        # Test sans fournir les inputs requis
        result = runner.invoke(epic, ['event', 'update'], input='\n')
        # La commande devrait demander l'ID de l'événement
        assert ("event-id" in result.output.lower()
                or "id" in result.output.lower())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
