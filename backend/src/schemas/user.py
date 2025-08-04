from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: str
    username: str
    email: EmailStr


class Web3UserRead(BaseModel):
    id: str
    wallet: str
