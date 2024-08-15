from tinyget.package import ManagerType
from ..common_utils import get_os_package_manager

package_manager_name = get_os_package_manager(["apt", "dnf", "pacman"])

if package_manager_name == "apt":
    from ._apt import APT as PackageManager

    MANAGER = ManagerType.apt
elif package_manager_name == "dnf":
    from ._dnf import DNF as PackageManager

    MANAGER = ManagerType.dnf
elif package_manager_name == "pacman":
    from ._pacman import PACMAN as PackageManager

    MANAGER = ManagerType.pacman
else:
    raise NotImplementedError(f"Unsupported package manager: {package_manager_name}")
