import asyncio
import numpy as np
from sqlmodel import text
from loguru import logger
from src.config import settings
from src.application import utils
from src.infra.postgres.database_sync import get_db_sync
from src.infra.postgres.database_async import get_db

""" Run the code with:
python -m src.infra.postgres.create_vdb
"""

async def setup_schema(session):
    await session.exec(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA};"))
    await session.exec(text(f"SET search_path TO {settings.DB_SCHEMA}, public;"))
    logger.info(f"Schema '{settings.DB_SCHEMA}' ensured and search_path set.")


async def setup_pgvector_extension(session):
    await session.exec(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    logger.info("pgvector extension ensured.")


async def create_embeddings_table(session, table_name: str = "embeddings", dim: int = 3):
    await session.exec(text(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id BIGSERIAL PRIMARY KEY,
            label TEXT,
            url TEXT,
            content TEXT,
            tokens INTEGER,
            embedding VECTOR({dim})
        );
    """))
    logger.info(f"Table '{table_name}' ensured with vector dimension {dim}.")


async def insert_data(session, table_name: str = "embeddings", dim: int = 3):
    data = [
        ("label1", "http://example.com/1", "The article on dogs", 100, np.random.rand(dim).tolist()),
        ("label2", "http://example.com/2", "The article on cats", 150, np.random.rand(dim).tolist()),
        ("label3", "http://example.com/3", "The article on cars", 200, np.random.rand(dim).tolist()),
        ("label4", "http://example.com/4", "The article on books", 250, np.random.rand(dim).tolist()),
        ("label5", "http://example.com/5", "The article on embeddings", 300, np.random.rand(dim).tolist())
    ]

    insert_stmt = text(f"""
        INSERT INTO {table_name} (label, url, content, tokens, embedding)
        VALUES (:label, :url, :content, :tokens, :embedding)
    """)

    for record in data:
        vector_str = str(record[4])  # pgvector wants JSON-like list format: "[...,...]"
        await session.exec(
            insert_stmt.params(
                label=record[0],
                url=record[1],
                content=record[2],
                tokens=record[3],
                embedding=vector_str
            )
        )

    logger.info(f"Sample data inserted into '{table_name}' table.")


async def run_async():
    utils.set_logger(level=settings.LOG_LEVEL)

    async with get_db() as session:
        await setup_schema(session)
        await setup_pgvector_extension(session)
        await create_embeddings_table(session)
        await insert_data(session)
        await session.commit()
        logger.info("Async database setup completed successfully.")


if __name__ == "__main__":
    asyncio.run(run_async())
