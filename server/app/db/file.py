DBG = """
import functools
import os

from sqlalchemy import types, Column

from app.core import settings
# from app.utils import stablehash


def stablehash(data):
    return data


class File:
    def __init__(self, data=None, upload_to=None, ext=None):
        self.upload_to = upload_to
        self.data = data or {}
        self.ext = ext

    @property
    def url(self):
        assert self.upload_to is not None
        return os.path.join(
            settings.MEDIA_URL, self.upload_to,
            self.data['filename'] + self.ext
        )

    @property
    def path(self):
        assert self.upload_to is not None
        return os.path.join(
            settings.MEDIA_ROOT, self.upload_to,
            self.data['filename'] + self.ext
        )

    async def save(self, file, filename=None):
        data = await file.read()

        filename = filename or f'{stablehash(data)}'
        self.data['filename'] = filename
        with open(self.path, 'wb') as f:
            f.write(data)
        return self

class FileField(types.TypeDecorator): # TypeDecorator):
    impl = types.JSON

    def __init__(self, *args, upload_to=None, ext=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.upload_to = upload_to
        self.ext = '' if ext is None else f'.{ext.lstrip(".")}'

    def copy(self, **kw):
        return FileField(upload_to=self.upload_to, ext=self.ext, **kw)

    def process_bind_param(self, value, dialect):
        return value.data

    def process_result_value(self, value, dialect):
        if value is not None:
            return self.file_cls(value)
        return None

    def process_literal_param(self, value, dialect):
        raise ValueError('literals not supported')

    @property
    def python_type(self):
        return dict

    @property
    def file_cls(self):
        return functools.partial(File, upload_to=self.upload_to, ext=self.ext)


def Media(upload_to=None, ext=None, none_as_null=True, **kwargs) -> tuple[Column, type]:  # pylint: disable=invalid-name
    MEDIA_DIRS.add(upload_to)

    f = FileField(upload_to=upload_to, ext=ext, none_as_null=none_as_null)
    return Column(
        f,
        **kwargs
    ), f.file_cls

MEDIA_DIRS: set[str] = set()

def setup_media():
    for path in MEDIA_DIRS:
        root = os.path.join(settings.MEDIA_ROOT, path)
        os.makedirs(root, exist_ok=True)
"""
