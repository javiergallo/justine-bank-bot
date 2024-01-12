import databases
import sqlalchemy

import ormar

from datetime import datetime

from justine_bank.constants import USERNAME_REGEX
from justine_bank.settings import config

database = databases.Database(config.database.url)
metadata = sqlalchemy.MetaData()


class Wallet(ormar.Model):
    class Meta:
        database = database
        metadata = metadata

    id: int = ormar.Integer(primary_key=True)

    creation_datetime: datetime = ormar.DateTime(default=datetime.utcnow)
    update_datetime: datetime = ormar.DateTime(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    owner_username: str = ormar.String(max_length=120, regex=USERNAME_REGEX)
    balance: float = ormar.Float(default=0.0, minimum=0.0)


class Issue(ormar.Model):
    class Meta:
        database = database
        metadata = metadata

    id: int = ormar.Integer(primary_key=True)

    creation_datetime: datetime = ormar.DateTime(default=datetime.utcnow)

    recipient: Wallet = ormar.ForeignKey(Wallet, nullable=False)
    amount: float = ormar.Float(minimum=0.0)


class Transfer(ormar.Model):
    class Meta:
        database = database
        metadata = metadata

    id: int = ormar.Integer(primary_key=True)

    creation_datetime: datetime = ormar.DateTime(default=datetime.utcnow)

    sender: Wallet = ormar.ForeignKey(
        Wallet, nullable=False, related_name="debits"
    )
    recipient: Wallet = ormar.ForeignKey(
        Wallet, nullable=False, related_name="credits"
    )
    amount: float = ormar.Float(minimum=0.0)


engine = sqlalchemy.create_engine(config.database.url)
metadata.create_all(engine)
