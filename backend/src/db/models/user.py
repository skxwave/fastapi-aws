from datetime import datetime
from uuid import uuid4, UUID

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    wallet_address: Mapped[str] = mapped_column(nullable=True, unique=True)
    nonce: Mapped[str] = mapped_column(nullable=True)
    hashed_password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Web3User(Base):
    __tablename__ = "web3_users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    wallet_address: Mapped[str] = mapped_column(unique=True)
    nonce: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
