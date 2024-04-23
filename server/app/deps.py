import urllib
from fastapi import Depends, HTTPException, Request

from app.db import Session
from app.db.deps import get_db, DbDependency
from app.models import User, Singleton

from app.models.user import get_current_user

__all__ = ('get_db', 'DbDependency')



def get_current_superuser(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


async def check_maintenance(*, db: Session = Depends(get_db), request: Request) -> None:
    if '/maintenance' in urllib.parse.urlparse(request.url._url).path:  # pylint: disable=protected-access
        return

    if (await Singleton.get(db)).maintenance:
        raise HTTPException(status_code=503, detail="maintenance")

    return
