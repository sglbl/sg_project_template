# app/infra/repository/postgres/database.py
from sqlmodel import create_engine, Session, SQLModel, text
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import settings
from src.domain.models.sql_models import Data # TODO: EVERY_SQL_MODEL_TO_CREATE_DECLARATIVELY

# # Create the engine
engine = create_async_engine(url=settings.DB_URL, echo=settings.SQLALCHEMY_DEBUG_LOG) # Set echo=True for debugging

# # sessionmaker version
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        # change schema
        await session.execute(text(f"SET search_path TO {settings.DB_SCHEMA}"))
        yield session


async def init_db():    
    async with engine.begin() as conn:
        if settings.DB_SCHEMA == "":
            raise Exception("DB_SCHEMA is not set")

        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA};"))    
        

async def create_tables():    
    # engine.url = settings.DB_SCHEMA_URL
    # engine.execution_options(schema_translate_map={"schema": settings.DB_SCHEMA})
    
    async with engine.begin() as conn:
        await conn.execute(text(f"SET search_path TO {settings.DB_SCHEMA}"))
        await conn.run_sync(SQLModel.metadata.create_all)
        