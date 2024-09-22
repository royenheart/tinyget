from typing import Optional
from tinyget.repos.third_party import (
    AllMirrorInfo,
    ThirdPartyMirrors,
    get_os_version,
    judge_os_in_systemlist,
    AllSystemInfo,
)
from tinyget.common_utils import logger


class _archlinux(ThirdPartyMirrors):
    MIRROR_NAME = AllMirrorInfo.ARCHLINUX

    def get_template(self) -> Optional[str]:
        os_ver = get_os_version()
        if not judge_os_in_systemlist(os_ver, [AllSystemInfo.ARCH])[0]:
            logger.warning(f"Your os {os_ver} is not ArchLinux!")
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
