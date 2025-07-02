#!/usr/bin/env python3
"""
Test de sanity check pour s'assurer que l'environnement de test fonctionne correctement.
"""

import sys
import subprocess


def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    try:
        import pytest
        import click
        import sqlalchemy
        import argon2
        import sentry_sdk
        print("✅ Toutes les dépendances principales sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        return False


def check_test_structure():
    """Vérifie que la structure des tests est correcte"""
    import os
    
    required_files = [
        "tests/__init__.py",
        "tests/test_unit.py", 
        "tests/test_services.py",
        "tests/test_integration.py",
        "tests/README.md",
        "pytest.ini"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Fichiers de test manquants: {missing_files}")
        return False
    else:
        print("✅ Structure des tests correcte")
        return True


def run_quick_test():
    """Exécute un test rapide pour vérifier que pytest fonctionne"""
    try:
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/test_unit.py::TestAuth::test_login_success", 
            "-v", "--tb=short"
        ], capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print("✅ Test rapide réussi")
            return True
        else:
            print(f"❌ Test rapide échoué: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test rapide: {e}")
        return False


def main():
    print("🔍 Vérification de l'environnement de test Epic Events CRM\n")
    
    checks = [
        ("Dépendances", check_dependencies),
        ("Structure des tests", check_test_structure),
        ("Test rapide", run_quick_test)
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        print(f"Vérification: {name}")
        if not check_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 Tous les checks sont passés ! L'environnement de test est prêt.")
        print("\nPour exécuter les tests :")
        print("  python test_runner.py                    # Tous les tests")
        print("  python test_runner.py --unit            # Tests unitaires")
        print("  python test_runner.py --coverage --html  # Avec couverture")
    else:
        print("💥 Certains checks ont échoué. Veuillez corriger les problèmes avant d'exécuter les tests.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
