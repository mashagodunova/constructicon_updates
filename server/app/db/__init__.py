from typing import Any
from sqlmodel import Field, Relationship
import sqlalchemy as sa

from .crud import BaseCRUD
from .base_model import Base, BaseModel, SABaseModel, metadata
from .session import *


__all__ = (
    'SABaseModel', 'Session', 'BaseModel', 'BaseCRUD',
    'configure', 'create_async_engine', 'Base', 'metadata',
)


def SAColumn(*args: Any, **kwargs: Any) -> Any:  # pylint: disable=invalid-name
    return Field(sa_column=sa.Column(*args, **kwargs))

def SARelationship(**kwargs: Any) -> Any:  # pylint: disable=invalid-name
    return Relationship(sa_relationship_kwargs=kwargs)
