# permission model

## Discovery

Automatic and read-only. The agent checks candidate locations and reports path metadata.

## Reading contents

Requires authorization:

- Mode A: user pre-authorized recommended safe scan
- Mode B: agent asks one approval question
- Manual: user names exact paths

Exclusions always apply: secrets, tokens, private DMs, client data, binaries, vendor/build folders, sensitive material.

## Control panel file operations

The optional local control panel enforces the same model in code:

- discovery endpoint is read-only and returns source *categories*, never file contents
- reads are confined to `outputs/`, `templates/`, `docs/`, `prompts/`
- writes are confined to `outputs/` and the local-only `.catalyst/` config — `templates/` are never written
- path traversal is rejected; every path is resolved and checked against the allowlisted roots
- no shell or arbitrary-filesystem endpoint exists
- the panel binds localhost only; a non-local bind requires a bearer token
- pasted/imported context is written only under `outputs/<name>/sources/`; filenames are sanitized and confined to `outputs/`
- agent detection is existence-only (`shutil.which`); no CLI is executed and no user input is run as a command

## MCP server (`tools/mcp_server.py`)

- local-only stdio JSON-RPC; no network
- read access limited to `outputs/<name>/catalyst-brain/*.md`
- the only write paths are `append_feedback` (→ `feedback-memory.md`) and `propose_brain_update` (→ `proposed-updates/`), confined to `outputs/`
- the brain is never silently overwritten; updates land as proposals for review
