"""Core domain constants."""
from __future__ import annotations

OBJECT_TYPES = {
    "memory_atom",
    "taste_delta",
    "judgment_atom",
    "identity_atom",
    "context_atom",
    "standard_atom",
    "anti_pattern",
    "eval_check",
    "reference_item",
    "retrieval_policy",
    "agent_packet",
    "proof_record",
}

MEMORY_FAMILIES = {
    "episodic",
    "semantic",
    "procedural",
    "preference",
    "negative",
    "reference",
    "social_customer",
    "strategic",
}

EDGE_TYPES = {
    "extracted_from",
    "supports",
    "contradicts",
    "refines",
    "consolidates",
    "scoped_to",
    "retrieved_for",
    "compiled_into",
    "evaluated_by",
    "updated_by",
    "improved_by",
}

EVENT_TYPES = {
    "evidence.ingested",
    "object.proposed",
    "object.confirmed",
    "edge.created",
    "packet.compiled",
    "eval.ran",
    "feedback.received",
    "confidence.updated",
    "retrieval_weight.updated",
    "proof.created",
    "engine.ran",
    "retrieval.ran",
}

OBJECT_STATUS = {
    "candidate",
    "active",
    "consolidated",
    "stale",
    "contradicted",
    "archived",
    "low_confidence",
}

BAD_SAAS_TERMS = {
    "generic saas",
    "saas slop",
    "linkedin slop",
    "unlock productivity",
    "seamless ai workflows",
    "platform helps teams",
    "productivity platform",
    "ai workflows",
}

