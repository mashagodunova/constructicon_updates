from typing import AsyncIterable

from .session import Session, Engine


class DbDependency:
    def __init__(self) -> None:
        self.engine: Engine | None = None

    async def __call__(self) -> AsyncIterable[Session]:
        async with Session(self.engine) as db:
            try:
                yield db
                await db.commit()
            except:
                await db.rollback()
                raise
            finally:
                await db.close()

    def init(self, engine: Engine) -> None:
        self.engine = engine

get_db = DbDependency()
