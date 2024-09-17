import subprocess
import pytest


def test_cli_help():
    command = "tinyget --no-live-output --help"
    p = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    exit_code = p.returncode
    assert exit_code == 0, f"'tinyget --help' failed: {err.decode()}"


def test_cli_search():
    command = "tinyget --no-live-output search vim"
    p = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    exit_code = p.returncode
    assert exit_code == 0, f"'tinyget search vim' failed: {err.decode()}"


def test_cli_list():
    command = "tinyget --no-live-output list"
    p = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    exit_code = p.returncode
    assert exit_code == 0, f"'tinyget list' failed: {err.decode()}"


if __name__ == "__main__":
    pytest.main([__file__])
