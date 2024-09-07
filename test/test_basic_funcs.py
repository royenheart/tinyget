from tinyget.wrappers import PackageManager
import pytest


def test_list_packages():
    package_manager = PackageManager()
    packages = package_manager.list_packages(
        only_installed=False, only_upgradable=False
    )
    assert len(packages) > 0


def test_search():
    package_manager = PackageManager()
    packages = package_manager.search("gcc")
    assert len(packages) > 0


if __name__ == "__main__":
    pytest.main([__file__])
