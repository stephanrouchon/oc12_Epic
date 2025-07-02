from sqlalchemy import select, insert
from database.database import engine
from database.schema import meta, departement


def init_db():
    # Création des tables si elles n'existent pas
    meta.create_all(engine)

    # Insertion des départements de référence
    departements_init = ["Gestion", "Commercial", "Support"]

    with engine.begin() as conn:
        result = conn.execute(select(departement.c.name))
        existing = {row[0] for row in result}
        to_insert = [{"name": name}
                     for name in departements_init if name not in existing]
        if to_insert:
            conn.execute(insert(departement), to_insert)
            print(f"Départements ajoutés : {[d['name'] for d in to_insert]}")
        else:
            print("Tous les départements existent déjà.")


if __name__ == "__main__":
    init_db()
