# -*- coding: utf-8 -*-

import subprocess
import sys
from pathlib import Path
import argparse
from win32 import win32process
import time


def check_process_is_alive(pid_file: Path) -> bool:
    with open(pid_file) as f:
        pid = int(f.read().strip("\r\n"))

    return pid in win32process.EnumProcesses()


def run_background_process(pid_file: Path) -> None:
    exe = Path(sys.executable)
    subprocess.Popen([str(exe.parent / "pythonw.exe"), "forever_loop.py"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("output_file", type=str)
    args = parser.parse_args()
    input_file, output_file = (
        Path(args.input_file).absolute(),
        Path(args.output_file).absolute(),
    )
    output_file.unlink(missing_ok=True)

    pid_file = Path("pid")
    if not pid_file.exists() or not check_process_is_alive(pid_file):
        pid_file.unlink(missing_ok=True)
        run_background_process(pid_file)

    ipc_dir = Path("ipc")
    if not ipc_dir.exists():
        ipc_dir.mkdir()

    wait_seconds = 0
    wait_unit = 0.01
    timeout = 5
    while True:
        if pid_file.exists():
            with open(ipc_dir / "args.txt", "w") as f:
                f.write(f"{input_file},{output_file}")
        if Path(output_file).exists():
            break
        if wait_seconds >= timeout:
            raise TimeoutError
        wait_seconds += wait_unit
        time.sleep(wait_unit)
