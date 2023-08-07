from apt.cache import Cache as _Cache
from .pkg_manager import PackageManagerBase
from ..package import ManagerType, Package


class APT(PackageManagerBase):
    def __init__(self):
        pass

    def get_packages(self):
        cache = _Cache()
        installed_packages = []
        for pkg in cache:
            if pkg.is_installed:
                installed_packages.append(Package(ManagerType.apt, pkg.name))

        return installed_packages


if __name__ == "__main__":
    apt = APT()
    print(apt.get_packages())
