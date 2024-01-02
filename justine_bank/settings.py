from pydantic import AnyUrl, BaseModel, BaseSettings, conint


class DatabaseConfig(BaseModel):
    url: AnyUrl = "sqlite:///db.sqlite"


class Config(BaseSettings):
    api_token: str
    username: str = "JustineBankBot"

    database_config: DatabaseConfig = DatabaseConfig()

    poll_interval: conint(gt=0) = 3


config = Config(_env_file=".env")
