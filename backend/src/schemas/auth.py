from pydantic import BaseModel


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class LoginRequest(BaseModel):
    identifier: str
    password: str
