from apt.cache import Cache as _Cache
from apt.package import Version as _Version
from apt.package import Package as _Package
import apt_pkg
from .pkg_manager import PackageManagerBase
from ..package import ManagerType, Package, PackageInfo
from ..common import match_str_from_list
from ..common.exceptions import PackageNotFound, PackageNotInstalled

from typing import Union


def get_architecture() -> str:
    return apt_pkg.get_architectures()[0]


def convert_package_info(version: _Version) -> PackageInfo:
    return PackageInfo(
        architecture=version.architecture,
        description=version.raw_description,
        is_installed=version.is_installed,
        version=version.version,
    )


def convert_package(pkg: _Package) -> Package:
    if installed_pkg_version := pkg.installed:
        installed = convert_package_info(installed_pkg_version)
    else:
        installed = None

    available = []
    for version in pkg.versions:
        available.append(convert_package_info(version))

    candidate = convert_package_info(pkg.candidate)
    upgradable = pkg.is_upgradable
    return Package(
        manager=ManagerType.apt,
        installed=installed,
        is_installed=pkg.is_installed,
        is_auto_installed=pkg.is_auto_installed,
        name=pkg.name,
        available=available,
        upgradable=upgradable,
        candidate=candidate,
    )


class APT(PackageManagerBase):
    def __init__(self):
        self.cache = _Cache()
        self.architecture = get_architecture()

    def list(self):
        installed_packages = []
        for pkg in self.cache:
            if pkg.is_installed:
                installed_packages.append(self.get_package(pkg.name))

        return installed_packages

    def update(self):
        self.cache.update()
        self.cache.open()

    def upgrade(self):
        self.cache.upgrade()
        self.cache.open()

    def search(self, keyword, limit=10):
        package_name_list = self.cache.keys()
        return match_str_from_list(keyword, package_name_list, limit)

    def get_package(self, package_name: str) -> Package:
        if package_name not in self.cache:
            raise PackageNotFound(package_name)
        return convert_package(self.cache[package_name])

    def install(self, package: Package):
        package_name = package.name

        if package_name not in self.cache:
            raise PackageNotFound(package_name)

        pkg = self.cache[package_name]
        pkg.mark_install()
        # commit
        self.cache.commit()

    def uninstall(self, package: Package):
        if not package.is_installed:
            raise PackageNotInstalled(package.name)
        pkg = self.cache[package.name]
        pkg.mark_delete()
        self.cache.commit()


if __name__ == "__main__":
    apt = APT()
    package = apt.get_package("curl")
    apt.install(package)
