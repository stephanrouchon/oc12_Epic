from database.dao.client_dao import ClientDAO
from database.dao.user_dao import UserDAO
from database.database import engine
import services.utils as utils
from services.sentry_service import log_exception


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
        """Création d'un client

        Args:
            fullname (str): nom du client_
            contact (str): contact client_
            email (str): email du client_
            phone_number (str): telephone du client_
            commercial_id (int): id du commercial assigné_

        Returns:
            tupple: 
                success (bool): True if client is created, False else
                message (str): Message de résultat
        """

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
        except Exception as e:
            log_exception(e, {
                "action":"create_user",
            })
            return False, "erreur lors de la création"

    def get_clients(self):
        """retourne la liste des clients
        
        Returns:
            tuple: (success, message)
                - success (bool): True si la liste à été récupérée, False sinon
                - message (str): Message décrivant le résultat de l'opération
        
        """

        try:
            clients = self.client_dao.get_all_clients()
            if clients:
                return True, clients, "clients récupérés"
            else:
                return True, [], "Aucun client trouvé"
        except Exception as e:
            log_exception(e, {
                "action":"get clients"
            })

            return False, "Erreur lors de la récupération"

    def update_client(self,
                      client_id,
                      user_id,
                      user_departement,
                      **update_data
                      ):
        """Met à jour les informations d'un client existant.

        Cette méthode permet de modifier les données d'un client après avoir 
        vérifié les permissions d'accès et validé les données fournies.

        Contrôles d'accès :
        - Les utilisateurs du département "Commercial" ne peuvent modifier que leurs propres clients
        - Les autres départements (Gestion) peuvent modifier tous les clients

        Validations effectuées :
        - Vérification de l'existence du client
        - Validation du format email si fourni
        - Vérification que le commercial_id correspond à un utilisateur commercial

        Args:
            client_id (int): Identifiant unique du client à modifier
            user_id (int): Identifiant de l'utilisateur effectuant la modification
            user_departement (str): Département de l'utilisateur ("Commercial", "Gestion", etc.)
            **update_data: Données à mettre à jour. Clés possibles :
                - fullname (str): Nom complet du client
                - contact (str): Informations de contact
                - email (str): Adresse email (sera validée)
                - phone_number (str): Numéro de téléphone
                - commercial_id (int): ID du commercial assigné (sera vérifié)

        Returns:
            tuple: (success, message)
                - success (bool): True si la mise à jour a réussi, False sinon
                - message (str): Message décrivant le résultat de l'opération
                
        Raises:
            Exception: En cas d'erreur lors de l'accès à la base de données
        """

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
        except Exception as e:
            return False, "Erreur lors de la mise à jour"
