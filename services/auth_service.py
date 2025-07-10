import os
import jwt
import click
from argon2 import PasswordHasher
import functools
from datetime import datetime, timedelta, timezone
from database.database import engine
from database.dao.user_dao import UserDAO
from database.dao.departement_dao import DepartementDAO

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_EXPIRE_SECONDS = os.getenv("JWT_EXPIRE_SECONDS")
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')

ph = PasswordHasher()


class AuthService:
    def __init__(self):
        self.user_dao = UserDAO(engine)
        self.departement_dao = DepartementDAO(engine)

    def login(self, session, username, password):
        """_summary_

        Args:
            session (_type_): _description_
            username (_type_): n
            password (_type_): password

        Returns:
            _type_: creation d'un token
        """

        result = self.user_dao.select_user(session, username)

        if not result:
            return False, None, 'Utilisateur non trouvé'

        try:
            ph.verify(result.password, password)
        except Exception:
            return False, None, "Mot de passe incorect"

        dept_name = self.departement_dao.get_departement_name_by_id(
            session, result.departement_id)

        payload = {
            "user_id": result.id,
            "username": result.username,
            "departement": dept_name,
            "exp": (datetime.now(timezone.utc) +
                    timedelta(seconds=int(JWT_EXPIRE_SECONDS)))
        }

        try:
            token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
            return True, token, "Connexion réussie"
        except Exception:
            return False, None, "Erreur lors de la création du token"

    def logout(self):
        """deconnecte l'utilisateur en supprimant le token"""
        try:
            if os.path.exists(".token"):
                os.remove(".token")
                return True, "Deconnexion réussie"
            else:
                return True, "Vous n'etiez pas connecté"
        except Exception:
            return False, "Erreur lors de la deconnexion"


def get_token():
    if not os.path.exists(".token"):
        return None
    with open(".token", "r") as f:
        return f.read().strip()


def get_current_user_info():
    token = get_token()
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        click.echo("Token expiré. Veuillez vous reconnecter.")
    except jwt.InvalidTokenError:
        click.echo("Token invalide. Veuillez vous reconnecter.")


def require_auth(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user = get_current_user_info()
        if not user:
            click.echo("Vous devez être connecté pour utiliser cette commande")
            return
        return f(*args, **kwargs)
    return wrapper


def require_departement(*dept_names):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            user = get_current_user_info()
            if not user:
                click.echo("Vous n'etes pas connectés")
                return
            user_dept = user.get("departement", "").lower()
            if user_dept not in [d.lower() for d in dept_names]:
                click.echo(
                    f"Accès refusé : reservé au(x) "
                    f"departement(s) {dept_names}.")
                return
            return f(*args, **kwargs)
        return wrapper
    return decorator
