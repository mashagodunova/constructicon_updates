import datetime
from typing import Any, Optional, AsyncGenerator
import contextlib

from fastapi import Depends, Request

from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase

from sqlalchemy import Column, Integer, String

from app.db import SABaseModel, Session
from app.db.crud import BaseCRUD
from app.db.deps import get_db
from app.utils import send_new_account_email, signing
from app.schemas.user import UserCreate
from app.core import settings


__all__ = ('User',)


class CRUD(BaseCRUD['User']):
    async def create(self, db: Session, **kwargs: Any) -> 'User':
        async with get_user_db_context(db) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                return await user_manager.create(UserCreate(**kwargs))


class User(SQLAlchemyBaseUserTable[int], SABaseModel):  # type: ignore
    id: int = Column(Integer, primary_key=True, autoincrement=True)  # type: ignore
    username: str = Column(String(length=32), nullable=False, unique=True, index=True)  # type: ignore

    crud: CRUD = CRUD.default()

User.crud = CRUD(User)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(
            self, user: User, request: Optional[Request] = None
        ) -> None:

        if request is None:
            return

        url = request.url
        key = signing.sign(user.id, expires=datetime.timedelta(days=1), salt='verify_new_user')
        link = f'{url.scheme}://{url.hostname}/api/user/verify/?key={key}'
        send_new_account_email(link=link, email=user.email, username=user.username)

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
        ) -> None:

        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
        ) -> None:

        print(f"Verification requested for user {user.id}. Verification token: {token}")


# DEPS

UserDb = SQLAlchemyUserDatabase[User, int]

async def get_user_db(session: Session = Depends(get_db)) -> AsyncGenerator[UserDb, None]:
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
        user_db: UserDb = Depends(get_user_db)
    ) -> AsyncGenerator[UserManager, None]:

    yield UserManager(user_db)

get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


def get_jwt_strategy() -> JWTStrategy[Any, int]:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="auth/jwt/login"),
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

get_current_user = fastapi_users.current_user(active=True)
