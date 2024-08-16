from typing import List, Optional
from ..package import History, Package


class PackageManagerBase:
    def list(self, enable_third_party: bool) -> List[Package]:
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def install(self, package: Package):
        raise NotImplementedError

    def uninstall(self, package: Package):
        raise NotImplementedError

    def upgrade(self):
        raise NotImplementedError

    def search(self, package, enable_third_party: bool) -> List[Package]:
        raise NotImplementedError

    def build(self, folder) -> Optional[str]:
        raise NotImplementedError

    def history(self) -> List[History]:
        raise NotImplementedError

    def rollback(self, id):
        raise NotImplementedError

    def repo_manager(self):
        raise NotImplementedError

    def get_package(self, package_name: str) -> Package:
        raise NotImplementedError
