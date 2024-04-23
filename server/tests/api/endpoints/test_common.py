import pytest
from conftest import Client


def test_info(client: Client) -> None:
    resp = client.get('/info/')
    assert resp.status_code == 200, resp
    res = resp.json()
    assert res == {
        'docs_url': 'http://testserver/docs',
        'info': 'Hello! This is api info page.',
        'redoc_url': 'http://testserver/redoc',
    }

def test_schema(client: Client) -> None:
    resp = client.get('/api/schema.json')
    assert resp.status_code == 200, resp
