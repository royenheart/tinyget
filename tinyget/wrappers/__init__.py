from typing import List, Optional
import click
from tinyget.package import ManagerType
from ..common_utils import (
    get_config_path,
    get_configuration,
    get_os_package_manager,
    setup_logger_level,
)
from rich.console import Console
from rich.panel import Panel
from tinyget.globals import global_configs

package_manager_name = get_os_package_manager(["apt", "dnf", "pacman"])

if package_manager_name == "apt":
    from ._apt import APT as PackageManager

    MANAGER = ManagerType.apt
elif package_manager_name == "dnf":
    from ._dnf import DNF as PackageManager

    MANAGER = ManagerType.dnf
elif package_manager_name == "pacman":
    from ._pacman import PACMAN as PackageManager

    MANAGER = ManagerType.pacman
else:
    raise NotImplementedError(f"Unsupported package manager: {package_manager_name}")


@click.group()
def sim_apt():
    config_path = get_config_path(path=None)
    exist_config = get_configuration(path=None)
    for k, v in exist_config.items():
        if v is not None:
            global_configs[k] = v
    global_configs["config_path"] = config_path


@sim_apt.command("install", help="install packages")
@click.argument("pkg_names", nargs=-1, required=True)
def sim_apt_install(pkg_names: List[str]):
    pkg_manager = PackageManager()
    pkg_manager.install(pkg_names)


@sim_apt.command("remove", help="remove packages")
@click.argument("pkg_names", nargs=-1, required=True)
def sim_apt_uninstall(pkg_names: List[str]):
    pkg_manager = PackageManager()
    pkg_manager.uninstall(pkg_names)


@sim_apt.command("list", help="list packages based on package names")
@click.option(
    "--installed",
    is_flag=True,
    default=False,
    help="show installed packages",
)
@click.option(
    "--upgradeable",
    is_flag=True,
    default=False,
    help="show upgrades packages",
)
def sim_apt_list_pkgs(installed: bool, upgradeable: bool):
    pkg_manager = PackageManager()
    pkgs = pkg_manager.list_packages(
        only_installed=installed, only_upgradable=upgradeable
    )
    for pkg in pkgs:
        click.echo(pkg)


@sim_apt.command("search", help="search in package descriptions")
@click.argument("package", nargs=1, required=True)
def sim_apt_search(package: str):
    pkg_manager = PackageManager()
    pkgs = pkg_manager.search(package)
    for pkg in pkgs:
        click.echo(pkg)


@sim_apt.command("upgrade", help="upgrade the system by installing/upgrading packages")
def sim_apt_upgrade():
    pkg_manager = PackageManager()
    pkg_manager.upgrade()


@sim_apt.command("update", help="update list of available packages")
def sim_apt_update():
    pkg_manager = PackageManager()
    pkg_manager.update()


@click.group()
@click.option(
    "--debuglevel", "-d", "debug_", default="INFO", help="debugging output level"
)
def sim_dnf(debug_: str):
    config_path = get_config_path(path=None)
    exist_config = get_configuration(path=None)
    for k, v in exist_config.items():
        if v is not None:
            global_configs[k] = v
    global_configs["config_path"] = config_path
    setup_logger_level(level=debug_)


@sim_dnf.command("install", help="install a package or packages on your system")
@click.argument("pkg_names", nargs=-1, required=True)
def sim_dnf_install(pkg_names: List[str]):
    pkg_manager = PackageManager()
    pkg_manager.install(pkg_names)


@sim_dnf.command("remove", help="remove a package or packages from your system")
@click.argument("pkg_names", nargs=-1, required=True)
def sim_dnf_uninstall(pkg_names: List[str]):
    pkg_manager = PackageManager()
    pkg_manager.uninstall(pkg_names)


@sim_dnf.command("list", help="list a package or groups of packages")
@click.option(
    "--installed",
    is_flag=True,
    default=False,
    help="show only installed packages",
)
@click.option(
    "--updates",
    is_flag=True,
    default=False,
    help="show only upgrades packages",
)
@click.option(
    "--upgrades",
    is_flag=True,
    default=False,
    help="show only upgrades packages",
)
def sim_dnf_list_pkgs(installed: bool, updates: bool, upgrades: bool):
    pkg_manager = PackageManager()
    pkgs = pkg_manager.list_packages(
        only_installed=installed, only_upgradable=updates | upgrades
    )
    for pkg in pkgs:
        click.echo(pkg)


