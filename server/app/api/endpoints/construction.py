# pylint: disable=no-member

from typing import Any
import re
import csv
import itertools

from fastapi import APIRouter, Depends, Query, BackgroundTasks, UploadFile
from sqlalchemy import func as F, select
import sqlalchemy as sa

from app.db import Session
from app.deps import get_db
from app import schemas
from app.models import (
    ConstructionRead, Construction,
    ConstructionExample, ConstructionDefinition, SyntacticType,
    Equivalent,
    MorphologicalTag, MorphologicalTag2Construction,
    # SemanticType2Construction,
    SemanticType,
    # SyntacticFunction2Construction,
    SyntacticFunction,
    SyntacticStructure,
    SemanticRole2Construction,
    SemanticRole,
    AnchorPos2Construction,
    AnchorPos,
    CefrLevel,
    SemanticTypeRead,
    GlossIndex,
)

from app.models.construction_import import import_constructions, parse_constructions, parse_glosses, Tag

router = APIRouter()

class ConstructionSearchResponse(schemas.BaseModel):
    total: int
    # items: list[schemas.ConstructionShort]
    items: list[ConstructionRead]

def parse_list(value: str | None, cls: Any) -> list[Any] | None:
    if not value:
        return None
    res = value.split(',')
    return [cls(v) for v in res]

def parse_cefr_level(cefr_level: str | None = Query(None)) -> list[CefrLevel] | None:
    return parse_list(cefr_level, CefrLevel)

def parse_syntactic_types(syntactic_types: str | None = Query(None)) -> list[int] | None:
    return parse_list(syntactic_types, int)

def parse_syntactic_functions(syntactic_function: str | None = Query(None)) -> list[int] | None:
    return parse_list(syntactic_function, int)

def parse_syntactic_structures(syntactic_structures: str | None = Query(None)) -> list[int] | None:
    return parse_list(syntactic_structures, int)

def parse_semantic_types(semantic_types: str | None = Query(None)) -> list[int] | None:
    return parse_list(semantic_types, int)

def parse_morphological_tags(morphological_tags: str | None = Query(None)) -> list[int] | None:
    return parse_list(morphological_tags, int)

def parse_semantic_roles(semantic_roles: str | None = Query(None)) -> list[int] | None:
    return parse_list(semantic_roles, int)

def parse_anchor_poss(anchor_poss: str | None = Query(None)) -> list[int] | None:
    return parse_list(anchor_poss, int)

GlossesParam = list[tuple[str | None, str | None]]

def parse_glosses_params(glosses: str | None = Query(None)) -> GlossesParam | None:
    return parse_list(glosses, lambda x: tuple((
        a or None for a in (x.split('-') + [None, None])[:2]
    )))


