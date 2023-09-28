import subprocess

command = "while true; do ls; sleep 1; done"
p = subprocess.Popen(
    command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
