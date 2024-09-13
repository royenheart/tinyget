from typing import Optional
from tinyget.repos.third_party import (
    ask_for_mirror_options,
    get_os_version,
    ThirdPartyMirrors,
)
from tinyget.common_utils import logger, strip_str_lines


support_os = [
    ("ubuntu", "jammy"),
    ("ubuntu", "focal"),
    ("ubuntu", "bionic"),
    ("ubuntu", "trusty"),
    ("ubuntu", "xenial"),
    ("ubuntu", "lunar"),
    ("ubuntu", "mantic"),
    ("ubuntu", "noble"),
]


class _ubuntu(ThirdPartyMirrors):
    MIRROR_NAME = "ubuntu"

    def get_template(self) -> Optional[str]:
        os, _, os_codename = get_os_version()
        if (os, os_codename) not in support_os:
            logger.warning(
                f"Couldn't find ubuntu mirror for your os {os} {os_codename}"
            )
            return None
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
