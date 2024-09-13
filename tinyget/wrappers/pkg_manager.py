from tempfile import mkdtemp
from typing import Dict, List, Optional
from venv import logger
from ..package import History, Package
from tinyget.repos.third_party import (
    get_third_party_mirror_template,
    get_third_party_mirrors,
)
import os


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

    def repo_configure_get_script(self, repo: str) -> Optional[str]:
        """Configure a repository, will generate a script.

        Args:
            repo (str): The repository name.

        Returns:
            Optional[str]: The script, will be None if the repository is not supported in tinyget.
        """
        temp = get_third_party_mirror_template(mirror=repo)
        if temp is None:
            return None
        dir = mkdtemp()
        script = os.path.join(dir, f"{repo}_configure_script.sh")
        with open(script, "w+") as f:
            f.write(temp)
        logger.debug(f"Generated configure script for {repo} at {script}")
        return script

    def repo_list(self) -> Dict[str, List[str]]:
        return get_third_party_mirrors()

    def get_package(self, package_name: str) -> Package:
        raise NotImplementedError
