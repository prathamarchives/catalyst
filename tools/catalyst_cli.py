"""catalyst_cli.py — dev CLI for the Catalyst loop (the consumer uses the UI).

  init <name>                 scaffold a brain from templates
  guide <name>                print the next-step agent setup guide
  status                      list brains + readiness
  context <name> <task>       print the context packet (the headline primitive)
  route <name> <task>         show classification + routed files
  evaluate <name> <task> --output <file>
  feedback <name> <task> --feedback <text> [--output <file>]
  audit <name>                brain self-audit (thin/stale/duplicate + readiness)

--outputs-root overrides outputs/ (for tests/sandboxes). --json for machine output.
Stdlib only, local only. Thin layer over catalyst_core.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from catalyst_core import paths, registry, router, packet, evaluator, feedback, quality  # noqa: E402


def _root(args):
    return Path(args.outputs_root) if args.outputs_root else paths.OUTPUTS


def _emit(obj, as_json, human):
    print(json.dumps(obj, indent=2) if as_json else human)


def cmd_init(args):
    root = _root(args)
    dest = root / paths.slug(args.name)
    for sub in ["catalyst-brain", "skills", "workflows", "evals"]:
        shutil.copytree(paths.TEMPLATES / sub, dest / sub, dirs_exist_ok=True)
    (dest / "README.md").write_text(
        f"# {args.name} - Catalyst Brain\n\nScaffolded by `catalyst init`. "
        "This is not a usable brain yet. Fill it by giving this repo to your agent "
        "with REPO-USE-PROMPT.md, then run approved source extraction.\n", encoding="utf-8")
    _emit({"ok": True, "brain": f"outputs/{paths.slug(args.name)}"}, args.json,
          f"created scaffold at {dest}\n"
          "status: scaffold only - not a usable Catalyst Brain yet\n"
          f"next: run `catalyst guide {args.name}` and paste the setup prompt into your agent")


def cmd_guide(args):
    root = _root(args)
    slug = paths.slug(args.name)
    brain_path = root / slug
    repo = paths.REPO_ROOT
    prompt = (
        f"Read README.md, AGENTS.md, and REPO-USE-PROMPT.md in {repo}.\n"
        f"Build my Catalyst Brain under {brain_path}.\n"
        "First run tools/discover_sessions.py for read-only source discovery. "
        "Read .catalyst/permissions.json if it exists; otherwise ask one approval question "
        "(recommended safe scan, manual paths, or skip). Read contents only inside the approved scope.\n"
        "Write BUILD-STATUS.json while you work, then SUMMARY.md, catalyst-brain/, skills/, "
        "workflows/, evals/, and proposed-updates/. Do not overwrite templates/.\n"
        "When ready, use the loop on real tasks: context -> produce -> evaluate -> capture feedback -> audit."
    )
    obj = {"brain": str(brain_path), "repo": str(repo), "prompt": prompt}
    human = (
        f"brain path: {brain_path}\n"
        "status: the CLI scaffold is only a starting folder; the agent is the v0 builder.\n\n"
        "paste this into your agent:\n"
        f"{prompt}\n\n"
        "after the brain is built:\n"
        f"  catalyst context {args.name} \"<task>\"\n"
        f"  catalyst evaluate {args.name} \"<task>\" --output \"<draft text or file>\"\n"
        f"  catalyst audit {args.name}"
    )
    _emit(obj, args.json, human)


def cmd_status(args):
    rows = [{"name": b["name"], "ready": quality.audit_brain(b["name"], _root(args)).get("ready_score", 0.0)}
            for b in registry.list_brains(_root(args))]
    _emit({"brains": rows}, args.json, "\n".join(f"{r['name']}  ready={r['ready']}" for r in rows) or "(no brains)")


def cmd_route(args):
    r = router.route_task(args.name, args.task, _root(args))
    _emit(r, args.json, f"task_type: {r['task_type']} ({r['confidence']})\n"
                        f"load: {', '.join(r['files_to_load']) or '(none)'}\n"
                        f"warnings: {'; '.join(r['warnings']) or 'none'}")


def cmd_context(args):
    pkt = packet.build_context_packet(args.name, args.task, args.mode, _root(args))
    _emit({"packet": pkt}, args.json, pkt)


def cmd_evaluate(args):
    text = (Path(args.output).read_text(encoding="utf-8")
            if (args.output and Path(args.output).is_file()) else (args.output or ""))
    rep = evaluator.evaluate_output(args.name, args.task, text, args.mode, _root(args))
    _emit(rep, args.json, f"verdict: {rep['verdict']}\nscores: {rep['scores']}\nissues: {rep['issues']}")


def cmd_feedback(args):
    text = Path(args.output).read_text(encoding="utf-8") if (args.output and Path(args.output).is_file()) else ""
    res = feedback.capture_feedback(args.name, args.task, text, args.feedback, _root(args))
    human = ("\n".join("wrote: " + w for w in res["written"]) if res.get("ok") else f"error: {res.get('error')}")
    _emit(res, args.json, human)


def cmd_audit(args):
    rep = quality.audit_brain(args.name, _root(args))
    human = (f"ready: {rep.get('ready_score')}  ({rep.get('summary')})\n" +
             "\n".join(f"  {f}: {', '.join(v)}" for f, v in rep.get("flags", {}).items()))
    _emit(rep, args.json, human)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="catalyst", description="Run the Catalyst loop on a local brain.")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--outputs-root", help="override outputs/ root (tests/sandboxes)")
    common.add_argument("--json", action="store_true")
    common.add_argument("--mode", default="auto", choices=["auto", "quick", "full"])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", parents=[common]).add_argument("name")
    sub.add_parser("guide", parents=[common]).add_argument("name")
    sub.add_parser("status", parents=[common])
    for c in ("context", "route"):
        p = sub.add_parser(c, parents=[common])
        p.add_argument("name")
        p.add_argument("task")
    pe = sub.add_parser("evaluate", parents=[common])
    pe.add_argument("name")
    pe.add_argument("task")
    pe.add_argument("--output")
    pf = sub.add_parser("feedback", parents=[common])
    pf.add_argument("name")
    pf.add_argument("task")
    pf.add_argument("--feedback", required=True)
    pf.add_argument("--output")
    sub.add_parser("audit", parents=[common]).add_argument("name")
    args = ap.parse_args(argv)
    {"init": cmd_init, "guide": cmd_guide, "status": cmd_status, "route": cmd_route, "context": cmd_context,
     "evaluate": cmd_evaluate, "feedback": cmd_feedback, "audit": cmd_audit}[args.cmd](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
