#! /usr/bin/bash

set -ex

rm ./coverage.xml htmlcov -rf && \
  SQLALCHEMY_SILENCE_UBER_WARNING=1 \
  FASTAPI_DOTENV=/home/web/etc/env/test python -m cProfile -o tmp/profile -m pytest && \
  python -m coverage html
