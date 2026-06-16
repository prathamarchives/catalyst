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
