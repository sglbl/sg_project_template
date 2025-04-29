from sqlmodel import SQLModel, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import inspect
from src.infra.postgres.database import get_db
from loguru import logger
from src.domain.models.sql_models import DataGraph, Data


async def insert_sqlmodel_list(model_list: list[SQLModel]):
    async for session in get_db():
        for entity in model_list.values():
            session.add(entity)
        await session.commit()


async def get_data_by_id(data_id: str) -> Data:
    async for session in get_db():
        query = select(Data).where(Data.id_ == data_id)
        result = await session.execute(query)
        bf = result.scalars().first()
        if bf is None:
            raise ValueError(f"Data with id {data_id} not found")
        return bf
