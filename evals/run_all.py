import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import repo_structure_check
import content_slop_check
import protocol_completeness_check
import privacy_check
import install_protocol_check
import output_consistency_check
import agent_runnability_static_check
import vision_fit_check
import task_time_evaluation_check
import positioning_check
import local_first_ui_check
import agent_native_check
import catalyst_flow_check
import hybrid_runtime_check

EVALS = [
    ("repo_structure_check", repo_structure_check),
    ("content_slop_check", content_slop_check),
    ("protocol_completeness_check", protocol_completeness_check),
    ("privacy_check", privacy_check),
    ("install_protocol_check", install_protocol_check),
    ("output_consistency_check", output_consistency_check),
    ("agent_runnability_static_check", agent_runnability_static_check),
    ("vision_fit_check", vision_fit_check),
    ("task_time_evaluation_check", task_time_evaluation_check),
    ("positioning_check", positioning_check),
    ("local_first_ui_check", local_first_ui_check),
    ("agent_native_check", agent_native_check),
    ("catalyst_flow_check", catalyst_flow_check),
    ("hybrid_runtime_check", hybrid_runtime_check),
]

def main() -> int:
    root = Path(__file__).resolve().parent.parent
    any_failed = False
    for name, module in EVALS:
        try:
            failures = module.run(root)
        except Exception as exc:
            failures = [f"eval crashed: {exc!r}"]
        if failures:
            any_failed = True
            print(f"FAIL {name}")
            for failure in failures:
                print(f"  - {failure}")
        else:
            print(f"PASS {name}")
    print()
    print("RESULT: FAIL" if any_failed else "RESULT: ALL PASS")
    return 1 if any_failed else 0

if __name__ == "__main__":
    sys.exit(main())
