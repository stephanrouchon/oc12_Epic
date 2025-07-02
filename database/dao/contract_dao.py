from sqlalchemy import insert, update, select
from database.schema import contract, client


class ContractDAO:
    def __init__(self, engine):
        self.engine = engine

    def create_contract(self, contract_data):
        with self.engine.begin() as conn:
            stmt = insert(contract).values(**contract_data)
            result = conn.execute(stmt)
            return result

    def update_contract(self, contract_id, update_data):

        with self.engine.begin() as conn:
            stmt = (
                update(contract)
                .where(contract.c.id == contract_id)
                .values(**update_data)
            )
            result = conn.execute(stmt)
            return result.rowcount

    def exists(self, contract_id):

        with self.engine.begin() as conn:
            stmt = (
                select(
                    contract.c.id
                )
                .where(contract.c.id == contract_id)
            )
            result = conn.execute(stmt).fetchone()
            return result is not None

    def get_all_contracts(self):
        with self.engine.connect()as conn:
            query = (
                select(
                    contract, client.c.fullname
                )
                .select_from(
                    contract.join(client, contract.c.client_id == client.c.id)
                )

            )

            result = conn.execute(query).fetchall()
            return result

    def get_contract_by_id(self, contract_id):
        with self.engine.connect()as conn:
            query = (
                select(
                    contract, client.c.fullname, client.c.commercial_id
                )
                .select_from(
                    contract.join(client, contract.c.client_id == client.c.id)
                )
                .where(
                    contract.c.id == contract_id
                )

            )

            result = conn.execute(query).fetchone()
            return result

    def get_all_contracts_filter_by_client(self, client_id):
        with self.engine.connect() as conn:
            query = (
                select(contract, client.c.fullname)
                .select_from(
                    contract.join(client, contract.c.client_id == client.c.id)
                )
                .where(contract.c.client_id == client_id)
            )
            result = conn.execute(query).fetchall()
            return result

    def get_contracts_not_sign(self):
        with self.engine.connect() as conn:
            query = (
                select(contract,
                       client.c.fullname
                       )
                .select_from(
                    contract.join(client, contract.c.client_id == client.c.id)
                )
                .where(contract.c.status.is_(False))
            )
            result = conn.execute(query).fetchall()
            return result

    def get_contracts_not_fully_paid(self):
        with self.engine.connect() as conn:
            query = (select(
                contract,
                client.c.fullname,
            )
                .select_from(
                    contract.join(client, contract.c.client_id == client.c.id)
            )
                .where((contract.c.paid_amount < contract.c.amount))
            )

            result = conn.execute(query).fetchall()
            return result
