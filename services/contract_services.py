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
        except Exception:
            return False, "Erreur lors de la création."

    def update_contract(self, contract_id,
                        user_id,
                        user_departement,
                        sign=None,
                        paid_amount=None):
        contract = self.contract_dao.get_contract_by_id(contract_id)
        if not contract:
            return False, "Contrat introuvable"

        if user_departement.lower() == "commercial":
            if contract.commercial_id != user_id:
                return False, "Vous ne pouvez mettre à jour que les" \
                    " contrats de vos clients"

        update_data = {}

        if sign:
            update_data["status"] = True

        if paid_amount is not None and paid_amount > 0:
            if paid_amount > contract.amount:
                return False, "Le montant payé ne doit pas être supérieur" \
                      "au montant du contrat"
            update_data["paid_amount"] = paid_amount

        if not update_data:
            return False, "Aucune donnée à mettre à jour"

        try:
            nb = self.contract_dao.update_contract(contract_id, update_data)
            if nb > 0:
                # Journaliser la signature de contrat si le statut passe à True
                if "status" in update_data and update_data["status"] is True:
                    current_user = get_current_user_info()
                    signed_by = current_user.get("username", "Unknown") if current_user else "System"
                    
                    # Récupérer les informations du client pour le contrat
                    client = self.client_dao.get_client_by_id(contract.client_id)
                    client_name = client.fullname if client else f"Client-{contract.client_id}"
                    
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
        try:
            contracts = self.contract_dao.get_all_contracts()
            if contracts:
                return True, contracts, "Contrats récupérés"
            else:
                return True, [], "Aucun contrats trouvés"
        except Exception:
            return False, [], "Erreur lors de la récupération"

    def get_contract_list_not_sign(self):
        try:
            contracts = self.contract_dao.get_contracts_not_sign()
            if contracts:
                return True, contracts, "Contrats récupérés"
            else:
                return True, [], "Aucun contrats non signés trouvés"
        except Exception:
            return False, [], "Erreur lors de la récupération"

    def get_contract_list_not_fully_paid(self):
        try:
            contracts = self.contract_dao.get_contracts_not_fully_paid()
            if contracts:
                return True, contracts, "Contrats récupérés"
            else:
                return True, [], "Tous les contrats ont étés entièrement payés"
        except Exception:
            return False, [], "Erreur lors de la récupération"
