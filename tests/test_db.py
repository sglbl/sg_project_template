# tests/test_db.py
import pytest
import asyncio
from sqlmodel import select
from httpx import AsyncClient
from src.infra.postgres.database import (
    engine,
    get_db,
    create_tables,
    init_db
)
from src.infra.postgres.db_operations import insert_sqlmodel_list, get_data_by_name
from src.domain.models.sql_models import Data, DataGraph
from src.config import settings

# @pytest.mark.asyncio
# async def test_force_schema_create():
#     await init_db()
#     await create_tables(drop_first=True)
    
@pytest.fixture(scope="session")
def event_loop():
    """Ensure event loop works for pytest-asyncio."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def db_session():
    """Provide a session with the test DB schema set."""
    async with get_db() as session:
        yield session


# @pytest.fixture(scope="session", autouse=True)
# async def prepare_test_db():
#     """
#     Set up the database schema and tables before tests.
#     Assumes test database URL and schema are set via settings.
#     """
#     await init_db()
#     await create_tables(drop_first=True)
#     yield
#     # Optional teardown logic

@pytest.mark.asyncio
async def test_insert_and_retrieve_data_graph(db_session):
    # Create a Data object
    test_data = Data(name="test_dataset")

    # Create associated DataGraph(s)
    data_graph = DataGraph(
        data_fk="test_dataset",
        values={"2023-01-01T00:00:00": 1.23, "2023-01-02T00:00:00": 2.34}
    )

    # Link DataGraph to Data
    test_data.graphs = [data_graph]

    # Insert using your insert function
    await insert_sqlmodel_list([test_data, data_graph])

    # Retrieve using your retrieval function
    fetched_data = await get_data_by_name("test_dataset")

    assert fetched_data.name == "test_dataset"
    assert len(fetched_data.graphs) == 1
    assert isinstance(fetched_data.graphs[0], DataGraph)
    assert fetched_data.graphs[0].values["2023-01-01T00:00:00"] == 1.23
