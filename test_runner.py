#!/usr/bin/env python3
"""
Script pour exécuter les tests avec différentes options.

Usage:
    python run_tests.py                    # Tous les tests
    python run_tests.py --unit             # Tests unitaires seulement
    python run_tests.py --integration      # Tests d'intégration seulement
    python run_tests.py --coverage         # Avec rapport de couverture
    python run_tests.py --html             # Avec rapport HTML
"""

import subprocess
import sys
import argparse


def run_command(cmd):
    """Exécute une commande et affiche le résultat"""
    print(f"Exécution: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Exécuteur de tests pour Epic Events CRM")
    parser.add_argument("--unit", action="store_true", help="Tests unitaires seulement")
    parser.add_argument("--integration", action="store_true", help="Tests d'intégration seulement")
    parser.add_argument("--services", action="store_true", help="Tests des services seulement")
    parser.add_argument("--coverage", action="store_true", help="Génération de rapport de couverture")
    parser.add_argument("--html", action="store_true", help="Rapport HTML (nécessite --coverage)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbose")
    parser.add_argument("--fail-fast", "-x", action="store_true", help="Arrêt au premier échec")
    
    args = parser.parse_args()
    
    # Construction de la commande pytest
    cmd = ["python", "-m", "pytest"]
    
    # Sélection des tests
    if args.unit:
        cmd.append("tests/test_unit.py")
    elif args.integration:
        cmd.append("tests/test_integration.py")
    elif args.services:
        cmd.append("tests/test_services.py")
    else:
        cmd.append("tests/")
    
    # Options
    if args.verbose:
        cmd.append("-v")
    
    if args.fail_fast:
        cmd.append("-x")
    
    # Couverture de code
    if args.coverage:
        cmd.extend([
            "--cov=services",
            "--cov=cli",
            "--cov-report=term-missing"
        ])
        
        if args.html:
            cmd.append("--cov-report=html")
    
    # Exécution
    return_code = run_command(cmd)
    
    if return_code == 0:
        print("\n✅ Tous les tests sont passés avec succès!")
        
        if args.coverage and args.html:
            print("\n📊 Rapport de couverture HTML généré dans le dossier htmlcov/")
            print("   Ouvrez htmlcov/index.html dans votre navigateur pour voir le rapport détaillé.")
    else:
        print("\n❌ Certains tests ont échoué.")
        
    return return_code


if __name__ == "__main__":
    sys.exit(main())
