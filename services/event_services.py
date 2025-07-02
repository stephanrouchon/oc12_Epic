from database.dao.contract_dao import ContractDAO
from database.dao.event_dao import EventDAO
from database.dao.user_dao import UserDAO
from database.database import engine
from services.auth_service import get_current_user_info


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
            return False, f"erreur lors de la création : {str(e)}"

    def update_event(self,
                     event_id,
                     **kwargs):

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
                return False, "Vous ne pouvez mettre à jour que les événements qui vous sont attribués"

        # Validation et préparation des données
        update_data = {}
        for field, value in kwargs.items():
            if value is not None and value != "":
                if field == "support_contact_id":
                    try:
                        value = int(value)
                        if value <= 0:
                            return False, "L'ID du support doit être un entier positif"
                        # Vérifier que le nouvel ID est bien un membre du support
                        if not self.user_dao.is_support(value):
                            return False, "L'ID fourni n'est pas celui d'un membre de l'équipe support"
                    except (ValueError, TypeError):
                        return False, "L'ID du support doit être un nombre entier valide"
                elif field in ["start_date", "end_date"]:
                    # Validation des dates (déjà faite au niveau CLI, mais double vérification)
                    from datetime import datetime
                    if not isinstance(value, datetime):
                        return False, f"Le champ {field} doit être une date valide"
                elif field == "attendees":
                    try:
                        value = int(value)
                        if value <= 0:
                            return False, "Le nombre de participants doit être un entier positif"
                    except (ValueError, TypeError):
                        return False, "Le nombre de participants doit être un nombre entier valide"
                
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
            return False, f"Erreur lors de la mise à jour de l'événement : {str(e)}"

    def get_events_by_support_contact_id(self):
        """Récupère les événements attribués à l'utilisateur support connecté"""
        
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
            return False, [], f"Erreur lors de la récupération : {str(e)}"
