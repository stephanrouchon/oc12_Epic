from database.dao.contract_dao import ContractDAO
from database.dao.client_dao import ClientDAO
from database.dao.user_dao import UserDAO
from database.database import engine
from services.sentry_service import log_contract_signature, log_exception
from services.auth_service import get_current_user_info


class ContractService:
    def __init__(self):
        self.contract_dao = ContractDAO(engine)
        self.client_dao = ClientDAO(engine)
        self.user_dao = UserDAO(engine)

    def create_contract(self, title, client_id, amount):
        """
        Crée un nouveau contrat pour un client existant.

        Cette méthode valide l'existence du client avant de créer le contrat.
        Le contrat est créé avec un statut non signé (status=False) et sans
        commercial assigné.

        Args:
            title (str): Titre descriptif du contrat
            client_id (int): Identifiant du client auquel le contrat est
                rattaché
            amount (float): Montant total du contrat en euros

        Returns:
            tuple: (success, message)
                - success (bool): True si la création du contrat a réussi,
                  False sinon
                - message (str): Message décrivant le résultat de l'opération

        Raises:
            Les exceptions sont capturées et loggées via Sentry, retournant
            un tuple d'erreur
        """

        client = self.client_dao.exists(client_id)
        if not client:
            return False, "Client introuvable"

        contract_data = {
            "title": title,
            "client_id": client_id,
            "amount": amount
        }

        try:
            self.contract_dao.create_contract(contract_data)
            return True, "Le contrat a été crée"
        except Exception as e:
            log_exception(e, {
                "action": "create-contract"
            })
            return False, "Erreur lors de la création."

    def update_contract(self, contract_id, user_id, user_departement,
                        sign=None, paid_amount=None):
        """
        Permet la mise à jour d'un contrat existant.

        Cette méthode gère la signature et le paiement des contrats avec les
        règles suivantes :
        - Un commercial peut signer un contrat s'il est assigné au client ou
          si le client n'a pas de commercial
        - Seuls les utilisateurs du département "Gestion" peuvent modifier
          les montants payés
        - Les montants payés ne peuvent pas excéder le montant total du
          contrat

        Args:
            contract_id (int): Identifiant du contrat à mettre à jour
            user_id (int): Identifiant de l'utilisateur courant
            user_departement (str): Département de l'utilisateur
                ("Commercial", "Gestion", etc.)
            sign (bool, optional): Le contrat doit-il être signé.
                Defaults to None.
            paid_amount (float, optional): montant déjà payé.
                Defaults to None.

        Returns:
            tuple: (success, message)
                - success (bool): True si la mise à jour a réussi, False sinon
                - message (str): Message décrivant le résultat de l'opération
        """

        contract = self.contract_dao.get_contract_by_id(contract_id)
        if not contract:
            return False, f"Contrat avec l'ID {contract_id} introuvable"

        # Validation des droits pour les commerciaux
        # Note: contract.commercial_id vient de la table client (via JOIN)
        if user_departement.lower() == "commercial":
            # Un commercial peut mettre à jour un contrat si:
            # 1. Il est assigné au client du contrat, OU
            # 2. Le client n'a pas de commercial assigné
            if (contract.commercial_id is not None and
                    contract.commercial_id != user_id):
                return False, (f"Vous ne pouvez mettre à jour que les "
                               f"contrats de vos clients. Ce contrat "
                               f"appartient à un client assigné à un autre "
                               f"commercial (ID: {contract.commercial_id})")

        update_data = {}

        # Gestion de la signature
        if sign:
            update_data["status"] = True

            # Si le client n'a pas de commercial assigné et que l'utilisateur
            # est commercial, on peut assigner le commercial au client lors
            # de la signature
            if (contract.commercial_id is None and
                    user_departement.lower() == "commercial"):
                # Mettre à jour le commercial du client
                self.client_dao.update_client(
                    contract.client_id, {"commercial_id": user_id})

        # Gestion du paiement
        if paid_amount is not None and paid_amount > 0:
            if paid_amount > contract.amount:
                return False, (f"Le montant payé ({paid_amount}€) ne doit "
                               f"pas être supérieur au montant du contrat "
                               f"({contract.amount}€)")
            update_data["paid_amount"] = paid_amount

        if not update_data:
            return False, "Aucune donnée à mettre à jour"

        try:
            nb = self.contract_dao.update_contract(contract_id, update_data)
            if nb > 0:
                # Journaliser la signature de contrat si le statut passe à
                # True
                if "status" in update_data and update_data["status"] is True:
                    current_user = get_current_user_info()
                    signed_by = (current_user.get("username", "Unknown")
                                 if current_user else "System")

                    # Récupérer les informations du client pour le contrat
                    client = self.client_dao.get_client_by_id(
                        contract.client_id)
                    client_name = (client.fullname if client
                                   else f"Client-{contract.client_id}")

                    log_contract_signature(
                        contract_id=contract_id,
                        client_name=client_name,
                        amount=contract.amount,
                        signed_by=signed_by
                    )

                return True, "Le contrat a été mis à jour"
            else:
                return False, "Aucun contrat trouvé avec cet ID"
        except Exception as e:
            # Journaliser l'exception inattendue
            log_exception(e, {
                "action": "update_contract",
                "contract_id": contract_id,
                "update_data": update_data
            })
            return False, "Erreur lors de la mise à jour"

    def get_contract_list(self):
        """
        Récupère la liste complète de tous les contrats.

        Cette méthode retourne tous les contrats présents dans la base de
        données, peu importe leur statut (signé ou non signé).

        Returns:
            tuple: (success, contracts, message)
                - success (bool): True si la récupération a réussi, False
                  sinon
                - contracts (list): Liste des contrats ou liste vide en cas
                  d'erreur
                - message (str): Message décrivant le résultat de l'opération

        Raises:
            Les exceptions sont capturées et loggées via Sentry, retournant
            un tuple d'erreur
        """

        try:
            contracts = self.contract_dao.get_all_contracts()
            if contracts:
                return True, contracts, "Contrats récupérés"
            else:
                return True, [], "Aucun contrats trouvés"
        except Exception as e:

            log_exception(e, {
                "action": "get_contact_list",
                'contracts': contracts

            })
            return False, [], "Erreur lors de la récupération"

    def get_contract_list_not_sign(self):
        """
        Récupère la liste des contrats non signés.

        Cette méthode filtre les contrats ayant un statut False (non signé)
        et les retourne pour faciliter le suivi des contrats en attente.

        Returns:
            tuple: (success, contracts, message)
                - success (bool): True si la récupération a réussi, False sinon
                - contracts (list): Liste des contrats non signés ou liste vide
                - message (str): Message décrivant le résultat de l'opération

        Raises:
            Les exceptions sont capturées et loggées via Sentry,

            retournant un tuple d\'erreur
        """
        try:
            contracts = self.contract_dao.get_contracts_not_sign()
            if contracts:
                return True, contracts, "Contrats récupérés"
            else:
                return True, [], "Aucun contrats non signés trouvés"
        except Exception as e:

            log_exception(e, {
                "action": "get_contracts_not_sign",
            })
            return False, [], "Erreur lors de la récupération"

    def get_contract_list_not_fully_paid(self):
        """
        Récupère la liste des contrats non entièrement payés.

        Cette méthode filtre les contrats où le montant payé (paid_amount)
        est inférieur au montant total du contrat (amount), permettant
        un suivi efficace des paiements en attente.

        Returns:
            tuple: (success, contracts, message)
                - success (bool): True si la récupération a réussi, False sinon
                - contracts (list): Liste des contrats partiellement payés
                ou liste vide
                - message (str): Message décrivant le résultat de l'opération

        Raises:
            Les exceptions sont capturées et loggées via Sentry,
            retournant un tuple d'erreur
        """
        try:
            contracts = self.contract_dao.get_contracts_not_fully_paid()
            if contracts:
                return True, contracts, "Contrats récupérés"
            else:
                return True, [], ("Tous les contrats ont étés "
                                  "entièrement payés")
        except Exception as e:

            log_exception(e, {
                "action": "get_contracts_not_fully_paid",
            })
            return False, [], "Erreur lors de la récupération"
