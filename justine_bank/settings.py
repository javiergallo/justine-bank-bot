from typing import List

from pydantic import AnyUrl, BaseModel, BaseSettings, conint, constr

from justine_bank.constants import USERNAME_REGEX


class DatabaseConfig(BaseModel):
    url: AnyUrl = "sqlite:///db.sqlite"


class Config(BaseSettings):
    api_token: str = ""
    staff_usernames: List[constr(regex=USERNAME_REGEX)] = []
    database_config: DatabaseConfig = DatabaseConfig()
    poll_interval: conint(gt=0) = 3


config = Config(_env_file=".env")
