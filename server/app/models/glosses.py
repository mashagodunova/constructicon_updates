from typing import TYPE_CHECKING
import sqlalchemy as sa
from app.db import BaseModel, BaseCRUD, SAColumn, SARelationship, Relationship
from sqlmodel import Field

from .construction_types import Language
from .construction_tags import BaseTag

if TYPE_CHECKING:
    from .construction import Construction


class BaseGloss(BaseModel):
    language: Language = Field(primary_key=True)
    number: int = Field(primary_key=True)
    value: str


class Gloss(BaseGloss, table=True):
    construction_id: int = SAColumn(sa.ForeignKey("construction.id", ondelete='CASCADE'), primary_key=True)
    construction: 'Construction' = Relationship(back_populates="glosses")

    @property
    def id(self) -> tuple[int, Language, int]:
        return (self.construction_id, self.language, self.number)

    crud: BaseCRUD['Gloss'] = BaseCRUD.default()


class GlossRead(BaseModel):
    value: str


class GlossIndex(BaseModel, table=True):
    id: int = Field(primary_key=True)
    root: str = Field(index=True)
    attr: str | None = Field(index=True)
    construction_id: int = SAColumn(sa.ForeignKey("construction.id", ondelete='CASCADE'), index=True)

    construction: 'Construction' = Relationship()

    crud: BaseCRUD['Gloss'] = BaseCRUD.default()
