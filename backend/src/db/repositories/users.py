from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.models import User, Web3User
from src.schemas.auth import Nonce, Web3NonceRequest
from src.schemas.user import UserCreate
from src.services.auth import hash_password, verify_password
from src.services.jwt_service import create_token_pair
from src.services.web3_auth import create_nonce


class UserRepository:
    async def register_user(
        self,
        user_create: UserCreate,
        session: AsyncSession,
    ) -> User:
        existing_user = await session.scalar(
            select(User).where(
                (User.email == user_create.email)
                | (User.username == user_create.username)
            )
        )
        if existing_user:
            raise ValueError("User with this email or username already exists")

        user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hash_password(user_create.password),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return create_token_pair(user)

    async def authenticate_user(
        self,
        identifier: str,
        password: str,
        session: AsyncSession,
    ) -> User | None:
        user = await session.scalar(
            select(User).where(
                or_(
                    User.username == identifier,
                    User.email == identifier,
                )
            )
        )
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        return create_token_pair(user)

    async def get_and_save_nonce(
        self,
        data: Web3NonceRequest,
        session: AsyncSession,
    ):
        user: Web3User = await session.scalar(
            select(Web3User).where(Web3User.wallet_address == data.wallet)
        )
        nonce = create_nonce()

        if not user:
            user = Web3User(
                wallet_address=data.wallet,
                nonce=nonce,
            )
            session.add(user)
        else:
            user.nonce = nonce
        await session.commit()
        return Nonce(nonce=nonce)


user_repo = UserRepository()
