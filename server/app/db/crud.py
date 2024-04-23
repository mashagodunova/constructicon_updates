from typing import TypeVar, Generic, Any, cast
from sqlalchemy import select
from sqlalchemy.sql import Executable
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from .session import Session

T = TypeVar('T', bound='AbstractBase')
_DEFAULT = object()


class BaseCRUD(Generic[T]):
    def __init__(self, model: type[T]):
        self.model = model

    @staticmethod
    def default() -> Any:
        def not_implemented(self: Any) -> Any:
            raise ValueError('set Model.crud = CRUD(model)')
        return property(not_implemented)

    async def create(self, db: Session, *, save_: bool = True, **attrs: Any) -> T:
        obj = self.model(**attrs)
        db.add(obj)
        if save_:
            await obj.save(db)
        return obj

    def get_query(self, **kv_conditions: Any) -> Executable:
        query = select(self.model)
        if kv_conditions:
            query = query.filter_by(**kv_conditions)
        return query

    async def all(self, db: Session, **kv_conditions: Any) -> T:
        return cast(  # TODO: remove cast
            T,
            (await db.execute(self.get_query(**kv_conditions))).scalars(),
        )

    async def get(self, db: Session, **kv_conditions: Any) -> T:
        return cast(  # TODO: remove cast
            T,
            (await db.execute(self.get_query(**kv_conditions))).scalar_one(),
        )

    async def get_or_create(
            self, db: Session, save_: bool=True,
            defaults_: dict[str, Any] | None = None, **kv_conditions: Any,
            ) -> tuple[bool, T]:
        # if kv_conditions == {'name': 'Nom'}:
        #    1 / 0

        try:
            created, obj = False, await self.get(db, **kv_conditions)
        except NoResultFound:
            created, obj = True, await self.create(db, **(defaults_ or {}), save_=save_)
        return created, obj

    async def get_or_404(self, db: Session, detail_: str | None = None, **kv_conditions: Any) -> T:
        try:
            return await self.get(db, **kv_conditions)
        except NoResultFound as e:
            raise HTTPException(status_code=404, detail=detail_) from e

    async def get_or_none(self, db: Session, **kv_conditions: Any) -> T | None:
        try:
            return await self.get(db, **kv_conditions)
        except NoResultFound:
            return None

    async def update(
            self, db: Session, obj: T, obj_in: Any=None, save_: bool=True, **kwargs: Any
            ) -> T:
        # if isinstance(obj, dict):
        #     kwargs.update(obj_in)
        # else:
        # kwargs.update(obj_in.dict(exclude_unset=True))

        obj_data = jsonable_encoder(obj)
        for field in obj_data:
            value = kwargs.get(field, _DEFAULT)
            if value is not _DEFAULT:
                setattr(obj, field, value)

        db.add(obj)
        if save_:
            await obj.save(db)
        return obj

from .base_model import AbstractBase, SABaseModel, BaseModel  # pylint: disable=unused-import,wrong-import-position,cyclic-import
