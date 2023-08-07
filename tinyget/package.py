from dataclasses import dataclass
from enum import Enum


ManagerType = Enum("ManagerType", "apt dnf pacman")


@dataclass
class Package:
    manager: ManagerType
    package_name: str
