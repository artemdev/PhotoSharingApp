from typing import Optional, Sequence
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, func, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar
from typing import List

from src.database.db import get_db
from src.database.models import User, Role, Picture
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


async def get_all_users(db: AsyncSession = Depends(get_db)) -> Sequence[User]:
    """
    Retrieves all users from the database.

    :param db: AsyncSession instance for database interaction.
    :return: List of User objects.
    """
    stmt = select(User)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users


async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)) -> Optional[User]:
    """
    Retrieves a user from the database by ID.

    :param user_id: ID of the user.
    :param db: AsyncSession instance for database interaction.
    :return: Optional[User] if the user is found, otherwise None.
    """
    stmt = select(User).filter_by(id=user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def update_user_role(user_id: int, new_role: Role, db: AsyncSession = Depends(get_db)) -> User:
    """
    Updates the role of a user in the database.

    :param user_id: The ID of the user to update.
    :param new_role: The new role to assign to the user.
    :param db: AsyncSession instance for database interaction.
    :return: Updated User object.
    """
    try:
        user_id = int(user_id)
        stmt = update(User).where(User.id == user_id).values(role=new_role).returning(User)
        result = await db.execute(stmt)
        await db.commit()
        user = result.scalar_one()
        return user
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_user_photo_count(user_id: int, db: AsyncSession):
    """
    Returns the count of photos belonging to a user.
    """
    stmt = select(func.count()).where(Picture.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar()
