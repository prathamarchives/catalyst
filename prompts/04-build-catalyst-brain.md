# 04 — build Catalyst Brain

Create `outputs/<name>/` from the templates. Never edit templates directly.

Required generated structure:

```txt
outputs/<name>/
  catalyst-brain/
    README.md
    identity.md
    context.md
    goals.md
    constraints.md
    standards.md
    judgment.md
    taste.md
    voice.md
    anti-slop.md
    references.md
    rejected-examples.md
    decision-rules.md
    task-patterns.md
    feedback-memory.md
    lexicon.md
    open-questions.md
  skills/
    catalyst-skill.md
    use-catalyst-brain.md
    update-catalyst-brain.md
    review-against-standards.md
    extract-feedback.md
    task-routing.md
    distill-memory.md
  workflows/
    start-task.md
    produce-output.md
    review-output.md
    update-after-feedback.md
    weekly-distillation.md
  evals/
    output-review.md
    standards-check.md
    identity-alignment.md
    judgment-check.md
    feedback-capture.md
    improvement-log.md
  README.md
```

Every Catalyst Brain file must include:

```txt
purpose
when to load
tasks affected
how to apply
how to update
what not to put here
evidence / rules
```

Do not leave placeholders. If evidence is missing, mark the claim as assumed and put it in open-questions.
