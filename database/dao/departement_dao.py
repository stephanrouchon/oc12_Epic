from sqlalchemy import insert, select
from database.schema import departement


class DepartementDAO:
    def __init__(self, engine):
        self.engine = engine

    def create_departement(self, departement_data):
        with self.engine.begin() as conn:
            stmt = insert(departement).values(**departement_data)
            result = conn.execute(stmt)
            return result.inserted_primary_key[0]

    def get_all_departements(self):
        with self.engine.connect() as conn:
            result = conn.execute(select(departement))
            return [(row.id, row.name) for row in result]

    def get_departement_by_id(self, departement_id):
        with self.engine.connect() as conn:
            stmt = select(departement).where(
                departement.c.id == departement_id)
            result = conn.execute(stmt).fetchone()
            return result

    def get_departement_name_by_id(self, session, departement_id):
        stmt = select(departement).where(departement.c.id == departement_id)
        dept = session.execute(stmt).fetchone()
        return dept.name if dept else None
