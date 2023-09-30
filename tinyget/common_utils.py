from typing import List, Dict, Union
import click
import pwd
import json
import os
from contextlib import contextmanager

from .globals import global_configs


def get_os_package_manager(possible_package_manager_names: List[str]):
    """
    Returns the first supported package manager found in the system's PATH environment variable.

    Parameters:
        possible_package_manager_names (List[str]): A list of possible package manager names to search for.

    Returns:
        str: The name of the first supported package manager found in the system's PATH environment variable.

    Raises:
        Exception: If no supported package manager is found in the system's PATH environment variable.
    """
    paths = os.environ["PATH"].split(os.pathsep)
    for bin_path in paths:
        for package_manager_name in possible_package_manager_names:
            if package_manager_name in os.listdir(bin_path):
                return package_manager_name
    raise Exception("No supported package manager found in PATH")


@contextmanager
def impersonate(username=os.environ.get("SUDO_USER")):
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

    if need_impersonate:
        home_dir = user_info.pw_dir
    else:
        home_dir = os.environ["HOME"]
    config_path = os.path.join(home_dir, ".tinyget.conf")
    try:
        yield config_path
    finally:
        if need_impersonate:
            if os.path.exists(config_path):
                os.chown(config_path, user_info.pw_uid, user_info.pw_gid)


def get_configuration(
    path: str = None, key: Union[str, List[str]] = None
) -> Dict[str, str]:
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
    with impersonate() as default_config_path:
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


def set_configuration(path: str = None, conf: Dict = {}):
    """
    Set the configuration by updating the specified path with the given configuration.

    Parameters:
    - path (str): The path to the configuration file. If not provided, the default configuration path will be used.
    - conf (Dict): The configuration to update. It is a dictionary where the keys represent the configuration keys and the values represent the new values.

    Returns:
    None
    """
    with impersonate() as default_config_path:
        if path is None:
            path = default_config_path
        origin_config = get_configuration(path=path)
        for key, value in conf.items():
            origin_config[key] = value

        with open(path, "w") as f:
            json.dump(origin_config, f, indent=4)


def get_configuration_with_environ(path: str = None, key_environ: Dict[str, str] = {}):
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


if __name__ == "__main__":
    # set_configuration(conf={"host": "https://api.openai.com", "okok": "okok"})
    with impersonate() as default_config_path:
        print(default_config_path)
        with open(default_config_path, "w") as f:
            f.write("??????")
        input("continue?")
