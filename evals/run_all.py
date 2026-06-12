"""Run every script eval. Exit 0 only if all pass.

Usage:
    python evals/run_all.py
    py evals/run_all.py        (Windows launcher)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import repo_structure_check
import content_slop_check
import protocol_completeness_check
import privacy_check
import example_proof_check
import agent_runnability_static_check

EVALS = [
    ("repo_structure_check", repo_structure_check),
    ("content_slop_check", content_slop_check),
    ("protocol_completeness_check", protocol_completeness_check),
    ("privacy_check", privacy_check),
    ("example_proof_check", example_proof_check),
    ("agent_runnability_static_check", agent_runnability_static_check),
]


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    any_failed = False

    for name, module in EVALS:
        try:
            failures = module.run(root)
        except Exception as exc:  # an eval crashing is itself a failure
            failures = ["eval crashed: %r" % exc]
        if failures:
            any_failed = True
            print("FAIL %s" % name)
            for failure in failures:
                print("  - %s" % failure)
        else:
            print("PASS %s" % name)

    print()
    if any_failed:
        print("RESULT: FAIL")
        return 1
    print("RESULT: ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
