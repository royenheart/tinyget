from typing import List, Union
from ..package import Package


class PackageManagerBase:
    def list(self) -> List[Package]:
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def install(self, package: Package):
        raise NotImplementedError

    def uninstall(self, package: Package):
        raise NotImplementedError

    def upgrade(self):
        raise NotImplementedError

    def search(self, package):
        raise NotImplementedError

    def get_package(self, package_name: str) -> Package:
        raise NotImplementedError
