import itertools
from typing import Iterable, Any, TypeVar, Type, DefaultDict
import asyncio
import collections
import re
import csv
import sqlalchemy as sa
import functools

from app.db import Session

from .singleton import with_maintenance

from .construction import BaseConstruction, Construction
from .construction_related import *
from .construction_tags import *
from .construction_types import CefrLevel, UsageLabel, CommunicativeType, Language
from .glosses import Gloss, GlossIndex

T = TypeVar('T')

def get_key(cls: Type[T], args: dict[str, Any]) -> Any:
    return (cls.__name__,) +  tuple(sorted(args.items()))

'''
async def c(cls, cache, db, extra=None, *args, **kwargs):
    key = get_key(kwargs)
    obj = cache.get(key)
    if obj is not None:
        return False, obj
    cache[key] = obj = cls(*args, **kwargs, **(extra if extra else {}))
    db.add(obj)
    await db.flush()
    return True, obj


async def add_tags(  # pylint: disable=too-many-arguments
        db: Session, cache, args_list: Any, cls: Any, right_id: int | None = None, secondary: Any = None,
        extra: Any = None, append: Any = None,
        ) -> None:


    for args in args_list:
        extras = {cur: args.pop(cur) for cur in extra} if extra else {}
        created, obj = await c(cls, cache, db, **args)
        if secondary:
            pass
            s = secondary(left_id=obj.id, **extras)
            append(s)
            # db.add(s)
        else:
            append(obj)


def list_unique1(lst):
    new = []
    for elt in lst:
        if elt not in new:
            new.append(elt)
        # else:
        #     print('AAA', elt)
    return new
'''


class ConstructionCreate(BaseConstruction):
    examples: list['BaseConstructionExample']
    definitions: list['BaseConstructionDefinition']
    equivalents: list['BaseEquivalent']

    syntactic_types: list['TagCreate']
    semantic_types: list[list['TagCreate']]
    syntactic_functions: list['TagCreate']
    syntactic_structures: list['TagCreate']

    morphological_tags: list['OrderedTagCreate']
    semantic_roles: list['OrderedTagCreate']
    anchor_poss: list['OrderedTagCreate']

    def __init__(self, id_number: str, dependency_structure_of_illustration: str, **data: Any) -> None:
        def split_tags(value: str, sep: str = ',') -> list[tuple[str, int]]:
            return [
                (name.strip(), i)
                for i, name in enumerate(value.strip().split(sep))
                if name.strip()
            ]

        sem_types = []
        for i in range(1, 5):
            cur_type = []
            for key in [f'sem_type{i}', f'sem_sub_type{i}']:
                values = data.pop(key, '').split(':')
                cur_type.extend([
                    TagCreate(name=v.strip()) for v in values if v.strip()
                ])

            if cur_type:
                sem_types.append(cur_type)
        # sem_types = list_unique(sem_types)

        # print('L', [data['communicative_type']])
        super().__init__(
            id=id_number,
            illustration_dependency_structure=dependency_structure_of_illustration,
            cefr_level=CefrLevel.parse(data.pop('cefr_level')),
            usage_label=UsageLabel.parse(data.pop('usage_label')),
            communicative_type=CommunicativeType.parse(data.pop('communicative_type')),
            # communicative_type=[],
            definitions=[x for x in (
                BaseConstructionDefinition(
                    value=data.pop(f'definition_in_{language.name}', '').strip(),
                    language=language,
                )
                for language in Language
            ) if x.value],
            equivalents=[x for x in (
                BaseEquivalent(
                    value=data.pop(f'{language.name}_equivalent', '').strip(),
                    language=language,
                )
                for language in Language
            ) if x.value],
            examples=[x for x in (
                BaseConstructionExample(
                    value=data.pop(f'example_{i}', '').strip(),
                    number=i,
                )
                for i in range(1, 6)
            ) if x.value],
            # unordered
            semantic_types=sem_types,
            syntactic_types=[
                TagCreate(name=name)
                for name, _i in split_tags(data.pop('synt_type_of_construction', ''))
            ],
            syntactic_functions=[
                TagCreate(name=name)
                for name, _i in split_tags(data.pop('synt_func_of_anchor', ''))
            ],
            syntactic_structures=[
                TagCreate(name=name)
                for name, _i in split_tags(data.pop('synt_structure_of_anchor', ''))
            ],
            # ordered
            anchor_poss=[
                OrderedTagCreate(name=name, number=i)
                for name, i in split_tags(data.pop('part_of_speech_of_anchor', ''))
            ],
            morphological_tags=[
                OrderedTagCreate(name=name, number=i)
                for name, i in split_tags(data.pop('morphology', ''))
            ],
            semantic_roles=[
                OrderedTagCreate(name=name, number=i)
                for name, i in split_tags(data.pop('semantic_role', ''))
            ],
            **data,
        )
    # 'communicative_type', 'usage_label',



