from datetime import datetime
import re
import traceback
from tinyget.common_utils import logger
from tinyget.repos.third_party import get_pkg_url, get_third_party_packages
from tinyget.globals import ERROR_HANDLED, ERROR_UNKNOWN, SUCCESS, global_configs
from tinyget.interact.process import CommandExecutionError
from rich.console import Console
from rich.panel import Panel
from .pkg_manager import PackageManagerBase
from ..interact import execute_command as _execute_command
from tinyget.package import History, Package, ManagerType
from typing import Optional, List
from tinyget.i18n import load_translation
from tinyget.interact import try_to_get_ai_helper

aihelper = try_to_get_ai_helper()

_ = load_translation("_apt")


def execute_apt_command(args: List[str], timeout: Optional[float] = None):
    """
    Executes apt with the given arguments and optional timeout.

    Parameters:
        args (List[str]): The arguments to pass to the apt. Can be a list of strings or a single string.
        timeout (int, optional): The maximum time to wait for the apt to complete, in seconds. Defaults to None.

    Returns:
        The result of executing the command.

    """
    envp = {"DEBIAN_FRONTEND": "noninteractive"}
    args.insert(0, "apt")
    out, err, retcode = _execute_command(args, envp, timeout)
    if retcode == 0:
        # Operation successful
        return (out, err, SUCCESS)
    else:
        raise CommandExecutionError(
            # 0: args the operation. 1: envp the execution environment
            message=_("APT error during operation {0} with {1}").format(args, envp),
            args=list(args),
            envp=envp,
            stdout=out,
            stderr=err,
        )


