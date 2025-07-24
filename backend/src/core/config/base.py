from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field


class Database(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: str = Field(..., exclude=True)

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class BaseConfig(BaseSettings):
    environment: str = "local"
    db: Database
