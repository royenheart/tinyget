from typing import List, Union
import subprocess
import os


class CommandExecutionError(Exception):
    def __init__(self, message, args, envp, stdout, stderr):
        super().__init__(message)
        print(message)
        self.args = args
        self.envp = envp
        self.stdout = stdout
        self.stderr = stderr


def spawn(args: Union[List[str], str], envp: dict = {}):
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


def execute_command(args: Union[List[str], str], envp: dict = {}, timeout: int = None):
    p = spawn(args, envp)
    stdout, stderr = p.communicate(input=None, timeout=timeout)
    if p.returncode != 0:
        raise CommandExecutionError(
            message=f"Executing command failed {args} with {envp}",
            args=args,
            envp=envp,
            stdout=stdout.decode(),
            stderr=stderr.decode(),
        )
    return stdout.decode(), stderr.decode()


if __name__ == "__main__":
    execute_command("apt install ojbk")
