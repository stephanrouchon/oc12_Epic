from sqlalchemy import insert, update, select
from database.schema import client, user


class ClientDAO:
    def __init__(self, engine):
        self.engine = engine

    def create_client(self, client_data):
        with self.engine.begin() as conn:
            stmt = insert(client).values(**client_data)
            result = conn.execute(stmt)
            return result.inserted_primary_key

    def get_client_by_id(self, client_id):
        with self.engine.connect() as conn:
            stmt = (
                select(
                    client
                )
                .where(client.c.id == client_id)
            )

            result = conn.execute(stmt)
            return result

    def exists(self, client_id):
        with self.engine.connect() as conn:
            stmt = (
                select(
                    client.c.id
                )
                .where(client.c.id == client_id)
            )
            result = conn.execute(stmt).fetchone()
            return result is not None

    def update_client(self, client_id, client_data):
        with self.engine.begin() as conn:
            stmt = (
                update(client)
                .where(client.c.id == client_id)
                .values(**client_data)
            )
            result = conn.execute(stmt)
            return result.rowcount

    def get_all_clients(self):
        with self.engine.connect() as conn:
            stmt = (
                select(
                    client,
                    user.c.first_name.label("commercial_first_name"),
                    user.c.last_name.label("commercial_last_name")
                )
                .join(user, client.c.commercial_id == user.c.id)
            )

            result = conn.execute(stmt)

            return result
