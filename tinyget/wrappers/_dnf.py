import re
from .pkg_manager import PackageManagerBase
from ..interact import execute_command, just_execute
from ..package import Package, ManagerType
from typing import Union, List


def get_unique_id(package_info: dict):
    """
    Generates a unique ID based on the given package information.

    Parameters:
    - package_info (dict): A dictionary containing the package information. It should have the following keys:
        - name (str): The name of the package.
        - version (str): The version of the package.
        - release (str): The release of the package.
        - arch (str): The architecture of the package.
        - epoch (str): The epoch of the package.

    Returns:
    - uid (str): The generated unique ID based on the package information. It is in the format "{name}-{arch}".

    Note:
    - If the package information does not contain a value for "epoch", the epoch part will not be included in the generated unique ID.
    """
    # uid = f"{package_info['name']}-{package_info['version']}-{package_info['release']}-{package_info['arch']}"
    # if package_info["epoch"] != "":
    #     uid += f"-{package_info['epoch']}"
    # return uid
    uid = f"{package_info['name']}-{package_info['arch']}"
    return uid


def repoquery(flags: Union[List[str], str] = []):
    """
    Query the repository for package information.

    Args:
        flags (Union[List[str], str], optional): A list of flags or a single flag as a string. Defaults to [].

    Raises:
        ValueError: If `flags` is neither a string nor a list.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing package information. Each dictionary contains the following keys:
            - 'name': The name of the package.
            - 'version': The version of the package.
            - 'release': The release version of the package.
            - 'epoch': The epoch of the package.
            - 'arch': The architecture of the package.
            - 'reponame': The name of the repository.
            - 'summary': A summary of the package.
            - 'reason': The reason for the package being installed.
            - 'installtime': The installation time of the package.
    """
    query_tags = [
        "name",
        "version",
        "release",
        "epoch",
        "arch",
        "reponame",
        "summary",
        "reason",
        "installtime",
    ]

    if isinstance(flags, str):
        flags = flags.split()
    elif isinstance(flags, list):
        pass
    else:
        raise ValueError("flags must be a string or a list")
    format_tags = [f"%{{{tag}}}" for tag in query_tags]
    format_string = "^^^"
    format_string += "|^".join(format_tags)
    format_string += "$$$"
    args = ["dnf", "repoquery", *flags, "--queryformat", format_string]

    stdout, stderr = execute_command(args)
    regex = re.compile(r"\^\^\^(?P<line>.+)\$\$\$")
    matches = regex.finditer(stdout)
    lines = []
    for match in matches:
        lines.append(match.groupdict()["line"])
    packages = []
    for line in lines:
        line = line.strip()
        info_list = line.split("|^")
        if len(info_list) < len(query_tags):
            continue
        package_info = {tag: info for tag, info in zip(query_tags, info_list)}
        packages.append(package_info)

    info_set = set([p["reason"] for p in packages])
    return packages


def check_update():
    """
    Check for available updates using the 'dnf check-update' command.

    Returns:
        A list of dictionaries containing information about the available updates.
        Each dictionary has the following keys:
        - name: the name of the package
        - version: the new version of the package
        - arch: the architecture of the package
        - repo: the repository where the package is located
    """
    args = ["dnf", "check-update"]
    stdout, stderr = execute_command(args)
    lines = stdout.split("\n")
    upgradable = []
    for line in lines:
        line = line.strip()
        blocks = line.split()
        if len(blocks) != 3:
            continue
        split_idx = blocks[0].rfind(".")
        if split_idx == -1:
            continue
        name = blocks[0][:split_idx]
        arch = blocks[0][split_idx + 1 :]
        version = blocks[1]
        repo = blocks[2]
        upgradable.append(
            {"name": name, "version": version, "arch": arch, "repo": repo}
        )
    return upgradable


def get_all_packages() -> List[Package]:
    """
    Retrieves information about all packages.

    Returns:
        List[Package]: A list of Package objects representing the packages.
    """
    package_info_list = repoquery()
    package_info_dict = {}
    for p in package_info_list:
        uid = get_unique_id(p)
        if (
            uid in package_info_dict
            and p["version"] > package_info_dict[uid]["version"]
        ) or uid not in package_info_dict:
            package_info_dict[uid] = p

    # Query installed packages
    installed_package_info_list = repoquery(flags="--installed")
    for info in installed_package_info_list:
        uid = get_unique_id(info)
        new_info = package_info_dict[uid]
        new_info["reason"] = info["reason"]
        new_info["installtime"] = info["installtime"]
        package_info_dict[uid] = new_info

    # Query upgradable packages
    upgradable_package_info_list = check_update()
    upgradable_dict = {}
    for info in upgradable_package_info_list:
        uid = get_unique_id(info)
        upgradable_dict[uid] = info["version"]

    # Convert to Package structure
    package_list = []
    for uid, info in package_info_dict.items():
        upgradable = uid in upgradable_dict.keys()
        available_version = upgradable_dict.get(uid)
        package = Package(
            package_type=ManagerType.dnf,
            package_name=info["name"],
            architecture=info["arch"],
            description=info["summary"],
            version=info["version"],
            installed=(info["installtime"] != ""),
            automatically_installed="dependency" in info["reason"],
            upgradable=upgradable,
            available_version=available_version,
            remain={"repo": [info["reponame"]]},
        )
        package_list.append(package)
    return package_list


class DNF(PackageManagerBase):
    def __init__(self):
        pass

    def list_packages(self, only_installed: bool, only_upgradable: bool):
        """
        Retrieves a list of packages based on the specified filters.

        Args:
            only_installed (bool): If True, only return installed packages.
            only_upgradable (bool): If True, only return upgradable packages.

        Returns:
            List[Package]: A list of packages that match the specified filters.
        """
        package_list = get_all_packages()
        # Process filter
        if only_installed:
            package_list = [p for p in package_list if p.installed]
        if only_upgradable:
            package_list = [p for p in package_list if p.upgradable]
        return package_list

    def update(self):
        """
        Updates the system by checking for and applying available updates.

        :return: The output of the command executed to update the system.
        """
        args = ["dnf", "check-update", "-y"]
        return execute_command(args)

    def upgrade(self):
        """
        Upgrade the system by running the `dnf upgrade` command with the specified arguments.

        :return: The output of the `execute_command` function.
        """
        args = ["dnf", "upgrade", "--refresh", "-y"]
        return execute_command(args)

    def install(self, packages: List[str]):
        """
        Installs the specified packages using the DNF package manager.

        Parameters:
            packages (List[str]): A list of package names to install.

        Returns:
            The return value of the execute_command function.
        """
        args = ["dnf", "install", "-y", *packages]
        return execute_command(args)

    def uninstall(self, packages: List[str]):
        """
        Uninstalls a list of packages.

        Parameters:
            packages (List[str]): A list of package names to be uninstalled.

        Returns:
            None
        """
        args = ["dnf", "remove", "-y", *packages]
        return execute_command(args)

    def search(self, package: str):
        """
        Searches for a package using the DNF package manager.

        Parameters:
            package (str): The name of the package to search for.

        Returns:
            The return value of the execute_command function.
        """
        args = ["dnf", "search", package]
        just_execute(args)


if __name__ == "__main__":
    dnf = DNF()
    stdout, stderr = dnf.install(["wget"])