def clean_raw_table_column_name(name: str) -> str:
    # camel_to_snake
    name = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    # collapse_not_alpha
    name = re.sub(r'[^A-Za-z0-9]+', '_', name)
    name = name.strip('_')
    return name


def parse_constructions(raw_data: bytes) -> Iterable[ConstructionCreate]:
    reader = csv.reader(raw_data.decode('utf-8').split('\n'), delimiter=',', quotechar='"')
    header = [clean_raw_table_column_name(name) for name in next(reader)]
    values = (dict(zip(header, row)) for row in reader)
    return (
        ConstructionCreate(**args)
        for args in values
        if args['cefr_level'].strip()
            and args['communicative_type'].strip() != 'v'
    )

def parse_glosses(raw_data: bytes, limit: int | None) -> dict[int, dict[Language, list[str]]]:
    reader = csv.reader(itertools.islice(raw_data.decode('utf-8').split('\n'), limit), delimiter=',', quotechar='"')
    header = [clean_raw_table_column_name(name) for name in next(reader)]
    it = (dict(zip(header, row)) for row in reader)
    values: DefaultDict[int, dict[Language, list[str]]] = collections.defaultdict(dict)
    for value in it:
        if not value or not value['id_number']:
            continue
        cur_id = int(value['id_number'])
        cur_values = values[cur_id]
        cur_values[Language.parse(value['line'])] = [
            token for i in range(len(value))
            # if (cell := value.get(str(i))) and (token := cell.split(':', 1)[1])
            if (token := value.get(str(i)))
        ]
    return  dict(values)

def check_unique(tags, args):
    if len(tags) != len(set(tags)):
        raise ValueError(f'Duplicated tags: {tags}, {args}')
    return tags

