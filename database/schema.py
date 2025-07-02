from sqlalchemy import (MetaData, Table, Column, Integer, String, Float,
                        DateTime, ForeignKey, Boolean, Text)
from sqlalchemy import func

meta = MetaData()

departement = Table(
    "departement",
    meta,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False)
)

user = Table(
    "user",
    meta,
    Column('id', Integer, primary_key=True),
    Column('employee_number', Integer, unique=True),
    Column('username', String(40), nullable=False, unique=True),
    Column('password', String(255), nullable=False),
    Column('last_name', String(50), nullable=False),
    Column('first_name', String(50), nullable=False),
    Column('email', String(200), unique=True, nullable=False),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(),
           onupdate=func.now()),
    Column('departement_id', Integer, ForeignKey(
        'departement.id'), nullable=False)
)

client = Table(
    "client",
    meta,
    Column('id', Integer, primary_key=True),
    Column('fullname', String(255), nullable=False),
    Column('contact', String(255)),
    Column('email', String(255), unique=True),
    Column('phone_number', String(20)),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(),
           onupdate=func.now()),
    Column('commercial_id', Integer, ForeignKey(
        'user.id', ondelete='SET NULL'), nullable=True)
)

contract = Table(
    "contract",
    meta,
    Column('id', Integer, primary_key=True),
    Column('title', String(255)),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(),
           onupdate=func.now()),
    Column('client_id', Integer, ForeignKey('client.id'), nullable=False),
    Column('status', Boolean, server_default='0'),
    Column('amount', Float, server_default='0'),
    Column('paid_amount', Float, server_default='0')
)

event = Table(
    "event",
    meta,
    Column('id', Integer, primary_key=True),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(),
           onupdate=func.now()),
    Column('contract_id', Integer, ForeignKey('contract.id'),
           nullable=False),
    Column('start_date', DateTime),
    Column('end_date', DateTime, nullable=True),
    Column('location', Text, nullable=True),
    Column('attendees', Integer, nullable=True),
    Column('notes', Text, nullable=True),
    Column('support_contact_id', Integer, ForeignKey('user.id'),
           nullable=True)
)
