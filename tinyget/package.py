from dataclasses import dataclass
from typing import List
from enum import Enum


ManagerType = Enum("ManagerType", "apt dnf pacman")


@dataclass
class PackageInfo:
    architecture: str
    description: str
    is_installed: bool
    version: str

    def __repr__(self):
        return f"<PackageInfo {self.version}>"


@dataclass
class Package:
    manager: ManagerType
    name: str
    upgradable: bool
    available: List[PackageInfo]
    candidate: PackageInfo
    installed: PackageInfo
    is_installed: bool
    is_auto_installed: bool

    def __repr__(self):
        return f"<Package {self.name}>"
