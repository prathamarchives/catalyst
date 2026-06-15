# INSTALL

Catalyst has no package install. It is a markdown protocol that an agent runs.

Do not stop at clone. Cloning/opening the repo is only step one; the protocol install is complete only after setup has run and `outputs/<name>/` contains the Catalyst Brain, skills, workflows, evals, and first task-time evaluation loop.

## Install means

1. receive the GitHub repo link / repo URL, then clone or open this repo
2. read `README.md` and `AGENTS.md`
3. optionally run verification with `python evals/run_all.py` or `py evals/run_all.py`
4. run setup: discover candidate local sources with `tools/discover_sessions.py`
5. determine authorization mode:
   - autonomous authorized mode: if the user pre-authorized the recommended scan, proceed without a second approval
   - cautious approval mode: ask one approval question — approve recommended scan, edit scope, or manual mode
6. read contents only inside the approved scope / authorized scope
7. build `outputs/<name>/` from templates
8. write skills/workflows/evals
9. run the first real task through task-time evaluation
10. update the Catalyst Brain from feedback

## Permission-block handling

If content access is blocked or authorization is unclear, stop before reading file contents and ask for approval, edited scope, or manual mode. Exclusions always bind under authorization: secrets, tokens, private DMs, client data, binaries, vendor/build folders, and sensitive material stay excluded.

## Minimal user burden

The user burden should be almost no path hunting: the agent discovers candidate locations, recommends a safe scan preset, asks only for approval/feedback when needed, and then runs setup.

## Privacy

Discovery is read-only. Content scanning is authorized. Exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, and sensitive material. Outputs are gitignored. Hosted model/provider tools may receive approved context.

## Verify

```txt
python evals/run_all.py
py evals/run_all.py
```
