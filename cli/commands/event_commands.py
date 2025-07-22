import click
from datetime import datetime
from services.event_services import EventService
from services.auth_service import (
    require_departement, require_auth
)


@click.group()
def event():
    pass


@event.command()
@require_departement("Gestion")
@click.option("--contract-id",
              type=int, prompt=True, help="Entrer l'ID du contrat concerné")
@click.option("--start",
              type=click.DateTime(), prompt=True,
              help="Entrez la date de démarrage")
@click.option("--attendees",
              type=int, prompt=True, help="Combien de personnes")
@click.option("--location",
              prompt=True, help="Event location")
@click.option("--notes",
              prompt=True, default="",
              required=False,
              help="Ajoutez des informations complémentaires")
@click.option("--support-id",
              prompt=True, default="", required=False,
              help="Entrez l'ID d'un membre de l'équipe support")
def create(contract_id,
           start,
           attendees,
           location,
           notes,
           support_id):

    # Convert empty string to None for optional support_id
    if support_id == "":
        support_id = None

    event_service = EventService()
    success, message = event_service.create_event(
        contract_id=contract_id,
        start_date=start,
        attendees=attendees,
        location=location,
        notes=notes,
        support_id=support_id
    )

    click.echo(message)


@event.command(name='update')
@require_departement("Gestion", "Support")
@click.option('--event-id',
              type=int, prompt=True,
              help="Entrez l'id de l'évenement")
def event_update(event_id):
    """Mettre à jour un évènement existant"""

    click.echo(f"Mise à jour de l'événement ID: {event_id}")
    click.echo("Laissez vide les champs que \
               vous ne voulez pas modifier")

    # Validation de la date de début
    start_date = None
    start_date_input = click.prompt("Nouvelle date de début \
                                    (YYYY-MM-DD HH: MM: SS ou YYYY-MM-DD)",
                                    default="", show_default=False)
    if start_date_input.strip():
        while True:
            try:
                # Essayer différents formats de date
                if len(start_date_input.strip()) == 10:  # Format YYYY-MM-DD
                    start_date = datetime.strptime(
                        start_date_input.strip(), "%Y-%m-%d")
                else:  # Format YYYY-MM-DD HH: MM: SS
                    start_date = datetime.strptime(
                        start_date_input.strip(), "%Y-%m-%d %H:%M:%S")
                break
            except ValueError:
                click.echo(
                    "Format de date invalide. Utilisez YYYY-MM-DD ou\
                         YYYY-MM-DD HH: MM: SS")
                start_date_input = click.prompt("Nouvelle date de début")
                if not start_date_input.strip():
                    break

    # Validation de la date de fin
    end_date = None
    end_date_input = click.prompt("Nouvelle date de fin (YYYY-MM-DD HH: \
                                  MM: SS ou YYYY-MM-DD)",
                                  default="", show_default=False)
    if end_date_input.strip():
        while True:
            try:
                # Essayer différents formats de date
                if len(end_date_input.strip()) == 10:  # Format YYYY-MM-DD
                    end_date = datetime.strptime(
                        end_date_input.strip(), "%Y-%m-%d")
                else:  # Format YYYY-MM-DD HH: MM: SS
                    end_date = datetime.strptime(
                        end_date_input.strip(), "%Y-%m-%d %H:%M:%S")

                # Vérifier que la date de fin est après la date de début
                if start_date and end_date <= start_date:
                    click.echo(
                        "La date de fin doit être postérieure\
                            à la date de début")
                    end_date_input = click.prompt("Nouvelle date de fin")
                    if not end_date_input.strip():
                        end_date = None
                        break
                    continue
                break
            except ValueError:
                click.echo(
                    "Format de date invalide. Utilisez YYYY-MM-DD ou\
                        YYYY-MM-DD HH: MM: SS")
                end_date_input = click.prompt("Nouvelle date de fin")
                if not end_date_input.strip():
                    break

    # Validation du nombre de participants
    attendees = None
    attendees_input = click.prompt(
        "Nouveau nombre de participants", default="", show_default=False)
    if attendees_input.strip():
        while True:
            try:
                attendees = int(attendees_input)
                if attendees <= 0:
                    click.echo(
                        "Le nombre de participants doit \
                            être un entier positif")
                    attendees_input = click.prompt(
                        "Nouveau nombre de participants")
                    if not attendees_input.strip():
                        attendees = None
                        break
                    continue
                break
            except ValueError:
                click.echo(
                    "Le nombre de participants doit être un nombre entier")
                attendees_input = click.prompt(
                    "Nouveau nombre de participants")
                if not attendees_input.strip():
                    attendees = None
                    break

    location = click.prompt("Nouveau lieu", default="", show_default=False)
    notes = click.prompt("Nouvelles notes", default="", show_default=False)
    support_contact_id = click.prompt("Nouvel ID du responsable support",
                                      default="",
                                      show_default=False)

    # Préparation des données de mise à jour
    update_data = {}
    if start_date is not None:
        update_data["start_date"] = start_date
    if end_date is not None:
        update_data["end_date"] = end_date
    if location.strip():
        update_data["location"] = location.strip()
    if attendees is not None:
        update_data["attendees"] = attendees
    if notes.strip():
        update_data["notes"] = notes.strip()
    if support_contact_id.strip():
        try:
            update_data["support_contact_id"] = int(support_contact_id)
        except ValueError:
            click.echo("L'ID du responsable support \
                       doit être un nombre entier")
            return

    # Appel du service
    event_service = EventService()
    success, message = event_service.update_event(event_id, **update_data)

    click.echo(message)


@event.command(name="assigned-events")
@require_departement("Gestion", "Support")
def get_assign_events_by_support_contact_id():

    event_service = EventService()
    success, events, message = event_service.get_events_by_support_contact_id()

    if success:
        if events:
            for event in events:
                print(f"Evenement ID: {event.id} "
                      f"date de début: {event.start_date}"
                      f"Date de fin : {event.end_date}"
                      f"nombre de personnes : {event.attendees}"
                      f"Lieu: {event.location}")
        else:
            click.echo("Aucun événément affecté")
    else:
        click.echo(message)


@event.command(name="list")
@require_auth
def get_events():

    event_service = EventService()
    success, events, message = event_service.get_event_list()

    if success:
        if events:
            for event in events:
                print(f"Evenement ID: {event.id} "
                      f"date de début: {event.start_date}"
                      f"Date de fin : {event.end_date}"
                      f"nombre de personnes : {event.attendees}"
                      f"Lieu: {event.location}")
        else:
            click.echo("Aucun événément affecté")
    else:
        click.echo(message)
