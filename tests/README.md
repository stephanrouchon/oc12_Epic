# Guide des Tests - Epic Events CRM

## Structure des Tests

```
tests/
├── __init__.py
├── test_unit.py          # Tests des commandes CLI
├── test_services.py      # Tests des services métier
└── test_integration.py   # Tests d'intégration end-to-end
```

## Types de Tests

### 1. Tests Unitaires (`test_unit.py`)
Tests des commandes CLI avec mocking des services :
- Tests d'authentification (login/logout)
- Tests des commandes utilisateur (create, list, update)
- Tests des commandes client
- Tests des commandes contrat
- Tests des commandes événement
- Tests des décorateurs d'autorisation

### 2. Tests des Services (`test_services.py`)
Tests de la logique métier avec mocking des DAOs :
- UserService (création, validation email, etc.)
- ClientService (création, validation commercial)
- ContractService (création, validation client)
- EventService (création, contrat signé requis)

### 3. Tests d'Intégration (`test_integration.py`)
Tests end-to-end des workflows complets :
- Workflow utilisateur complet
- Workflow client complet
- Workflow d'authentification
- Tests du système de permissions
- Tests de gestion d'erreur

## Exécution des Tests

# Tous les tests
pytest

# Tests spécifiques
pytest tests/test_unit.py
pytest tests/test_services.py
pytest tests/test_integration.py

# Tests avec couverture
pytest --cov=services --cov=cli --cov-report=html

# Tests par classe
pytest tests/test_unit.py::TestAuth

# Test spécifique
pytest tests/test_unit.py::TestAuth::test_login_success

# Tests avec marqueurs
pytest -m "not slow"  # Exclure les tests lents
pytest -m integration  # Seulement les tests d'intégration
```

## Configuration

### pytest.ini
Configuration pytest avec :
- Chemins de test
- Patterns de fichiers
- Marqueurs personnalisés
- Options par défaut

### Marqueurs Disponibles
- `@pytest.mark.unit` : Tests unitaires
- `@pytest.mark.integration` : Tests d'intégration
- `@pytest.mark.slow` : Tests lents

## Mocking Strategy

### Services
Les tests unitaires mockent les services pour isoler les commandes CLI :
```python
monkeypatch.setattr("services.user_services.UserService.create_user", mock_function)
```

### DAOs
Les tests des services mockent les DAOs pour isoler la logique métier :
```python
user_service.user_dao = mock_user_dao
```

### Authentification
Mock de l'utilisateur connecté :
```python
def mock_get_current_user_info():
    return {"user_id": 1, "departement": "Gestion"}
monkeypatch.setattr("services.auth_service.get_current_user_info", mock_get_current_user_info)
```

## Bonnes Pratiques

### Structure d'un Test
```python
def test_fonction_success(self, monkeypatch):
    # 1. Setup - Préparer les mocks
    def mock_dependency():
        return expected_result
    
    monkeypatch.setattr("module.dependency", mock_dependency)
    
    # 2. Execute - Exécuter la fonction testée
    result = function_to_test()
    
    # 3. Assert - Vérifier les résultats
    assert result == expected
    mock_dependency.assert_called_once()
```

### Données de Test
Utilisez des données représentatives mais simples :
```python
fake_user = type('User', (), {
    'id': 1,
    'username': 'test_user',
    'email': 'test@test.com'
})()
```

### Tests d'Erreur
Testez toujours les cas d'erreur :
```python
def test_function_with_invalid_input(self):
    result = function_with_validation("invalid_input")
    assert result[0] is False  # success = False
    assert "erreur" in result[1].lower()  # message d'erreur
```

## Couverture de Code

### Génération du Rapport
```bash
python run_tests.py --coverage
```

### Consultation
Le rapport HTML est généré dans `htmlcov/index.html`

### Objectifs
- **Services** : > 90% de couverture
- **CLI Commands** : > 80% de couverture
- **Global** : > 85% de couverture

## Intégration Continue

Les tests peuvent être intégrés dans un pipeline CI/CD :
```yaml
# Exemple GitHub Actions
- name: Run Tests
  run: |
    pip install -r requirements.txt
    python run_tests.py --coverage
```

## Debugging

### Tests qui Échouent
```bash
# Mode verbeux avec traceback complet
pytest -vvs --tb=long

# Arrêter au premier échec
pytest -x

# Débugger avec pdb
pytest --pdb
```

### Tests Lents
```bash
# Profiling des tests
pytest --durations=10
```
