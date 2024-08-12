"""Metadata hook."""

from typing import List
from hatchling.metadata.plugin.interface import MetadataHookInterface
import os

supported_package_managers = ["apt", "dnf", "pacman"]


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
            if not os.path.exists(bin_path):
                continue
            if package_manager_name in os.listdir(bin_path):
                return package_manager_name
    raise Exception("No supported package manager found in PATH")


class CheckDepsHook(MetadataHookInterface):
    PLUGIN_NAME = "ckdeps"

    def update(self, metadata: dict) -> None:
        try:
            current_package_manager = get_os_package_manager(supported_package_managers)
        except Exception as e:
            print(f"{e}")

        common_deps = ["requests", "click", "dataclasses", "rich", "trogon"]

        if current_package_manager == "apt":
            common_deps += []
        elif current_package_manager == "dnf":
            common_deps += []
        elif current_package_manager == "pacman":
            common_deps += []
        else:
            print(f"{current_package_manager} not support in tinyget")
            common_deps += []

        metadata["dependencies"] = common_deps
