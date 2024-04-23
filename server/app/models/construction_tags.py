import enum
from typing import Optional, Any, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.db import BaseModel, BaseCRUD, SAColumn, SARelationship
import sqlalchemy as sa


if TYPE_CHECKING:
    from .construction import Construction

__all__ = (
    'SyntacticType', 'SemanticType', 'SemanticRole', 'SyntacticFunction',
    'SyntacticStructure', 'MorphologicalTag', 'AnchorPos',
    'SyntacticType2Construction', 'SemanticType2Construction', 'SemanticRole2Construction', 'SyntacticFunction2Construction',
    'SyntacticStructure2Construction', 'MorphologicalTag2Construction', 'AnchorPos2Construction',
    'SemanticTypeRead', 'Tag', 'TagCreate', 'OrderedTagCreate',
)


# related
class BaseTag(BaseModel):
    id: int = Field(primary_key=True)
    name: str = Field(max_length=160, unique=True)


class Tag(BaseTag):
    pass


class TagCreate(BaseModel):
    name: str


class OrderedTagCreate(TagCreate):
    number: int


class BaseAssociation(BaseModel):
    pass


class BaseOrderedAssociation(BaseModel):
    number: int = Field(primary_key=True)


# unordered
class SyntacticType2Construction(BaseAssociation, table=True):
    left_id: int = SAColumn(sa.ForeignKey('syntactictype.id', ondelete='CASCADE'), primary_key=True)
    right_id: int = SAColumn(sa.ForeignKey('construction.id', ondelete='CASCADE'), primary_key=True)


class SyntacticType(BaseTag, table=True):
    crud: BaseCRUD['SyntacticType']


class SemanticType2Construction(BaseAssociation, table=True):
    left_id: int = SAColumn(sa.ForeignKey('semantictype.id', ondelete='CASCADE'), primary_key=True)
    right_id: int = SAColumn(sa.ForeignKey('construction.id', ondelete='CASCADE'), primary_key=True)


class SemanticType(BaseTag, table=True):
    parent_id: Optional[int] = Field(foreign_key="semantictype.id", nullable=True)

    children: list["SemanticType"] = Relationship(back_populates="parent", sa_relationship_kwargs={'cascade': 'all, delete'})
    parent: Optional["SemanticType"] = Relationship(back_populates="children", sa_relationship_kwargs={'cascade': 'all, delete', 'remote_side': 'SemanticType.id'})

    crud: BaseCRUD['SemanticType']


class SemanticTypeRead(BaseModel):
    id: int
    name: str
    parent_id: int | None


class SyntacticFunction2Construction(BaseAssociation, table=True):
    left_id: int = SAColumn(sa.ForeignKey('syntacticfunction.id', ondelete='CASCADE'), primary_key=True)
    right_id: int = SAColumn(sa.ForeignKey('construction.id', ondelete='CASCADE'), primary_key=True)



class SyntacticFunction(BaseTag, table=True):
    crud: BaseCRUD['SyntacticFunction']


class SyntacticStructure2Construction(BaseAssociation, table=True):
    left_id: int = SAColumn(sa.ForeignKey('syntacticstructure.id', ondelete='CASCADE'), primary_key=True)
    right_id: int = SAColumn(sa.ForeignKey('construction.id', ondelete='CASCADE'), primary_key=True)



class SyntacticStructure(BaseTag, table=True):
    crud: BaseCRUD['SyntacticStructure']


# ordered

class MorphologicalTag2Construction(BaseOrderedAssociation, table=True):
    left_id: int = SAColumn(sa.ForeignKey('morphologicaltag.id', ondelete='CASCADE'), primary_key=True)
    left: 'MorphologicalTag' = SARelationship()
    right_id: int = SAColumn(sa.ForeignKey('construction.id', ondelete='CASCADE'), primary_key=True)
    right: 'Construction' = SARelationship(back_populates='morphological_tag_associations')


class MorphologicalTag(BaseTag, table=True):
    crud: BaseCRUD['MorphologicalTag']


class SemanticRole2Construction(BaseOrderedAssociation, table=True):
    left_id: int = SAColumn(sa.ForeignKey('semanticrole.id', ondelete='CASCADE'), primary_key=True)
    left: 'SemanticRole' = SARelationship()
    right_id: int = SAColumn(sa.ForeignKey('construction.id', ondelete='CASCADE'), primary_key=True)
    right: 'Construction' = SARelationship(back_populates='semantic_role_associations')


class SemanticRole(BaseTag, table=True):
    crud: BaseCRUD['SemanticRole']


class AnchorPos2Construction(BaseOrderedAssociation, table=True):
    left_id: int = SAColumn(sa.ForeignKey('anchorpos.id', ondelete='CASCADE'), primary_key=True)
    left: 'AnchorPos' = SARelationship()
    right_id: int = SAColumn(sa.ForeignKey('construction.id', ondelete='CASCADE'), primary_key=True)
    right: 'Construction' = SARelationship(back_populates="anchor_pos_associations")


class AnchorPos(BaseTag, table=True):
    crud: BaseCRUD['AnchorPos']
