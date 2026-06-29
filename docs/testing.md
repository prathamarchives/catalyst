# Catalyst Core Testing

The primary behavioral test is:

```txt
test_feedback_changes_future_packet()
```

It proves:

- a packet initially lacks a specific anti-pattern
- rejection feedback is recorded as an event
- the core creates taste, judgment, anti-pattern, standard, and eval objects
- graph edges preserve provenance
- retrieval pulls those objects for the next similar task
- the next packet changes
- eval catches repeated failure
- proof links before -> feedback -> after

Run:

```bash
python -m pytest
python evals/run_all.py
```

Static evals check that the old UI/CLI/MCP/product shell is gone and the Layer 2 kernel boundary exists.

