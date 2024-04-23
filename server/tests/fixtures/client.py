import pytest
from typing import AsyncIterator, Any
import functools

from fastapi.testclient import TestClient as Client
# from httpx import AsyncClient as Client
import pytest
from sqlalchemy.orm import sessionmaker


from app import deps, models
from app.db import configure, Session, Base, create_async_engine, Engine, metadata
from app.core import settings
from app.main import app
from sqlmodel import SQLModel

import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session as OrmSession
from sqlalchemy.pool import StaticPool


__all__ = ('engine_fixture', 'Client', 'db_fixture', 'client_fixture')

@pytest.fixture(name="engine")
async def engine_fixture() -> AsyncIterator[Engine]:
    engine = create_async_engine(
        "sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    meta = metadata
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)

    '''
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    async with AsyncSession(engine) as session:
        statement = select(Hero).where(Hero.name == "Spider-Boy")
        h = (await session.exec(statement)).first()
        print(h)  # name='Spider-Boy' id=2 age=None secret_name='Pedro Parqueador'
    '''

@pytest.fixture(name="db")
async def db_fixture(engine: Engine) -> AsyncIterator[Session]:
    get_db = deps.DbDependency()
    get_db.init(engine)
    async for db in get_db():
        yield db


@pytest.fixture(name="client")
async def client_fixture(db: Session) -> AsyncIterator[Client]:
    try:
        app.dependency_overrides[deps.get_db] = lambda: db
        with Client(app) as client:
        # async with Client(app=app, base_url='http://testhost.example') as client:
            yield client
    finally:
        app.dependency_overrides.clear()

