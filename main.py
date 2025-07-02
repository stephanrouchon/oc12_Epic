from cli.epic import epic
from services.sentry_service import init_sentry

if __name__ == "__main__":
    # Initialiser Sentry avant de démarrer l'application
    init_sentry()
    epic()
