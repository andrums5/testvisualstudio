from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable or "python"


def run(cmd):
    print("$", " ".join(cmd))
    res = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(res.stderr.strip())
    print("EXIT:", res.returncode)
    print("-" * 60)


def py_utf8(*args: str) -> list[str]:
    # Fuerza UTF-8 en los procesos hijo para evitar problemas en Windows
    return [PY, "-X", "utf8", *args]


def main():
    tp = str(ROOT / "test.py")
    run(py_utf8(tp, "-h"))  # ayuda
    run(py_utf8(tp, "text", "Hola hola mundo, mundo mundo!", "--top", "2"))  # texto
    run(
        py_utf8(
            tp,
            "stats",
            "--file",
            str(ROOT / "datasets" / "numbers.txt"),
            "--bins",
            "5",
        )
    )  # stats desde archivo
    run(py_utf8(tp, "path", "--edges", "A-B:3,B-C:4,A-C:10", "--start", "A", "--end", "C"))  # grafo
    run(py_utf8(tp, "async", "0.2", "0.1", "0.05"))  # async
    run(py_utf8(tp, "cache", "30"))  # cache
    run(py_utf8(tp, "doctest"))  # doctest


if __name__ == "__main__":
    main()
