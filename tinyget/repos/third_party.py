"""
Parse third-party softwares' configuration and provide information
"""

from abc import abstractmethod
from collections import defaultdict
import importlib
import importlib.util
import re
from typing import Callable, Dict, List, Optional, Tuple
from tinyget.package import Package
from tinyget.globals import global_configs
from tinyget.common_utils import logger
from rich.prompt import Prompt
import os
import requests


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

    Returns:
        Tuple[Optional[str], Optional[str], Optional[str]]: return (OS Name, OS Version ID, OS Version Codename)
    """
    try:
        with open("/etc/os-release") as f:
            lines = f.readlines()
            info = {}
            for line in lines:
                key, value = line.rstrip().split("=")
                info[key] = value.strip('"')

            name = info.get("ID", None)
            version = info.get("VERSION_ID", None)
            version_codename = info.get("VERSION_CODENAME", None)
            return (name, version, version_codename)
    except FileNotFoundError as e:
        logger.warning("Not found /etc/os-release, could not detect os version!")
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
            for repo in repos:
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
