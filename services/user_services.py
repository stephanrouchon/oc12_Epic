from argon2 import PasswordHasher
from database.dao.user_dao import UserDAO
from database.database import engine
from services import utils
from services.sentry_service import log_user_creation, log_user_update, log_exception
from services.auth_service import get_current_user_info


class UserService:
    def __init__(self):
        self.user_dao = UserDAO(engine)

    def create_user(self,
                    username,
                    employee_number,
                    email,
                    first_name,
                    last_name,
                    password,
                    departement_id,
                    ):

        ph = PasswordHasher()
        hash_password = ph.hash(password)

        if not utils.is_valid_email(email):
            return False, "Email invalide"

        user_data = {
            "username": username,
            "employee_number": employee_number,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": hash_password,
            "departement_id": departement_id,
        }

        try:
            user_id = self.user_dao.create_user(user_data)
            
            # Journaliser la création d'utilisateur dans Sentry
            current_user = get_current_user_info()
            created_by = current_user.get("username", "Unknown") if current_user else "System"
            
            # Récupérer le nom du département
            from database.dao.departement_dao import DepartementDAO
            dept_dao = DepartementDAO(engine)
            dept_name = dept_dao.get_departement_name_by_id(None, departement_id)
            
            log_user_creation(
                user_id=user_id,
                username=username,
                departement=dept_name or "Unknown",
                created_by=created_by
            )
            
            return True, "L'utilisateur a été crée avec succès"
        except Exception as e:
            # Journaliser l'exception inattendue
            log_exception(e, {
                "action": "create_user",
                "username": username,
                "email": email
            })
            return False, f"Erreur lors de la création : {str(e)}"

    def get_users(self):
        users = self.user_dao.get_users()
        return users

    def update_user(self, user_id, **kwargs):
        """
        Met à jour un utilisateur avec les champs fournis
        """
        update_data = {}

        # Validation et préparation des données
        for field, value in kwargs.items():
            if value is not None and value != "":
                if field == "email" and not utils.is_valid_email(value):
                    return False, "Email invalide"
                elif field == "employee_number":
                    try:
                        value = int(value)
                        if value <= 0:
                            return False, "Le matricule doit être " \
                                "un entier positif"
                    except (ValueError, TypeError):
                        return False, "Le matricule doit être"\
                            " un nombre entier valide"
                elif field == "password":
                    # Hasher le mot de passe si fourni
                    ph = PasswordHasher()
                    value = ph.hash(value)

                update_data[field] = value

        if not update_data:
            return False, "Aucune donnée à mettre à jour"

        try:
            rows_updated = self.user_dao.update_user(user_id, update_data)
            if rows_updated > 0:
                # Journaliser la modification d'utilisateur
                current_user = get_current_user_info()
                updated_by = current_user.get("username", "Unknown") if current_user else "System"
                
                # Récupérer le nom d'utilisateur de celui qui est modifié
                updated_user = self.user_dao.get_user_by_id(user_id)
                username = updated_user.username if updated_user else f"User-{user_id}"
                
                log_user_update(
                    user_id=user_id,
                    username=username,
                    updated_fields=list(update_data.keys()),
                    updated_by=updated_by
                )
                
                return True, "Utilisateur mis à jour avec succès"
            else:
                return False, "Aucun utilisateur trouvé avec cet ID"
        except Exception as e:
            # Journaliser l'exception inattendue
            log_exception(e, {
                "action": "update_user",
                "user_id": user_id,
                "update_fields": list(update_data.keys())
            })
            return False, f"Erreur lors de la mise à jour : {str(e)}"
