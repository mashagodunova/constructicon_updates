import enum
from typing import Optional, Any
from sqlmodel import Field, Relationship
from app.db import BaseModel, BaseCRUD, SAColumn, SARelationship
import sqlalchemy as sa

from .construction_types import *

from typing import TYPE_CHECKING  # pylint: disable=wrong-import-position
if TYPE_CHECKING:
    from .construction import Construction   # pylint: disable=wrong-import-position

__all__ = (
    'ConstructionExample', 'ConstructionDefinition', 'Equivalent',
    'BaseConstructionExample', 'BaseConstructionDefinition', 'BaseEquivalent',
)


class BaseConstructionExample(BaseModel):
    number: int = Field(primary_key=True)
    value: str


class ConstructionExample(BaseConstructionExample, table=True):
    # construction_id: int = Field(sa_column=sa.ForeignKey("construction.id", ondelete='CASCADE'), primary_key=True)
    construction_id: int = SAColumn(sa.ForeignKey("construction.id", ondelete='CASCADE'), primary_key=True)
    construction: 'Construction' = Relationship(back_populates="examples")

    @property
    def id(self) -> tuple[int, int]:
        return (self.construction_id, self.number)

    # class CRUD(BaseCRUD['ConstructionExample']): pass
    crud: BaseCRUD['ConstructionExample']  # = CRUD.default()

# ConstructionExample.crud = ConstructionExample.CRUD(ConstructionExample)

class BaseConstructionDefinition(BaseModel):
    language: Language = Field(primary_key=True)
    value: str


class ConstructionDefinition(BaseConstructionDefinition, table=True):
    construction_id: int = SAColumn(sa.ForeignKey("construction.id", ondelete='CASCADE'), primary_key=True)
    construction: 'Construction' = Relationship(back_populates="definitions")

    @property
    def id(self) -> tuple[int, Language]:
        return (self.construction_id, self.language)

    # class CRUD(BaseCRUD['ConstructionDefinition']): pass
    crud: BaseCRUD['ConstructionDefinition'] # = CRUD.default()

# ConstructionDefinition.crud = ConstructionDefinition.CRUD(ConstructionDefinition)

class BaseEquivalent(BaseModel):
    language: Language = Field(primary_key=True)
    value: str


class Equivalent(BaseEquivalent, table=True):
    construction_id: int = SAColumn(sa.ForeignKey("construction.id", ondelete='CASCADE'), primary_key=True)
    construction: 'Construction' = Relationship(back_populates="equivalents")

    @property
    def id(self) -> tuple[int, Language]:
        return (self.construction_id, self.language)

    # class CRUD(BaseCRUD['Equivalent']): pass
    crud: BaseCRUD['Equivalent']  # = CRUD.default()

# Equivalent.crud = Equivalent.CRUD(Equivalent)
