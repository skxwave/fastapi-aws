import secrets
import string

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eth_account import Account
from eth_account.messages import encode_defunct

from src.services.auth import create_token_pair
from src.db.models import Web3User


def create_nonce(length: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def verify_signature(
    signature: str,
    expected_address: str,
    session: AsyncSession,
) -> bool:
    user = await session.scalar(
        select(Web3User).where(Web3User.wallet_address == expected_address)
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    try:
        # EIP-191 encoding
        encoded_message = encode_defunct(text=user.nonce)
        recovered_address = Account.recover_message(
            encoded_message,
            signature=signature,
        )
        # Compare lowercase to avoid checksum issues
        if recovered_address.lower() == expected_address.lower():
            return create_token_pair(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e,
        )
