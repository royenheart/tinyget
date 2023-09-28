import dnf
from dnf.package import Package as _Package
from .pkg_manager import PackageManagerBase
from ..package import ManagerType, Package, PackageInfo
from ..common import match_str_from_list
from ..common.exceptions import PackageNotFound, PackageNotInstalled
from typing import List

class DNF(PackageManagerBase):
    def __init__(self):
        self.base = dnf.Base()
        self.base.read_all_repos()
        self.base.fill_sack()
    
    def convert_package(self, pkg: _Package) -> Package:
        def get_package_info(p: _Package) -> PackageInfo:
            return PackageInfo(
                architecture=p.arch,
                description=p.description,
                is_installed=p.installed,
                version=p.version
            )
        available_packages = self.base.sack.query().filter(name=pkg.name).available()
        installed_packages = [p for p in available_packages if p.installed]
        is_installed = len(installed_packages) > 0
        if is_installed:
            installed = get_package_info(installed_packages[0])
        else:
            installed = None
        
        newest_pkg = max(available_packages, key=lambda p: p.version)
        candidate = get_package_info(newest_pkg)
        upgradable = newest_pkg.version > pkg.version
        
        return Package(
            manager=ManagerType.dnf,
            name=pkg.name,
            upgradable=upgradable,
            available=[get_package_info(p) for p in available_packages],
            candidate=candidate,
            installed=installed,
            is_installed=is_installed,
            is_auto_installed=False,
        )
    
    def pkg_from_package(self, package: Package) -> _Package:
        return pkgs[0]
        
    def list(self) -> List[Package]:
        installed_packages = []
        for pkg in self.base.sack.query().installed():
            installed_packages.append(self.convert_package(pkg))
        return installed_packages

    def update(self):
        self.base.reset()
        self.base.update_cache()
        self.base.read_all_repos()
        self.base.fill_sack()
    
    def install(self, package: Package):
        pkgs = self.base.sack.query().filter(name=package.name, version=package.candidate.version).available()
        pkg = pkgs[0]
        self.base.package_install(pkg)
        self.base.resolve()
        self.base.download_packages(self.base.transaction.install_set)
        self.base.do_transaction()
    
    def uninstall(self, package: Package):
        pkgs = self.base.sack.query().filter(name=package.name, version=package.candidate.version).installed()
        if len(pkgs) == 0:
            raise PackageNotInstalled(package.name)
        pkg = pkgs[0]
        self.base.package_remove(pkg)
        self.base.resolve()
        self.base.do_transaction()
    
    def upgrade(self):
        self.base.upgrade_all()
        self.base.resolve()
        self.base.download_packages(self.base.transaction.install_set)
        self.base.do_transaction()
    
    def search(self, keyword, limit=10) -> List[Package]:
        pkgs = self.base.sack.query().filter(name__glob="*"+keyword+"*").run()
        deduped_pkgs = []
        for pkg in pkgs:
            if pkg.name not in [p.name for p in deduped_pkgs]:
                deduped_pkgs.append(pkg)
        return [self.convert_package(pkg) for pkg in deduped_pkgs[:limit]]
    
    def get_package(self, package_name: str) -> Package:
        pass
    

if __name__ == '__main__':
    dnf = DNF()
    packages = dnf.search("vim")
    package = packages[0]
    import ipdb; ipdb.set_trace()
    dnf.uninstall(package)
    