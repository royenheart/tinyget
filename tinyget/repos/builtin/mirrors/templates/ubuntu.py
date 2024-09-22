from typing import Optional
from tinyget.repos.third_party import (
    AllMirrorInfo,
    AllSystemInfo,
    ask_for_mirror_options,
    get_os_version,
    ThirdPartyMirrors,
    judge_os_in_systemlist,
)
from tinyget.common_utils import logger, strip_str_lines


class _ubuntu(ThirdPartyMirrors):
    MIRROR_NAME = AllMirrorInfo.UBUNTU

    def get_template(self) -> Optional[str]:
        oinfo = get_os_version()
        if not judge_os_in_systemlist(
            oinfo,
            [
                AllSystemInfo.UBUNTU_JAMMY,
                AllSystemInfo.UBUNTU_FOCAL,
                AllSystemInfo.UBUNTU_BIONIC,
                AllSystemInfo.UBUNTU_TRUSTY,
                AllSystemInfo.UBUNTU_XENIAL,
                AllSystemInfo.UBUNTU_LUNAR,
                AllSystemInfo.UBUNTU_MANTIC,
                AllSystemInfo.UBUNTU_NOBLE,
            ],
        )[0]:
            logger.warning(f"Couldn't find ubuntu mirror for your os {oinfo}")
            return None
        _, _, os_codename = oinfo
        VERSION = os_codename
        USE_OFFICIAL_SECURITY_UPDATES = False
        USE_PROPOSED = False
        USE_SOURCE_MIRROR = False
        w = ask_for_mirror_options(
            options=None,
            true_or_false=[
                (
                    "use_proposed",
                    "Enable proposed?",
                ),
                ("use_source_mirror", "Enable source mirror?"),
                ("use_official_security_updates", "Enable official security updates?"),
            ],
        )
        for qa in w:
            q, a = qa
            if q == "use_proposed":
                USE_PROPOSED = bool(a)
            elif q == "use_source_mirror":
                USE_SOURCE_MIRROR = bool(a)
            elif q == "use_official_security_updates":
                USE_OFFICIAL_SECURITY_UPDATES = bool(a)
        USE_SOURCE_MIRROR_ENABLE = "" if USE_SOURCE_MIRROR else "#"
        USE_PROPOSED_ENABLE = "" if USE_PROPOSED else "#"
        USE_OFFICIAL_SECURITY_UPDATES_ENABLE = (
            "" if USE_OFFICIAL_SECURITY_UPDATES else "#"
        )
        USE_OFFICIAL_SECURITY_UPDATES_DISABLE = (
            "#" if USE_OFFICIAL_SECURITY_UPDATES else ""
        )
        TEMPLATE = f"""#!/bin/bash
# Script contents are from https://mirrors.help/
# Thanks to mirrorz project: https://mirrorz.org/

cat <<'EOF' > /etc/apt/sources.list
# Source image is commented out by default to increase the speed of apt update. You can uncomment it if you want.
deb https://mirrors.cernet.edu.cn/ubuntu/ {VERSION} main restricted universe multiverse
{USE_SOURCE_MIRROR_ENABLE} deb-src https://mirrors.cernet.edu.cn/ubuntu/ {VERSION} main restricted universe multiverse
deb https://mirrors.cernet.edu.cn/ubuntu/ {VERSION}-updates main restricted universe multiverse
{USE_SOURCE_MIRROR_ENABLE} deb-src https://mirrors.cernet.edu.cn/ubuntu/ {VERSION}-updates main restricted universe multiverse
deb https://mirrors.cernet.edu.cn/ubuntu/ {VERSION}-backports main restricted universe multiverse
{USE_SOURCE_MIRROR_ENABLE} deb-src https://mirrors.cernet.edu.cn/ubuntu/ {VERSION}-backports main restricted universe multiverse

# The following security update include both official sources and mirror site configurations. You can modify them as needed by uncommenting.
{USE_OFFICIAL_SECURITY_UPDATES_DISABLE} deb https://mirrors.cernet.edu.cn/ubuntu/ {VERSION}-security main restricted universe multiverse
{USE_OFFICIAL_SECURITY_UPDATES_DISABLE} {USE_SOURCE_MIRROR_ENABLE} deb-src https://mirrors.cernet.edu.cn/ubuntu/ {VERSION}-security main restricted universe multiverse

{USE_OFFICIAL_SECURITY_UPDATES_ENABLE} deb http://security.ubuntu.com/ubuntu/ {VERSION}-security main restricted universe multiverse
{USE_OFFICIAL_SECURITY_UPDATES_ENABLE} {USE_SOURCE_MIRROR_ENABLE} deb-src http://security.ubuntu.com/ubuntu/ {VERSION}-security main restricted universe multiverse

# Proposed software, not recommended to be enabled
{USE_PROPOSED_ENABLE} deb https://mirrors.cernet.edu.cn/ubuntu/ {VERSION}-proposed main restricted universe multiverse
{USE_PROPOSED_ENABLE} {USE_SOURCE_MIRROR_ENABLE} deb-src https://mirrors.cernet.edu.cn/ubuntu/ {VERSION}-proposed main restricted universe multiverse
EOF"""
        logger.info(
            "The script contents are from MirrorZ Project: https://mirrorz.org/. The script has some modifications"
        )
        return strip_str_lines(TEMPLATE)
