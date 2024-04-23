from fastapi import APIRouter

from app.core import settings

from .endpoints import (
    common, user, construction,
)


api_router = APIRouter()
api_router.include_router(user.router, prefix='/user')
api_router.include_router(construction.router, prefix='/construction')

router = APIRouter()
router.include_router(common.router)
router.include_router(api_router, prefix=settings.API_PREFIX)
