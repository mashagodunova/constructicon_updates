from typing import AsyncIterator
import contextlib
from sqlmodel import Field
import sqlalchemy as sa

from app.db import BaseModel, Session


class Singleton(BaseModel, table=True):
    id: int = Field(primary_key=True) # TODO, autoincrement=False)
    maintenance: bool = Field(default=False)

    @classmethod
    async def get(cls, db: Session) -> 'Singleton':
        obj = await db.get(cls, 1)
        if obj is None:
            obj = cls(id=1)
            db.add(obj)
            await obj.save(db)
        return obj


@contextlib.asynccontextmanager
async def with_maintenance(db: Session) -> AsyncIterator[Singleton]:
    singleton = await Singleton.get(db)
    singleton.maintenance = True
    await singleton.save(db)

    try:
        yield singleton
    finally:
        singleton.maintenance = False
        await singleton.save(db)
