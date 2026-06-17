"""Eval: v0.3 agent-native onboarding stays honest.

Guards:
- the control panel connects an AI/agent BEFORE identity onboarding
- connectors are labeled export/drop/paths, not faked live OAuth
- mock mode is never presented as live AI
- the MCP scaffold is documented with its five tools and called a scaffold
- the agent connection idea is established in docs/UI
"""
from pathlib import Path

STATIC = "apps/control-panel/static"


def _read(root: Path, rel: str) -> str:
    p = root / rel
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def run(root: Path) -> list:
    failures = []
    index = _read(root, f"{STATIC}/index.html")
    appjs = _read(root, f"{STATIC}/app.js")
    readme = _read(root, "README.md").lower()
    onboarding = _read(root, "docs/local-onboarding.md").lower()
    mcp = _read(root, "docs/mcp.md")
    corpus = "\n".join([index, appjs, readme, onboarding]).lower()

    # 1. connect-AI stage exists and comes before identity in the UI
    ci = index.find('data-stage="connect"')
    ii = index.find('data-stage="identity"')
    if ci == -1:
        failures.append("UI has no 'connect' stage")
    elif ii == -1:
        failures.append("UI has no 'identity' stage")
    elif ci > ii:
        failures.append("UI puts identity before connecting an AI/agent")

    # 2. the agent-first idea is established
    if not any(m in corpus for m in ["connect an ai", "connect ai", "connect an agent", "connect a model"]):
        failures.append("agent-first framing ('connect an AI') missing from UI/docs")

    # 3. no faked live OAuth for connectors
    low_static = (index + "\n" + appjs).lower()
    for bad in ["sign in with notion", "connect notion account", "oauth", "log in with slack", "connect with discord"]:
        if bad in low_static:
            failures.append(f"UI implies a live connector that is not implemented: '{bad}'")
    # connectors must be present AND labeled as export/drop/paths
    if "notion" in low_static and "export" not in low_static:
        failures.append("connector cards present but not labeled export/drop/paths")

    # 4. mock honesty: mock must be marked as demo/not-live somewhere in the UI
    if "mock" in low_static and not any(m in low_static for m in ["not live", "demo", "no network", "preview"]):
        failures.append("mock mode is not clearly distinguished from live AI")

    # 5. MCP scaffold documented honestly with its five tools
    if not mcp:
        failures.append("docs/mcp.md missing")
    else:
        ml = mcp.lower()
        if "scaffold" not in ml:
            failures.append("docs/mcp.md does not call the MCP server a scaffold")
        for tool in ["list_brain_sections", "read_brain_section",
                     "review_output_against_brain", "append_feedback", "propose_brain_update"]:
            if tool not in mcp:
                failures.append(f"docs/mcp.md missing MCP tool: {tool}")

    # 6. MCP server must not overwrite the brain silently
    server = _read(root, "tools/mcp_server.py")
    if server and "propose_brain_update" in server and "proposed-updates" not in server:
        failures.append("MCP propose_brain_update should write proposals, not overwrite the brain")

    return failures


if __name__ == "__main__":
    import sys
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL agent_native_check:", p)
    if not problems:
        print("PASS agent_native_check")
    sys.exit(1 if problems else 0)