async def import_main(db: Session, it: Iterable[ConstructionCreate]) -> None:  # pylint: disable=too-many-locals
    await asyncio.gather(
        db.execute(sa.delete(Construction)),

        db.execute(sa.delete(ConstructionExample)),
        db.execute(sa.delete(ConstructionDefinition)),
        db.execute(sa.delete(Equivalent)),
        db.execute(sa.delete(SyntacticType)),
        db.execute(sa.delete(SemanticType)),
        db.execute(sa.delete(SyntacticFunction)),
        db.execute(sa.delete(SyntacticStructure)),
        db.execute(sa.delete(MorphologicalTag)),
        db.execute(sa.delete(SemanticRole)),
        db.execute(sa.delete(AnchorPos)),

        db.execute(sa.delete(SyntacticType2Construction)),
        db.execute(sa.delete(SemanticType2Construction)),
        db.execute(sa.delete(SyntacticFunction2Construction)),
        db.execute(sa.delete(SyntacticStructure2Construction)),
        db.execute(sa.delete(MorphologicalTag2Construction)),
        db.execute(sa.delete(SemanticRole2Construction)),
        db.execute(sa.delete(AnchorPos2Construction)),
    )

    # await db.commit()
    # await db.flush()

    cache: dict[Any, Any] = {}

    def init_tag(cls: Type[T], args: dict[str, Any]) -> tuple[bool, T]:
        new_obj = cls(**args)
        obj = cache.setdefault(get_key(cls, new_obj.dict()), new_obj)
        if new_obj is obj:
            db.add(obj)
        return (new_obj is obj, obj)

    def init_tags(cls: Type[T], args: list[dict[str, Any]]) -> list[T]:
        res = []
        for cur_args in args:
            res.append(init_tag(cls, cur_args)[1])
        return res

    rows = [x.dict() for x in it]
    strange_ids = []
    ids_counter = collections.Counter(x['id'] for x in rows)
    bad_ids = {k: v for k, v in ids_counter.items() if v > 1}
    if bad_ids:
        raise ValueError(f'Duplicated ids {bad_ids}')
    for args in rows:
        syntactic_structures = args.pop('syntactic_structures')
        syntactic_functions = args.pop('syntactic_functions')
        syntactic_types = args.pop('syntactic_types')

        args['syntactic_structures'] = init_tags(SyntacticStructure, syntactic_structures)
        args['syntactic_functions'] = init_tags(SyntacticFunction, syntactic_functions)
        args['syntactic_types'] = init_tags(SyntacticType, syntactic_types)

        morphological_tags = args.pop('morphological_tags')
        anchor_poss = args.pop('anchor_poss')
        semantic_roles = args.pop('semantic_roles')

        args['morphological_tags'] = list(zip(
            morphological_tags, init_tags(MorphologicalTag, morphological_tags)))
        args['anchor_poss'] = zip(
            anchor_poss, init_tags(AnchorPos, anchor_poss))
        args['semantic_roles'] = zip(
            semantic_roles, init_tags(SemanticRole, semantic_roles))

        semantic_types = args.pop('semantic_types')
        args['semantic_types'] = []
        # if len(semantic_types) != len(set(semantic_types)):
        #     print(semantic_types)

        for args_line in semantic_types:
            prev: None | SemanticType = None
            for cur_args in args_line:
                created, obj = init_tag(SemanticType, cur_args)
                if created and prev is not None:
                    prev.children.append(obj)
                prev = obj
                args['semantic_types'].append(obj)
        sem_types = [x.name for x in args['semantic_types']]
        if len(sem_types) != len(set(sem_types)):
            # print(sem_types)
            # print(semantic_types)
            strange_ids.append(args['id'])
            print('Strange id', args['id'])

    # await db.commit()
    # await db.flush()

    for args in rows:
        # construction = await Construction.crud.create(db, **args, save_=False)
        examples = args.pop('examples')
        definitions = args.pop('definitions')
        equivalents = args.pop('equivalents')

        morphological_tags = args.pop('morphological_tags')
        anchor_poss = args.pop('anchor_poss')
        semantic_roles = args.pop('semantic_roles')

        # semantic_types = args.pop('semantic_types')

        construction = await Construction.crud.create(db, **args, save_=False)

        for example_args in examples:
            await ConstructionExample.crud.create(db, construction=construction, **example_args, save_=False)

        for definition_args in definitions:
            await ConstructionDefinition.crud.create(db, construction=construction, **definition_args, save_=False)

        for equivalent_args in equivalents:
            await Equivalent.crud.create(db, construction=construction, **equivalent_args, save_=False)

        for args, obj in morphological_tags:
            db.add(MorphologicalTag2Construction(number=args['number'], left=obj, right=construction))

        for args, obj in anchor_poss:
            db.add(AnchorPos2Construction(number=args['number'], left=obj, right=construction))

        for args, obj in semantic_roles:
            db.add(SemanticRole2Construction(number=args['number'], left=obj, right=construction))

        '''
        for args_line in semantic_types:
            prev = None
            for args in args_line:
                created, semantic_type = await c(SemanticType, cache, db, extra={'parent': prev})
                construction.semantic_types.append(semantic_type)
                prev = semantic_type
        '''

    # print(strange_ids)


async def import_glosses(db: Session, it: dict[int, dict[Language, list[str]]]) -> None:
    await asyncio.gather(
        db.execute(sa.delete(Gloss)),
    )

    for construction_id, data in it.items():
        for lang, glosses in data.items():
            for number, value in enumerate(glosses):
                gloss = await Gloss.crud.create(
                    db,
                    construction_id=construction_id,
                    language=lang,
                    number=number,
                    value=value,
                    save_=False,
                )
                vs = re.sub(r'[\[\]()]', '', value.lower()).split('/')
                for v in vs:
                    as_, b, *_ = re.split(r'[-.]', v, 1) + [None]
                    for a in as_.split('<'):
                        # print(a, b)
                        await GlossIndex.crud.create(
                            db,
                            attr=b,
                            root=a,
                            construction_id=construction_id,
                            save_=False,
                        )


async def import_constructions(db: Session, it: Iterable[ConstructionCreate] | None, glosses_it: dict[int, dict[Language, list[str]]] | None) -> None:  # pylint: disable=too-many-locals
    async with with_maintenance(db):
        if it:
            await import_main(db, it)
        if glosses_it:
            await import_glosses(db, glosses_it)
        await db.commit()
