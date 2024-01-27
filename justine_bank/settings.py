from typing import List

from pydantic import AnyUrl, BaseModel, BaseSettings, conint, constr

from justine_bank.constants import USERNAME_REGEX


class DatabaseConfig(BaseModel):
    url: AnyUrl = "sqlite:///db.sqlite"


class WalletsConfig(BaseModel):
    list_restricted: bool = True
    show_restricted: bool = False

    sorted_by_username: bool = True


class TransfersConfig(BaseModel):
    action_restricted: bool = False
    list_restricted: bool = True


class Config(BaseSettings):
    api_token: str = ""
    staff_usernames: List[constr(regex=USERNAME_REGEX)] = []
    poll_interval: conint(gt=0) = 3

    database: DatabaseConfig = DatabaseConfig()

    wallets: WalletsConfig = WalletsConfig()
    transfers: TransfersConfig = TransfersConfig()

    class Config:
        env_nested_delimiter = '__'


config = Config(_env_file=".env")
