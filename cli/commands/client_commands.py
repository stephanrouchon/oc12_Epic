
import click
from tabulate import tabulate
from services.client_services import ClientService
from services.auth_service import (
    require_departement,
    require_auth,
    get_current_user_info)


@click.group
def client():
    pass


@client.command()
@require_departement("Commercial")
def create():

    # Récupération de l'utilisateur connecté
    user = get_current_user_info()
    if not user:
        click.echo("vous devez être connecté pour créer un client")
        return

    # Collecte des données
    fullname = click.prompt("Fullname", type=str)
    contact = click.prompt("Contact", type=str)
    email = click.prompt("email", type=str)
    phone_number = click.prompt("phone number", type=str)

    client_services = ClientService()
    success, message = client_services.create_client(
        fullname=fullname,
        contact=contact,
        email=email,
        phone_number=phone_number,
        commercial_id=user["user_id"]
    )

    click.echo(message)


@client.command(name="get-clients")
@require_auth
def get():

    client_service = ClientService()
    success, clients, message = client_service.get_clients()

    if success and clients:

        headers = ["ID", "Nom", "Email", "Telephone", "Commercial"]
        rows = []
        for row in clients:
            commercial = f"{row.commercial_first_name} " \
                f"{row.commercial_last_name}" \
                f"({row.commercial_id})"
            rows.append([
                row.id,
                row.fullname,
                row.email,
                row.phone_number,
                f"{commercial}"
            ])

        click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        click.echo(message)


@client.command(name="update-client")
@require_departement("Gestion", "Commercial")
@click.option("--client-id",
              prompt=True,
              type=int, help="Entrez l'id du client")
@click.option("--fullname",
              prompt=False,
              type=str, help="Entrez le nom complet du client")
@click.option('--email',
              prompt=False,
              type=str, help="Email du client")
@click.option('--phone-number',
              prompt=False,
              type=str, help="nouveau numero du client")
@click.option('--commercial-id',
              prompt=False,
              type=int, help="Id du nouveau commercial")
def update(client_id, fullname, email, phone_number, commercial_id):

    user = get_current_user_info()
    if not user:
        click.echo("Vous n'êtes pas connecté.")
        return

    update_data = {
        "fullname": fullname,
        "email": email,
        "phone_number": phone_number,
        "commercial_id": commercial_id
    }

    client_service = ClientService()
    success, message = client_service.update_client(
        client_id=client_id,
        user_id=user.get("user_id"),
        user_departement=user.get("departement", ""),
        **update_data
    )

    click.echo(message)
