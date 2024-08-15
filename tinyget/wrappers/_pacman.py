import os
import re
import traceback
from tinyget.common_utils import logger
from tinyget.globals import ERROR_HANDLED, ERROR_UNKNOWN
from tinyget.interact.process import CommandExecutionError
from rich.console import Console
from rich.panel import Panel

from tinyget.repos.third_party import get_pkg_url, get_third_party_packages
from .pkg_manager import PackageManagerBase
from ..interact import execute_command as _execute_command
from ..package import Package, ManagerType
from typing import Optional, Union, List, Dict
from tinyget.i18n import load_translation
from tinyget.interact import try_to_get_ai_helper

aihelper = try_to_get_ai_helper()

_ = load_translation("_pacman")


def execute_pacman_command(args: List[str], timeout: Optional[float] = None):
    """
    Executes pacman with the given arguments and optional timeout.

    Parameters:
        args (List[str]): The arguments to pass to the pacman. Should be a list of strings.
        timeout (int, optional): The maximum time to wait for the pacman to complete, in seconds. Defaults to None.

    Returns:
        The result of executing the dnf.

    """
    envp = {}
    args.insert(0, "pacman")
    out, err, retcode = _execute_command(args, envp, timeout)
    if retcode == 0:
        # Operation successful
        return (out, err, retcode)
    else:
        raise CommandExecutionError(
            # 0: args the operation, 1: envp the execution environment
            message=_("Pacman Error during operation {0} with {1}").format(args, envp),
            args=list(args),
            envp=envp,
            stdout=out,
            stderr=err,
        )


def execute_makepkg_command(
    args: List[str], timeout: Optional[float] = None, cwd: Optional[str] = None
):
    """
    Executes pacman with the given arguments and optional timeout.

    Parameters:
        args (List[str]): The arguments to pass to the pacman. Should be a list of strings.
        timeout (int, optional): The maximum time to wait for the pacman to complete, in seconds. Defaults to None.

    Returns:
        The result of executing the dnf.

    """
    envp = {}
    args.insert(0, "makepkg")
    out, err, retcode = _execute_command(args, envp, timeout, cwd)
    if retcode == 0:
        # Operation successful
        return (out, err, retcode)
    else:
        raise CommandExecutionError(
            message=f"makepkg command error during operation {args} with {envp}",
            args=list(args),
            envp=envp,
            stdout=out,
            stderr=err,
        )


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
        raise ValueError(_("package_name must be a string or a list of strings"))
    args = ["-Qi", "--noconfirm", *package_name_list]
    try:
        stdout, stderr, retcode = execute_pacman_command(args)
    except CommandExecutionError as e:
        stderr = e.stderr
        if _("was not found") in stderr and _("error") in stderr:
            logger.debug(f"Packages not found in local db: {stderr}")
            stdout = e.stdout
        else:
            raise

    blocks = stdout.split("\n\n")
    info_list = []
    for block in blocks:
        info = {}
        lines = block.split("\n")
        for line in lines:
            if line.startswith(_("Name")):
                info["name"] = line[line.find(":") + 1 :].strip()
            if line.startswith(_("Version")):
                info["version"] = line[line.find(":") + 1 :].strip()
            if line.startswith(_("Description")):
                info["description"] = line[line.find(":") + 1 :].strip()
            if line.startswith(_("Architecture")):
                info["architecture"] = line[line.find(":") + 1 :].strip()
            if line.startswith(_("Install Reason")):
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
        raise ValueError(_("package_name must be a string or a list of strings"))
    args = ["-Si", *package_name_list]
    try:
        stdout, stderr, retcode = execute_pacman_command(args)
    except CommandExecutionError as e:
        stderr = e.stderr
        if _("was not found") in stderr and _("error") in stderr:
            logger.debug(f"Packages not found in source: {stderr}")
            stdout = e.stdout
        else:
            raise

    blocks = stdout.split("\n\n")
    info_list = []
    for block in blocks:
        info = {}
        lines = block.split("\n")
        for line in lines:
            if line.startswith(_("Name")):
                info["name"] = line[line.find(":") + 1 :].strip()
            if line.startswith(_("Version")):
                info["version"] = line[line.find(":") + 1 :].strip()
            if line.startswith(_("Description")):
                info["description"] = line[line.find(":") + 1 :].strip()
            if line.startswith(_("Architecture")):
                info["architecture"] = line[line.find(":") + 1 :].strip()
            if line.startswith(_("Replaces")):
                info["replaces"] = line[line.find(":") + 1 :].strip()
            if line.startswith(_("Repository")):
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
    args = ["-Ssq"]
    stdout, stderr, retcode = execute_pacman_command(args)
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
    args = ["-Qq"]
    stdout, stderr, retcode = execute_pacman_command(args)
    packages = [
        package_name for package_name in stdout.split("\n") if package_name != ""
    ]
    return packages


