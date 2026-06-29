# Core Loops

Catalyst Core is defined by loops, not static files.

## 1. Ingestion

```txt
raw evidence -> normalized evidence object -> pending extraction
```

Evidence must keep source, scope, task type, project, outcome, and sensitivity.

## 2. Extraction

```txt
evidence -> engine signals -> typed memory objects -> graph links
```

The first deterministic extractor creates taste deltas, judgment atoms, anti-patterns, standards, eval checks, identity/context atoms, and memory atoms.

## 3. Retrieval

```txt
task -> task type -> ranked objects -> retrieval set
```

Ranking uses task overlap, object type, task type, confidence, and stale penalties. It is simple by design until the object loop is proven.

## 4. Packet

```txt
retrieval set -> compact operating packet -> packet trace
```

Packets include task, active context, identity, standards, taste rules, judgment rules, anti-patterns, references, eval checks, and workflow.

## 5. Review

```txt
agent output -> eval checks + anti-patterns -> verdict + issues
```

Eval results are graph nodes linked to the packet and violated objects.

## 6. Feedback

```txt
user review -> feedback event -> extracted updates -> graph links -> proof
```

Feedback must change future packets by creating or strengthening objects.

## 7. Health

```txt
core state -> counts, warnings, engine status, next actions
```

Health should surface unprocessed evidence, orphan objects, low-confidence objects, stale objects, missing proof, and eval coverage gaps.
