import collections
import enum
from pydantic import validator
import pydantic
from typing import Optional, Any, TypeVar, Iterable, Callable, Type
from sqlmodel import Field, Relationship
from app.db import BaseModel, BaseCRUD, SAColumn, SARelationship
import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from .construction_types import *
from .construction_related import (
    ConstructionExample, ConstructionDefinition, Equivalent,
    BaseConstructionExample, BaseConstructionDefinition, BaseEquivalent,
)
from .construction_tags import (
    SyntacticType, SemanticType, SemanticRole, SyntacticFunction,
    SyntacticStructure, MorphologicalTag, AnchorPos,
    SyntacticType2Construction, SemanticType2Construction, SemanticRole2Construction, SyntacticFunction2Construction,
    SyntacticStructure2Construction, MorphologicalTag2Construction, AnchorPos2Construction,
    SemanticTypeRead, Tag, TagCreate, OrderedTagCreate,
)

from .glosses import Gloss, GlossRead, BaseGloss, GlossIndex


T = TypeVar('T')
K = TypeVar('K')

def groupby(it: Iterable[T], key: Callable[[T], K]) -> dict[K, list[T]]:
    res = collections.defaultdict(list)
    for row in it:
        res[key(row)].append(row)
    return dict(res)


class BaseConstruction(BaseModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    references: str = Field()
    family: str = Field()
    name_ud: str = Field(index=True)
    illustration:str = Field(index=True)
    cefr_level: CefrLevel = Field(index=True)
    communicative_type: CommunicativeType | None = Field(index=True)
    usage_label: UsageLabel | None = Field(index=True)
    anchor_words: str = Field()
    common_fillers: str = Field()
    comment: str = Field()
    dependency_structure: str = Field()
    illustration_dependency_structure: str = Field()


class Construction(BaseConstruction, table=True):
    # related
    examples: list['ConstructionExample'] = SARelationship(
        lazy='selectin', cascade='all, delete', passive_deletes=True)
    definitions: list['ConstructionDefinition'] = SARelationship(
        lazy='selectin', cascade='all, delete')
    equivalents: list['Equivalent'] = SARelationship(
        lazy='selectin', cascade='all, delete')

    glosses: list['Gloss'] = SARelationship(
        lazy='selectin', cascade='all, delete')


    _rel_args = {'lazy': 'selectin'}

    # unordered
    syntactic_types: list['SyntacticType'] = SARelationship(
        secondary='syntactictype2construction', **_rel_args)
    semantic_types: list['SemanticType'] = SARelationship(
        secondary='semantictype2construction', **_rel_args)
    syntactic_functions: list['SyntacticFunction'] = SARelationship(
        secondary='syntacticfunction2construction', **_rel_args)
    syntactic_structures: list['SyntacticStructure'] = SARelationship(
        secondary='syntacticstructure2construction', **_rel_args)

    # ordered
    morphological_tags: list['MorphologicalTag'] = SARelationship(
        secondary='morphologicaltag2construction', viewonly=True,
        order_by="MorphologicalTag2Construction.number", **_rel_args)
    morphological_tag_associations: list['MorphologicalTag2Construction'] = SARelationship(
        back_populates='right',
        order_by="MorphologicalTag2Construction.number", **_rel_args)

    semantic_roles: list['SemanticRole'] = SARelationship(
        secondary='semanticrole2construction', viewonly=True,
        order_by="SemanticRole2Construction.number", **_rel_args)
    semantic_role_associations: list['SemanticRole2Construction'] = SARelationship(
        back_populates='right',
        order_by="SemanticRole2Construction.number", **_rel_args)

    anchor_poss: list['AnchorPos'] = SARelationship(
        secondary='anchorpos2construction', viewonly=True,
        order_by="AnchorPos2Construction.number", **_rel_args)
    anchor_pos_associations: list['AnchorPos2Construction'] = SARelationship(
        back_populates='right',
        order_by="AnchorPos2Construction.number", **_rel_args)

    gloss_index: list['GlossIndex'] = SARelationship(
        back_populates='construction', **_rel_args)


    '''
    semantic_roles: list['SemanticRole'] = SARelationship(
        secondary='semanticrole2construction',
        order_by="SemanticRole2Construction.number", **_rel_args)
    anchor_poss: list['AnchorPos'] = SARelationship(
        secondary='anchorpos2construction',
        order_by="AnchorPos2Construction.number", **_rel_args)
    '''

    '''
    _rel_args = {'lazy': 'selectin', 'cascade': 'all, delete'}

    # unordered
    syntactic_types = sa.orm.relationship(
        'SyntacticType', secondary='syntactictype2construction', **_rel_args)
    semantic_types = sa.orm.relationship(
        'SemanticType', secondary='semantictype2construction', **_rel_args)
    syntactic_functions = sa.orm.relationship(
        'SyntacticFunction', secondary='syntacticfunction2construction', **_rel_args)
    syntactic_structures = sa.orm.relationship(
        'SyntacticStructure', secondary='syntacticstructure2construction', **_rel_args)

    # ordered
    morphological_tags = sa.orm.relationship(
        'MorphologicalTag', secondary='morphologicaltag2construction',
        order_by="MorphologicalTag2Construction.number", **_rel_args)
    semantic_roles = sa.orm.relationship(
        'SemanticRole', secondary='semanticrole2construction',
        order_by="SemanticRole2Construction.number", **_rel_args)
    anchor_poss = sa.orm.relationship(
        'AnchorPos', secondary='anchorpos2construction',
        order_by="AnchorPos2Construction.number", **_rel_args)

    '''

    crud: BaseCRUD['Construction']

# Construction.crud = Construction.CRUD(Construction)

GlossesDict = dict[Language, list[GlossRead]]

class ConstructionRead(BaseConstruction):
    examples: list['BaseConstructionExample']
    definitions: list['BaseConstructionDefinition']
    equivalents: list['BaseEquivalent']

    glosses: list['BaseGloss'] = pydantic.Field(hidden=True)

    glosses_dict: GlossesDict | None = pydantic.Field(default_factory=dict)

    @validator("glosses_dict", always=True)
    def glosses_dict_val(
            cls: Type['ConstructionRead'], v: None,
            values: dict[str, Any], **kwargs: dict[str, Any]
            ) -> GlossesDict:

        glosses: list[Gloss] = values['glosses']

        res = {
            k: [GlossRead(**x.dict()) for x in sorted(v, key=lambda x: x.number)]
            for k, v in groupby(glosses, lambda x: x.language).items()
        }
        return res

    # unordered
    syntactic_types: list['Tag']
    semantic_types: list['SemanticTypeRead']
    syntactic_functions: list['Tag']
    syntactic_structures: list['Tag']

    # ordered
    morphological_tags: list['Tag']
    semantic_roles: list['Tag']
    anchor_poss: list['Tag']
