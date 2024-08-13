import re
import traceback

from tinyget.globals import ERROR_HANDLED, ERROR_UNKNOWN
from tinyget.interact.process import CommandExecutionError
from rich.console import Console
from rich.panel import Panel
from .pkg_manager import PackageManagerBase
from ..interact import execute_command as _execute_command
from ..interact import just_execute
from ..package import Package, ManagerType
from typing import Optional, List
from tinyget.interact import try_to_get_ai_helper

aihelper = try_to_get_ai_helper()


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
        return (out, err, retcode)
    else:
        raise CommandExecutionError(
            message=f"APT error during operation {args} with {envp}",
            args=list(args),
            envp=envp,
            stdout=out,
            stderr=err,
        )


def get_all_packages() -> List[Package]:
    """
    Retrieves a list of all installed and uninstalled packages.

    Returns:
        List[Package]: A list of Package objects representing the installed and uninstalled packages.

    Explains:
        This code defines a function get_all_packages() that retrieves a list of all installed and uninstalled packages on a system using the apt package manager. It executes the command apt list -v and parses the output to extract information about each package, such as the package name, repository, version, architecture, installation status, and description. It uses regular expressions to match and extract the relevant information from the output. The extracted information is then used to create Package objects, which are appended to a list and returned as the result.
    """
    args = ["list", "-v"]
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
    return packages


class APT(PackageManagerBase):
    def __init__(self):
        pass

    def list_packages(
        self, only_installed: bool = False, only_upgradable: bool = False
    ):
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
            packages = get_all_packages()
        except CommandExecutionError:
            console.print(
                Panel(
                    traceback.format_exc(),
                    border_style="red",
                    title="Operation Failed",
                )
            )
        except Exception as e:
            console.print(
                Panel(
                    traceback.format_exc(), border_style="red", title="Operation Failed"
                )
            )
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
        args = ["update", "-y"]
        console = Console()
        try:
            result = execute_apt_command(args)
        except CommandExecutionError:
            console.print(
                Panel(
                    traceback.format_exc(),
                    border_style="red",
                    title="Operation Failed",
                )
            )
            return (None, None, ERROR_HANDLED)
        except Exception:
            console.print(
                Panel(
                    traceback.format_exc(),
                    border_style="red",
                    title="Operation Failed",
                )
            )
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
        args = ["upgrade", "-y"]
        console = Console()
        try:
            result = execute_apt_command(args)
        except CommandExecutionError:
            console.print(
                Panel(
                    traceback.format_exc(),
                    border_style="red",
                    title="Operation Failed",
                )
            )
            return (None, None, ERROR_HANDLED)
        except Exception:
            console.print(
                Panel(
                    traceback.format_exc(),
                    border_style="red",
                    title="Operation Failed",
                )
            )
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
        args = ["install", "-y", *packages]
        console = Console()
        try:
            result = execute_apt_command(args)
        except CommandExecutionError as e:
            console.print(
                Panel(
                    traceback.format_exc(),
                    border_style="red",
                    title="Operation Failed",
                )
            )
            if aihelper is None:
                console.print(
                    Panel(
                        "AI Helper not started, will enabled after configured by 'tinyget config'/'tinyget ui'",
                        border_style="bright_black",
                    )
                )
            else:
                with console.status(
                    "[bold green] AI Helper started, getting command advise",
                    spinner="bouncingBar",
                ) as status:
                    recommendation = aihelper.fix_command(args, e.stdout, e.stderr)
                console.print(
                    Panel(
                        recommendation,
                        border_style="green",
                        title="Advise from AI Helper",
                    )
                )
            return (None, None, ERROR_HANDLED)
        except Exception:
            console.print(
                Panel(
                    traceback.format_exc(),
                    border_style="red",
                    title="Operation Failed",
                )
            )
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
        args = ["remove", "-y", *packages]
        console = Console()
        try:
            result = execute_apt_command(args)
        except CommandExecutionError as e:
            console.print(
                Panel(
                    traceback.format_exc(),
                    border_style="red",
                    title="Operation Failed",
                )
            )
            if aihelper is None:
                console.print(
                    Panel(
                        "AI Helper not started, will enabled after configured by 'tinyget config'/'tinyget ui'",
                        border_style="bright_black",
                    )
                )
            else:
                with console.status(
                    "[bold green] AI Helper started, getting command advise",
                    spinner="bouncingBar",
                ) as status:
                    recommendation = aihelper.fix_command(args, e.stdout, e.stderr)
                console.print(
                    Panel(
                        recommendation,
                        border_style="green",
                        title="Advise from AI Helper",
                    )
                )
            return (None, None, ERROR_HANDLED)
        except Exception:
            console.print(
                Panel(
                    traceback.format_exc(),
                    border_style="red",
                    title="Operation Failed",
                )
            )
            return (None, None, ERROR_UNKNOWN)
        return result

    def search(self, package_name: str):
        """
        Searches for the specified package.

        Args:
            package_name (str): The name of the package to search for.

        Returns:
            The result of executing the command to search for the package.
        """
        args = ["apt", "search", package_name]
        just_execute(args)


if __name__ == "__main__":
    apt = APT()
    apt.search("vim")

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
