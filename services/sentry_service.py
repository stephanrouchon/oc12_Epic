import sentry_sdk
import os
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

def init_sentry():
    """Initialise Sentry pour la journalisation des erreurs et événements"""
    sentry_dsn = os.getenv("SENTRY_DSN")
    
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=1.0,  # Capture 100% des transactions pour le monitoring de performance
            environment=os.getenv("ENVIRONMENT", "development"),
            release=os.getenv("RELEASE_VERSION", "1.0.0")
        )
        print("Sentry initialisé avec succès")
    else:
        print("SENTRY_DSN non configuré dans les variables d'environnement")

def sentry_exception_handler(func_name=None):
    """Décorateur pour capturer automatiquement les exceptions avec Sentry"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Journaliser l'exception avec le contexte
                sentry_sdk.capture_exception(
                    e,
                    extra={
                        "function_name": func_name or func.__name__,
                        "function_module": func.__module__,
                        "args": str(args) if args else None,
                        "kwargs": str(kwargs) if kwargs else None,
                        "event_type": "unexpected_exception"
                    }
                )
                # Re-lever l'exception pour que le comportement normal continue
                raise
        return wrapper
    return decorator

def log_user_creation(user_id, username, departement, created_by):
    """Journalise la création d'un utilisateur"""
    sentry_sdk.capture_message(
        f"Création d'utilisateur: {username} (ID: {user_id}) dans le département {departement}",
        level="info",
        extra={
            "event_type": "user_creation",
            "user_id": user_id,
            "username": username,
            "departement": departement,
            "created_by": created_by,
            "action": "create_user"
        }
    )

def log_user_update(user_id, username, updated_fields, updated_by):
    """Journalise la modification d'un utilisateur"""
    sentry_sdk.capture_message(
        f"Modification d'utilisateur: {username} (ID: {user_id}). Champs modifiés: {', '.join(updated_fields)}",
        level="info",
        extra={
            "event_type": "user_update",
            "user_id": user_id,
            "username": username,
            "updated_fields": updated_fields,
            "updated_by": updated_by,
            "action": "update_user"
        }
    )

def log_contract_signature(contract_id, client_name, amount, signed_by):
    """Journalise la signature d'un contrat"""
    sentry_sdk.capture_message(
        f"Signature de contrat: Contrat ID {contract_id} pour {client_name} d'un montant de {amount}€",
        level="info",
        extra={
            "event_type": "contract_signature",
            "contract_id": contract_id,
            "client_name": client_name,
            "amount": amount,
            "signed_by": signed_by,
            "action": "sign_contract"
        }
    )

def log_event_create(event_id, client_name, contract_id, signed_by):
    """Journalise la création d'un event"""
    sentry_sdk.capture_message(
        f"Création d'un évènement: Event ID: {event_id} pour {client_name} pour le contrat {contract_id}",
        level="info",
        extras={
            "event_type": "Création d'un événement",
            "event_id": event_id,
            "client_name": client_name,
            "signed_by": signed_by,
            "action": "Event_create"
        }
    )

def log_exception(exception, context=None):
    """Journalise une exception inattendue"""
    sentry_sdk.capture_exception(
        exception,
        extra={
            "event_type": "unexpected_exception",
            "context": context or {}
        }
    )
