import os
import asyncio
from loguru import logger
from contextlib import asynccontextmanager
from asyncpg.exceptions import ConnectionDoesNotExistError
from sqlmodel import SQLModel, text
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import settings
from src.domain.models.sql_models import Data 

# NOTE: Call all the tables (in domain.models) to register them

# # Create the engine
engine = create_async_engine(
    url=settings.DB_URL, echo=settings.SQLALCHEMY_LOG_LEVEL,
    pool_size=10,
    pool_pre_ping=True,
    max_overflow=0, future=True) # Set echo=True for debugging


# # sessionmaker version
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False,
    autocommit=False, autoflush=False)


@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as session:
        # change schema
        await session.exec(text(f"SET search_path TO {settings.DB_SCHEMA}"))
        yield session


@logger.catch(reraise=True)
async def init_db_with_retry(retries=10, delay=2):
    for attempt in range(retries):
        try:
            await init_db()
            return
        except (ConnectionError, ConnectionDoesNotExistError) as e:
            logger.warning(f"DB connection failed on attempt {attempt+1}/{retries}: {e}")
            await asyncio.sleep(delay)
    raise RuntimeError(f"Could not connect to the database after {retries} retries")


@logger.catch(reraise=True)
async def init_db():
    async with engine.begin() as conn:
        if settings.DB_SCHEMA == "":
            raise Exception("DB_SCHEMA is not set")

        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA};"))


@logger.catch(reraise=True)
async def create_tables(drop_first: bool = False): 
    async with engine.begin() as conn:
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA};"))
        await conn.execute(text(f"SET search_path TO {settings.DB_SCHEMA}"))
        if drop_first:
            logger.warning(f"Dropping all tables in schema '{settings.DB_SCHEMA}' before creation...")
            # Drop all tables managed by SQLModel's metadata
            await conn.run_sync(SQLModel.metadata.drop_all)
            logger.info("Tables dropped.")
        await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Tables created (or re-created).")
