from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field


class JWT(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: float = 60
    refresh_token_expire_minutes: float = 60


class Redis(BaseModel):
    url: str


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
    jwt: JWT
    db: Database
    redis: Redis
