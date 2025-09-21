import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import config


class DatabaseSessionManager:
    """
    Manages asynchronous SQLAlchemy database sessions.

    Args:
        url (str): Database connection URL.

    Attributes:
        _engine (AsyncEngine): SQLAlchemy async engine.
        _session_maker (async_sessionmaker): Factory for async sessions.
    """

    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Async context manager for database session.

        Yields:
            AsyncSession: SQLAlchemy async session.

        Raises:
            Exception: If session maker is not initialized.
            SQLAlchemyError: If a database error occurs.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DATABASE_URL)


async def get_db():
    """
    FastAPI dependency that provides a database session.

    Yields:
        AsyncSession: SQLAlchemy async session.
    """
    async with sessionmanager.session() as session:
        yield session
