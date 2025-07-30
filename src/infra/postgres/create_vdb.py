import psycopg2
from psycopg2 import sql
from loguru import logger
from src.application import utils
from src.config import settings


def connect_to_db():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME
        )
        logger.info("Database connection established.")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        raise


def setup_schema(cursor, schema_name: str):
    """Create schema if it doesn't exist and set the search_path."""
    try:
        cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema_name)))
        cursor.execute(sql.SQL("SET search_path TO {}, public").format(sql.Identifier(schema_name)))
        logger.info(f"Schema '{schema_name}' ensured and search_path set.")
    except Exception as e:
        logger.error(f"Failed to setup schema '{schema_name}': {e}")
        raise


def setup_pgvector_extension(cursor):
    """Ensure the pgvector extension is installed."""
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        logger.info("pgvector extension ensured.")
    except Exception as e:
        logger.error(f"Failed to create pgvector extension: {e}")
        raise


def create_embeddings_table(cursor, table_name: str = "embeddings", dim: int = 3):
    """Create the embeddings table with specified vector dimension."""
    try:
        create_table_sql = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                id BIGSERIAL PRIMARY KEY,
                label TEXT,
                url TEXT,
                content TEXT,
                tokens INTEGER,
                embedding VECTOR(%s)
            );
        """).format(sql.Identifier(table_name))
        
        cursor.execute(create_table_sql, (dim,))
        logger.info(f"Table '{table_name}' ensured with vector dimension {dim}.")
    except Exception as e:
        logger.error(f"Failed to create table '{table_name}': {e}")
        raise


def run():
    """Main function to set up the database schema and table."""
    utils.set_logger(level=settings.LOG_LEVEL)

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("SELECT NOW();")
        logger.debug(f"Connected at: {cursor.fetchone()}")

        setup_schema(cursor, settings.DB_SCHEMA)
        setup_pgvector_extension(cursor)
        create_embeddings_table(cursor)

        conn.commit()
        logger.info("Database setup completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred during setup: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            logger.info("Database connection closed.")


if __name__ == "__main__":
    run()
