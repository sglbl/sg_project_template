from src.database.db_engine import create_schema_and_tables, insert_validated_data

if __name__ == "__main__":
    # Create schema and tables
    create_schema_and_tables()

    # # Example usage
    # insert_validated_data(
    #     prompt="What is the capital of France?",
    #     json_data={"answer": "Paris"},
    #     feedback=True,
    # )
