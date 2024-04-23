from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware import cors, Middleware
from sqlalchemy.exc import NoResultFound
from pathlib import Path

from app import deps
from app.db import configure
from app.core import settings
from app.api.urls import router


# TODO: add correct origins, methods and headers
middleware = [
    Middleware(
        cors.CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=settings.SCHEMA_URL,
    middleware=middleware,
	docs_url=None, redoc_url=None,
    dependencies=[Depends(deps.check_maintenance)],
)

app.include_router(router)


# Use nginx or fastapi for static and media files
app.mount(settings.MEDIA_URL, StaticFiles(directory=settings.MEDIA_ROOT), name='media')

# Use nginx or fastapi for static and media files
app.mount(settings.MEDIA_URL, StaticFiles(directory=settings.MEDIA_ROOT), name='media')


app.mount(
    "/",
    StaticFiles(directory=Path(settings.STATIC_ROOT) / 'other', html=True),
    name="site"
)


@app.on_event('startup')
def startup_event() -> None:
    if settings.ENV_TYPE == 'test':
        return

    configure(settings.DATABASE_URL)


@app.exception_handler(NoResultFound)
async def sa_no_result_found(request: Request, exc: NoResultFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={'detail': "Not Found"})
