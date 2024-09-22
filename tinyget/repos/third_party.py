"""
Parse third-party softwares' configuration and provide information
"""

from abc import abstractmethod
from collections import defaultdict
import importlib
import importlib.util
import re
from enum import Enum, unique
from typing import Callable, Dict, List, Optional, Tuple
from tinyget.package import Package
from tinyget.globals import global_configs
from tinyget.common_utils import logger
from rich.prompt import Prompt
import os
import requests

ROLLING_SYSTEM = -1


@unique
class AllSystemInfo(tuple, Enum):
    """All os info

    Due to os release not support upper case, use upper case to identity Name. the value is (OS ID (name), OS VERSION ID, OS VERSION CODENAME)

    The key is OS ID
    """

    # https://www.debian.org/releases/
    # the sid / testing is actually based on trixie (next release's codename)
    # so the version codename should be trixie, thus no sid / testing but trixie specified
    # TODO: Automatically update debian's sid / testing version code name
    # DEBIAN_SID = ("debian", None, "trixie")
    # DEBIAN_TESTING = ("debian", None, "trixie")
    DEBIAN_TRIXIE = ("debian", None, "trixie")
    DEBIAN_BOOKWORM = ("debian", "12", "bookworm")
    DEBIAN_BULLSEYE = ("debian", "11", "bullseye")
    DEBIAN_BUSTER = ("debian", "10", "buster")
    DEBIAN_STRETCH = ("debian", "9", "stretch")
    DEBIAN_JESSIE = ("debian", "8", "jessie")
    # https://releases.ubuntu.com/
    UBUNTU_JAMMY = ("ubuntu", "22.04", "jammy")
    UBUNTU_FOCAL = ("ubuntu", "20.04", "focal")
    UBUNTU_BIONIC = ("ubuntu", "18.04", "bionic")
    UBUNTU_TRUSTY = ("ubuntu", "14.04", "trusty")
    UBUNTU_XENIAL = ("ubuntu", "16.04", "xenial")
    UBUNTU_LUNAR = ("ubuntu", "23.04", "lunar")
    UBUNTU_MANTIC = ("ubuntu", "23.10", "mantic")
    UBUNTU_NOBLE = ("ubuntu", "24.04", "noble")
    # archlinux has not VERSION CODENAME but has VERSION ID and it not stable
    # since it's a rolling release, the VERSION ID will change
    # we specify (-1, -1) for those rolling system
    # just compare the ID
    ARCH = ("arch", ROLLING_SYSTEM, ROLLING_SYSTEM)

    def __eq__(self, value: object) -> bool:
        return self.value == value

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


def judge_os_in_systemlist(
    mversion: Tuple[Optional[str], Optional[str], Optional[str]],
    syslist: List[AllSystemInfo],
) -> Tuple[bool, Optional[AllSystemInfo]]:
    """Jude the os info (get from get_os_version()) is in the system list (list of AllSystemInfo).

    Args:
        mversion (Tuple[Optional[str], Optional[str], Optional[str]]): Tuple of (OS ID (NAME), OS VERSION ID, OS VERSION CODENAME)
        syslist (List[AllSystemInfo]): List of AllSystemInfo

    Returns:
        Tuple[bool, Optional[AllSystemInfo]]: return if os is in the list and the matched system
    """
    mysys_id, mysys_version_id, mysys_version_code = mversion
    # OS ID must be the key, so no OS ID, no other judgements
    if mysys_id is None:
        return (False, None)
    for osys in syslist:
        # all equal
        if osys == mversion:
            return (True, osys)
        sys_id, sys_version_id, sys_version_code = osys
        # for rolling system
        if (
            sys_version_code == ROLLING_SYSTEM
            and sys_version_id == ROLLING_SYSTEM
            and sys_id == mysys_id
        ):
            return (True, osys)
        # Next unmatched
        # The key OS ID is equal and at least one of the (OS VERSION ID / OS VERSION CODENAME) is equal
        if (sys_id == mysys_id) and (
            (sys_version_id == mysys_version_id and sys_version_id is not None)
            or (sys_version_code == mysys_version_code and sys_version_code is not None)
        ):
            return (True, osys)
    return (False, None)


