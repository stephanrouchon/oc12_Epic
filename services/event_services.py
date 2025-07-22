from database.dao.contract_dao import ContractDAO
from database.dao.event_dao import EventDAO
from database.dao.user_dao import UserDAO
from database.database import engine
from services.auth_service import get_current_user_info
from services.sentry_service import log_exception


class EventService:
    def __init__(self):
        self.contract_dao = ContractDAO(engine)
        self.event_dao = EventDAO(engine)
        self.user_dao = UserDAO(engine)

    def create_event(self,
                     contract_id,
                     start_date,
                     attendees,
                     location,
                     notes,
                     support_id):
        """Crée un nouvel événement associé à un contrat signé.

        Cette méthode permet de créer un
        événement après avoir vérifié que le contrat
        existe, qu'il est signé, et que les données fournies sont valides.
        Un événement ne peut être créé que sur un contrat ayant le statut
        "signé".

        Validations effectuées :
        - Vérification de l'existence du contrat
        - Vérification que le contrat est signé (status = True)
        - Validation que le support_id correspond à un utilisateur du
        département Support
        - Toutes les données obligatoires sont présentes

        Règles métier :
        - Un événement ne peut être créé que sur un contrat signé
        - Le support_id peut être None (assignation ultérieure possible)
        - Si un support_id est fourni, il doit correspondre à un membre de
        l'équipe Support

        Args:
            contract_id (int): Identifiant du contrat auquel associer
            l'événement
            start_date (datetime): Date et heure de début de l'événement
            attendees (int): Nombre de participants attendus
            location (str): Lieu où se déroulera l'événement
            notes (str): Notes ou description de l'événement
            support_id (int, optional): Identifiant du contact support assigné.
            Peut être None pour une assignation ultérieure.

        Returns:
            tuple: (success, message)
                - success (bool): True si la création a réussi, False sinon
                - message (str): Message décrivant le résultat de l'opération

        Raises:
            Exception: En cas d'erreur lors de l'accès à la base de données
                      (les exceptions sont loggées via Sentry)

        Note:
            - Le contrat doit exister et être signé avant la création de
            l'événement
            - Si support_id est None, l'événement sera créé sans assignation
            - Les erreurs sont automatiquement loggées dans Sentry
            - La validation du support_id est optionnelle (peut être None)
        """

        if not self.contract_dao.exists(contract_id):
            return False, "le contrat n'existe pas"

        contract = self.contract_dao.get_contract_by_id(contract_id)
        if not contract or not getattr(contract, "status", False):
            return False, "impossible de créer un évènement :" \
                "contrat non signé"

        if support_id is not None:
            if not self.user_dao.is_support(support_id):
                return False, "ID du support n'est pas un" \
                    "membre de l'équipe support"

        event_data = {
            "contract_id": contract_id,
            "start_date": start_date,
            "attendees": attendees,
            "location": location,
            "notes": notes,
            "support_contact_id": support_id
        }

        try:
            self.event_dao.create_event(event_data)
            return True, "L'évènement a été crée"
        except Exception as e:
            log_exception(e, {
                "action": "create_event"
            })
            return False, f"erreur lors de la création : {str(e)}"

    def update_event(self,
                     event_id,
                     **kwargs):
        """Met à jour les informations d'un événement existant.

        Cette méthode permet de modifier les données d'un événement après avoir
        vérifié les permissions d'accès et validé les données fournies.
        L'authentification de l'utilisateur est vérifiée automatiquement.

        Contrôles d'accès :
        - Les utilisateurs du département "Support" ne peuvent modifier
        que les événements qui leur sont attribués
        - Les autres départements (Gestion) peuvent modifier tous les
          événements
        - Authentification requise via get_current_user_info()

        Validations effectuées :
        - Vérification de l'existence de l'événement
        - Validation du format des dates (start_date, end_date)
        - Validation du nombre de participants (entier positif)
        - Vérification que le support_contact_id correspond à un utilisateur
          support
        - Filtrage des données vides (None ou chaîne vide)

        Args:
            event_id (int): Identifiant unique de l'événement à modifier
            **kwargs: Données à mettre à jour. Clés possibles :
                - start_date (datetime): Date et heure de début de l'événement
                - end_date (datetime): Date et heure de fin de l'événement
                - attendees (int): Nombre de participants (entier positif)
                - location (str): Lieu de l'événement
                - notes (str): Notes ou description de l'événement
                - support_contact_id (int): ID du contact support assigné
                (sera vérifié)

        Returns:
            tuple: (success, message)
                - success (bool): True si la mise à jour a réussi, False sinon
                - message (str): Message décrivant le résultat de l'opération

        Raises:
            Exception: En cas d'erreur lors de l'accès à la base de données
                      (les exceptions sont loggées via Sentry)

        Note:
            - Seuls les champs fournis dans kwargs seront mis à jour
            - Les valeurs None ou chaînes vides sont ignorées
            - L'utilisateur doit être authentifié pour utiliser cette méthode
            - Les erreurs sont automatiquement loggées dans Sentry
        """

        # Récupérer les informations de l'utilisateur courant
        current_user = get_current_user_info()
        if not current_user:
            return False, "Utilisateur non authentifié"

        user_id = current_user.get('user_id')
        user_departement = current_user.get('departement')

        if not user_id or not user_departement:
            return False, "Informations utilisateur incomplètes"

        # Vérifier que l'événement existe
        event = self.event_dao.get_event_by_id(event_id)
        if not event:
            return False, "Evenement introuvable"

        # Contrôle d'accès pour le département Support
        if user_departement.lower() == "support":
            if event.support_contact_id != user_id:
                return (False,
                        "Vous ne pouvez mettre à jour que les événements"
                        "qui vous sont attribués")

        # Validation et préparation des données
        update_data = {}
        for field, value in kwargs.items():
            if value is not None and value != "":
                if field == "support_contact_id":
                    try:
                        value = int(value)
                        if value <= 0:
                            return (False, "L'ID du support doit \
                            être un entier positif")
                        # Vérifier que le nouvel ID est bien un membre
                        # du support
                        if not self.user_dao.is_support(value):
                            return (False, "L'ID fourni n'est pas celui \
                                    d'un membre de l'équipe support")
                    except (ValueError, TypeError):
                        return (False, "L'ID du support doit être un nombre\
                                 entier valide")
                elif field in ["start_date", "end_date"]:
                    # Validation des dates (déjà faite au niveau CLI,
                    # mais double vérification)
                    from datetime import datetime
                    if not isinstance(value, datetime):
                        return False, f"Le champ {field} doit être\
                            une date valide"
                elif field == "attendees":
                    try:
                        value = int(value)
                        if value <= 0:
                            return (False, "Le nombre de participants doit \
                                être un entier positif")
                    except (ValueError, TypeError) as e:
                        log_exception(e, {
                            "action": "update_event"
                        })
                        return (False, "Le nombre de participants doit être un\
                            nombre entier valide")

                update_data[field] = value

        if not update_data:
            return False, "Aucune donnée à mettre à jour"

        try:
            nb = self.event_dao.update_event(event_id, update_data)
            if nb > 0:
                return True, "L'événement a été mis à jour avec succès"
            else:
                return False, "Aucun événement trouvé avec cet ID"
        except Exception as e:
            log_exception(e, {
                "action": "update_event"
            })
            return (False,
                    f"Erreur lors de la mise à jour de l'événement : {str(e)}")

    def get_events_by_support_contact_id(self):
        """Récupère les événements attribués à l'utilisateur support connecté

        Returns:
            tupple:
                   bool: True si la liste a bien été récupérée, False sinon
                   array: Liste des évenements (vide si erreur)
                   message:  message du résultat de l'opération

        """

        user = get_current_user_info()
        if not user:
            return False, [], "Utilisateur non authentifié"

        user_id = user.get("user_id")
        user_departement = user.get("departement", "").lower()

        if not user_id:
            return False, [], "ID utilisateur manquant"

        # Vérifier que l'utilisateur fait partie du département Support
        if user_departement != "support":
            return False, [], "Accès réservé au département Support"

        try:
            events = self.event_dao.get_event_if_assign(user_id)
            if events:
                return True, events, f"{len(events)} événement(s) attribué(s)"
            else:
                return True, [], "Aucun événement attribué"
        except Exception as e:
            log_exception(e, {
                "action": "get_events_by_support_contact_id"
            })
            return False, [], f"Erreur lors de la récupération : {str(e)}"

    def get_event_list(self):
        try:
            events = self.event_dao.get_all_events()
            if events:
                return True, events, "evenements récupérés"
            else:
                return True, [], "Aucun événements trouvés"
        except Exception as e:

            log_exception(e, {
                "action": "get_event_list",
                "events": events
            })
