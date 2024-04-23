server_down:
	podman-compose -f docker-compose.yml down -t 1

down: server_down

server_build:
	podman-compose -f docker-compose.yml build 

server_up: server_down
	podman-compose -f docker-compose.yml up

server_bash:
	podman-compose -f docker-compose.yml run web bash

server_test: server_down
	podman-compose -f docker-compose.yml run web bash /home/web/etc/scripts/test.sh

server_tests: server_test

api_export_schema: server_down
	rm ./etc/api_schema.yaml -f && \
	podman-compose -f docker-compose.yml run web \
		python etc/scripts/export_schema.py -e etc/env/dev -o etc/api_schema.yaml

api_generate_client: api_export_schema
	rm -rf "${PWD}/var/volumes/api_clients/*" && \
	cp ./etc/api_schema.yaml "${PWD}/var/volumes/api_clients/api_schema.yaml" && \
	podman build etc/docker/openapitools -t local-openapitools && \
	podman run \
	    -u "${USER_ID}:${GROUP_ID}" \
		-v "${PWD}/var/volumes/api_clients/":/home/user/api_clients \
	    --rm local-openapitools \
		generate -c ./etc/config-typescript-axios.yaml --enable-post-process-file && \
	podman run \
	    -u "${USER_ID}:${GROUP_ID}" \
		-v "${PWD}/var/volumes/api_clients/":/home/user/api_clients \
	    --rm local-openapitools \
		generate -c ./etc/config-javascript-promise-es6.yaml --enable-post-process-file
	podman run \
	    -u "${USER_ID}:${GROUP_ID}" \
		-v "${PWD}/var/volumes/api_clients/":/home/user/api_clients \
	    --rm local-openapitools \
		generate -c ./etc/config-python.yaml --enable-post-process-file && \

# UI
ui_build:
	podman build -t ui \
		--build-arg UID="${USER_ID}" \
        --build-arg GID="${GROUP_ID}" \
        --build-arg=UNAME=ui \
		etc/docker/ui

ui_bash:
	podman run -it -u "1002:${GROUP_ID}" \
		-p 8100:8100 -p 3000:3000 \
		-v "${PWD}/var/volumes/ui_home/":/home/ui \
		-v "${PWD}/ui/":/home/ui/ui \
		--env=DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
		ui bash

ui_compile:
	podman run --rm -u "1002:${GROUP_ID}" \
		-v "${PWD}/var/volumes/ui_home/":/home/ui \
		-v "${PWD}/ui/":/home/ui/ui \
		ui yarn build && \
	mv ./ui/public/static/js/*.js ./server/app/static/js/ && \
	mv ./ui/public/static/css/*.css ./server/app/static/css/ && \
	mv ./ui/public/static/img/* ./server/app/static/img/ && \
	rm -rf ./server/app/static/other && \
	mv -f ./ui/public ./server/app/static/other

db_migrations: server_down
	podman-compose -f docker-compose.yml run web \
        alembic --config ./alembic/alembic.ini revision --autogenerate -m "$(msg)"

db_migrate: server_down
	podman-compose -f docker-compose.yml run web \
        alembic --config ./alembic/alembic.ini upgrade head

pip_install: server_down server_build
	podman-compose -f docker-compose.yml run web \
		python -m pip install -e .[dev]
