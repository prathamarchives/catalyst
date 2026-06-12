# privacy

A Creative Brain is intimate by design — it holds how you think, talk, and judge. The repo treats that accordingly.

## local-first

Everything runs on your machine, in your files. The markdown protocol makes no network calls and requires no API keys, no accounts, no telemetry. (Your agent itself may call a model API — that's between you and your agent vendor; this repo adds nothing on top.)

## you control what gets read

The agent *discovers* candidate locations automatically — that's the point; you shouldn't have to know where Cursor hides its chat history. But discovery is not reading. The discovery helper only checks which known paths exist and shows you the list. The agent reads contents only inside the scope you approve, and never beyond it. You can shrink the scope, expand it, or skip discovery entirely and point at files yourself.

So the honest version of the promise is: it discovers likely places your sessions/workspaces live, then reads only the locations you say yes to. Nothing is collected silently by this repo.

Important caveat: the discovery output contains local path metadata (for example, which tools/folders exist on your machine). If you run this through a hosted agent/model, that path list and any approved context may be sent to that provider. This repo itself makes no network calls, but your agent/model may. Check your tool's privacy policy before approving sensitive locations.

## no cloud upload by default

Nothing this protocol produces leaves your machine unless you deliberately move it.

## outputs are gitignored

`.gitignore` excludes `outputs/**` by default, so your generated brain never lands in a commit accidentally. If you want to publish your brain (some people will — it's a portfolio of taste), that's a deliberate act: remove the ignore rule for your folder, review every file, then commit.

## what not to feed it

Do not include in source material — or flag for the agent to skip:

- secrets: API keys, tokens, passwords, .env contents
- client data and anything under NDA
- private DMs and other people's messages, unless you have a real reason and their context in mind
- financial/medical/identity documents

The protocol instructs agents to skip and flag this material rather than copy it into a brain. But the user is the last line: you know what's sensitive in your world.

## review before sharing

Before sending a brain (or this repo with your outputs in it) to anyone — collaborator, client, the internet — read through every generated file. Extraction is thorough by design; make sure nothing personal rode along that you didn't intend.
