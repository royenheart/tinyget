from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from rich.table import Table
from rich.console import Console


class ManagerType(Enum):
    apt = "deb"
    dnf = "rpm"
    pacman = "pkg.tar.zst"

    def __eq__(self, value: object) -> bool:
        return self.name == value

    def __str__(self) -> str:
        return self.name

    @property
    def ext(self) -> str:
        return self.value


@dataclass
class Package:
    package_type: ManagerType
    package_name: str = field(default_factory=str)
    architecture: str = field(default_factory=str)
    description: str = field(default_factory=str)
    version: str = field(default_factory=str)
    installed: bool = field(default_factory=bool)
    automatically_installed: bool = field(default_factory=bool)
    upgradable: bool = field(default_factory=bool)
    available_version: Optional[str] = field(default_factory=str)
    remain: dict = field(default_factory=dict)

    def __repr__(self):
        result = ""
        result += f"package_name: {self.package_name}\n"
        result += f" architecture: {self.architecture}\n"
        result += f" description: {self.description}\n"
        result += f" version: {self.version}\n"
        result += f" installed: {self.installed}\n"
        result += f" automatically_installed: {self.automatically_installed}\n"
        result += f" upgradable: {self.upgradable}\n"
        result += f" available_version: {self.available_version}\n"
        result += f" remain: {self.remain}\n"
        return result


def show_packages(packages: List[Package]):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("package_type")
    table.add_column("package_name")
    table.add_column("architecture")
    table.add_column("description")
    table.add_column("version")
    table.add_column("installed")
    table.add_column("automatically_installed")
    table.add_column("upgradable")
    table.add_column("available_version")
    table.add_column("remain")
    for package in packages:
        table.add_row(
            str(package.package_type),
            str(package.package_name),
            str(package.architecture),
            str(package.description),
            str(package.version),
            str(package.installed),
            str(package.automatically_installed),
            str(package.upgradable),
            str(package.available_version),
            str(package.remain),
        )
    console = Console()
    console.print(table)
