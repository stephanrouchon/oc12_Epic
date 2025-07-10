import os
from argon2 import PasswordHasher
from database.database import engine

from database.dao.user_dao import UserDAO
from database.dao.departement_dao import DepartementDAO

ph = PasswordHasher()

class AdminService:

    def __init__(self):
        self.departement_dao = DepartementDAO(engine)
        self.user_dao = UserDAO(engine)
    
    def create_first_user(self, username, email, first_name, last_name, employee_number, password):       
        departements = self.departement_dao.get_all_departements()

        gestion_id = next(
        (id for id, name in departements if name.lower() == "gestion"), None)

        if gestion_id is None:
            print("Département 'gestion' introuvable. Crée-le d'abord.")
            return
        
        hashed_password = ph.hash(password)

        user_data = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": hashed_password,
        "employee_number": employee_number,
        "departement_id": gestion_id
        }
        
        self.user_dao.create_user(user_data)