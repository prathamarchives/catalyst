# eval loop

Catalyst evals are task-time checks, not staged demos.

They help the agent ask:

- does this output match identity?
- does it meet standards?
- does judgment say ship, revise, reject, or ask?
- did feedback reveal a missing rule?
- should a checklist catch this failure next time?

Repo evals in `evals/` keep the protocol coherent. Generated evals in `outputs/<name>/evals/` keep the user's agent improving.
