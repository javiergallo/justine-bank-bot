from pydantic import AnyUrl, BaseModel, BaseSettings


class DatabaseConfig(BaseModel):
    url: AnyUrl = "sqlite:///db.sqlite"


class Config(BaseSettings):
    database_config: DatabaseConfig = DatabaseConfig()


config = Config()
