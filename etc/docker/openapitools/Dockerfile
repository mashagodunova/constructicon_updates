FROM docker.io/openapitools/openapi-generator-cli

RUN useradd --create-home --shell /bin/bash --home /home/user user
USER user
WORKDIR /home/user

COPY ./config* ./etc/
