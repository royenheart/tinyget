from enum import Enum
from typing import List, Dict, Optional, Union
import click
import pwd
import json
import os
import logging
from contextlib import contextmanager

from .globals import global_configs


def get_os_package_manager(possible_package_manager_names: List[str]):
    """
    Returns the supported package manager in current system.

    Parameters:
        possible_package_manager_names (List[str]): A list of possible package manager names to search for.

    Returns:
        str: The name of the first supported package manager found in the system's PATH environment variable.

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


def get_path_parts(path: str):
    path = os.path.normpath(path)
    path_list = []
    while path != "/":
        path_list.append(path)
        path = os.path.dirname(path)
    path_list.append("/")
    return path_list


logger = logging.getLogger()


def setup_logger(debug: bool):
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s - %(name)s: %(message)s",
        )
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s %(levelname)s - %(name)s: %(message)s",
        )


def setup_logger_level(level: str):
    logging.basicConfig(
        level=str_to_log_level(level),
        format="%(asctime)s %(levelname)s - %(name)s: %(message)s",
    )


def str_to_log_level(level: str):
    level = level.upper()
    if level == "CRITICAL":
        return logging.CRITICAL
    elif level == "FATAL":
        return logging.FATAL
    elif level == "ERROR":
        return logging.ERROR
    elif level == "WARNING":
        return logging.WARNING
    elif level == "WARN":
        return logging.WARN
    elif level == "INFO":
        return logging.INFO
    elif level == "DEBUG":
        return logging.DEBUG
    elif level == "NOTSET":
        return logging.NOTSET
    else:
        return logging.INFO


@contextmanager
def impersonate(
    username=os.environ.get("SUDO_USER"), config_path: Optional[str] = None
):
    """
    This code snippet defines a context manager function called impersonate. When used with the with statement, it temporarily impersonates a specified user by changing the current user and group IDs.
    If a username is provided, the function checks if the current user ID or group ID is different from the specified user's ID or group's ID. If they are different, the function changes the current user and group IDs to the specified user's IDs.
    After changing the user and group IDs, the function yields the path to a configuration file (config_path).
    Once the with block is exited, the function checks if the user was initially impersonated. If so, it changes the ownership of the configuration file to the impersonated user.

    Args:
        username (str, optional): The username to impersonate. Defaults to the value of the "SUDO_USER" environment variable.

    Yields:
        str: The path to the configuration file.

    Raises:
        OSError: If the specified user does not exist.
    """

    if username is None:
        need_impersonate = False
    else:
        original_uid = os.geteuid()
        original_gid = os.getegid()
        user_info = pwd.getpwnam(username)

        need_impersonate = (
            original_uid != user_info.pw_uid or original_gid != user_info.pw_gid
        )

    if config_path is None:
        if need_impersonate:
            home_dir = user_info.pw_dir
        else:
            home_dir = os.environ["HOME"]
        config_path = os.path.join(home_dir, ".config", "tinyget", "config.json")

    not_exists = []
    for sub_path in get_path_parts(config_path):
        if not os.path.exists(sub_path):
            not_exists.append(sub_path)
    try:
        yield config_path
    finally:
        if need_impersonate:
            for path in not_exists:
                if os.path.exists(path):
                    # Change ownership of the newly created config file to the impersonated user
                    os.chown(path, user_info.pw_uid, user_info.pw_gid)

        if len(not_exists) > 0 and os.path.exists(config_path):
            # This means the config file does not exist
            # Change permissions of the newly created config file to 600
            os.chmod(config_path, 0o600)


def get_configuration(
    path: Optional[str] = None, key: Optional[Union[str, List[str]]] = None
) -> Dict[str, Optional[str]]:
    """
    Retrieves the configuration from a specified path and returns the values
    corresponding to the given key(s).

    Args:
        path (str, optional): The path to the configuration file. If not provided,
            the default configuration path will be used.
        key (str or list of str, optional): The key(s) to retrieve the values for.
            If not provided, all configuration values will be returned.

    Returns:
        dict: A dictionary containing the configuration values. If the path does not
            exist, an empty dictionary will be returned. If the key is not found, the
            value will be set to None.

    Raises:
        None
    """
    with impersonate(config_path=path) as default_config_path:
        if path is None:
            path = default_config_path
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


def get_config_path(path: Optional[str] = None) -> str:
    with impersonate(config_path=path) as default_config_path:
        if path is None:
            path = default_config_path
    return path


def set_configuration(path: Optional[str] = None, conf: Dict = {}):
    """
    Set the configuration by updating the specified path with the given configuration.

    Parameters:
    - path (str): The path to the configuration file. If not provided, the default configuration path will be used.
    - conf (Dict): The configuration to update. It is a dictionary where the keys represent the configuration keys and the values represent the new values.

    Returns:
    None
    """
    with impersonate(config_path=path) as default_config_path:
        if path is None:
            path = default_config_path
        origin_config = get_configuration(path=path)
        for key, value in conf.items():
            origin_config[key] = value

        dir_path = os.path.dirname(path)
        os.makedirs(dir_path, exist_ok=True)
        with open(path, "w") as f:
            json.dump(origin_config, f, indent=4)


def get_configuration_with_environ(
    path: Optional[str] = None, key_environ: Dict[str, str] = {}
):
    """
    This code defines a function get_configuration_with_environ that retrieves configuration values from multiple sources and returns them as a dictionary. The function takes two parameters: path, which is the path to the configuration file (if not provided, the default configuration file is used), and key_environ, which is a dictionary mapping configuration keys to environment variable names. The function first gets the configuration values from the specified file or the default file. Then, for each key in key_environ, it checks if there is a corresponding environment variable with the given name. If found, the value is added to the result dictionary. If not found, it checks if there is a global configuration value for the key. If found, the value is added to the result dictionary. If neither the environment variable nor the global configuration value is found, the value from the configuration file is added to the result dictionary. Finally, the function returns the resulting dictionary.

    Parameters:
        path (str): The path to the configuration file. If not provided, the default configuration file will be used.
        key_environ (Dict[str, str]): A dictionary mapping configuration keys to environment variable names.

    Returns:
        Dict[str, Any]: A dictionary containing the configuration values. The keys are the configuration keys, and the values are the corresponding values retrieved from the configuration file, environment variables, or global configuration.

    """
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


def strip_str_lines(orig: str) -> str:
    origs = orig.split("\n")
    return "\n".join([x.strip() for x in origs])
