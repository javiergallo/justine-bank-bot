from typing import List

from pydantic import AnyUrl, BaseModel, BaseSettings, conint, constr

from justine_bank.constants import USERNAME_REGEX


class DatabaseConfig(BaseModel):
    url: AnyUrl = "sqlite:///db.sqlite"


class Config(BaseSettings):
    api_token: str = ""
    staff_usernames: List[constr(regex=USERNAME_REGEX)] = []
    database: DatabaseConfig = DatabaseConfig()
    poll_interval: conint(gt=0) = 3

    class Config:
        env_nested_delimiter = '__'


config = Config(_env_file=".env")
