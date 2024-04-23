from typing import Any

# from sqlalchemy.orm import sessionmaker, Session as OrmSession
# from sqlalchemy.pool import StaticPool
# from sqlmodel import Session, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine as Engine
from sqlmodel.ext.asyncio.session import AsyncSession as Session


__all__ = ('Session', 'Engine', 'configure', 'create_async_engine',)


def configure(uri: str) -> dict[str, Any]:  # pylint: disable=redefined-outer-name
    engine = create_async_engine(
        uri,
        # future=True,
        # pool_pre_ping=True,
        # poolclass=StaticPool,
        # connect_args={'check_same_thread': False},
    )
    from .deps import get_db  # pylint: disable=import-outside-toplevel,cyclic-import
    get_db.init(engine)

    return {'Session': Session, 'engine': engine}
