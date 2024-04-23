import json
from typing import Any, Generator
from pathlib import Path
import pytest
from fastapi.testclient import TestClient as Client
import contextlib


@contextlib.contextmanager
def context_none() -> Generator[None, None, None]:
    yield None


async def import_constructions(client: Client, path: Path, glosses_path: Path | None = None) -> None:
    with (
            path.open('rb') if path else context_none() as f,
            glosses_path.open('rb') if glosses_path else context_none() as gf,
        ):
        resp = client.post(
            '/api/construction/import/',
            params={'limit': 50},
            files={k: v for k, v in {'table': f, 'glosses_table': gf}.items() if v},
        )
    assert resp.status_code == 200, resp.json()


async def test_construction_import(client: Client, testdir: Path, data_regression: Any) -> None:
    testdata = {}
    with (testdir / 'data/data50.csv').open('rb') as f:
        resp = client.post('/api/construction/import/', params={'limit': 1}, files={'table': f})
    res = resp.json()
    assert resp.status_code == 200, res
    testdata['import'] = res

    resp = client.get('/api/construction/')
    res = resp.json()
    assert resp.status_code == 200, res
    testdata['constructions'] = res
    assert res['items'][0]['examples'] != [], 'in_test'

    data_regression.check(res)


async def test_construction_import_glosses(client: Client, testdir: Path, data_regression: Any) -> None:
    testdata = {}
    await import_constructions(client, testdir / 'data/full_data.csv')
    with (testdir / 'data/glosses_data.csv').open('rb') as f:
        resp = client.post('/api/construction/import/', params={'limit': 50}, files={'glosses_table': f})

    res = resp.json()
    assert resp.status_code == 200, res
    testdata['import'] = res

    resp = client.get('/api/construction/')
    res = resp.json()
    assert resp.status_code == 200, res
    testdata['get'] = res

    data_regression.check(res)



async def test_construction_import_multiple_times(client: Client, testdir: Path, data_regression: Any) -> None:
    with (testdir / 'data/data50.csv').open('rb') as f:
        resp = client.post('/api/construction/import/', params={'limit': 5}, files={'table': f})
        resp2 = client.post('/api/construction/import/', params={'limit': 50}, files={'table': f})
        resp3 = client.post('/api/construction/import/', params={'limit': 50}, files={'table': f})
    assert resp.status_code == 200, resp.json()
    assert resp2.status_code == 200, resp2.json()
    assert resp3.status_code == 200, resp3.json()
    assert resp3.json() == resp2.json()

    resp = client.get('/api/construction/')
    assert resp.status_code == 200, resp.json()
    

def get_keys(data: Any) -> list[int]:
    return [x['id'] for x in data['items']]


async def test_construction_list_random_sort(client: Client, testdir: Path, data_regression: Any) -> None:
    with (testdir / 'data/data50.csv').open('rb') as f:
        resp = client.post('/api/construction/import/', params={'limit': 50}, files={'table': f})
    assert resp.status_code == 200

    resp = client.get('/api/construction/', params={'random_sort': True})
    assert resp.status_code == 200, resp.json()
    random1 = get_keys(resp.json())
    resp = client.get('/api/construction/', params={'random_sort': True})
    assert resp.status_code == 200, resp.json()
    random2 = get_keys(resp.json())
    assert random1 != random2, 'Random sort returned same results'


params = [
    ({}, False),
    ({'text': 'мама'}, False),
    ({'name': 'nom'}, False),
    ({'cefr_level': 'A1'}, False),
    ({'cefr_level': 'A1,C1'}, False),
    ({'syntactic_types': '6,2'}, False),
    ({'semantic_types': '6,2'}, False),
    ({'syntactic_functions': '6,2'}, False),
    ({'syntactic_structures': '6,2'}, False),
    ({'morphological_tags': '6,2'}, False),
    ({'semantic_roles': '6,2'}, False),
    ({'anchor_poss': '6,2'}, False),
    ({'glosses': 'vp-pfv,нечего,-3sg'}, True),
]


@pytest.fixture()
async def constructions_sample(testdir: Path, client: Client, import_glosses: bool) -> None:
    await import_constructions(
        client,
        testdir / 'data/data50.csv',
        testdir / 'data/glosses_data.csv' if import_glosses else None)


@pytest.mark.parametrize(
    "params,import_glosses",
    params,
    ids=[json.dumps(cur[0], sort_keys=True, ensure_ascii=False) for cur in params],
)
async def test_construction_list(
        client: Client,
        data_regression: Any,
        constructions_sample: None,
        params: dict[str, str],
        ) -> None:
    resp = client.get('/api/construction/', params=params)
    assert resp.status_code == 200, resp.json()
    data_regression.check(get_keys(resp.json()))


async def test_search_info(client: Client, testdir: Path, data_regression: Any) -> None:
    await import_constructions(client, testdir / 'data/full_data.csv')

    resp = client.get('/api/construction/search_info/')
    assert resp.status_code == 200, resp.json()

    data_regression.check(resp.json())


async def test_construction(client: Client, testdir: Path, data_regression: Any) -> None:
    ress: dict[int, Any] = {}
    await import_constructions(client, testdir / 'data/data50.csv')

    resp = client.get('/api/construction/', params={'limit': 3})
    assert resp.status_code == 200, resp.json()
    for id_ in get_keys(resp.json()):
        resp = client.get(f'/api/construction/{id_}/')
        assert resp.status_code == 200, resp.json()
        ress[id_] = resp.json()

    data_regression.check(ress)


async def test_construction_get_missing(client: Client) -> None:
    resp = client.get('/api/construction/404/')
    assert resp.status_code == 404
    res = resp.json()
    assert res == {'detail': 'Not Found'}, res
