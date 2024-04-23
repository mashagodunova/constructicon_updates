from typing import Any
from sqlalchemy.ext.declarative import declared_attr, DeclarativeMeta
from sqlmodel import SQLModel, MetaData
from sqlmodel.main import SQLModelMetaclass, default_registry

from .session import Session
from .crud import BaseCRUD


naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=naming_convention)
default_registry.metadata = metadata
Base: DeclarativeMeta = default_registry.generate_base()  # type: ignore
SQLModel.metadata = Base.metadata


class BaseModelMetaclassMixin:
    def __new__(
            cls: Any,
            name: str, bases: tuple[type[Any], ...], attrs: dict[str, Any],
            **kwargs: Any
            ) -> Any:
        table = kwargs.get('table', False) or not attrs.get('__abstract__', False)
        crud_annotation = attrs.get('__annotations__', {}).get('crud')

        if table and crud_annotation:
            attrs['crud'] = BaseCRUD.default()

        obj = super().__new__(cls, name, bases, attrs, **kwargs)   # type: ignore

        if table and crud_annotation: #  and CRUD:
            obj.crud = crud_annotation(obj)
        return obj


class BaseModelMetaclass(BaseModelMetaclassMixin, SQLModelMetaclass):
    pass


class SABaseModelMetaclass(BaseModelMetaclassMixin, DeclarativeMeta):
    pass


class AbstractBase:
    __config__ = {}  # type: ignore
    id: Any

    def __str__(self) -> str:
        return f'<{type(self).__name__}: id={self.id}>'

    def __repr__(self) -> str:
        return f'<{type(self).__name__} object at 0x{id(self):x}: id={self.id}>'

    async def save(self, db: Session) -> None:
        await db.flush()
        await db.refresh(self)


class SABaseModel(Base, AbstractBase, metaclass=SABaseModelMetaclass):  # type: ignore
    __abstract__ = True

    @declared_attr
    def __tablename__(cls: DeclarativeMeta) -> str:    # pylint: disable=no-self-argument
        return cls.__name__.lower()    # pylint: disable=no-member


class BaseModel(SQLModel, AbstractBase, metaclass=BaseModelMetaclass):  # type: ignore
    def dict(self, **kwargs: Any) -> dict[str, Any]:
        hidden_fields = set(
            attribute_name
            for attribute_name, model_field in self.__fields__.items()
            if model_field.field_info.extra.get("hidden") is True
        )
        kwargs['exclude'] = (set(kwargs.get('exclude') or set()) | hidden_fields) or None
        return super().dict(**kwargs)