def get_packages(softs: str = "", enable_third_party: bool = True) -> List[Package]:
    """
    Retrieves a list of all installed and uninstalled packages.

    Parameters:
        enable_third_party (bool): Enable third party softwares.

    Returns:
        List[Package]: A list of Package objects representing the installed and uninstalled packages.

    Explains:
        This code defines a function get_packages() that retrieves a list of all installed and uninstalled packages on a system using the apt package manager. It executes the command apt list -v and parses the output to extract information about each package, such as the package name, repository, version, architecture, installation status, and description. It uses regular expressions to match and extract the relevant information from the output. The extracted information is then used to create Package objects, which are appended to a list and returned as the result.
    """
    args = ["list", "-v"]
    if softs != "":
        args.append(softs)
    content, stderr, retcode = execute_apt_command(args)

    blocks = content.split("\n\n")

    package_name_regex = r"(?P<package_name>.+)"
    repo_regex = r"(?P<repo>.+)"
    version_regex = r"(?P<version>.+)"
    architecture_regex = r"(?P<architecture>.+)"
    install_status_regex = r"(?P<install_status>.+)"
    description_regex = r"(?P<description>.+)"
    installed_pattern = rf"^{package_name_regex}/{repo_regex}\s{version_regex}\s{architecture_regex}\s\[{install_status_regex}\]\n  {description_regex}$"
    uninstalled_pattern = rf"^{package_name_regex}/{repo_regex}\s{version_regex}\s{architecture_regex}\n  {description_regex}$"
    installed_regex = re.compile(installed_pattern, re.MULTILINE)
    uninstalled_regex = re.compile(uninstalled_pattern, re.MULTILINE)

    packages = []

    for block in blocks:
        match = installed_regex.search(block)
        if match:
            installed_status = match.group("install_status").split(_(","))
            installed = False
            automatically_installed = False
            upgradable = False
            available_version = None
            for status in installed_status:
                if _("installed") in status:
                    installed = True
                if _("auto") in status:
                    automatically_installed = True
                if _("upgradable") in status:
                    upgradable = True
                    installed = True
                    # upgradable from: xxx, which is the current version
                    # : 's format depends on the LANG
                    cv = status.split(_(":"), maxsplit=1)
                    if len(cv) == 2:
                        available_version = cv[1].strip()
                    else:
                        logger.warning(
                            # 0: The status captured
                            _("Can't parse status is upgradable: {0}").format(status)
                        )
            version = match.group("version")
            if upgradable:
                t = version
                version = available_version if available_version is not None else ""
                available_version = t
            package = Package(
                package_type=ManagerType.apt,
                package_name=match.group("package_name"),
                architecture=match.group("architecture"),
                description=match.group("description"),
                version=version,
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

    # Append third party softs
    if enable_third_party:
        packages.extend(get_third_party_packages(softs, wrapper_softs=packages))

    return packages


class APT(PackageManagerBase):
    def __init__(self):
        pass

    def list_packages(
        self,
        only_installed: bool = False,
        only_upgradable: bool = False,
        enable_third_party: bool = True,
    ) -> List[Package]:
        """
        Returns a list of packages based on the specified filters.

        Args:
            only_installed (bool, optional): If True, only return installed packages.
                Defaults to False.
            only_upgradable (bool, optional): If True, only return upgradable packages.
                Defaults to False.

        Returns:
            List[Package]: A list of packages that match the specified filters.
        """
        console = Console()
        try:
            packages = get_packages(enable_third_party=enable_third_party)
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
        if only_upgradable:
            packages = [package for package in packages if package.upgradable]

        if only_installed:
            packages = [package for package in packages if package.installed]

        return packages

    def update(self):
        """
        Updates the system by running the 'apt update' command.

        :return: The output of the 'apt update' command.
        """
        use_input = global_configs["live_output"]
        if use_input:
            args = ["update"]
        else:
            args = ["update", "-y"]
        console = Console()
        try:
            result = execute_apt_command(args)
        except CommandExecutionError as e:
            if _("Permission denied") in e.stderr:
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
        Upgrade the system by running the 'apt upgrade' command with the '-y' flag.

        Parameters:
            None

        Returns:
            The output of the 'execute_apt_command' function.
        """
        use_input = global_configs["live_output"]
        if use_input:
            args = ["upgrade"]
        else:
            args = ["upgrade", "-y"]
        console = Console()
        try:
            result = execute_apt_command(args)
        except CommandExecutionError as e:
            if _("Permission denied") in e.stderr:
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
        Installs the specified packages.

        Args:
            packages (List[str]): A list of packages to be installed.

        Returns:
            The result of executing the command to install the packages.
        """
        packages = list(packages)
        logger.debug(f"Will install packages: {packages}")
        # replace third party softs' url
        for i, pkg in enumerate(packages):
            r = get_pkg_url(softs=pkg)
            if r is not None:
                packages[i] = r
        use_input = global_configs["live_output"]
        if use_input:
            args = ["install", *packages]
        else:
            args = ["install", "-y", *packages]
        console = Console()
        try:
            result = execute_apt_command(args)
        except CommandExecutionError as e:
            if _("Permission denied") in e.stderr:
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
            None: This function does not return anything.
        """
        use_input = global_configs["live_output"]
        if use_input:
            args = ["remove", *packages]
        else:
            args = ["remove", "-y", *packages]
        console = Console()
        try:
            result = execute_apt_command(args)
        except CommandExecutionError as e:
            if _("Permission denied") in e.stderr:
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

    def search(
        self, package_name: str, enable_third_party: bool = True
    ) -> List[Package]:
        """
        Searches for the specified package.

        Args:
            package_name (str): The name of the package to search for.
            enable_third_party (bool): Enable third party softs.

        Returns:
            The result of executing the command to search for the package.
        """
        console = Console()
        package_list = []
        try:
            package_list = get_packages(
                softs=f"{package_name}", enable_third_party=enable_third_party
            )
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

    def build(self, folder) -> Optional[str]:
        raise NotImplementedError

    def history(self) -> List[History]:
        console = Console()
        histories = []
        try:
            with open("/var/log/apt/history.log", "r") as f:
                out = f.read()
            out = out.strip().split("\n\n")
            out = [block for block in out if block != ""]
            for i, l in enumerate(out):
                blocks = l.splitlines()
                his = History(
                    id=str(i),
                    command=blocks[1].split(":")[1].strip(),
                    date=datetime.strptime(
                        blocks[0].split(":", maxsplit=1)[1].strip(), "%Y-%m-%d %H:%M:%S"
                    ),
                    operations=[blocks[2].split(":")[0]],
                )
                histories.append(his)
        except Exception as e:
            console.print(
                Panel(
                    f"{e}",
                    border_style="red",
                    title="Operation Failed",
                )
            )
            logger.debug(f"{traceback.format_exc()}")
        return histories

    def rollback(self, id: str):
        raise NotImplementedError