@sim_dnf.command("search", help="search package details for the given string")
@click.argument("package", nargs=1, required=True)
def sim_dnf_search(package: str):
    pkg_manager = PackageManager()
    pkgs = pkg_manager.search(package)
    for pkg in pkgs:
        click.echo(pkg)


@sim_dnf.command("upgrade", help="upgrade a package or packages on your system")
def sim_dnf_upgrade():
    pkg_manager = PackageManager()
    pkg_manager.upgrade()


@sim_dnf.command("check-update", help="check for available package upgrades")
def sim_dnf_update():
    pkg_manager = PackageManager()
    pkg_manager.update()


@click.command("pacman")
@click.option(
    "-S",
    "--sync",
    "sync_",
    is_flag=True,
    default=False,
    help="sync or install packages",
)
@click.option(
    "-R", "--remove", "remove_", is_flag=True, default=False, help="remove packages"
)
@click.option("-l", "list_", is_flag=True, default=False, help="list packages")
@click.option("-s", "search_", is_flag=True, default=False, help="search packages")
@click.option(
    "-y", "refresh_", is_flag=True, default=False, help="refresh package databases"
)
@click.option(
    "-u", "upgrade_", is_flag=True, default=False, help="upgrade installed packages"
)
@click.option(
    "--installed",
    is_flag=True,
    default=False,
    help="show installed packages",
)
@click.option(
    "--upgradeable",
    is_flag=True,
    default=False,
    help="show upgrades packages",
)
@click.argument("urls", nargs=-1, required=False)
def sim_pacman(
    sync_: bool,
    remove_: bool,
    list_: bool,
    search_: bool,
    refresh_: bool,
    upgrade_: bool,
    installed: bool,
    upgradeable: bool,
    urls: Optional[List[str]],
):
    config_path = get_config_path(path=None)
    exist_config = get_configuration(path=None)
    for k, v in exist_config.items():
        if v is not None:
            global_configs[k] = v
    global_configs["config_path"] = config_path

    console = Console()
    is_one_cmd = sum([sync_, remove_])
    if is_one_cmd > 1:
        console.print(
            Panel(
                "only one operation is allowed!",
                border_style="red",
                title="Operation Failed",
            )
        )
        return
    elif is_one_cmd < 1:
        console.print(
            Panel(
                "No operation is specified!",
                border_style="red",
                title="Operation Failed",
            )
        )
        return

    if sync_:
        sync_is_one_cmd = sum([list_, search_, refresh_])
        if sync_is_one_cmd > 1:
            console.print(
                Panel(
                    "only one operation is allowed in Sync!",
                    border_style="red",
                    title="Operation Failed",
                )
            )
            return
        if list_:
            pkg_manager = PackageManager()
            pkgs = pkg_manager.list_packages(
                only_installed=installed, only_upgradable=upgradeable
            )
            for pkg in pkgs:
                click.echo(pkg)
        elif search_:
            pkg_manager = PackageManager()
            if urls is None or len(urls) == 0:
                console.print(
                    Panel(
                        "No packages specified to search!",
                        border_style="red",
                        title="Operation Failed",
                    )
                )
            elif len(urls) > 1:
                console.print(
                    Panel(
                        "multiply packages glob for search!",
                        border_style="red",
                        title="Operation Failed",
                    )
                )
            else:
                pkgs = pkg_manager.search(urls[0])
                for pkg in pkgs:
                    click.echo(pkg)
        elif refresh_:
            pkg_manager = PackageManager()
            if upgrade_:
                pkg_manager.upgrade()
            else:
                pkg_manager.update()
        else:
            pkg_manager = PackageManager()
            if urls is None:
                console.print(
                    Panel(
                        "No packages specified to install!",
                        border_style="red",
                        title="Operation Failed",
                    )
                )
            else:
                pkg_manager.install(urls)
    elif remove_:
        pkg_manager = PackageManager()
        if urls is None:
            console.print(
                Panel(
                    "No packages specified to uninstall!",
                    border_style="red",
                    title="Operation Failed",
                )
            )
        else:
            pkg_manager.uninstall(urls)
