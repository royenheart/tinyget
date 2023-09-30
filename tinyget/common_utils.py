from typing import List, Dict, Union
import click
import json
import os

from .globals import global_configs


def get_os_package_manager(possible_package_manager_names: List[str]):
    paths = os.environ["PATH"].split(os.pathsep)
    for bin_path in paths:
        for package_manager_name in possible_package_manager_names:
            if package_manager_name in os.listdir(bin_path):
                return package_manager_name
    raise Exception("No supported package manager found in PATH")


def default_config_path():
    return os.path.join(os.environ.get("HOME"), ".tinyget.conf")


def get_configuration(
    path: str = None, key: Union[str, List[str]] = None
) -> Dict[str, str]:
    if path is None:
        path = default_config_path()
    # Normalize key to list or None
    if key is None:
        keys = None
    else:
        keys = key if isinstance(key, list) else [key]

    # If path does not exist
    # If key is None, return an empty dict
    if not os.path.exists(path):
        if keys is None:
            return {}
        else:
            return {key: None for key in keys}

    # Load configuration
    with open(path, "r") as f:
        broken_conf = False
        try:
            configs = json.load(f)
            if not isinstance(configs, dict):
                broken_conf = True
        except Exception:
            broken_conf = True

    if broken_conf and click.confirm(
        "Configuration file is invalid, delete it?", abort=True
    ):
        os.remove(path)
        configs = {}

    if keys is None:
        return configs
    else:
        return {key: configs[key] if key in configs else None for key in keys}


def set_configuration(path: str = None, conf: Dict = {}):
    if path is None:
        path = default_config_path()
    origin_config = get_configuration(path=path)
    for key, value in conf.items():
        origin_config[key] = value

    with open(path, "w") as f:
        json.dump(origin_config, f, indent=4)


def get_configuration_with_environ(path: str = None, key_environ: Dict[str, str] = {}):
    configs = get_configuration(path=path)
    result = {}
    for key, environ_name in key_environ.items():
        val = os.environ.get(environ_name)
        if val is not None:
            result[key] = val
            break

        val = global_configs.get(key)
        if val is not None:
            result[key] = val
            break

        result[key] = configs.get(key)

    return result


if __name__ == "__main__":
    set_configuration(conf={"host": "https://api.openai.com", "okok": "okok"})
