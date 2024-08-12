import subprocess
import pytest


def test_subprocess_cmd():
    command = "ls"
    subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


if __name__ == "__main__":
    pytest.main([__file__])
