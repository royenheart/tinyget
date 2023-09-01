from ..common_utils import get_os_package_manager

package_manager_name = get_os_package_manager(["apt", "dnf"])

if package_manager_name == "apt":
    from ._apt import APT as PackageManager
elif package_manager_name == "dnf":
    from ._dnf import DNF as PackageManager
