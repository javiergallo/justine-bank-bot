import databases
import sqlalchemy

import ormar

DATABASE_URL = "sqlite:///db.sqlite"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


class Wallet(ormar.Model):
    class Meta:
        database = database
        metadata = metadata

    id: int = ormar.Integer(primary_key=True)

    owner_username: str = ormar.String(max_length=120)
    balance: float = ormar.Float(default=0.0, minimum=0.0)


class Issue(ormar.Model):
    class Meta:
        database = database
        metadata = metadata


    id: int = ormar.Integer(primary_key=True)

    recipient: Wallet = ormar.ForeignKey(Wallet, nullable=False)
    amount: float = ormar.Float(minimum=0.0)


class Transfer(ormar.Model):
    class Meta:
        database = database
        metadata = metadata


    id: int = ormar.Integer(primary_key=True)

    sender: Wallet = ormar.ForeignKey(
        Wallet, nullable=False, related_name="debits"
    )
    recipient: Wallet = ormar.ForeignKey(
        Wallet, nullable=False, related_name="credits"
    )
    amount: float = ormar.Float(minimum=0.0)


engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)