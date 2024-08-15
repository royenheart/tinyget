"""
Parse third-party softwares' configuration and provide information
"""

from abc import abstractmethod
import importlib
import importlib.util
import re
from typing import Callable, List, Optional
from tinyget.package import Package
from tinyget.globals import global_configs
from tinyget.common_utils import logger
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
                pkgs_path = os.path.join(repo, "packages")
                if not os.path.exists(pkgs_path):
                    continue
                for module_name in os.listdir(pkgs_path):
                    pkg_full_p = os.path.join(pkgs_path, module_name)
                    pkg_f = os.path.join(pkg_full_p, "package.py")
                    if not os.path.exists(pkg_f):
                        continue
                    spec = importlib.util.spec_from_file_location(
                        f"{repo_name}:{module_name}", pkg_f
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
