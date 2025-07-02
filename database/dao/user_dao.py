from sqlalchemy import insert, update, select
from sqlalchemy.exc import IntegrityError
from database.schema import user, departement


class UserDAO:
    def __init__(self, engine):
        self.engine = engine

    def create_user(self, user_data):
        try:
            with self.engine.begin() as conn:
                stmt = insert(user).values(**user_data)
                result = conn.execute(stmt)
                return result.inserted_primary_key[0]
        except IntegrityError as e:
            if 'user_email_key' in str(e.orig):
                raise ValueError("Cet email existe déjà")
            raise

    def get_users(self):
        with self.engine.connect() as conn:
            stmt = select(user)
            result = conn.execute(stmt).fetchall()
            return result

    def get_user_by_id(self, user_id):
        """Récupère un utilisateur par son ID"""
        with self.engine.connect() as conn:
            stmt = select(user).where(user.c.id == user_id)
            result = conn.execute(stmt).fetchone()
            return result

    def select_user(self, session, username):
        with self.engine.connect():
            stmt = select(user).where(user.c.username == username)
            result = session.execute(stmt).fetchone()
            return result

    def update_user(self, user_id, user_data):
        with self.engine.begin() as conn:
            stmt = (
                update(user)
                .where(user.c.id == user_id)
                .values(**user_data)
            )
            result = conn.execute(stmt)
            return result.rowcount

    def has_departement(self, user_id, dept_name):
        with self.engine.connect() as conn:
            smtp = (
                select(
                    user.c.id, user.c.departement_id
                )
                .where(user.c.id == user_id)
            )
            result = conn.execute(smtp).fetchone()
            if not result or not result.departement_id:
                return False
            dept_stmt = select(departement.c.name).where(
                departement.c.id == result.departement_id)
            dept = conn.execute(dept_stmt).fetchone()
            return dept and dept.name.lower() == dept_name.lower()

    def is_commercial(self, user_id):
        return self.has_departement(user_id, "commercial")

    def is_gestion(self, user_id):
        return self.has_departement(user_id, "gestion")

    def is_support(self, user_id):
        return self.has_departement(user_id, "support")
