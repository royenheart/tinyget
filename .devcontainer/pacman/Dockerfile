FROM archlinux

COPY .devcontainer/pacman/mirror.txt /tmp/
RUN cat /tmp/mirror.txt > /etc/pacman.d/mirrorlist && \
    pacman -Syyu --noconfirm && \
    pacman -S --noconfirm python-pip git
