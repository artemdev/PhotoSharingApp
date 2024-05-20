"""
Module for authentication services.

This module defines an `Auth` class that provides various methods for user authentication and token management.
An instance of the `Auth` class named `auth_service` is created for authentication purposes.

"""

import pickle
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from server.src.conf.config import config
from server.src.database.db import get_db
from server.src.repository import users as repository_users
import redis


class Auth:
    """
    Class containing authentication methods.
    Attributes:
    - pwd_context (CryptContext): Password hashing context.
    - SECRET_KEY (str): Secret key for token generation.
    - ALGORITHM (str): JWT encryption algorithm.
    - oauth2_scheme (OAuth2PasswordBearer): OAuth2 password bearer scheme.
    - r (Redis): Redis instance for caching user data.

    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.CLD_API_SECRET
    ALGORITHM = config.ALGORITHM
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        Verify password hash.

        :param plain_password: Plain password.
        :type plain_password: str
        :param hashed_password: Hashed password.
        :type hashed_password: str
        :return: True if the plain password matches the hashed password, False otherwise.
        :rtype: bool

        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Get password hash.

        :param password: Password.
        :type password: str
        :return: Hashed password
        :rtype: str

        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create access token.

        :param data: Data to encode in the token.
        :type data: dict
        :param expires_delta: Expiry time for the token. Defaults to None.
        :type expires_delta: float, optional
        :return: Encoded access token.
        :rtype: str

        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=45)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create refresh token.

        :param data: Data to encode in the token.
        :type data: dict
        :param expires_delta: Expiry time for the token. Defaults to None.
        :type expires_delta: float, optional
        :return: Encoded refresh token.
        :rtype: str

        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode refresh token.

        :param refresh_token: Refresh token to decode.
        :type refresh_token: str
        :return: Email associated with the refresh token.
        :rtype: str

        Raises:
        HTTPException: If the token is invalid.

        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    def create_email_token(self, data: dict):
        """
        Create email verification token.

        :param data: Data to encode in the token.
        :type data: dict
        :return: Encoded email verification token.
        :rtype: str

        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Get current user from token.

        :param token: Authentication token. Defaults to Depends(oauth2_scheme).
        :type token: str
        :param db: The database session.
        :type db: Session
        :return: Current user details.
        :rtype: User model

        Raises:
        HTTPException: If the token is invalid or user is not found.

        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user

    async def get_email_from_token(self, token: str):
        """
        Get email from token.

        :param token: Token to decode.
        :type token: dict
        :return: Email extracted from the token.
        :rtype: str

        Raises:
        HTTPException: If the token is invalid.

        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()

