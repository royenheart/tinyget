from dataclasses import dataclass, field
from typing import List
from enum import Enum


ManagerType = Enum("ManagerType", "apt dnf pacman")


@dataclass
class Package:
    package_type: ManagerType
    package_name: str = field(default_factory=str)
    architecture: str = field(default_factory=str)
    description: str = field(default_factory=str)
    version: str = field(default_factory=str)
    installed: bool = field(default_factory=bool)
    automatically_installed: bool = field(default_factory=bool)
    upgradable: str = field(default_factory=bool)
    available_version: str = field(default_factory=str)
    remain: dict = field(default_factory=dict)

    def __repr__(self):
        result = ""
        result += f"package_name: {self.package_name}\n"
        result += f" architecture: {self.architecture}\n"
        result += f" description: {self.description}\n"
        result += f" version: {self.version}\n"
        result += f" installed: {self.installed}\n"
        result += f" automatically_installed: {self.automatically_installed}\n"
        return result
