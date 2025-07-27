from pydantic import BaseModel


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class LoginRequest(BaseModel):
    identifier: str
    password: str


class Web3NonceRequest(BaseModel):
    wallet: str


class Web3LoginRequest(BaseModel):
    nonce: str
    address: str
    signature: str


class Nonce(BaseModel):
    nonce: str
