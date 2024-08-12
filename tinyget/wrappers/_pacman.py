import re
from .pkg_manager import PackageManagerBase
from ..interact import execute_command, CommandExecutionError, just_execute
from ..package import Package, ManagerType
from typing import Union, List, Dict


def get_installed_info(package_name: Union[List[str], str]) -> List[dict]:
    """
    Retrieves information about the installed packages with the given package name(s).

    Parameters:
        package_name (Union[List[str], str]): The name(s) of the package(s) to retrieve information for.
            It can either be a single package name as a string or a list of package names.

    Returns:
        List[dict]: A list of dictionaries containing information about each installed package. Each dictionary
            contains the following keys:
            - 'name': The name of the package.
            - 'version': The version of the package.
            - 'description': A description of the package.
            - 'architecture': The architecture of the package.
            - 'reason': The reason for the package installation.

    Raises:
        ValueError: If the package_name is neither a string nor a list of strings.
        Exception: If the package is not found in the local database.
    """
    if isinstance(package_name, str):
        package_name_list = [package_name]
    elif isinstance(package_name, list):
        package_name_list = package_name
    else:
        raise ValueError("package_name must be a string or a list of strings")
    args = ["pacman", "-Qi", "--noconfirm", *package_name_list]
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
    """
    Retrieves available information for a given package or list of packages.

    Args:
        package_name (Union[List[str], str]): The name of the package or a list of package names.

    Returns:
        List[dict]: A list of dictionaries containing the available information for each package. Each dictionary contains the following keys:
            - name (str): The name of the package.
            - version (str): The version of the package.
            - description (str): A description of the package.
            - architecture (str): The architecture of the package.
            - replaces (str): The package that this package replaces.
            - repo (str): The repository where the package is located.

    Raises:
        ValueError: If `package_name` is neither a string nor a list of strings.
        Exception: If the package is not found in the source.
    """
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
    """
    Retrieves a list of all package names.

    Returns:
        A list of strings containing the names of all packages.
    """
    args = ["pacman", "-Ssq"]
    stdout, stderr = execute_command(args)
    packages = [
        package_name for package_name in stdout.split("\n") if package_name != ""
    ]
    return packages


def get_all_installed_package_name() -> List[str]:
    """
    Get the names of all installed packages.

    :return: A list of strings representing the names of installed packages.
    :rtype: List[str]
    """
    args = ["pacman", "-Qq"]
    stdout, stderr = execute_command(args)
    packages = [
        package_name for package_name in stdout.split("\n") if package_name != ""
    ]
    return packages


def get_upgradable() -> Dict[str, str]:
    """
    Retrieves a dictionary of upgradable packages and their available versions.

    Returns:
        A dictionary where the keys are the package names and the values are the available versions.
    """
    args = ["pacman", "-Qu"]
    try:
        stdout, stderr = execute_command(args)
    except CommandExecutionError as e:
        # If there is no upgradable packages, pacman returns nonzero, which is not an error
        # So we need to check stderr
        if e.stderr == "":
            stdout = e.stdout
            stderr = e.stderr
        else:
            raise
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
    """
    Retrieves information about all packages.

    Returns:
        List[Package]: A list of Package objects representing the information
        about each package.
    """
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
        """
        Retrieve a list of packages based on filter criteria.

        Args:
            only_installed (bool): If True, only return installed packages.
            only_upgradable (bool): If True, only return upgradable packages.

        Returns:
            List[Package]: A list of packages that match the filter criteria.
        """
        packages = get_all_packages()
        # Process filter
        if only_installed:
            packages = [package for package in packages if package.installed]

        if only_upgradable:
            packages = [package for package in packages if package.upgradable]

        return packages

    def update(self):
        """
        Updates the object with the latest information by executing the command "pacman -Sy --noconfirm" and returns the result.

        :return: The result of executing the command.
        """
        args = ["pacman", "-Sy", "--noconfirm"]
        return execute_command(args)

    def upgrade(self):
        """
        Upgrade the system by executing the command "pacman -Syu --noconfirm".

        :return: The result of executing the command.
        """
        args = ["pacman", "-Syu", "--noconfirm"]
        return execute_command(args)

    def install(self, packages: List[str]):
        """
        Installs the specified packages using the `pacman` package manager.

        Args:
            packages (List[str]): A list of package names to be installed.

        Returns:
            None
        """
        args = ["pacman", "-S", "--noconfirm", *packages]
        return execute_command(args)

    def uninstall(self, packages: List[str]):
        """
        Uninstalls the specified packages.

        Args:
            packages (List[str]): A list of package names to uninstall.

        Returns:
            The result of the execute_command function.
        """
        args = ["pacman", "-Rns", "--noconfirm", *packages]
        return execute_command(args)

    def search(self, package: str):
        """
        Searches for a package in the source.

        Args:
            package (str): The name of the package to search for.

        Returns:
            The result of the execute_command function.
        """
        args = ["pacman", "-Ss", package]
        just_execute(args)


if __name__ == "__main__":
    pacman = PACMAN()
    stdout, stderr = pacman.install(["wget"])
    print(stdout)
    print(stderr)
