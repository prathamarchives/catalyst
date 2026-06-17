"""Eval: the catalyst_core judgment flow works end-to-end and stays local-safe.

Checks (Phase 1 scope; docs checks added in Phase 2):
- core modules + dev CLI exist and import
- the router maps representative tasks to the right job type
- a context packet includes identity/standards/judgment + the agent judgment contract
- the evaluator returns a verdict in {ship,revise,reject,ask} with all five scores
- audit_brain returns a readiness score
- capture_feedback writes only under outputs/ and leaves a proposal
- templates/ is never written to
"""
import shutil
import sys
import tempfile
from pathlib import Path


def run(root: Path) -> list:
    failures = []
    sys.path.insert(0, str(root))
    try:
        from catalyst_core import router, packet, evaluator, feedback, quality, contract  # noqa: F401
    except Exception as exc:
        return [f"cannot import catalyst_core: {exc!r}"]

    for rel in ["catalyst_core/__init__.py", "catalyst_core/paths.py", "catalyst_core/registry.py",
                "catalyst_core/router.py", "catalyst_core/contract.py", "catalyst_core/packet.py",
                "catalyst_core/evaluator.py", "catalyst_core/feedback.py", "catalyst_core/quality.py",
                "tools/catalyst_cli.py"]:
        if not (root / rel).is_file():
            failures.append(f"missing flow file: {rel}")

    for task, jt in {"write a dm reply": "reply/dm",
                     "should i pivot the product": "strategy/decision",
                     "write a launch thread": "writing/content"}.items():
        got = router.classify_task(task)[0]
        if got != jt:
            failures.append(f"router: '{task}' -> {got}, expected {jt}")

    with tempfile.TemporaryDirectory() as td:
        outputs = Path(td) / "outputs"
        dest = outputs / "demo-flow-test"
        for sub in ["catalyst-brain", "skills", "workflows", "evals"]:
            shutil.copytree(root / "templates" / sub, dest / sub)
        name = "demo-flow-test"

        pkt = packet.build_context_packet(name, "write a launch post", "full", outputs_root=outputs)
        for need in ["identity.md", "standards.md", "judgment.md",
                     "## agent judgment contract", "## required evaluation"]:
            if need not in pkt:
                failures.append(f"context packet missing: {need}")

        ev = evaluator.evaluate_output(name, "write a launch post",
                                       "Unlock your seamless tapestry.", outputs_root=outputs)
        if ev["verdict"] not in ("ship", "revise", "reject", "ask"):
            failures.append(f"evaluator verdict invalid: {ev['verdict']}")
        for k in ["identity_alignment", "standards_match", "judgment_match", "taste_match", "anti_slop"]:
            if k not in ev["scores"]:
                failures.append(f"evaluator missing score: {k}")

        if "ready_score" not in quality.audit_brain(name, outputs_root=outputs):
            failures.append("audit_brain missing ready_score")

        fb = feedback.capture_feedback(name, "write a launch post", "draft", "too pitchy", outputs_root=outputs)
        if not fb.get("ok"):
            failures.append(f"feedback capture failed: {fb}")
        else:
            for w in fb["written"]:
                if not w.startswith("outputs/"):
                    failures.append(f"feedback wrote outside outputs/: {w}")
            if not list((dest / "proposals").glob("*-feedback-update.md")):
                failures.append("no proposal file written")

    if (root / "templates" / "proposals").exists():
        failures.append("templates/ was written to")
    return failures


if __name__ == "__main__":
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL catalyst_flow_check:", p)
    if not problems:
        print("PASS catalyst_flow_check")
    sys.exit(1 if problems else 0)
