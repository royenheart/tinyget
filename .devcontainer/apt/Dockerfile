FROM debian

COPY .devcontainer/apt/mirror.txt /tmp/
RUN cat /tmp/mirror.txt > /etc/apt/sources.list && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt update -y && \
    apt install -y python3-pip
