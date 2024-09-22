from typing import Optional
from tinyget.repos.third_party import (
    AllMirrorInfo,
    AllSystemInfo,
    ThirdPartyMirrors,
    get_os_version,
    ask_for_mirror_options,
    judge_os_in_systemlist,
)
from tinyget.common_utils import logger, strip_str_lines
import os


class _debian(ThirdPartyMirrors):
    MIRROR_NAME = AllMirrorInfo.DEBIAN

    def get_template(self) -> Optional[str]:
        oinfo = get_os_version()
        is_support, match_os = judge_os_in_systemlist(
            oinfo,
            [
                AllSystemInfo.DEBIAN_TRIXIE,
                AllSystemInfo.DEBIAN_BOOKWORM,
                AllSystemInfo.DEBIAN_BULLSEYE,
            ],
        )
        if not is_support:
            logger.warning(f"Couldn't find debian mirror for your os {oinfo}")
            return None
        _, _, os_codename = oinfo
        if match_os == AllSystemInfo.DEBIAN_TRIXIE:
            # unrelease version in debian, switch to sid / testing depends on existing file
            try:
                if os.path.exists("/etc/apt/sources.list.d/debian.sources"):
                    source_f = "/etc/apt/sources.list.d/debian.sources"
                elif os.path.exists("/etc/apt/sources.list"):
                    source_f = "/etc/apt/sources.list"
                else:
                    raise FileNotFoundError
                with open(source_f, "r") as f:
                    s = f.read()
                    if "Suites: testing" in s:
                        VERSION = "testing"
                    elif "Suites: sid" in s:
                        VERSION = "sid"
                    else:
                        logger.warning(
                            "Could not detect debian is sid or testing! Script can't generate!"
                        )
                        return None
            except FileNotFoundError as e:
                logger.warning(
                    "Not found existing source file for debian to judge whether it's sid / testing, script can't generate!"
                )
                return None
        else:
            VERSION = os_codename
        USE_TRADITIONAL_FORMAT = False
        USE_OFFICIAL_SECURITY_UPDATES = False
        USE_SOURCE_MIRROR = False
        w = ask_for_mirror_options(
            options=None,
            true_or_false=[
                (
                    "use_traditional_format",
                    "Use traditional format? No will use format DEB822. (requires debian 12 / sid / testing)",
                ),
                ("use_source_mirror", "Enable source mirror?"),
                ("use_official_security_updates", "Enable official security updates?"),
            ],
        )
        for qa in w:
            q, a = qa
            if q == "use_traditional_format":
                USE_TRADITIONAL_FORMAT = bool(a)
            elif q == "use_source_mirror":
                USE_SOURCE_MIRROR = bool(a)
            elif q == "use_official_security_updates":
                USE_OFFICIAL_SECURITY_UPDATES = bool(a)
        USE_SOURCE_MIRROR_ENABLED = "" if USE_SOURCE_MIRROR else "#"
        USE_OFFICIAL_SECURITY_UPDATES_ENABLED = (
            "" if USE_OFFICIAL_SECURITY_UPDATES else "#"
        )
        USE_OFFICIAL_SECURITY_UPDATES_DISABLED = (
            "#" if USE_OFFICIAL_SECURITY_UPDATES else ""
        )
        SID_DIS = "#" if VERSION == "sid" else ""
        SID_TEST_DIS = "#" if VERSION == "sid" or VERSION == "testing" else ""
        TEMPLATE = (
            f"""#!/bin/bash
# Script contents are from https://mirrors.help/
# Thanks to mirrorz project: https://mirrorz.org/

sudo apt install apt-transport-https ca-certificates

cat <<'EOF' > /etc/apt/sources.list
# Source image is commented out by default to increase the speed of apt update. You can uncomment it if you want.
deb https://mirrors.cernet.edu.cn/debian/ {VERSION} main contrib non-free non-free-firmware
{USE_SOURCE_MIRROR_ENABLED} deb-src https://mirrors.cernet.edu.cn/debian/ {VERSION} main contrib non-free non-free-firmware

{SID_DIS} deb https://mirrors.cernet.edu.cn/debian/ {VERSION}-updates main contrib non-free non-free-firmware
{SID_DIS} {USE_SOURCE_MIRROR_ENABLED} deb-src https://mirrors.cernet.edu.cn/debian/ {VERSION}-updates main contrib non-free non-free-firmware

{SID_DIS} deb https://mirrors.cernet.edu.cn/debian/ {VERSION}-backports main contrib non-free non-free-firmware
{SID_DIS} {USE_SOURCE_MIRROR_ENABLED} deb-src https://mirrors.cernet.edu.cn/debian/ {VERSION}-backports main contrib non-free non-free-firmware

# The following security update include both official sources and mirror site configurations. You can modify them as needed by uncommenting.
# deb https://mirrors.cernet.edu.cn/debian-security {VERSION}-security main contrib non-free non-free-firmware
# deb-src https://mirrors.cernet.edu.cn/debian-security {VERSION}-security main contrib non-free non-free-firmware

{SID_DIS} {USE_OFFICIAL_SECURITY_UPDATES_ENABLED} deb https://security.debian.org/debian-security {VERSION}-security main contrib non-free non-free-firmware
{SID_DIS} {USE_OFFICIAL_SECURITY_UPDATES_ENABLED} {USE_SOURCE_MIRROR_ENABLED} deb-src https://security.debian.org/debian-security {VERSION}-security main contrib non-free non-free-firmware
EOF"""
            if USE_TRADITIONAL_FORMAT and VERSION != "bullseye"
            else f"""#!/bin/bash
# Script contents are from https://mirrors.help/
# Thanks to mirrorz project: https://mirrorz.org/

sudo apt install apt-transport-https ca-certificates

cat <<'EOF' > /etc/apt/sources.list.d/debian.sources
Types: deb
URIs: https://mirrors.cernet.edu.cn/debian
Suites: {VERSION} {VERSION}-updates {VERSION}-backports
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

# Source image is commented out by default to increase the speed of apt update. You can uncomment it if you want.
{USE_SOURCE_MIRROR_ENABLED} Types: deb-src
{USE_SOURCE_MIRROR_ENABLED} URIs: https://mirrors.cernet.edu.cn/debian
{USE_SOURCE_MIRROR_ENABLED} Suites: {VERSION} {VERSION}-updates {VERSION}-backports
{USE_SOURCE_MIRROR_ENABLED} Components: main contrib non-free non-free-firmware
{USE_SOURCE_MIRROR_ENABLED} Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

# The following security update include both official sources and mirror site configurations. You can modify them as needed by uncommenting.
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_DISABLED} Types: deb
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_DISABLED} URIs: https://mirrors.cernet.edu.cn/debian-security
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_DISABLED} Suites: {VERSION}-security
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_DISABLED} Components: main contrib non-free non-free-firmware
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_DISABLED} Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_DISABLED} {USE_SOURCE_MIRROR_ENABLED} Types: deb-src
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_DISABLED} {USE_SOURCE_MIRROR_ENABLED} URIs: https://mirrors.cernet.edu.cn/debian-security
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_DISABLED} {USE_SOURCE_MIRROR_ENABLED} Suites: {VERSION}-security
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_DISABLED} {USE_SOURCE_MIRROR_ENABLED} Components: main contrib non-free non-free-firmware
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_DISABLED} {USE_SOURCE_MIRROR_ENABLED} Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_ENABLED} Types: deb
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_ENABLED} URIs: http://security.debian.org/debian-security
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_ENABLED} Suites: {VERSION}-security
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_ENABLED} Components: main contrib non-free non-free-firmware
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_ENABLED} Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_ENABLED} {USE_SOURCE_MIRROR_ENABLED} Types: deb-src
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_ENABLED} {USE_SOURCE_MIRROR_ENABLED} URIs: http://security.debian.org/debian-security
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_ENABLED} {USE_SOURCE_MIRROR_ENABLED} Suites: {VERSION}-security
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_ENABLED} {USE_SOURCE_MIRROR_ENABLED} Components: main contrib non-free non-free-firmware
{SID_TEST_DIS} {USE_OFFICIAL_SECURITY_UPDATES_ENABLED} {USE_SOURCE_MIRROR_ENABLED} Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
EOF"""
        )
        logger.info(
            "The script contents are from MirrorZ Project: https://mirrorz.org/. The script has some modifications"
        )
        return strip_str_lines(TEMPLATE)
