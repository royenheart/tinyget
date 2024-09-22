from typing import Optional
from tinyget.repos.third_party import (
    AllMirrorInfo,
    AllSystemInfo,
    ThirdPartyMirrors,
    ask_for_mirror_options,
    get_os_version,
    judge_os_in_systemlist,
)
from tinyget.common_utils import logger, strip_str_lines


class _llvm(ThirdPartyMirrors):
    MIRROR_NAME = AllMirrorInfo.LLVM_APT

    def get_template(self) -> Optional[str]:
        oinfo = get_os_version()
        if not judge_os_in_systemlist(
            oinfo,
            [
                AllSystemInfo.DEBIAN_BOOKWORM,
                AllSystemInfo.DEBIAN_BULLSEYE,
                AllSystemInfo.UBUNTU_JAMMY,
                AllSystemInfo.UBUNTU_FOCAL,
                AllSystemInfo.UBUNTU_BIONIC,
            ],
        )[0]:
            logger.warning(f"LLVM APT does not support os {oinfo}")
            return None
        _, _, os_codename = oinfo
        OS_VERSION = os_codename
        w = ask_for_mirror_options(
            options={
                ("llvm", "Use what llvm version"): [
                    "default",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                ]
            },
            true_or_false=[
                ("use_scripts", "Use scripts to atomatically install llvm?"),
                ("use_source_mirror", "Enable source mirror?"),
            ],
        )
        USE_SCRIPTS = False
        LLVM_VERSION = ""
        USE_SOURCE_MIRROR = False
        for qa in w:
            q, a = qa
            if q == "use_scripts":
                USE_SCRIPTS = bool(a)
            elif q == "llvm_version":
                LLVM_VERSION = "" if a == "default" else a
            elif q == "use_source_mirror":
                USE_SOURCE_MIRROR = bool(a)
        LLVM_VERSION_C = "-" + LLVM_VERSION if LLVM_VERSION != "" else ""
        USE_SOURCE_MIRROR_C = "" if USE_SOURCE_MIRROR else "#"
        TEMPLATE = (
            f"""#!/bin/bash
# Script contents are from https://mirrors.help/
# Thanks to mirrorz project: https://mirrorz.org/

# Download script for installing
INSTALL=$(mktemp -d)
wget -c https://mirrors.cernet.edu.cn/llvm-apt/llvm.sh -O ${{INSTALL}}/llvm.sh
chmod +x llvm.sh
sudo ./llvm.sh {LLVM_VERSION} all -m https://mirrors.cernet.edu.cn/llvm-apt
"""
            if USE_SCRIPTS
            else f"""
#!/bin/bash
# Script contents are from https://mirrors.help/
# Thanks to mirrorz project: https://mirrorz.org/

# Trust PGP public key
wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | sudo apt-key add -

cat <<'EOF' > /etc/apt/sources.list.d/llvm-apt.list
# Source image is commented out by default to increase the speed of apt update. You can uncomment it if you want.
deb https://mirrors.cernet.edu.cn/llvm-apt/{OS_VERSION}/ llvm-toolchain-{OS_VERSION}{LLVM_VERSION_C} main
{USE_SOURCE_MIRROR_C} deb-src https://mirrors.cernet.edu.cn/llvm-apt/{OS_VERSION}/ llvm-toolchain-{OS_VERSION}{LLVM_VERSION_C} main
EOF"""
        )
        logger.info(
            "The script contents are from MirrorZ Project: https://mirrorz.org/. The script has some modifications"
        )
        return strip_str_lines(TEMPLATE)