@unique
class AllMirrorInfo(str, Enum):
    """All mirror info

    When add a new mirror, please register its name (key) here and use it as your mirror's MIRROR_NAME

    The info will use its value to compare / compute

    The unique will prevent duplicate value for security
    """

    UBUNTU = "ubuntu"
    LLVM_APT = "llvm_apt"
    DEBIAN = "debian"
    ARCHLINUX = "archlinux"

    def __eq__(self, value: object) -> bool:
        return self.value == value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


@unique
class AllPkgInfo(str, Enum):
    """All managed package info

    When add a new third package, please register its name (key) here and use it as your package's PKG_NAME

    The info will use its value to compare / compute

    The unique will prevent duplicate value for security
    """

    LINUXQQ = "linuxqq"

    def __eq__(self, value: object) -> bool:
        return self.value == value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


class ThirdPartySofts:
    PKG_NAME = ""

    @abstractmethod
    def get_package(self, wrapper_softs) -> Optional[Package]:
        raise NotImplementedError

    @abstractmethod
    def get_pkg_url(self) -> Optional[str]:
        raise NotImplementedError


class ThirdPartyMirrors:
    MIRROR_NAME = ""

    @abstractmethod
    def get_template(self) -> Optional[str]:
        raise NotImplementedError


def ask_for_mirror_options(
    options: Optional[Dict[Tuple[str, str], List[str]]],
    true_or_false: Optional[List[Tuple[str, str]]],
) -> List[Tuple[str, str]]:
    """Provide an api for each mirror asks for options

    Args:
        options (Optional[Dict[Tuple[str, str], List[str]]]): A dict, the key is (question key, question contents), the value is a list of choices
        true_or_false (Optional[List[Tuple[str, str]]]): A list of (question key, question contents), each choice is either True or False

    Returns:
        List[Tuple[str, str]]: return each question's answer by (question key, answer)
    """
    qa = Prompt()
    answer = []
    if options:
        for q, value in options.items():
            key, question = q
            k = qa.ask(prompt=question, choices=value)
            answer.append((key, k))
    if true_or_false:
        for q in true_or_false:
            key, question = q
            k = qa.ask(prompt=question, choices=["True", "False"])
            answer.append((key, k))
    return answer


def get_os_version() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """get os version

    OS ID must be the key.

    Returns:
        Tuple[Optional[str], Optional[str], Optional[str]]: return (OS ID (Name), OS Version ID, OS Version Codename)
    """
    try:
        # See https://www.freedesktop.org/software/systemd/man/latest/os-release.html
        # ID: A lower-case string (no spaces or other characters outside of 0–9, a–z, ".", "_" and "-") identifying the operating system, excluding any version information.
        # VERSION_ID: A lower-case string (mostly numeric, no spaces or other characters outside of 0–9, a–z, ".", "_" and "-") identifying the operating system version, excluding any OS name information or release code name.
        # VERSION_CODENAME: A lower-case string (no spaces or other characters outside of 0–9, a–z, ".", "_" and "-") identifying the operating system release code name, excluding any OS name information or release version. This field is optional and may not be implemented on all systems.
        if os.path.exists("/etc/os-release"):
            os_file = "/etc/os-release"
        elif os.path.exists("/usr/lib/os-release"):
            os_file = "/usr/lib/os-release"
        else:
            raise FileNotFoundError
        with open(os_file) as f:
            lines = f.readlines()
            info = {}
            for line in lines:
                key, value = line.rstrip().split("=")
                info[key] = value.strip('"')

            id = info.get("ID", None)
            if id is not None and len(id) == 0:
                id = None

            version = info.get("VERSION_ID", None)
            if version is not None and len(version) == 0:
                version = None

            version_codename = info.get("VERSION_CODENAME", None)
            if version_codename is not None and len(version_codename) == 0:
                version_codename = None

            return (id, version, version_codename)
    except FileNotFoundError as e:
        logger.warning("Not found os release file, could not detect os version!")
        return (None, None, None)
    except Exception as e:
        logger.warning(f"Unexpected error: {e}. Could not detect os version!")
        return (None, None, None)


