import os
import subprocess
import sys


def main():
    base_path = os.path.dirname(__file__)

    if os.name == 'nt':
        script_name = "dynawo-algorithms.cmd"
    else:
        script_name = "dynawo-algorithms.sh"

    script_path = base_path / script_name

    if not script_path.exists():
        print(f"Error: Dynawo algorithms binary not found at {script_path}")
        print("This package might have been built for a different Operating System.")
        sys.exit(1)

    subprocess.run([script_path] + sys.argv[1:])