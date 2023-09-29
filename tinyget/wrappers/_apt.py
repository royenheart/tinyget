import re
from .pkg_manager import PackageManagerBase
from ..interact import execute_command
from ..package import Package, ManagerType
from typing import Union, List


class APT(PackageManagerBase):
    def __init__(self):
        pass

    def list_packages(
        self, only_installed: bool = False, only_upgradable: bool = False
    ):
        """
        Returns a list of packages based on the specified criteria.

        Args:
            only_installed (bool, optional): If True, only installed packages will be returned. Defaults to False.
            only_upgradable (bool, optional): If True, only upgradable packages will be returned. Defaults to False.

        Returns:
            List[Package]: A list of Package objects representing the packages that match the specified criteria.
        """
        args = ["apt", "list", "-v"]
        content, stderr = execute_command(args, {"DEBIAN_FRONTEND": "noninteractive"})

        blocks = content.split("\n\n")

        package_name_regex = r"(?P<package_name>.+)"
        repo_regex = r"(?P<repo>.+)"
        version_regex = r"(?P<version>.+)"
        architecture_regex = r"(?P<architecture>.+)"
        install_status_regex = r"(?P<install_status>.+)"
        description_regex = r"(?P<description>.+)"
        installed_pattern = f"^{package_name_regex}/{repo_regex}\s{version_regex}\s{architecture_regex}\s\[{install_status_regex}\]\n  {description_regex}$"
        uninstalled_pattern = f"^{package_name_regex}/{repo_regex}\s{version_regex}\s{architecture_regex}\n  {description_regex}$"
        installed_regex = re.compile(installed_pattern, re.MULTILINE)
        uninstalled_regex = re.compile(uninstalled_pattern, re.MULTILINE)

        packages = []

        for block in blocks:
            match = installed_regex.search(block)
            if match:
                installed_status = match.group("install_status").split(",")
                installed = False
                automatically_installed = False
                upgradable = False
                available_version = None
                for status in installed_status:
                    if "installed" in status:
                        installed = True
                    if "auto" in status:
                        automatically_installed = True
                    if "upgradable" in status:
                        upgradable = True
                        installed = True
                        available_version = status[: -len("upgradable from: ")]
                package = Package(
                    package_type=ManagerType.apt,
                    package_name=match.group("package_name"),
                    architecture=match.group("architecture"),
                    description=match.group("description"),
                    version=match.group("version"),
                    installed=installed,
                    automatically_installed=automatically_installed,
                    upgradable=upgradable,
                    available_version=available_version,
                    remain={"repo": match.group("repo").split(",")},
                )
                packages.append(package)
                continue

            match = uninstalled_regex.search(block)
            if match:
                package = Package(
                    package_type=ManagerType.apt,
                    package_name=match.group("package_name"),
                    architecture=match.group("architecture"),
                    description=match.group("description"),
                    version=match.group("version"),
                    installed=False,
                    automatically_installed=False,
                    upgradable=False,
                    available_version=None,
                    remain={"repo": match.group("repo").split(",")},
                )
                packages.append(package)
                continue
        if only_upgradable:
            packages = [package for package in packages if package.upgradable]
        if only_installed:
            packages = [package for package in packages if package.installed]
        return packages

    def install(self, package: Union[List[str], str]):
        """
        Install one or more packages.

        Args:
            package (Union[List[str], str]): The package or list of packages to install.

        Returns:
            None
        """
        if isinstance(package, str):
            package_list = [package]
        else:
            package_list = package

        args = ["apt", "install", "-y", *package_list]

    def update(self):
        args = ["apt", "update", "-y"]
        return execute_command(args)


if __name__ == "__main__":
    pass

    # upgradable = 0
    # installed = 0
    # auto = 0
    # total = 0
    # for package in packages:
    #     total += 1
    #     if package.installed:
    #         installed += 1
    #     if package.automatically_installed:
    #         auto += 1
    #     if package.upgradable:
    #         upgradable += 1

    # print(
    #     f"total: {total}, installed: {installed}, auto: {auto}, upgradable: {upgradable}"
    # )
