import re
from .pkg_manager import PackageManagerBase
from ..interact import execute_command
from ..package import Package, ManagerType
from typing import Union, List, Dict
import subprocess


def get_installed_info(package_name: Union[List[str], str]) -> List[dict]:
    if isinstance(package_name, str):
        package_name_list = [package_name]
    elif isinstance(package_name, list):
        package_name_list = package_name
    else:
        raise ValueError("package_name must be a string or a list of strings")
    args = ["pacman", "-Qi", *package_name_list]
    stdout, stderr = execute_command(args)
    if "was not found" in stderr and "error" in stderr:
        raise Exception(f"Package {package_name} not found in local db")

    blocks = stdout.split("\n\n")
    info_list = []
    for block in blocks:
        info = {}
        lines = block.split("\n")
        for line in lines:
            if line.startswith("Name"):
                info["name"] = line[line.find(":") + 1 :].strip()
            if line.startswith("Version"):
                info["version"] = line[line.find(":") + 1 :].strip()
            if line.startswith("Description"):
                info["description"] = line[line.find(":") + 1 :].strip()
            if line.startswith("Architecture"):
                info["architecture"] = line[line.find(":") + 1 :].strip()
            if line.startswith("Install Reason"):
                info["reason"] = line[line.find(":") + 1 :].strip()

        keys_needed = ["name", "version", "description", "architecture", "reason"]
        if not all(key in info for key in keys_needed):
            continue
        info_list.append(info)
    return info_list


def get_available_info(package_name: Union[List[str], str]) -> List[dict]:
    if isinstance(package_name, str):
        package_name_list = [package_name]
    elif isinstance(package_name, list):
        package_name_list = package_name
    else:
        raise ValueError("package_name must be a string or a list of strings")
    args = ["pacman", "-Si", *package_name_list]
    stdout, stderr = execute_command(args)
    if "was not found" in stderr and "error" in stderr:
        raise Exception(f"Package {package_name} not found in source")

    blocks = stdout.split("\n\n")
    info_list = []
    for block in blocks:
        info = {}
        lines = block.split("\n")
        for line in lines:
            if line.startswith("Name"):
                info["name"] = line[line.find(":") + 1 :].strip()
            if line.startswith("Version"):
                info["version"] = line[line.find(":") + 1 :].strip()
            if line.startswith("Description"):
                info["description"] = line[line.find(":") + 1 :].strip()
            if line.startswith("Architecture"):
                info["architecture"] = line[line.find(":") + 1 :].strip()
            if line.startswith("Replaces"):
                info["replaces"] = line[line.find(":") + 1 :].strip()
            if line.startswith("Repository"):
                info["repo"] = line[line.find(":") + 1 :].strip()
        keys_needed = [
            "name",
            "version",
            "description",
            "architecture",
            "replaces",
            "repo",
        ]
        if not all(key in info for key in keys_needed):
            continue
        info_list.append(info)
    return info_list


def get_all_package_name() -> List[str]:
    args = ["pacman", "-Ssq"]
    stdout, stderr = execute_command(args)
    packages = [
        package_name for package_name in stdout.split("\n") if package_name != ""
    ]
    return packages


def get_all_installed_package_name() -> List[str]:
    args = ["pacman", "-Qq"]
    stdout, stderr = execute_command(args)
    packages = [
        package_name for package_name in stdout.split("\n") if package_name != ""
    ]
    return packages


def get_upgradable() -> Dict[str, str]:
    args = ["pacman", "-Qu"]
    stdout, stderr = execute_command(args)
    regex = re.compile(
        r"^(?P<package_name>.+)\s(?P<version>.+)\s->\s(?P<available_version>.+)$"
    )
    upgradable = {}
    for line in stdout.split("\n"):
        match = regex.match(line)
        if match:
            package_name = match.group("package_name")
            available_version = match.group("available_version")
            upgradable[package_name] = available_version
    return upgradable


def get_all_packages() -> List[Package]:
    installed_packages = get_all_installed_package_name()
    packages = get_all_package_name()
    installed_info = get_installed_info(installed_packages)
    package_info = get_available_info(packages)

    installed_info_dict = {info["name"]: info for info in installed_info}
    package_info_dict = {info["name"]: info for info in package_info}

    upgradable_dict = get_upgradable()

    packages = []
    for name, info in package_info_dict.items():
        if name in installed_info_dict:
            installed = True
            automatically_installed = (
                "Installed as a dependency" in installed_info_dict[name]["reason"]
            )
        else:
            installed = False
            automatically_installed = False

        if name in upgradable_dict:
            upgradable = True
            available_version = upgradable_dict[name]
        else:
            upgradable = False
            available_version = None

        remain = {"repo": [info["repo"]]}
        package = Package(
            package_type=ManagerType.pacman,
            package_name=info["name"],
            architecture=info["architecture"],
            description=info["description"],
            version=info["version"],
            installed=installed,
            automatically_installed=automatically_installed,
            upgradable=upgradable,
            available_version=available_version,
            remain=remain,
        )
        packages.append(package)
    return packages


class PACMAN(PackageManagerBase):
    def __init__(self):
        pass

    def list_packages(self, only_installed, only_upgradable) -> List[Package]:
        packages = get_all_packages()
        # Process filter
        if only_installed:
            packages = [package for package in packages if package.installed]

        if only_upgradable:
            packages = [package for package in packages if package.upgradable]

        return packages


if __name__ == "__main__":
    upgradable = get_upgradable()
    print(upgradable)