@router.get('/', response_model=ConstructionSearchResponse)
async def construction_list(  # pylint: disable=too-many-locals
        *, db: Session = Depends(get_db),
        offset: int = 0, limit: int = 10,
        text: str | None = None,
        name: str | None = None, name_ud: str | None = None,
        illustration_text: str | None = None,
        cefr_level: list[CefrLevel] | None = Depends(parse_cefr_level),
        syntactic_types: list[int] | None = Depends(parse_syntactic_types),
        semantic_types: list[int] | None = Depends(parse_semantic_types),
        syntactic_functions: list[int] | None = Depends(parse_syntactic_functions),
        syntactic_structures: list[int] | None = Depends(parse_syntactic_structures),
        morphological_tags: list[int] | None = Depends(parse_morphological_tags),
        semantic_roles: list[int] | None = Depends(parse_semantic_roles),
        anchor_poss: list[int] | None = Depends(parse_anchor_poss),
        random_sort: bool = False,
        glosses: GlossesParam | None = Depends(parse_glosses_params),
    ) -> Any:

    def search_text(name: str, value: str | None) -> Any:
        if value is None:
            return None
        return F.lower(getattr(Construction, name)).contains(value.lower())

    query = select(Construction)

    if text:
        query = query.filter(sa.or_(
            search_text('name', text),
            search_text('illustration', text),
        ))
    query = query.filter(*[v for v in [
        search_text('name', name),
        search_text('name_ud', name_ud),
        search_text('illustration', illustration_text),
        Construction.cefr_level.in_(cefr_level) if cefr_level else None,
        # Construction.cefr_level == cefr_level[0] if cefr_level else None,
    ] if v is not None])

    if syntactic_types:
        query = query.filter(Construction.syntactic_types.any(
            SyntacticType.id.in_(syntactic_types)))
    if semantic_types:
        query = query.filter(Construction.semantic_types.any(
            SemanticType.id.in_(semantic_types)))
    if syntactic_functions:
        query = query.filter(Construction.syntactic_functions.any(
            SyntacticFunction.id.in_(syntactic_functions)))
    if syntactic_structures:
        query = query.filter(Construction.syntactic_structures.any(
            SyntacticStructure.id.in_(syntactic_structures)))
    if morphological_tags:
        query = query.filter(Construction.morphological_tags.any(
            MorphologicalTag.id.in_(morphological_tags)))
    if semantic_roles:
        query = query.filter(Construction.semantic_roles.any(
            SemanticRole.id.in_(semantic_roles)))
    if anchor_poss:
        query = query.filter(Construction.anchor_poss.any(
            AnchorPos.id.in_(anchor_poss)))
    if glosses:
        def and_(root: str | None, attr: str | None) -> Any:
            if root and attr:
                return sa.and_(
                    GlossIndex.root.contains(root),  # type: ignore
                    GlossIndex.attr.contains(attr),  # type: ignore
                )
            if root:
                return GlossIndex.root.contains(root)  # type: ignore
            if attr:
                return GlossIndex.attr.contains(attr)  # type: ignore
            return None

        glosses_filter_args = [f for f in (
            and_(root, attr)
            for root, attr in glosses
        ) if f is not None]
        if len(glosses_filter_args) == 1:
            glosses_filter = glosses_filter_args[0]
        else:
            glosses_filter = sa.or_(*glosses_filter_args)
        glosses_query = select(GlossIndex.id).where(glosses_filter)
        query = query.filter(Construction.gloss_index.any(glosses_filter))

    total = await db.scalar(select(F.count()).select_from(query.subquery()))

    query = query.order_by(F.random() if random_sort else Construction.id)

    query = query.offset(offset).limit(limit)
    items = (await db.scalars(query)).all()

    return {
        'total': total,
        'items': items,
    }


@router.post('/import/')
async def constructions_import(
        *, db: Session = Depends(get_db), background_tasks: BackgroundTasks,
        limit: int | None = Query(default=None), background: bool = Query(default=False),
        table: UploadFile | None = None,
        glosses_table: UploadFile | None = None,
        ) -> Any:
    it = None
    if table:
        raw_data = await table.read()
        it = list(itertools.islice(parse_constructions(raw_data), limit))
    glosses_it = None
    if glosses_table:
        glosses_raw_data = await glosses_table.read()
        glosses_it = parse_glosses(glosses_raw_data, limit)
    if not background:
        await import_constructions(db, it, glosses_it)
    else:
        background_tasks.add_task(import_constructions, db, it, glosses_it)
    return {'status': 'ok'}


class SearchInfoResponse(schemas.BaseModel):
    semantic_types: list[SemanticTypeRead]
    syntactic_types: list[Tag]
    syntactic_functions: list[Tag]
    syntactic_structures: list[Tag]

    morphological_tags: list[Tag]
    semantic_roles: list[Tag]
    anchor_poss: list[Tag]


@router.get('/search_info/', response_model=SearchInfoResponse)
async def search_info(*, db: Session = Depends(get_db)) -> Any:
    return {
        'semantic_types': (await db.scalars(select(SemanticType))).all(),
        'syntactic_types': (await db.scalars(select(SyntacticType))).all(),
        'syntactic_functions': (await db.scalars(select(SyntacticFunction))).all(),
        'syntactic_structures': (await db.scalars(select(SyntacticStructure))).all(),

        'morphological_tags': (await db.scalars(select(MorphologicalTag))).all(),
        'semantic_roles': (await db.scalars(select(SemanticRole))).all(),
        'anchor_poss': (await db.scalars(select(AnchorPos))).all(),
    }


@router.get('/{id}/', response_model=ConstructionRead)
async def construction_get(*, id: int, db: Session = Depends(get_db)) -> Construction:
    return await Construction.crud.get_or_404(db, id=id)
