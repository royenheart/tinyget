from tinyget.wrappers import PackageManager
import pytest


def test_install_vim():
    package_manager = PackageManager()
    out, err = package_manager.install(["vim"])
    assert out != b""


if __name__ == "__main__":
    pytest.main([__file__])
