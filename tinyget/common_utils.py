from typing import List
import os


def get_os_package_manager(possible_package_manager_names: List[str]):
    paths = os.environ["PATH"].split(os.pathsep)
    for bin_path in paths:
        for package_manager_name in possible_package_manager_names:
            if package_manager_name in os.listdir(bin_path):
                return package_manager_name
    raise Exception("No supported package manager found in PATH")
