from time import sleep
from loguru import logger
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from src.config import settings
from src.domain.models.sql_models import Data

# NOTE: Call all the tables (in domain.models) to register them

# --- Sync SQLAlchemy engine ---
sync_engine = create_engine(
    url=f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
    echo=settings.SQLALCHEMY_LOG_LEVEL,
    future=True,
    pool_pre_ping=True
)

# --- Sync session factory ---
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

# --- Sync context manager ---
@contextmanager
def get_db_sync():
    db = SyncSessionLocal()
    try:
        if not settings.DB_SCHEMA:
            raise ValueError("DB_SCHEMA is not set")
        db.execute(text(f"SET search_path TO {settings.DB_SCHEMA}, public"))
        yield db
    finally:
        db.close()

# --- Retry wrapper for init_db ---
@logger.catch(reraise=True)
def init_db_with_retry(retries: int = 10, delay: int = 2):
    for attempt in range(1, retries + 1):
        try:
            init_db()
            return
        except Exception as e:
            logger.warning(f"DB connection failed on attempt {attempt}/{retries}: {e}")
            sleep(delay)
    raise RuntimeError(f"Could not connect to the database after {retries} retries")

# --- Initialize schema ---
@logger.catch(reraise=True)
def init_db():
    if not settings.DB_SCHEMA:
        raise ValueError("DB_SCHEMA is not set")
    with sync_engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA};"))

# --- Create or recreate tables ---
@logger.catch(reraise=True)
def create_tables(drop_first: bool = False):
    with sync_engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA};"))
        conn.execute(text(f"SET search_path TO {settings.DB_SCHEMA}, public"))

        if drop_first:
            logger.warning(f"Dropping all tables in schema '{settings.DB_SCHEMA}' before creation...")
            SQLModel.metadata.drop_all(bind=conn)
            logger.info("Tables dropped.")

        SQLModel.metadata.create_all(bind=conn)
        logger.info("Tables created (or re-created).")
