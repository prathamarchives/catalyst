"""Markdown <-> structured Catalyst Brain parsing.

The parser is intentionally conservative: it extracts useful rule-shaped data
while preserving the full original markdown as `raw_markdown` /
`unknown_markdown`.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import paths
from .models import (
    ApprovedExample,
    BrainSection,
    ContextSource,
    DecisionRule,
    FeedbackMemory,
    JudgmentRule,
    RejectedPattern,
    Standard,
    TaskPattern,
)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _items(text: str) -> list[str]:
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith(("-", "*")):
            s = s[1:].strip()
        if re.match(r"^(status|evidence):", s, re.I):
            continue
        m = re.search(r"(?:rule|evidence|decision|pattern):\s*(.+)", s, re.I)
        if m:
            s = m.group(1).strip()
        low = s.lower()
        if low in {"pending", "replace with extracted material"}:
            continue
        if len(s) >= 4 and not s.startswith("#"):
            out.append(_clean(s))
    return out


def _id(prefix: str, section: str, index: int) -> str:
    return f"{prefix}_{section.replace('.md', '').replace('-', '_')}_{index}"


def parse_brain_section(name: str, text: str, path: str = "") -> BrainSection:
    raw = text or ""
    title = ""
    for line in raw.splitlines():
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            break
    status = "missing" if not raw else "placeholder" if paths.is_placeholder(raw) else "active"
    parsed = paths.parse_sections(raw)
    signal_heads = (
        "evidence", "rule", "seeded", "feedback", "example", "approved",
        "rejected", "memory", "decision", "standard", "pattern",
    )
    signal_sections = [body for head, body in parsed.items() if any(key in head for key in signal_heads)]
    joined = "\n".join(signal_sections) if signal_sections else (raw if not parsed else "")
    items = _items(joined)
    section = BrainSection(
        name=name,
        title=title or name.replace(".md", ""),
        path=path,
        status=status,
        raw_markdown=raw,
        unknown_markdown=raw,
    )
    low_name = name.lower()
    for idx, item in enumerate(items[:80], 1):
        evidence = item
        if "standards" in low_name or "anti-slop" in low_name:
            section.standards.append(Standard(id=_id("std", name, idx), text=item, evidence=evidence, confidence=0.65))
        if "judgment" in low_name or "decision" in low_name:
            section.judgment_rules.append(JudgmentRule(id=_id("judge", name, idx), text=item, evidence=evidence, confidence=0.65))
        if "rejected" in low_name or "anti-slop" in low_name:
            section.rejected_patterns.append(RejectedPattern(id=_id("reject", name, idx), pattern=item, evidence=evidence, confidence=0.65))
        if "taste" in low_name or "references" in low_name:
            section.approved_examples.append(ApprovedExample(id=_id("approved", name, idx), summary=item, evidence=evidence, confidence=0.55))
        if "feedback" in low_name:
            section.feedback_memories.append(FeedbackMemory(id=_id("fb", name, idx), text=item, evidence=evidence, confidence=0.65))
        if "task-pattern" in low_name or "workflow" in low_name:
            section.task_patterns.append(TaskPattern(id=_id("task", name, idx), task_type="general", rule=item, evidence=evidence, confidence=0.6))
        if "decision" in low_name:
            section.decision_rules.append(DecisionRule(id=_id("decision", name, idx), if_then=item, evidence=evidence, confidence=0.6))
        if "context" in low_name or "identity" in low_name or "goals" in low_name or "constraints" in low_name:
            section.context_sources.append(ContextSource(id=_id("src", name, idx), path=path, excerpt=item, trust=0.55))
    return section


def append_structured_block(raw: str, heading: str, lines: list[str]) -> str:
    block = ["", "", f"## {heading}", ""]
    block.extend(f"- {line}" for line in lines if line.strip())
    block.append("")
    return (raw.rstrip() + "\n".join(block)).strip() + "\n"


def section_to_summary(section: BrainSection) -> dict:
    return {
        "name": section.name,
        "title": section.title,
        "status": section.status,
        "standards": len(section.standards),
        "judgment_rules": len(section.judgment_rules),
        "rejected_patterns": len(section.rejected_patterns),
        "approved_examples": len(section.approved_examples),
        "feedback_memories": len(section.feedback_memories),
        "task_patterns": len(section.task_patterns),
        "decision_rules": len(section.decision_rules),
        "context_sources": len(section.context_sources),
    }


def parse_file(path: Path) -> BrainSection:
    return parse_brain_section(path.name, path.read_text(encoding="utf-8"), str(path))
