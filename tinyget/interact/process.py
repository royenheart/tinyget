from typing import List, Union
import subprocess


class Process(object):
    def __init__(self, args: Union[List[str], str], interactive: bool = False):
        # If args is a string, assume it is a shell command
        # If args is a list, assume it is a list of arguments
        if not interactive:
            self.p = subprocess.Popen(
                args=args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                close_fds=True,
                bufsize=0,
                shell=isinstance(args, str),
            )
        else:
            self.p = subprocess.Popen(
                args=args,
                close_fds=True,
                shell=isinstance(args, str),
            )

    def recv_til_end(self, timeout: int = None):
        stdout, stderr = self.p.communicate(input=None, timeout=timeout)
        return stdout.decode(), stderr.decode()


if __name__ == "__main__":
    p = Process("apt list")
    print(p.recv_til_end())
