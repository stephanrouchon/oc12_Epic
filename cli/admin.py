import click
from argon2 import PasswordHasher
from dotenv import load_dotenv
import os
from database.database import engine
from database.dao.user_dao import UserDAO
from database.dao.departement_dao import DepartementDAO

load_dotenv()  # Charge les variables d'environnement du fichier .env

SECRET_KEY = os.getenv("SECRET_KEY")


def cli():
    pass


@cli.command()
@click.option('--username', prompt=True)
@click.option('--email', prompt=True)
@click.option('--first-name', prompt=True)
@click.option('--last-name', prompt=True)
@click.option('--employee-number', prompt=True, type=int)
@click.option('--password',
              prompt=True, hide_input=True, confirmation_prompt=True)
def bootstrap_admin(username,
                    email,
                    first_name,
                    last_name, employee_number,
                    password):
    """Créer le premier utilisateur admin (gestion) sans contrôle d'accès."""

    ph = PasswordHasher()
    departement_dao = DepartementDAO(engine)
    departements = departement_dao.get_all_departements()
    # Cherche le département "gestion"
    gestion_id = next(
        (id for id, name in departements if name.lower() == "gestion"), None)
    if gestion_id is None:
        click.echo("Département 'gestion' introuvable. Crée-le d'abord.")
        return
    hashed_password = ph.hash(password)
    user_dao = UserDAO(engine)
    user_data = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": hashed_password,
        "employee_number": employee_number,
        "departement_id": gestion_id
    }
    user_id = user_dao.create_user(user_data)
    click.echo(f"Premier utilisateur admin créé avec l'ID : {user_id}")

    if __name__ == "__main__":
        cli()
