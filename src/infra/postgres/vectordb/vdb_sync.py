import numpy as np
from sqlmodel import text
from loguru import logger
from psycopg2 import sql
from src.config import settings
from src.application import utils
from src.infra.postgres.database_sync import get_db_sync

""" Run the code with:
python -m src.infra.postgres.vectordb.vdb_sync
"""


def setup_schema(session):
    session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA};"))
    session.execute(text(f"SET search_path TO {settings.DB_SCHEMA}, public;"))
    logger.info(f"Schema '{settings.DB_SCHEMA}' ensured and search_path set.")


def setup_pgvector_extension(session):
    session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    logger.info("pgvector extension ensured.")


def create_embeddings_table(session, table_name: str = "embeddings_trial", dim: int = 3):
    session.execute(text(f"""
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


def insert_data(session, table_name: str = "embeddings_trial", dim: int = 3):
    data = [
        ("label1", "http://example.com/1", "The article on dogs", 100, np.random.rand(dim).tolist()),
        ("label2", "http://example.com/2", "The article on cats", 150, np.random.rand(dim).tolist()),
        ("label3", "http://example.com/3", "The article on cars", 200, np.random.rand(dim).tolist()),
        ("label4", "http://example.com/4", "The article on books", 250, np.random.rand(dim).tolist()),
        ("label5", "http://example.com/5", "The article on embeddings_trial", 300, np.random.rand(dim).tolist())
    ]

    insert_stmt = text(f"""
        INSERT INTO {table_name} (label, url, content, tokens, embedding)
        VALUES (:label, :url, :content, :tokens, :embedding)
    """)

    for record in data:
        vector_str = str(record[4])  # e.g., "[0.1, 0.2, 0.3]"
        session.execute(insert_stmt, {
            "label": record[0],
            "url": record[1],
            "content": record[2],
            "tokens": record[3],
            "embedding": vector_str,  # correct format for pgvector
        })

    logger.info(f"Sample data inserted into '{table_name}' table.")


def query_similar_embeddings_sync(session, query_vector, table_name: str = "embeddings_trial", top_k: int = 5):
    try:
        query_text = text(f"""
            SELECT id, label, url, content, tokens, embedding
            FROM {table_name}
            ORDER BY embedding <=> CAST(:query_vector AS vector)
            LIMIT :top_k;
        """).bindparams(
            query_vector=query_vector,
            top_k=top_k
        )

        result = session.execute(query_text)
        rows = result.all()

        logger.info(f"Retrieved {len(rows)} similar embeddings (sync).")
        logger.debug("Similar embeddings:\n" + "\n".join(str(r) for r in rows))
        return rows

    except Exception as e:
        logger.error(f"Failed to query similar embeddings (sync): {e}")
        raise


def run_sync():
    utils.set_logger(level=settings.LOG_LEVEL)

    with get_db_sync() as session:
        setup_schema(session)
        setup_pgvector_extension(session)
        create_embeddings_table(session)
        insert_data(session)
        query_similar_embeddings_sync(session, np.random.rand(3).tolist())
        session.commit()
        logger.info("Sync database setup completed successfully.")


if __name__ == "__main__":
    run_sync()
