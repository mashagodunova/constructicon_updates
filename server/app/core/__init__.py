import os
from .settings import Settings

settings = Settings(
    _env_file=os.environ['FASTAPI_DOTENV']  # type: ignore
)
