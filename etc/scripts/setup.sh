#!/usr/bin/env bash

python -m pip install -U pip
python -m pip install -e .
python -m alembic --config ./alembic/alembic.ini upgrade head
