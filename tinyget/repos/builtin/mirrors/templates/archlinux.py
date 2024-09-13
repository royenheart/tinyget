from typing import Optional
from tinyget.repos.third_party import ThirdPartyMirrors, get_os_version
from tinyget.common_utils import logger


class _archlinux(ThirdPartyMirrors):
    MIRROR_NAME = "archlinux"

    def get_template(self) -> Optional[str]:
        os, _, _ = get_os_version()
        if os != "arch":
            logger.warning(f"Your os {os} is not ArchLinux!")
            return None
        TEMPLATE = """#!/bin/bash
# Script contents are from https://mirrors.help/
# Thanks to mirrorz project: https://mirrorz.org/

cat <<'EOF' > /etc/pacman.d/mirrorlist
Server = https://mirrors.cernet.edu.cn/archlinux/$repo/os/$arch
EOF

sudo pacman -Syyu"""
        logger.info(
            "The script contents are from MirrorZ Project: https://mirrorz.org/. The script has some modifications"
        )
        return TEMPLATE
