import psycopg2
from psycopg2 import sql
from loguru import logger
from src.application import utils
from src.config import settings
from returns.result import Result, Success, Failure, safe
from psycopg2.extensions import connection
from typing import Tuple


@safe
def connect_to_db() -> connection:
    return psycopg2.connect(
        user=settings.DB_USER,
        password="2",
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME
    )

@safe
def setup_schema(conn: connection) -> connection:
    cursor = conn.cursor()
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA};")
    cursor.execute(f"SET search_path TO {settings.DB_SCHEMA}, public")
    cursor.close()
    return conn

@safe
def create_embeddings_table(conn: connection) -> connection:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id BIGSERIAL PRIMARY KEY,
            label TEXT,
            url TEXT,
            content TEXT,
            tokens INTEGER,
            embedding VECTOR(3)
        );
    """)
    conn.commit()
    cursor.close()
    return conn


def run():
    """Main function to orchestrate the database setup with safe error handling."""
    utils.set_logger(level=settings.LOG_LEVEL)
    
    result: Result[connection, Exception] = (
        connect_to_db()
        .bind(setup_schema)
        .bind(create_embeddings_table)
    )

    match result:
        case Success(_):
            logger.info("Setup complete.")
        case Failure(error):
            logger.error(f"Setup failed: {error}")
            
            
if __name__ == "__main__":
    run()
