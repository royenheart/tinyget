from typing import List, Optional
from tinyget.package import ManagerType, Package
from tinyget.repos.third_party import ThirdPartySofts, download_file, AllPkgInfo
from tinyget.wrappers import MANAGER
from tinyget.globals import ARCH, SupportArchs
from tinyget.wrappers import PackageManager
from tinyget.common_utils import logger
import tempfile
import os


class _QQ(ThirdPartySofts):

    HOMEPAGE = "https://im.qq.com/linuxqq/"
    VERSION = "3.2.12_26909"
    DOWNLOAD_PAGE = "https://dldir1.qq.com/qqfile/qq/QQNT/2b82dc28/"
    PKG_NAME = AllPkgInfo.LINUXQQ

    @property
    def is_support(self) -> bool:
        if (
            (MANAGER == ManagerType.dnf and ARCH == SupportArchs.arm64)
            or (MANAGER == ManagerType.dnf and ARCH == SupportArchs.x86_64)
            or (MANAGER == ManagerType.apt and ARCH == SupportArchs.arm64)
            or (MANAGER == ManagerType.apt and ARCH == SupportArchs.loongarch64)
        ):
            return True
        elif MANAGER == ManagerType.apt and ARCH == SupportArchs.x86_64:
            return True
        elif MANAGER == ManagerType.apt and ARCH == SupportArchs.mips:
            return True
        elif MANAGER == ManagerType.pacman and (
            ARCH == SupportArchs.x86_64
            or ARCH == SupportArchs.arm64
            or ARCH == SupportArchs.loongarch64
        ):
            return True
        else:
            return False

    def url(self) -> Optional[str]:
        tmpdir = tempfile.mkdtemp()
        if (
            (MANAGER == ManagerType.dnf and ARCH == SupportArchs.arm64)
            or (MANAGER == ManagerType.dnf and ARCH == SupportArchs.x86_64)
            or (MANAGER == ManagerType.apt and ARCH == SupportArchs.arm64)
            or (MANAGER == ManagerType.apt and ARCH == SupportArchs.loongarch64)
        ):
            n = f"{_QQ.PKG_NAME}_{_QQ.VERSION.replace('_', '-')}_{ARCH}.{MANAGER.ext}"
            url = f"{_QQ.DOWNLOAD_PAGE}/{n}"
            downloads = os.path.join(tmpdir, n)
            download_file(url=url, output_file=downloads)
            return downloads
        elif MANAGER == ManagerType.apt and ARCH == SupportArchs.x86_64:
            n = f"{_QQ.PKG_NAME}_{_QQ.VERSION.replace('_', '-')}_amd64.{MANAGER.ext}"
            url = f"{_QQ.DOWNLOAD_PAGE}/{n}"
            downloads = os.path.join(tmpdir, n)
            download_file(url=url, output_file=downloads)
            return downloads
        elif MANAGER == ManagerType.apt and ARCH == SupportArchs.mips:
            n = f"{_QQ.PKG_NAME}_{_QQ.VERSION.replace('_', '-')}_mips64el.{MANAGER.ext}"
            url = f"{_QQ.DOWNLOAD_PAGE}/{n}"
            downloads = os.path.join(tmpdir, n)
            download_file(url=url, output_file=downloads)
            return downloads
        elif MANAGER == ManagerType.pacman and (
            ARCH == SupportArchs.x86_64
            or ARCH == SupportArchs.arm64
            or ARCH == SupportArchs.loongarch64
        ):
            PKGBUILD = "https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=linuxqq"
            PKGBUILD_SOURCE = (
                "https://aur.archlinux.org/cgit/aur.git/plain/linuxqq.sh?h=linuxqq"
            )
            PKGBUILD_F = os.path.join(tmpdir, "PKGBUILD")
            PKGBUILD_SOURCE_F = os.path.join(tmpdir, "linuxqq.sh")
            download_file(url=PKGBUILD, output_file=PKGBUILD_F)
            download_file(url=PKGBUILD_SOURCE, output_file=PKGBUILD_SOURCE_F)
            pacman = PackageManager()
            return pacman.build(folder=tmpdir)
        else:
            return None

    def get_pkg_url(self) -> Optional[str]:
        return self.url()

    def get_package(
        self, wrapper_softs: Optional[List[Package]] = []
    ) -> Optional[Package]:
        # Means not support in current arch and package manager
        if not self.is_support:
            return None

        INSTALLED = False
        UPGRADABLE = False
        AVAILABLE_V = None
        if wrapper_softs is not None:
            for p in wrapper_softs:
                if p.package_name == _QQ.PKG_NAME and p.installed is True:
                    INSTALLED = True
                    # Judge versions updated
                    try:
                        INSTALLED_V = p.version.split("_")
                        INSTALLED_V = [*INSTALLED_V[0].split("."), INSTALLED_V[1]]
                        BUILTIN_V = _QQ.VERSION.split("_")
                        BUILTIN_V = [*BUILTIN_V[0].split("."), BUILTIN_V[1]]
                        if len(BUILTIN_V) != len(INSTALLED_V):
                            raise KeyError
                    except KeyError:
                        logger.warning(
                            f"Can't determine {_QQ.PKG_NAME} whether to update, check its version format and third party config"
                        )
                        break
                    for i, v in enumerate(BUILTIN_V):
                        v = int(v)
                        ov = int(INSTALLED_V[i])
                        if v > ov:
                            UPGRADABLE = True
                            AVAILABLE_V = _QQ.VERSION
                            break
                        elif v < ov:
                            UPGRADABLE = False
                            AVAILABLE_V = p.version
                            break
                    break

        return Package(
            package_type=MANAGER,
            package_name=_QQ.PKG_NAME,
            architecture=ARCH,
            description="QQ Linux, an instant messaging software",
            version=_QQ.VERSION,
            installed=INSTALLED,
            automatically_installed=False,
            upgradable=UPGRADABLE,
            available_version=AVAILABLE_V,
        )
