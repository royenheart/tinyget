"""Metadata hook."""

from enum import Enum
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
        Exception: If no supported package manager is found.
    """
    judges = Enum("Judges", "file folder")
    os_info = {
        "dnf": [(judges.file, "/etc/redhat-release")],
        "pacman": [(judges.file, "/etc/arch-release")],
        "emerge": [(judges.file, "/etc/gentoo-release")],
        "zypp": [(judges.file, "/etc/SuSE-release")],
        "apt": [(judges.file, "/etc/debian_version")],
        "apk": [(judges.file, "/etc/alpine-release")],
    }

    for possible_m in possible_package_manager_names:
        for checks in os_info[possible_m]:
            t = checks[0]
            f = checks[1]
            if (t is judges.file and os.path.isfile(f)) or (
                t is judges.folder and os.path.isdir(f)
            ):
                return possible_m
    raise Exception("No supported package manager found")


class CheckMetadataHook(MetadataHookInterface):
    PLUGIN_NAME = "ckmetadata"

    def update(self, metadata: dict) -> None:
        # Check Dependencies
        try:
            current_package_manager = get_os_package_manager(supported_package_managers)
        except Exception as e:
            print(f"{e}")

        common_deps = ["requests", "click", "dataclasses", "rich", "trogon"]
        simulate_managers = {
            "apt": "tinyget.wrappers:sim_apt",
            "dnf": "tinyget.wrappers:sim_dnf",
            "pacman": "tinyget.wrappers:sim_pacman",
        }

        if current_package_manager == "apt":
            common_deps += []
            simulate_managers.pop("apt")
        elif current_package_manager == "dnf":
            common_deps += []
            simulate_managers.pop("dnf")
        elif current_package_manager == "pacman":
            common_deps += []
            simulate_managers.pop("pacman")
        else:
            print(f"{current_package_manager} not support in tinyget")
            common_deps += []

        metadata["dependencies"] = common_deps
        # Check entry points
        metadata["scripts"] = {"tinyget": "tinyget.main:cli"}
        metadata["scripts"].update(simulate_managers)
