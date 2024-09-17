import re
import termios
from typing import List, Optional, Union
from tempfile import mktemp
import click
from tinyget.common_utils import logger
from concurrent.futures import ThreadPoolExecutor
import subprocess
import os
import asyncio
import sys
import select

# two workers: read_subprocess_output / read_input
executor = ThreadPoolExecutor(max_workers=4)


def non_blocking_input(proc: subprocess.Popen, fd: Optional[int] = None):
    while proc.poll() is None:
        r, _, _ = select.select([sys.stdin if fd is None else fd], [], [], 0.1)

        if r:
            k = sys.stdin.readline().strip()
            return k
    return ""


async def read_subprocess_output(master_fd: int):
    try:
        return await asyncio.get_running_loop().run_in_executor(
            executor=executor, func=lambda: os.read(master_fd, 1024).decode()
        )
    except Exception:
        raise


async def read_subprocess_err(errfd: int):
    try:
        return await asyncio.get_running_loop().run_in_executor(
            executor=executor,
            func=lambda: os.read(errfd, 1024).decode(),
        )
    except Exception:
        raise


async def read_input(proc: subprocess.Popen, master_fd: int):
    while proc.poll() is None:
        try:
            user_input = await asyncio.get_event_loop().run_in_executor(
                executor=executor,
                func=lambda: non_blocking_input(proc=proc),
            )
        except Exception as e:
            break
        try:
            os.write(master_fd, (user_input + "\n").encode())
        except Exception as e:
            break


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


def spawn(
    args: Union[List[str], str],
    envp: dict = {},
    cwd: Optional[str] = None,
    text: Optional[bool] = None,
    stdoutfd: Optional[int] = None,
    stderrfd: Optional[int] = None,
    stdinfd: Optional[int] = None,
):
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
        stdout=subprocess.PIPE if stdoutfd is None else stdoutfd,
        stderr=subprocess.PIPE if stderrfd is None else stderrfd,
        stdin=subprocess.PIPE if stdinfd is None else stdinfd,
        close_fds=True,
        env=orig_envp,
        bufsize=0,
        cwd=cwd,
        shell=isinstance(args, str),
        text=text,
    )


async def async_execute_command(
    proc: subprocess.Popen,
    master_fd: int,
    slave_fd: int,
    err_read_fd: int,
    err_write_fd: int,
):
    output_list = []
    err_list = []
    read_task = asyncio.create_task(read_input(proc, master_fd))
    while proc.poll() is None:
        try:
            disa = await asyncio.wait_for(read_subprocess_output(master_fd), timeout=1)
        except Exception as e:
            disa = None
        try:
            derr = await asyncio.wait_for(read_subprocess_err(err_read_fd), timeout=0.5)
        except Exception as e:
            derr = None
        if disa:
            output_list.append(disa)
            click.echo(disa, nl=False)
        if derr:
            err_list.append(derr)
            click.echo(derr, nl=False)

    pstderr = "".join(err_list)
    pretcode = proc.returncode

    os.close(slave_fd)
    os.close(master_fd)
    os.close(err_write_fd)
    os.close(err_read_fd)

    proc.terminate()
    read_task.cancel()

    return (output_list, pstderr, pretcode)


def execute_command(
    args: Union[List[str], str],
    envp: dict = {},
    timeout: Optional[float] = None,
    cwd: Optional[str] = None,
    realtime_output=False,
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
    if realtime_output:
        master_fd, slave_fd = os.openpty()
        attrs = termios.tcgetattr(slave_fd)
        # disable auto translate breaklines (NL to CRNL or something else to match the current platform)
        # https://stackoverflow.com/questions/1552749/difference-between-cr-lf-lf-and-cr-line-break-types
        # NL stands for New Line, it's the abstraction of the new line character
        # CR stands for Carriage Return
        # LF stands for Line Feed
        attrs[1] = attrs[1] & ~termios.ONLCR
        termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)
        stderrf_str = mktemp()
        logger.debug(f"stderr output file: {stderrf_str}")
        stderr_fi = open(stderrf_str, "w+")
        stderr_fd = stderr_fi.fileno()
        stderr_read_fi = open(stderrf_str, "r")
        stderr_read_fd = stderr_read_fi.fileno()
        p = spawn(
            args,
            envp,
            cwd,
            text=True,
            stdoutfd=slave_fd,
            stdinfd=slave_fd,
            stderrfd=stderr_fd,
        )
        output_list, pstderr, pretcode = asyncio.run(
            async_execute_command(p, master_fd, slave_fd, stderr_read_fd, stderr_fd)
        )
        # use regex to delete wrong escape sequences
        # https://stackoverflow.com/questions/15011478/ansi-questions-x1b25h-and-x1be
        output_list = [re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", x) for x in output_list]
        poutput = "".join(output_list)
        return poutput, pstderr, pretcode
    else:
        p = spawn(args, envp, cwd)
        stdout, stderr = p.communicate(input=None, timeout=timeout)
        return stdout.decode(), stderr.decode(), p.returncode


def just_execute(args: Union[List[str], str]):
    command_str = args if isinstance(args, str) else " ".join(args)
    os.system(command_str)


if __name__ == "__main__":
    execute_command("apt install ojbk")
