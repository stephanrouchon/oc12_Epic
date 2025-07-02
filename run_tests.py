#!/usr/bin/env python3
"""
Script pour exécuter les tests avec différentes options
"""

import subprocess
import sys
import os


def run_tests(test_type="all", coverage=False, verbose=False):
    """Exécute les tests selon les paramètres"""
    
    cmd = [sys.executable, "-m", "pytest"]
    
    if test_type == "unit":
        cmd.append("tests/test_unit.py")
    elif test_type == "services":
        cmd.append("tests/test_services.py")
    elif test_type == "all":
        cmd.append("tests/")
    else:
        cmd.append(f"tests/{test_type}")
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=services", "--cov=cli", "--cov-report=html", "--cov-report=term"])
    
    print(f"🧪 Exécution des tests: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=os.getcwd())
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n❌ Tests interrompus par l'utilisateur")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des tests: {e}")
        return False


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Exécuter les tests Epic Events")
    parser.add_argument("--type", choices=["all", "unit", "services"], 
                       default="all", help="Type de tests à exécuter")
    parser.add_argument("--coverage", action="store_true", 
                       help="Activer la couverture de code")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Mode verbeux")
    
    args = parser.parse_args()
    
    success = run_tests(args.type, args.coverage, args.verbose)
    
    if success:
        print("✅ Tous les tests sont passés !")
        if args.coverage:
            print("📊 Rapport de couverture généré dans htmlcov/index.html")
    else:
        print("❌ Certains tests ont échoué")
        sys.exit(1)


if __name__ == "__main__":
    main()
