import click
from tabulate import tabulate
from services.contract_services import ContractService
from services.auth_service import (
    require_auth,
    require_departement,
    get_current_user_info
)


@click.group
def contract():
    pass


@contract.command()
@require_departement('Gestion')
def create():

    user = get_current_user_info()
    if not user:
        click.echo("vous devez être connecté pour créer un contrat")
        return

    # Collecte des données

    title = click.prompt("Contract Title")
    client_id = click.prompt("Client ID", type=int)
    amount = click.prompt("Amount", type=float)

    contract_service = ContractService()
    success, message = contract_service.create_contract(
        title=title,
        client_id=client_id,
        amount=amount
    )

    click.echo(message)


@contract.command()
@require_departement("Gestion", "Commercial")
@click.option('--contract-id',
              prompt=True, type=int, help="ID du contrat")
@click.option('--sign',
              is_flag=True, prompt=False, help="Statut du contrat")
@click.option('--paid-amount',
              type=float, prompt=False, help="Total already paid")
def update(contract_id, sign, paid_amount):

    user = get_current_user_info()
    if not user:
        click.echo("vous devez être connecté")
        return

    contract_service = ContractService()
    success, message = contract_service.update_contract(
        contract_id=contract_id,
        user_id=user["user_id"],
        user_departement=user.get("departement", ""),
        sign=sign,
        paid_amount=paid_amount
    )

    click.echo(message)


@contract.command(name="list")
@require_auth
def get_contract_list():

    contract_service = ContractService()
    success, contracts, message = contract_service.get_contract_list()
    if success and contracts:
        headers = ["ID", "Client", "Title",
                   "Date de création", "Signé", "Montant", "Solde"]
        rows = []

        for row in contracts:
            solde = row.amount-row.paid_amount
            rows.append([
                row.id,
                row.fullname,
                row.title,
                row.created_at.strftime(
                    "%Y-%m-%d") if row.created_at else "N/A",
                "Oui" if row.status else "Non",
                f"{row.amount:.2f} €",
                f"{solde:.2f} €"
            ])

        click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
        click.echo(message)

    else:
        click.echo(message)


@contract.command(name="contracts-not-sign")
@require_departement("Commercial")
def get_not_sign_contracts():
    contract_service = ContractService()
    success, contracts, message = contract_service.get_contract_list_not_sign()
    if success and contracts:
        headers = ["ID", "Client", "Title",
                   "Date de création", "Signé", "Montant", "Solde"]
        rows = []

        for row in contracts:
            solde = row.amount-row.paid_amount
            rows.append([
                row.id,
                row.fullname,
                row.title,
                row.created_at.strftime(
                    "%Y-%m-%d") if row.created_at else "N/A",
                "Oui" if row.status else "Non",
                f"{row.amount:.2f} €",
                f"{solde:.2f} €"
            ])

        click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
        click.echo(message)

    else:
        click.echo(message)


@contract.command(name="contracts-not-paid")
@require_departement("Commercial","Gestion")
def get_contracts_not_fully_paid():
    contract_service = ContractService()
    success, contracts, message = contract_service\
        .get_contract_list_not_fully_paid()
    if success and contracts:
        headers = ["ID", "Client", "Title",
                   "Date de création", "Signé", "Montant", "Solde"]
        rows = []

        for row in contracts:
            solde = row.amount-row.paid_amount
            rows.append([
                row.id,
                row.fullname,
                row.title,
                row.created_at.strftime(
                    "%Y-%m-%d") if row.created_at else "N/A",
                "Oui" if row.status else "Non",
                f"{row.amount:.2f} €",
                f"{solde:.2f} €"
            ])

        click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
        click.echo(message)

    else:
        click.echo(message)
