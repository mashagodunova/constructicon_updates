import argparse
import os
import sys
from pathlib import Path

from fastapi.openapi.utils import get_openapi
from yaml import load, dump
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o', '--output',
        type=argparse.FileType('w', encoding='utf-8'),
        default=sys.stdout,
        help='Output path (default: stdout)')
    parser.add_argument(
        '-e', '--env-path',
        default=os.getenv("FASTAPI_DOTENV"),
        help=(
            'Fastapi dotenv path, FASTAPI_DOTENV environment variable value if not specified'
            f' (default: {os.getenv("FASTAPI_DOTENV")})'
        ),
    )

    return parser.parse_args()


def main():
    args = parse_args()
    os.environ["FASTAPI_DOTENV"] = args.env_path

    from app.main import app

    schema = app.openapi()
    data = dump(
        schema,
        Dumper=Dumper,
        allow_unicode=True,
        width=1000,
        sort_keys=True,
    )
    args.output.write(data)


if __name__ == '__main__':
    main()
