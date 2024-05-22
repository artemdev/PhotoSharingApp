# import contextlib
#
# from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
# from src.conf.config import config
#
#
# class DatabaseSessionManager:
#     """
#     Class for managing database sessions.
#     """
#
#     def __init__(self, url: str):
#         """
#          Initializes the DatabaseSessionManager object.
#
#          :param url: The database URL.
#          """
#         self._engine: AsyncEngine | None = create_async_engine(url)
#         self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
#                                                                      bind=self._engine)
#
#     @contextlib.asynccontextmanager
#     async def session(self):
#         """
#         Context manager for acquiring a database session.
#
#         :return: A database session.
#         """
#         if self._session_maker is None:
#             raise Exception("Session is not initialized")
#         session = self._session_maker()
#         try:
#             yield session
#         except Exception as err:
#             print(err)
#             await session.rollback()
#         finally:
#             await session.close()
#
#
# sessionmanager = DatabaseSessionManager(
#     config.DB_URL)
#
#
# async def get_db():
#     """
#     Asynchronous function for acquiring a database session.
#
#     :return: A database session.
#     """
#     async with sessionmanager.session() as session:
#         yield session

import contextlib
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from src.conf.config import config


class DatabaseSessionManager:
    """
    Class for managing database sessions.
    """

    def __init__(self, url: str):
        """
         Initializes the DatabaseSessionManager object.

         :param url: The database URL.
         """
        self._engine: AsyncEngine = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Context manager for acquiring a database session.

        :return: A database session.
        """
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    """
    Asynchronous function for acquiring a database session.

    :return: A database session.
    """
    async with sessionmanager.session() as session:
        yield session
