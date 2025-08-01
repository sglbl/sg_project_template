import numpy as np
import psycopg2
from psycopg2 import sql
from loguru import logger
from src.application import utils
from src.config import settings

""" Run the code with:
python -m src.infra.postgres.create_vdb
"""

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


def create_embeddings_table(cursor, table_name: str = "embeddings_trial", dim: int = 3):
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


def insert_data(cursor, table_name: str = "embeddings_trial"):
    """ Insert sample data into the embeddings table for testing purposes."""

    try:
        # Define the SQL command for inserting data
        insert_command = sql.SQL("""
        INSERT INTO embeddings (label, url, content, tokens, embedding)
        VALUES (%s, %s, %s, %s, %s);
        """).format(sql.Identifier(table_name))

        # Create sample data
        data = [
            ("label1", "http://example.com/1", "The article on dogs", 100, np.random.rand(3).tolist()),
            ("label2", "http://example.com/2", "The article on cats", 150, np.random.rand(3).tolist()),
            ("label3", "http://example.com/3", "The article on cars", 200, np.random.rand(3).tolist()),
            ("label4", "http://example.com/4", "The article on books", 250, np.random.rand(3).tolist()),
            ("label5", "http://example.com/5", "The article on embeddings_trial", 300, np.random.rand(3).tolist())
        ]

        # Insert data into the table
        for record in data:
            cursor.execute(insert_command, record)
        logger.info(f"Sample data inserted into '{table_name}' table.")
    except Exception as e:
        logger.error(f"Failed to insert data into '{table_name}': {e}")
        raise


def query_similar_embeddings(cursor, query_vector, table_name: str = "embeddings_trial", top_k: int = 5):
    """Query the top K similar embeddings from the table."""
    try:
        query = sql.SQL("""
            SELECT id, label, url, content, tokens, embedding
            FROM {}
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """).format(sql.Identifier(table_name))

        cursor.execute(query, (query_vector, top_k))
        results = cursor.fetchall()
        logger.info(f"Retrieved {len(results)} similar embeddings.")
        joined_results = '\n'.join(str(result) for result in results)
        logger.debug(f"Similar embeddings:\n{joined_results}")
        return results
    except Exception as e:
        logger.error(f"Failed to query similar embeddings: {e}")
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
        insert_data(cursor)
        query_similar_embeddings(cursor, np.random.rand(3).tolist())

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
