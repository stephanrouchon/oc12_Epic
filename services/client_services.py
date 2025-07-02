from database.dao.client_dao import ClientDAO
from database.dao.user_dao import UserDAO
from database.database import engine
import services.utils as utils


class ClientService:
    def __init__(self):
        self.client_dao = ClientDAO(engine)
        self.user_dao = UserDAO(engine)

    def create_client(self,
                      fullname,
                      contact,
                      email,
                      phone_number,
                      commercial_id
                      ):

        if not utils.is_valid_email(email):
            return False, "L'email n'est pas valide"

        if not self.user_dao.is_commercial(commercial_id):
            return False, "L'ID n'est pas celui d'un commercial"

        client_data = {
            "fullname": fullname,
            "contact": contact,
            "email": email,
            "phone_number": phone_number,
            "commercial_id": commercial_id
        }

        try:
            self.client_dao.create_client(client_data)
            return True, "Le client a été crée"
        except Exception:
            return False, "erreur lors de la création"

    def get_clients(self):

        try:
            clients = self.client_dao.get_all_clients()
            if clients:
                return True, clients, "clients récupérés"
            else:
                return True, [], "Aucun client trouvé"
        except Exception:
            return False, "Erreur lors de la récupération"

    def update_client(self,
                      client_id,
                      user_id,
                      user_departement,
                      **update_data
                      ):
        client = self.client_dao.get_client_by_id(client_id)
        if not client:
            return False, "Client introuvable"

        if user_departement.lower() == "Commercial":
            if client.commercial_id != user_id:
                return False, "Vous ne pouvez mettre à jour que vos clients"

        if 'email' in update_data and update_data["email"]:
            if not utils.is_valid_email(update_data['email']):
                return False, "Email invalide"

        if 'commercial_id' in update_data and update_data["commercial_id"]:
            if not self.user_dao.is_commercial(update_data['commercial_id']):
                return False, "L'ID n'est pas l'ID d'un commercial"

        filtered_data = {k: v for k, v in update_data.items()
                         if v is not None and v != ""}

        if not filtered_data:
            return False, "Aucune donnée mise à jour"

        try:
            nb = self.client_dao.update_client(client_id, filtered_data)
            if nb > 0:
                return True, "Le client a été mis à jour"
            else:
                return False, "Aucun client trouvé avec cet ID"
        except Exception:
            return False, "Erreur lors de la mise à jour"
