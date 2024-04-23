from app.models import User # , Token
from app.core import settings

from conftest import Client, SmtpServer, UserHeaders


def test_get_access_token(client: Client, user: User) -> None:
    login_data = {
        "username": "user@test.example",
        "password": "password"
    }
    resp = client.post(settings.TOKEN_URL, data=login_data)
    assert resp.status_code == 200
    res = resp.json()
    assert "access_token" in res, res
    assert res["access_token"], res


def test_use_token(client: Client, user_headers: UserHeaders) -> None:
    resp = client.get('/api/user/me', headers=user_headers)
    res = resp.json()
    assert resp.status_code == 200, res
    assert "email" in res, res


def test_use_invalid_token(client: Client, user_headers: UserHeaders) -> None:
    resp = client.get('/api/user/me', headers={
        'Authorization': user_headers['Authorization'] + '_invalid',
    })
    assert resp.status_code == 401
    res = resp.json()
    assert res == {'detail': 'Unauthorized'}, res

    strange_token = 'blahblah'
    resp = client.get('/api/user/me', headers={
        'Authorization': f'Bearer {strange_token}'
    })
    assert resp.status_code == 401
    res = resp.json()
    assert res == {'detail': 'Unauthorized'}, res


def test_missing_token(client: Client, user: User) -> None:
    resp = client.get('/api/user/me')
    assert resp.status_code == 401
    res = resp.json()
    assert res == {'detail': 'Unauthorized'}, res

# TODO: enable this test
# def test_user_get_with_invalid_id(client) -> None:
#     resp = client.get('/api/user/abacaba/')
#     assert resp.status_code == 200, res
#     assert res == {}, res

async def test_user_register(client: Client, smtp_server: SmtpServer) -> None:
    resp = client.post('/api/user/register', json={'password': 'pass', 'email': 'new@test.example', 'username': 'new'})
    res = resp.json()
    assert resp.status_code == 201, res
    # assert res == {'email': 'new@test.example', 'id': 1, 'is_active': False, 'is_superuser': False}, res
    assert res == {'email': 'new@test.example', 'id': 1, 'is_active': True, 'is_superuser': False, 'is_verified': False, 'username': 'new'}, res

    assert len(smtp_server.mails) == 1, smtp_server.mails
    mail = smtp_server.mails[0]
    assert len(mail.links) == 1, mail.links

    resp = client.get(mail.links[0])
    res = resp.json()
    assert resp.status_code == 200, res
    assert res == {'email': 'new@test.example', 'id': 1, 'is_active': True, 'is_superuser': False, 'is_verified': True, 'username': 'new'}, res
