# privacy

Catalyst is local-first and permission-gated.

- local-first: everything is built in files on your machine
- you control the scan and the files: discovery finds candidate paths, but contents are read only inside the scope you approve or pre-authorize
- discovery is read-only path checking; printed local paths are path metadata
- file contents are read only inside authorized scope
- exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, and sensitive material
- generated outputs live under `outputs/<name>/` and are gitignored
- no cloud upload by default: this repo itself makes no network calls or cloud uploads
- hosted-provider caveat: your agent/model provider may receive approved context; check that tool's privacy policy before approving sensitive material
- review before sharing: read through every generated file before committing, posting, or sending it anywhere

## Optional surfaces

- the local control panel (`apps/control-panel/`) binds `127.0.0.1` only, exposes no shell endpoint, confines file operations to allowlisted roots, writes only under `outputs/`, never writes `templates/`, and never returns a BYOK key to the browser
- BYOK is optional and off by default. With no key, the panel runs in mock mode and makes no network call. Enabling BYOK is the only path that sends approved text to a chosen model provider; the key is read from an environment variable only and is never committed (`.env` and `.catalyst/` are gitignored)
- context you paste or import in the Context step is written only under `outputs/<name>/sources/` (gitignored). It is not sent anywhere unless you enable a live provider and trigger an assisted action on it
- agent connection detection checks only whether a CLI exists on PATH (`shutil.which`); it never runs the CLI and never reads its data
- the MCP scaffold (`tools/mcp_server.py`) is local-only stdio with no network; it reads only the brain and writes only via feedback append / proposals, never overwriting the brain
