import click
from services.user_services import UserService
from services.departement_services import (get_departement_choice,
                                           get_departement_id_by_name)
from services.auth_service import (
    require_departement,
)


@click.group()
def user():
    pass


@user.command()
@require_departement("Gestion")
def create():

    username = click.prompt("Nom d'utilisateur")

    # Validation du matricule avec re-saisie
    while True:
        employee_number = click.prompt('Matricule')
        try:
            employee_number_int = int(employee_number)
            if employee_number_int <= 0:
                click.echo(
                    "Le matricule doit être un entier positif."
                    " Veuillez réessayer.")
                continue
            break
        except ValueError:
            click.echo(
                "Le matricule doit être un nombre entier valide."
                " Veuillez réessayer.")

    # Validation de l'email avec re-saisie
    while True:
        email = click.prompt("Email")
        if "@" in email and "." in email.split("@")[-1]:
            break
        click.echo("Format d'email invalide. Veuillez réessayer.")

    first_name = click.prompt("Prénom")
    last_name = click.prompt("Nom")
    password = click.prompt(
        "Mot de passe", hide_input=True, confirmation_prompt=True)

    departement_names = get_departement_choice()
    departement = click.prompt("Département",
                               click.Choice(departement_names))
    departement_id = get_departement_id_by_name(departement)

    # Vérification que le département a été trouvé
    if departement_id is None:
        click.echo(f"❌ Erreur : Le département '{departement}'\
                    n'a pas été trouvé.")
        return

    user_service = UserService()
    success, message = user_service.create_user(
        username=username,
        email=email,
        employee_number=employee_number_int,
        first_name=first_name,
        last_name=last_name,
        password=password,
        departement_id=departement_id
    )

    click.echo(message)


@user.command()
@require_departement("Gestion")
@click.option('--user-id',
              prompt=True,
              type=int,
              help="ID de l'utilisateur à modifier")
def update(user_id):
    """Mettre à jour un utilisateur existant"""

    click.echo(f"Mise à jour de l'utilisateur ID: {user_id}")
    click.echo("Laissez vide les champs que vous ne voulez pas modifier")

    # Collecte des nouvelles valeurs
    username = click.prompt("Nouveau nom d'utilisateur",
                            default="", show_default=False)

    # Validation du matricule si fourni
    employee_number = None
    employee_number_input = click.prompt(
        "Nouveau matricule", default="", show_default=False)
    if employee_number_input:
        while True:
            try:
                employee_number = int(employee_number_input)
                if employee_number <= 0:
                    click.echo("Le matricule doit être un entier positif.")
                    employee_number_input = click.prompt("Nouveau matricule")
                    continue
                break
            except ValueError:
                click.echo("Le matricule doit être un nombre entier valide.")
                employee_number_input = click.prompt("Nouveau matricule")

    # Validation de l'email si fourni
    email = None
    email_input = click.prompt("Nouvel email", default="", show_default=False)
    if email_input:
        from services import utils
        while True:
            if utils.is_valid_email(email_input):
                email = email_input
                break
            click.echo("Format d'email invalide.")
            email_input = click.prompt("Nouvel email")

    first_name = click.prompt("Nouveau prénom", default="", show_default=False)
    last_name = click.prompt("Nouveau nom", default="", show_default=False)

    # Changement de mot de passe optionnel
    change_password = click.confirm(
        "Voulez-vous changer le mot de passe ?", default=False)
    password = None
    if change_password:
        password = click.prompt("Nouveau mot de passe",
                                hide_input=True, confirmation_prompt=True)

    # Changement de département optionnel
    change_dept = click.confirm(
        "Voulez-vous changer le département ?", default=False)
    departement_id = None
    if change_dept:
        departement_names = get_departement_choice()
        departement = click.prompt(
            "Nouveau département", type=click.Choice(departement_names))
        departement_id = get_departement_id_by_name(departement)

    # Préparation des données de mise à jour
    update_data = {}
    if username:
        update_data["username"] = username
    if employee_number is not None:
        update_data["employee_number"] = employee_number
    if email:
        update_data["email"] = email
    if first_name:
        update_data["first_name"] = first_name
    if last_name:
        update_data["last_name"] = last_name
    if password:
        update_data["password"] = password
    if departement_id is not None:
        update_data["departement_id"] = departement_id

    # Appel du service
    user_service = UserService()
    success, message = user_service.update_user(user_id, **update_data)

    click.echo(message)


@user.command()
@require_departement("Gestion")
def list():
    """Afficher la liste de tous les utilisateurs"""
    user_service = UserService()
    users = user_service.get_users()

    if not users:
        click.echo("Aucun utilisateur trouvé.")
        return

    click.echo("Liste des utilisateurs :")
    click.echo("-" * 80)
    click.echo(
        f"{'ID':<5} {'Matricule':<10} {'Nom d\'utilisateur':<20}"
        f" {'Email':<30} {'Nom complet':<25}")
    click.echo("-" * 80)

    for user in users:
        click.echo(
            f"{user.id:<5} {user.employee_number:<10}"
            f" {user.username:<20} {user.email:<30}"
            f"{user.first_name} {user.last_name}")
