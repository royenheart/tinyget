from abc import ABCMeta, abstractclassmethod
from typing import List, Union
from ..package import Package


class PackageManagerBase(metaclass=ABCMeta):
    @abstractclassmethod
    def list(self) -> List[Package]:
        pass

    @abstractclassmethod
    def update(self):
        pass

    @abstractclassmethod
    def install(self, package: Package):
        pass

    @abstractclassmethod
    def uninstall(self, package: Package):
        pass

    @abstractclassmethod
    def upgrade(self):
        pass

    @abstractclassmethod
    def search(self, keyword, limit=10) -> List[Package]:
        pass

    @abstractclassmethod
    def get_package(self, package_name: str) -> Package:
        pass