def get_upgradable(package_name: Union[List[str], str] = []) -> Dict[str, str]:
    """
    Retrieves a dictionary of upgradable packages and their available versions.

    Args:
        package_name (Union[List[str], str]): The name of the package or a list of package names.

    Returns:
        A dictionary where the keys are the package names and the values are the available versions.
    """
    args = ["-Qu", *package_name]
    try:
        stdout, stderr, retcode = execute_pacman_command(args)
    except CommandExecutionError as e:
        # If there is no upgradable packages, pacman returns nonzero, which is not an error
        stderr = e.stderr
        if _("was not found") in stderr and _("error") in stderr:
            logger.debug(
                f"Packages not in local db, so can't determine upgradable: {stderr}"
            )
            stdout = e.stdout
        elif stderr == "":
            logger.debug("No packages found can be upgraded")
            stdout = e.stdout
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


def get_all_packages(enable_third_party: bool = True) -> List[Package]:
    """
    Retrieves information about all packages.

    Parameters:
        enable_third_party (bool): Enable third party softwares.

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
                _("Installed as a dependency") in installed_info_dict[name]["reason"]
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

    # Append third party softs
    if enable_third_party:
        packages.extend(get_third_party_packages(wrapper_softs=packages))

    return packages


class PACMAN(PackageManagerBase):
    def __init__(self):
        pass

    def list_packages(
        self, only_installed, only_upgradable, enable_third_party: bool = True
    ) -> List[Package]:
        """
        Retrieve a list of packages based on filter criteria.

        Args:
            only_installed (bool): If True, only return installed packages.
            only_upgradable (bool): If True, only return upgradable packages.

        Returns:
            List[Package]: A list of packages that match the filter criteria.
        """
        console = Console()
        try:
            packages = get_all_packages(enable_third_party=enable_third_party)
        except CommandExecutionError as e:
            console.print(
                Panel(
                    # 0: e.stdout the Output. 1: e.stderr the Error.
                    _("Output: {0}\nError: {1}").format(e.stdout, e.stderr),
                    border_style="red",
                    title=_("Operation Failed"),
                )
            )
            logger.debug(f"{traceback.format_exc()}")
            return []
        except Exception as e:
            console.print(
                Panel(f"{e}", border_style="red", title=_("Operation Failed"))
            )
            logger.debug(f"{traceback.format_exc()}")
            return []

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
        args = ["-Sy", "--noconfirm"]
        console = Console()
        try:
            result = execute_pacman_command(args)
        except CommandExecutionError as e:
            if (
                _("error: you cannot perform this operation unless you are root.")
                in e.stderr
            ):
                console.print(
                    Panel(
                        _(
                            "Run tinyget in superuser privileges (using sudo / sudo-rs or configuring one admin user and group)"
                        ),
                        border_style="red",
                        title=_("Operation Failed"),
                    )
                )
            else:
                console.print(
                    Panel(
                        # 0: e.stdout the Output. 1: e.stderr the Error.
                        _("Output: {0}\nError: {1}").format(e.stdout, e.stderr),
                        border_style="red",
                        title=_("Operation Failed"),
                    )
                )
            logger.debug(f"{traceback.format_exc()}")
            return (None, None, ERROR_HANDLED)
        except Exception as e:
            console.print(
                Panel(
                    f"{e}",
                    border_style="red",
                    title=_("Operation Failed"),
                )
            )
            logger.debug(f"{traceback.format_exc()}")
            return (None, None, ERROR_UNKNOWN)
        return result

    def upgrade(self):
        """
        Upgrade the system by executing the command "pacman -Syu --noconfirm".

        :return: The result of executing the command.
        """
        args = ["-Syu", "--noconfirm"]
        console = Console()
        try:
            result = execute_pacman_command(args)
        except CommandExecutionError as e:
            if (
                _("error: you cannot perform this operation unless you are root.")
                in e.stderr
            ):
                console.print(
                    Panel(
                        _(
                            "Run tinyget in superuser privileges (using sudo / sudo-rs or configuring one admin user and group)"
                        ),
                        border_style="red",
                        title=_("Operation Failed"),
                    )
                )
            else:
                console.print(
                    Panel(
                        # 0: e.stdout the Output. 1: e.stderr the Error.
                        _("Output: {0}\nError: {1}").format(e.stdout, e.stderr),
                        border_style="red",
                        title=_("Operation Failed"),
                    )
                )
            logger.debug(f"{traceback.format_exc()}")
            return (None, None, ERROR_HANDLED)
        except Exception as e:
            console.print(
                Panel(
                    f"{e}",
                    border_style="red",
                    title=_("Operation Failed"),
                )
            )
            logger.debug(f"{traceback.format_exc()}")
            return (None, None, ERROR_UNKNOWN)
        return result

    def install(self, packages: List[str]):
        """
        Installs the specified packages using the `pacman` package manager.

        Args:
            packages (List[str]): A list of package names to be installed.

        Returns:
            None
        """
        packages = list(packages)
        logger.debug(f"Will install packages: {packages}")
        # replace third party softs' url
        for i, pkg in enumerate(packages):
            r = get_pkg_url(softs=pkg)
            if r is not None:
                packages[i] = r
        args = ["-S", "--noconfirm", *packages]
        console = Console()
        try:
            result = execute_pacman_command(args)
        except CommandExecutionError as e:
            if (
                _("error: you cannot perform this operation unless you are root.")
                in e.stderr
            ):
                console.print(
                    Panel(
                        _(
                            "Run tinyget in superuser privileges (using sudo / sudo-rs or configuring one admin user and group)"
                        ),
                        border_style="red",
                        title=_("Operation Failed"),
                    )
                )
            else:
                console.print(
                    Panel(
                        # 0: e.stdout the Output. 1: e.stderr the Error.
                        _("Output: {0}\nError: {1}").format(e.stdout, e.stderr),
                        border_style="red",
                        title=_("Operation Failed"),
                    )
                )
            logger.debug(f"{traceback.format_exc()}")
            if aihelper is None:
                console.print(
                    Panel(
                        _(
                            "AI Helper not started, will enabled after configured by 'tinyget config'/'tinyget ui'"
                        ),
                        border_style="bright_black",
                    )
                )
            else:
                with console.status(
                    "[bold green] {}".format(
                        _("AI Helper started, getting command advise")
                    ),
                    spinner="bouncingBar",
                ) as status:
                    recommendation = aihelper.fix_command(args, e.stdout, e.stderr)
                console.print(
                    Panel(
                        recommendation,
                        border_style="green",
                        title=_("Advise from AI Helper"),
                    )
                )
            return (None, None, ERROR_HANDLED)
        except Exception as e:
            console.print(
                Panel(
                    f"{e}",
                    border_style="red",
                    title=_("Operation Failed"),
                )
            )
            logger.debug(f"{traceback.format_exc()}")
            return (None, None, ERROR_UNKNOWN)
        return result

    def uninstall(self, packages: List[str]):
        """
        Uninstalls the specified packages.

        Args:
            packages (List[str]): A list of package names to uninstall.

        Returns:
            The result of the execute_pacman_command function.
        """
        args = ["-Rns", "--noconfirm", *packages]
        console = Console()
        try:
            result = execute_pacman_command(args)
        except CommandExecutionError as e:
            if (
                _("error: you cannot perform this operation unless you are root.")
                in e.stderr
            ):
                console.print(
                    Panel(
                        _(
                            "Run tinyget in superuser privileges (using sudo / sudo-rs or configuring one admin user and group)"
                        ),
                        border_style="red",
                        title=_("Operation Failed"),
                    )
                )
            else:
                console.print(
                    Panel(
                        # 0: e.stdout the Output. 1: e.stderr the Error.
                        _("Output: {0}\nError: {1}").format(e.stdout, e.stderr),
                        border_style="red",
                        title=_("Operation Failed"),
                    )
                )
            logger.debug(f"{traceback.format_exc()}")
            if aihelper is None:
                console.print(
                    Panel(
                        _(
                            "AI Helper not started, will enabled after configured by 'tinyget config'/'tinyget ui'"
                        ),
                        border_style="bright_black",
                    )
                )
            else:
                with console.status(
                    "[bold green] {}".format(
                        _("AI Helper started, getting command advise")
                    ),
                    spinner="bouncingBar",
                ) as status:
                    recommendation = aihelper.fix_command(args, e.stdout, e.stderr)
                console.print(
                    Panel(
                        recommendation,
                        border_style="green",
                        title=_("Advise from AI Helper"),
                    )
                )
            return (None, None, ERROR_HANDLED)
        except Exception as e:
            console.print(
                Panel(
                    f"{e}",
                    border_style="red",
                    title=_("Operation Failed"),
                )
            )
            logger.debug(f"{traceback.format_exc()}")
            return (None, None, ERROR_UNKNOWN)
        return result

    def search(self, package: str, enable_third_party: bool = True) -> List[Package]:
        """
        Searches for a package in the source.

        Args:
            package (str): The name of the package to search for.
            enable_third_party (bool): Enable third party softwares.

        Returns:
            The result of the execute_pacman_command function.
        """
        args = ["-Ss", package]
        console = Console()
        package_list = []
        try:
            out, err, retcode = execute_pacman_command(args)
            pkgs = []
            out = out.strip()
            for l in out.split("\n"):
                if not l.startswith(" "):
                    pkgs.append(l.split(" ")[0].split("/")[-1])
            installed_info = get_installed_info(pkgs)
            package_info = get_available_info(pkgs)

            installed_info_dict = {info["name"]: info for info in installed_info}
            package_info_dict = {info["name"]: info for info in package_info}

            upgradable_dict = get_upgradable(pkgs)

            for name, info in package_info_dict.items():
                if name in installed_info_dict:
                    installed = True
                    automatically_installed = (
                        _("Installed as a dependency")
                        in installed_info_dict[name]["reason"]
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
                pkg = Package(
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
                package_list.append(pkg)

            # Append third party softs
            if enable_third_party:
                package_list.extend(get_third_party_packages(package, package_list))
        except CommandExecutionError as e:
            if e.stderr == "":
                logger.debug("Pacman searched nothing")
                return package_list
            console.print(
                Panel(
                    # 0: e.stdout the Output. 1: e.stderr the Error.
                    _("Output: {0}\nError: {1}").format(e.stdout, e.stderr),
                    border_style="red",
                    title=_("Operation Failed"),
                )
            )
            logger.debug(f"{traceback.format_exc()}")
        except Exception as e:
            console.print(
                Panel(
                    f"{e}",
                    border_style="red",
                    title=_("Operation Failed"),
                )
            )
            logger.debug(f"{traceback.format_exc()}")
        return package_list

    def build(self, folder: str) -> Optional[str]:
        """makepkg wrapper

        Args:
            folder (str): Specify the folder stores PKGBUILD file

        Returns:
            Optional[str]: Whether has output, if so, print the output(a package file)
        """
        args = ["-s", "--noconfirm"]
        console = Console()
        output = None
        try:
            out, err, retcode = execute_makepkg_command(args, cwd=folder)
            # Find pkg.tar.zst
            files = os.listdir(folder)
            for f in files:
                exts = f.split(os.extsep)
                if len(exts) >= 3 and ".".join(exts[-3:]) == "pkg.tar.zst":
                    output = os.path.join(folder, f)
        except CommandExecutionError as e:
            console.print(
                Panel(
                    f"Output: {e.stdout}\nError: {e.stderr}",
                    border_style="red",
                    title="Operation Failed",
                )
            )
            logger.debug(f"{traceback.format_exc()}")
        except Exception as e:
            console.print(
                Panel(
                    f"{e}",
                    border_style="red",
                    title="Operation Failed",
                )
            )
            logger.debug(f"{traceback.format_exc()}")
        return output


if __name__ == "__main__":
    pacman = PACMAN()
    stdout, stderr, retcode = pacman.install(["wget"])
    logger.debug(stdout)
    logger.debug(stderr)
