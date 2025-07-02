from sqlalchemy import insert, select, update
from database.schema import event


class EventDAO:
    def __init__(self, engine):
        self.engine = engine

    def create_event(self, event_data):
        with self.engine.begin() as conn:
            stmt = insert(event).values(**event_data)
            result = conn.execute(stmt)
            return result
        
    def update_event(self, event_id, update_data):
        with self.engine.begin() as conn:
            stmt = (
                update(event)
                .where(event.c.id == event_id)
                .values(**update_data)
            )
            result = conn.execute(stmt)
            return result.rowcount

    def get_all_events(self):
        with self.engine.connect() as conn:
            result = conn.execute(select(event))
            return result

    def get_event_by_id(self, event_id):
        with self.engine.connect() as conn:
            query = select(event).where(event.c.id == event_id)
            result = conn.execute(query).fetchone()
            return result

    def get_event_if_assign(self, user_id):
        with self.engine.connect() as conn:
            query = (
                select(event)
                .where(event.c.support_contact_id == user_id)
            )

            result = conn.execute(query).fetchall()
            return result
