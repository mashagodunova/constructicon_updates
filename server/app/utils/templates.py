from typing import Any
from fastapi.templating import Jinja2Templates

env = Jinja2Templates(directory="app/templates")

TemplateResponse = env.TemplateResponse

def render(path: str, *args: Any, **kwargs: Any) -> str:
    template = env.get_template(path)
    return template.render(*args, **kwargs)
