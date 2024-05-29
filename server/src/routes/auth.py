from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import users as repository_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.

    :param body: Data representing the new user.
    :param bt: BackgroundTasks to run email sending asynchronously.
    :param request: Request object to retrieve base URL.
    :param db: AsyncSession instance for database interaction.
    :return: Newly created UserResponse object.
    """
    try:
        print(f"Received signup request for email: {body.email}")
        exist_user = await repository_users.get_user_by_email(body.email, db)
        if exist_user:
            print(f"User with email {body.email} already exists.")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

        result = await db.execute(select(User))
        users = result.scalars().all()

        role = Role.admin if not users else Role.user

        body.password = auth_service.get_password_hash(body.password)

        new_user = User(
            username=body.username,
            email=body.email,
            password=body.password,
            role=role
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))

        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            avatar=new_user.avatar,
            role=new_user.role,
            registered_at=new_user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            num_photos=0
        )

    except HTTPException as e:
        print(f"HTTPException occurred: {e.detail}")
        raise e
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: " + str(e))
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Log in a user and generate access tokens.

    :param body: OAuth2PasswordRequestForm containing login credentials.
    :param db: AsyncSession instance for database interaction.
    :return: TokenSchema containing access_token and refresh_token.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email, "test": "ВалЄра"})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/logout")
async def logout_user(background_tasks: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Log out a user by revoking access tokens.

    :param background_tasks: BackgroundTasks to run token revocation asynchronously.
    :param request: Request object to retrieve user's email.
    :param db: AsyncSession instance for database interaction.
    :return: Success message if user is logged out.
    """
    authorization_header = request.headers.get("Authorization")
    if authorization_header is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is missing")

    token_parts = authorization_header.split(" ")
    if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")

    token = token_parts[1]
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    await repository_users.update_token(user, None, db)
    return {"message": "User logged out successfully"}


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
    Refresh access_token using refresh_token.

    :param credentials: HTTPAuthorizationCredentials containing refresh_token.
    :param db: AsyncSession instance for database interaction.
    :return: TokenSchema containing refreshed access_token and new refresh_token.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm user's email address.

    :param token: Verification token.
    :param db: AsyncSession instance for database interaction.
    :return: Success message if email is confirmed.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    Request email confirmation.

    :param body: RequestEmail containing email address.
    :param background_tasks: BackgroundTasks to run email sending asynchronously.
    :param request: Request object to retrieve base URL.
    :param db: AsyncSession instance for database interaction.
    :return: Success message if email is requested for confirmation.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation"}
