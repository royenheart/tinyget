from setuptools import setup, find_packages
from typing import List
import os

supported_package_managers = ["apt", "dnf"]

common_required_packages = ["requests", "click", "dataclasses"]


def get_os_package_manager(possible_package_manager_names: List[str]):
    """
    Get the operating system package manager from a list of possible package manager names.

    Args:
        possible_package_manager_names (List[str]): A list of possible package manager names.

    Returns:
        str: The name of the operating system package manager.

    Raises:
        Exception: If no supported package manager is found in the PATH.
    """
    paths = os.environ["PATH"].split(os.pathsep)
    for bin_path in paths:
        for package_manager_name in possible_package_manager_names:
            if package_manager_name in os.listdir(bin_path):
                return package_manager_name
    raise Exception("No supported package manager found in PATH")


current_package_manager = get_os_package_manager(supported_package_managers)

if current_package_manager == "apt":
    specific_required_packages = []
elif current_package_manager == "dnf":
    specific_required_packages = []
elif current_package_manager == "pacman":
    specific_required_packages = []
else:
    raise Exception("No supported package manager found in PATH")

required_packages = common_required_packages + specific_required_packages

setup(
    name="tinyget",
    version="0.0.1",
    install_requires=required_packages,
    packages=find_packages(),
    author="kongjiadongyuan",
    author_email="zhaggbl@outlook.com",
    description="A tiny package manager for Linux",
    license="MIT",
    entry_points={"console_scripts": ["tinyget=tinyget.main:cli"]},
)
