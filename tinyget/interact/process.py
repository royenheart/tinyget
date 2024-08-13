from typing import List, Optional, Union
from tinyget.common_utils import logger
import subprocess
import os


class CommandExecutionError(Exception):
    def __init__(self, message: str, args: list, envp: dict, stdout: str, stderr: str):
        """
        Initializes a new instance of the class.

        Parameters:
            message (str): The error message.
            args (list): The arguments passed to the function.
            envp (dict): The environment variables.
            stdout (str): The standard output.
            stderr (str): The standard error.

        Returns:
            None
        """
        super().__init__(message)
        logger.debug(message)
        self.args = tuple(args)
        self.envp = envp
        self.stdout = stdout
        self.stderr = stderr


def spawn(args: Union[List[str], str], envp: dict = {}):
    """
    Spawns a new process with the given arguments and environment variables.

    Args:
        args (Union[List[str], str]): If args is a string, assume it is a shell command.
                                      If args is a list, assume it is a list of arguments.
        envp (dict, optional): A dictionary containing additional environment variables
                               to be passed to the spawned process. Defaults to {}.

    Returns:
        subprocess.Popen: A subprocess.Popen object representing the spawned process.

    """
    # If args is a string, assume it is a shell command
    # If args is a list, assume it is a list of arguments
    orig_envp = dict(os.environ)
    for k, v in envp.items():
        orig_envp[k] = v
    return subprocess.Popen(
        args=args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        close_fds=True,
        env=orig_envp,
        bufsize=0,
        shell=isinstance(args, str),
    )


def execute_command(
    args: Union[List[str], str], envp: dict = {}, timeout: Optional[float] = None
):
    """
    Execute a command and capture its stdout and stderr.

    Args:
        args (Union[List[str], str]): The command to be executed. It can be a list of arguments or a single string.
        envp (dict, optional): The environment variables to be passed to the command. Defaults to an empty dictionary.
        timeout (int, optional): The maximum number of seconds to wait for the command to complete. Defaults to None.

    Returns:
        Tuple[str, str]: A tuple containing the stdout and stderr of the executed command.

    Raises:
        CommandExecutionError: If the command execution fails, an exception is raised with details about the command, environment variables, stdout, and stderr.
    """
    p = spawn(args, envp)
    stdout, stderr = p.communicate(input=None, timeout=timeout)
    if p.returncode != 0:
        raise CommandExecutionError(
            message=f"Executing command failed {args} with {envp}",
            args=list(args),
            envp=envp,
            stdout=stdout.decode(),
            stderr=stderr.decode(),
        )
    return stdout.decode(), stderr.decode()


def just_execute(args: Union[List[str], str]):
    command_str = args if isinstance(args, str) else " ".join(args)
    os.system(command_str)


if __name__ == "__main__":
    execute_command("apt install ojbk")