def download_file(url: str, output_file: str):
    logger.debug(f"Start download file from {url} to {output_file}")
    response = requests.get(url)

    if response.status_code == 200:
        with open(output_file, "wb") as file:
            file.write(response.content)
        logger.debug(f"{url} downloaded successfully and saved as {output_file}")
    else:
        raise ConnectionError(
            f"Failed to download file {url}. Status code: {response.status_code}"
        )


imported = False


def import_libs(f: Callable):
    def wrap(*args, **kwargs):
        global imported
        if not imported:
            repos = global_configs["repo_path"]
            # dynamically import package
            for repo in repos:  # type: ignore
                repo_name = f"tinyget@{repo.split(os.sep)[-1]}"
                # search for third party packages
                pkgs_path = os.path.join(repo, "packages")
                if not os.path.exists(pkgs_path):
                    continue
                for module_name in os.listdir(pkgs_path):
                    pkg_full_p = os.path.join(pkgs_path, module_name)
                    pkg_f = os.path.join(pkg_full_p, "package.py")
                    if not os.path.exists(pkg_f):
                        continue
                    spec = importlib.util.spec_from_file_location(
                        f"{repo_name}:package:{module_name}", pkg_f
                    )
                    if spec is not None and spec.loader is not None:
                        module = importlib.util.module_from_spec(spec=spec)
                        spec.loader.exec_module(module=module)
                # search for the mirror template
                mirrors_path = os.path.join(repo, "mirrors/templates")
                if not os.path.exists(mirrors_path):
                    continue
                for mirror_template in os.listdir(mirrors_path):
                    mirror_template_path = os.path.join(mirrors_path, mirror_template)
                    spec = importlib.util.spec_from_file_location(
                        f"{repo_name}:mirrortemp:{mirror_template.rstrip('.py')}",
                        mirror_template_path,
                    )
                    if spec is not None and spec.loader is not None:
                        module = importlib.util.module_from_spec(spec=spec)
                        spec.loader.exec_module(module=module)
            imported = True
        return f(*args, **kwargs)

    return wrap


@import_libs
def get_pkg_url(softs: str = "") -> Optional[str]:
    clss = ThirdPartySofts.__subclasses__()
    for cls in clss:
        instance = cls()
        # find match softwares
        if (softs != "" and softs == cls.PKG_NAME) or (softs == ""):
            url = instance.get_pkg_url()
            if url is not None:
                return url
    return None


@import_libs
def get_third_party_packages(
    softs: str = "", wrapper_softs: Optional[List[Package]] = []
) -> List[Package]:
    package_list = []
    clss = ThirdPartySofts.__subclasses__()
    for cls in clss:
        in_repo = cls.__module__.split(":")[0]
        instance = cls()
        # find match softwares
        if softs != "":
            search_regex = re.compile(softs)
            match = search_regex.search(cls.PKG_NAME)
            if match:
                pkg = instance.get_package(wrapper_softs=wrapper_softs)
                if pkg is not None:
                    pkg.remain["repo"] = [in_repo]
                    package_list.append(pkg)
        else:
            pkg = instance.get_package(wrapper_softs=wrapper_softs)
            if pkg is not None:
                pkg.remain["repo"] = [in_repo]
                package_list.append(pkg)
    return package_list


@import_libs
def get_third_party_mirror_template(mirror: str) -> Optional[str]:
    clss = ThirdPartyMirrors.__subclasses__()
    for cls in clss:
        instance = cls()
        # find match mirror
        if cls.MIRROR_NAME != mirror:
            continue
        temp = instance.get_template()
        if temp is not None:
            return temp
        else:
            return None
    return None


@import_libs
def get_third_party_mirrors() -> Dict[str, List[str]]:
    clss = ThirdPartyMirrors.__subclasses__()
    mirrors = defaultdict(lambda: [])
    for cls in clss:
        in_repo = cls.__module__.split(":")[0]
        mirrors[in_repo].append(cls.MIRROR_NAME)
    return mirrors
