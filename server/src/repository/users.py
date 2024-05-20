from typing import Optional
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.database.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)) -> Optional[User]:
    """
    Retrieves a user from the database by email.

    :param email: Email address of the user.
    :param db: AsyncSession instance for database interaction.
    :return: Optional[User] if the user is found, otherwise None.
    """
    stmt = select(User).filter_by(email=email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)) -> User:
    """
    Creates a new user in the database.

    :param body: UserSchema containing user data.
    :param db: AsyncSession instance for database interaction.
    :return: Created User object.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: Optional[str], db: AsyncSession):
    """
    Updates the refresh token for a user in the database.

    :param user: User object to update.
    :param token: New refresh token.
    :param db: AsyncSession instance for database interaction.
    """
    user.refresh_token = token
    await db.commit()
    await db.refresh(user)


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Confirms a user's email address in the database.

    :param email: Email address to confirm.
    :param db: AsyncSession instance for database interaction.
    """
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        await db.commit()
        await db.refresh(user)


async def update_avatar_url(email: str, url: Optional[str], db: AsyncSession) -> Optional[User]:
    """
    Updates the avatar URL for a user in the database.

    :param email: Email address of the user.
    :param url: New avatar URL.
    :param db: AsyncSession instance for database interaction.
    :return: Updated User object if found, otherwise None.
    """
    user = await get_user_by_email(email, db)
    if user:
        user.avatar = url
        await db.commit()
        await db.refresh(user)
    return user
