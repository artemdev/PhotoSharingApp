from libgravatar import Gravatar
from sqlalchemy.orm import Session

from server.src.database.models import User
from server.src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Identify a user with the specified email.

    :param email: The email of the user to identify.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user with the specified email, or None if it does not exist.
    :rtype: User | None

    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new contact for a specific user.

    :param body: The data for the user to create.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: The newly created user.
    :rtype: User

    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update the user's token.

    :param user: The user to update the token for.
    :type user: User
    :param token: The user's token or None.
    :type token: str | None
    :param db: The database session.
    :type db: Session
    :return: None.
    :rtype: None

    """

    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Set users.confirmed = True in the users table.

    :param email: The email of the user to confirm.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: None.
    :rtype: None

    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update the user's avatar.

    :param email: The user's email.
    :type email: str
    :param url: The user's email.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: The user with new avatar.
    :rtype: User

    """

    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
