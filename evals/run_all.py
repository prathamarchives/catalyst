from __future__ import annotations

from pathlib import Path

from core_kernel_check import run as run_core_kernel_check


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = run_core_kernel_check(root)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print("RESULT: FAIL")
        return 1
    print("PASS: core_kernel_check")
    print("RESULT: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

