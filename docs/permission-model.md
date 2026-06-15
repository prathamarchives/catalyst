# permission model

## Discovery

Automatic and read-only. The agent checks candidate locations and reports path metadata.

## Reading contents

Requires authorization:

- Mode A: user pre-authorized recommended safe scan
- Mode B: agent asks one approval question
- Manual: user names exact paths

Exclusions always apply: secrets, tokens, private DMs, client data, binaries, vendor/build folders, sensitive material.
