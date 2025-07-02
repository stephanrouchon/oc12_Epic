import click
from sqlalchemy.orm import Session
from services.auth_service import AuthService
from database.database import engine


@click.group()
def auth():
    pass


@auth.command()
@click.option("--username", prompt=True, help="Nom d'utilisateur")
@click.option("--password", prompt=True, help="Mot de passe", hide_input=True)
def login(username, password):

    auth_service = AuthService()

    with Session(engine) as session:
        success, token, message = auth_service.login(
            session, username, password)

        if success:
            with open(".token", "w") as f:
                f.write(token)
        click.echo(message)


@auth.command()
def logout():

    auth_service = AuthService()
    success, message = auth_service.logout()

    click.echo(message)
