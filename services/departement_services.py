
from database.dao.departement_dao import DepartementDAO
from database.database import engine

departement_dao = DepartementDAO(engine)


def get_departement_choice():
    """ renvoi le nom des départements existants """
    departements = departement_dao.get_all_departements()
    dept_names = [name for _, name in departements]

    return dept_names


def get_departement_id_by_name(dept_name):
    """Permet d'obtenir l'id par son nom 

    Args:
        dept_name (str): nom du département

    Returns:
        int : identifiant du département demandé
    """
    departements = departement_dao.get_all_departements()
    departement_id = next(
        (id for id, name in departements if name.lower() == dept_name.lower()), None)
    if departement_id is None:
        return None
    return departement_id
