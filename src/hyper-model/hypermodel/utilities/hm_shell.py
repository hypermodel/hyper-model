from typing import Dict, Tuple
import subprocess
import os


def sh(
    cmd: str, cwd: str = ".", env=None, debug: bool = False, ignore_error: bool = False
) -> Tuple[int, str, str]:
    """
        Execures a shell command using 'subprocess.Popen', returning a tuple
    """
    if env is None:
        env = os.environ

    try:
        print(f"> {cmd} (in {cwd})")

        channel = subprocess.Popen(
            [cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            encoding="utf-8",
            cwd=cwd,
        )

        stdout, stderr = channel.communicate()
        success = channel.returncode == True

        if channel.returncode == 0:
            return (channel.returncode, stdout, stderr)

        if not ignore_error:
            if debug == True or channel.returncode != 0:
                print(f"    return_code: {channel.returncode}")
                print(f"    out: {stdout}")
                print(f"    err: {stderr}")

    except Exception as e:
        if not ignore_error:
            error_message = str(e)
            print(f"> {cmd} Failed: {error_message}")
            return (False, error_message, error_message)

    return (channel.returncode, stdout, stderr)
