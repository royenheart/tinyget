import re
import traceback

from tinyget.globals import ERROR_HANDLED, ERROR_UNKNOWN
from tinyget.interact.process import CommandExecutionError
from rich.console import Console
from rich.panel import Panel
from .pkg_manager import PackageManagerBase
from ..interact import execute_command as _execute_command
from ..package import Package, ManagerType
from ..common_utils import logger
from typing import Optional, Union, List
from tinyget.i18n import load_translation
from tinyget.interact import try_to_get_ai_helper

aihelper = try_to_get_ai_helper()

_ = load_translation("_dnf")


def execute_dnf_command(args: List[str], timeout: Optional[float] = None):
    """
    Executes dnf with the given arguments and optional timeout.

    Parameters:
        args (List[str]): The arguments to pass to the dnf. Should be a list of strings.
        timeout (int, optional): The maximum time to wait for the dnf to complete, in seconds. Defaults to None.

    Returns:
        The result of executing the dnf.

    """
    envp = {}
    args.insert(0, "dnf")
    out, err, retcode = _execute_command(args, envp, timeout)
    # see 'man dnf'
    if retcode == 0:
        # Operation successful
        return (out, err, retcode)
    elif retcode == 1:
        raise CommandExecutionError(
            message=_(
                "An error occurred when executing {} with {}, was handled by dnf"
            ).format(args, envp),
            args=list(args),
            envp=envp,
            stdout=out,
            stderr=err,
        )
    elif retcode == 3:
        raise CommandExecutionError(
            message=_(
                "An unknown unhandled error occurred during operation {} with {}"
            ).format(args, envp),
            args=list(args),
            envp=envp,
            stdout=out,
            stderr=err,
        )
    elif retcode == 100:
        # there are updates available and a list of updates are printed
        return (out, err, retcode)
    elif retcode == 200:
        raise CommandExecutionError(
            message=_(
                "Problem with acquiring or releasing of locks raised during operation {} with {}"
            ).format(args, envp),
            args=list(args),
            envp=envp,
            stdout=out,
            stderr=err,
        )
    else:
        raise CommandExecutionError(
            message=_("Unknown dnf error during operation {} with {}").format(
                args, envp
            ),
            args=list(args),
            envp=envp,
            stdout=out,
            stderr=err,
        )


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


def repoquery(flags: Union[List[str], str] = [], softs: str = ""):
    """
    Query the repository for package information.

    Args:
        flags (Union[List[str], str], optional): A list of flags or a single flag as a string. Defaults to [].
        softs (str): The softwares search pattern

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
        raise ValueError(_("flags must be a string or a list"))
    format_tags = [f"%{{{tag}}}" for tag in query_tags]
    format_string = "^^^"
    format_string += "|^".join(format_tags)
    format_string += "$$$"
    args = ["repoquery", *flags, "--queryformat", format_string]
    if softs != "":
        args.append(softs)

    stdout, stderr, retcode = execute_dnf_command(args)
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
    args = ["check-update"]
    stdout, stderr, retcode = execute_dnf_command(args)
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


def get_packages(softs: str = "") -> List[Package]:
    """
    Retrieves information about specific packages. Default are all packages.

    Returns:
        List[Package]: A list of Package objects representing the packages.
    """
    package_info_list = repoquery(softs=softs)
    package_info_dict = {}
    for p in package_info_list:
        uid = get_unique_id(p)
        if (
            uid in package_info_dict
            and p["version"] > package_info_dict[uid]["version"]
        ) or uid not in package_info_dict:
            package_info_dict[uid] = p

    # Query installed packages
    installed_package_info_list = repoquery(flags="--installed", softs=softs)
    for info in installed_package_info_list:
        uid = get_unique_id(info)
        try:
            new_info = package_info_dict[uid]
            new_info["reason"] = info["reason"]
            new_info["installtime"] = info["installtime"]
            package_info_dict[uid] = new_info
        except KeyError as e:
            logger.debug(
                f"{uid} installed but not in any repo, see as userinstalled: {e}"
            )
            package_info_dict[uid] = info

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
        console = Console()
        try:
            package_list = get_packages()
        except CommandExecutionError as e:
            console.print(
                Panel(
                    _("Output: {}\nError: {}").format(e.stdout, e.stderr),
                    border_style="red",
                    title=_("Operation Failed"),
                )
            )
            logger.debug(f"{traceback.format_exc()}")
            return []
        except Exception as e:
            console.print(
                Panel(
                    f"{e}",
                    border_style="red",
                    title=_("Operation Failed"),
                )
            )
            logger.debug(f"{traceback.format_exc()}")
            return []

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
        args = ["check-update", "-y"]
        console = Console()
        try:
            result = execute_dnf_command(args)
        except CommandExecutionError as e:
            console.print(
                Panel(
                    _("Output: {}\nError: {}").format(e.stdout, e.stderr),
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
        Upgrade the system by running the `dnf upgrade` command with the specified arguments.

        :return: The output of the `execute_dnf_command` function.
        """
        args = ["upgrade", "--refresh", "-y"]
        console = Console()
        try:
            result = execute_dnf_command(args)
        except CommandExecutionError as e:
            console.print(
                Panel(
                    _("Output: {}\nError: {}").format(e.stdout, e.stderr),
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
        Installs the specified packages using the DNF package manager.

        Parameters:
            packages (List[str]): A list of package names to install.

        Returns:
            The return value of the execute_dnf_command function.
        """
        args = ["install", "-y", *packages]
        console = Console()
        try:
            result = execute_dnf_command(args)
        except CommandExecutionError as e:
            console.print(
                Panel(
                    _("Output: {}\nError: {}").format(e.stdout, e.stderr),
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
        Uninstalls a list of packages.

        Parameters:
            packages (List[str]): A list of package names to be uninstalled.

        Returns:
            None
        """
        args = ["remove", "-y", *packages]
        console = Console()
        try:
            result = execute_dnf_command(args)
        except CommandExecutionError as e:
            console.print(
                Panel(
                    _("Output: {}\nError: {}").format(e.stdout, e.stderr),
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

    def search(self, package: str):
        """
        Searches for a package using the DNF package manager.

        Parameters:
            package (str): The name of the package to search for.

        Returns:
            The return value of the execute_command function.
        """
        console = Console()
        package_list = []
        try:
            package_list = get_packages(softs=f"{package}")
        except CommandExecutionError as e:
            console.print(
                Panel(
                    _("Output: {}\nError: {}").format(e.stdout, e.stderr),
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


if __name__ == "__main__":
    dnf = DNF()
    stdout, stderr, retcode = dnf.install(["wget"])
