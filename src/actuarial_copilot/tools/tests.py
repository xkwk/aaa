from __future__ import annotations

import subprocess
import sys


def run_tests(test_path: str = "tests") -> dict:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", test_path],
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "status": "pass" if result.returncode == 0 else "fail",
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

