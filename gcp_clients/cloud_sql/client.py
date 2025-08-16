import logging
import sqlalchemy
from google.cloud.sql.connector import create_async_connector
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

class CloudSQLClient:
    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._session_factory = None
        self._connector = None
        self.engine = None

    async def init(
        self,
        instance_connection_name: str,
        user: str,
        password: str,
        db: str
    ) -> None:
        self._connector = await create_async_connector()

        self.engine = create_async_engine(
            "postgresql+asyncpg://",
            async_creator=lambda: self._connector.connect_async(
                instance_connection_name,
                "asyncpg",
                user=user,
                password=password,
                db=db
            ),
            echo=False,
            future=True,
            pool_size=5,
            max_overflow=2
        )

        self._session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        self.logger.info("Cloud SQL Async Engine initialized")

    async def get_session(self) -> AsyncSession:
        if not self._session_factory:
            raise RuntimeError("CloudSQLClient not initialized. Call await init() first.")
        return self._session_factory()
    
    async def test_connection(self) -> None:
        if not self.engine:
            raise RuntimeError("CloudSQLClient not initialized. Call await init() first.")
        try:
            async with self.get_session() as session:
                await session.execute(sqlalchemy.text("SELECT 1"))
            self.logger.info("Cloud SQL connection OK")
        except SQLAlchemyError as e:
            self.logger.error(f"Cloud SQL connection test failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Cloud SQL connection test failed: {e}")
            raise

    async def close(self) -> None:
        if self.engine:
            await self.engine.dispose()
        if self._connector:
            await self._connector.close_async()
        self.logger.info("Cloud SQL connector and engine disposed")