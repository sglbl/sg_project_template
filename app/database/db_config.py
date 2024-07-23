import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection details
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "supabase-db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

# Construct the database URL
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Define your postgres schema name (project granularity)
SCHEMA = os.getenv("DB_SCHEMA", "idbox_project")


# You can add a function to validate the configuration if needed
def validate_config():
    required_vars = [
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_SCHEMA",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


# Optionally, call the validation function
# validate_config()


# If you need to print the configuration (be careful with sensitive info)
def print_config():
    print(f"Database URL: {DB_URL.replace(DB_PASSWORD, '*****')}")
    print(f"Schema: {SCHEMA}")
