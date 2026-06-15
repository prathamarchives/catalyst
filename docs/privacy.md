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
