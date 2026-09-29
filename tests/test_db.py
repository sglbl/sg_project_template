# tests/test_db.py
import pytest
import asyncio
from sqlmodel import delete
from src.infra.postgres.database_async import get_db_async, init_db, create_tables
from src.infra.postgres.db_operations import insert_sqlmodel_list, get_data_by_name
from src.domain.models.sql_models import Data, DataGraph





@pytest.fixture()
async def db_session():
    """Provide a session with initialized tables and isolated test data."""
    try:
        await init_db()
        await create_tables()
    except Exception as e:
        pytest.skip(f"PostgreSQL connection unavailable: {e}")

    async with get_db_async() as session:
        # Pre-cleanup in case previous run was interrupted
        await session.exec(delete(DataGraph).where(DataGraph.data_fk == "test_dataset"))
        await session.exec(delete(Data).where(Data.name == "test_dataset"))
        await session.commit()
        try:
            yield session
        finally:
            # Post-cleanup
            await session.exec(delete(DataGraph).where(DataGraph.data_fk == "test_dataset"))
            await session.exec(delete(Data).where(Data.name == "test_dataset"))
            await session.commit()


@pytest.mark.integration
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
