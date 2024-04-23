FROM docker.io/node:19-bullseye-slim

ARG \
    UNAME=ui \
    UID=1000 \
    GID=1000

# build-essential qemu qemu-kvm
# RUN dpkg --add-architecture i386
RUN set -ex \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        procps iputils-ping curl xorg openbox \
        libnss3 libasound2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN set -ex \
    && groupadd -g $GID -o $UNAME \
    && useradd --create-home --shell /bin/bash --home /home/$UNAME \
        -u $UID -g $GID $UNAME

USER $UNAME

ENV \
    TERM=xterm-256color \
    PATH=/home/$UNAME/.yarn/bin:/home/$UNAME/etc/scripts:$PATH

EXPOSE 3000
EXPOSE 8100

WORKDIR /home/$UNAME/ui
