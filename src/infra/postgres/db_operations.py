from sqlmodel import SQLModel, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import inspect, engine
from src.infra.postgres.database_async import get_db
from loguru import logger
from src.domain.models.sql_models import DataGraph, Data


async def insert_sqlmodel_list(model_list: list[SQLModel]):
    async with get_db() as session:
        if not model_list:
            logger.warning("No value on the list to insert.")
            return
        for entity in model_list:
            session.add(entity)
        await session.commit()


async def get_data_by_name(name: str) -> Data:
    async with get_db() as session:
        query = select(Data).where(Data.name == name)
        result = await session.exec(query)
        # if it's scalar, it will return a single object, otherwise it will return a list,
        if isinstance(result, engine.result.ScalarResult):
            bf = result.first()
        else:
            bf = result.scalars().first()
        if bf is None:
            raise ValueError(f"Data not found for {name}")
        return bf


async def get_data_by_id(data_id: str) -> Data:
    async with get_db() as session:
        query = select(Data).where(Data.id_ == data_id)
        result = await session.exec(query)
        bf = result.scalars().first()
        if bf is None:
            raise ValueError(f"Data with id {data_id} not found")
        return bf