"""Brain loading, validation, and safe markdown proposal helpers."""
from __future__ import annotations

from pathlib import Path

from . import brain_parser, paths
from .models import BrainProfile, BrainSection

BRAIN_FILES = [
    "README.md", "identity.md", "context.md", "goals.md", "constraints.md",
    "standards.md", "judgment.md", "taste.md", "voice.md", "anti-slop.md",
    "references.md", "rejected-examples.md", "decision-rules.md",
    "task-patterns.md", "feedback-memory.md", "lexicon.md", "open-questions.md",
]


def load_brain_profile(project: str = "default", outputs_root: Path = paths.OUTPUTS) -> BrainProfile:
    bd = paths.brain_dir(project, outputs_root)
    profile = BrainProfile(project=paths.slug(project))
    if bd is None:
        profile.missing_sections = list(BRAIN_FILES)
        profile.warnings.append(f"no generated brain found for '{project}'")
        return profile
    for filename in BRAIN_FILES:
        path = bd / filename
        if path.is_file():
            section = brain_parser.parse_file(path)
        else:
            section = BrainSection(name=filename, path=str(path), status="missing")
        profile.sections[filename] = section
        if section.status == "missing":
            profile.missing_sections.append(filename)
        if section.status == "placeholder":
            profile.placeholder_sections.append(filename)
        profile.standards.extend(section.standards)
        profile.judgment_rules.extend(section.judgment_rules)
        profile.rejected_patterns.extend(section.rejected_patterns)
        profile.approved_examples.extend(section.approved_examples)
        profile.feedback_memories.extend(section.feedback_memories)
        profile.task_patterns.extend(section.task_patterns)
        profile.decision_rules.extend(section.decision_rules)
        profile.context_sources.extend(section.context_sources)
    return profile


def validate_brain_profile(profile: BrainProfile) -> dict:
    critical = ["identity.md", "standards.md", "judgment.md", "rejected-examples.md", "feedback-memory.md"]
    missing = [f for f in critical if f in profile.missing_sections]
    placeholders = [f for f in critical if f in profile.placeholder_sections]
    structured_counts = {
        "standards": len(profile.standards),
        "judgment_rules": len(profile.judgment_rules),
        "rejected_patterns": len(profile.rejected_patterns),
        "feedback_memories": len(profile.feedback_memories),
        "context_sources": len(profile.context_sources),
    }
    warnings = list(profile.warnings)
    if missing:
        warnings.append("critical brain files missing: " + ", ".join(missing))
    if placeholders:
        warnings.append("critical brain files still look like templates: " + ", ".join(placeholders))
    if not any(structured_counts.values()):
        warnings.append("no structured brain rules extracted yet")
    return {
        "ok": not missing,
        "project": profile.project,
        "missing_sections": profile.missing_sections,
        "placeholder_sections": profile.placeholder_sections,
        "structured_counts": structured_counts,
        "warnings": warnings,
    }


def brain_sections_summary(project: str = "default", outputs_root: Path = paths.OUTPUTS) -> dict:
    profile = load_brain_profile(project, outputs_root)
    validation = validate_brain_profile(profile)
    return {
        "project": profile.project,
        "sections": [brain_parser.section_to_summary(s) for s in profile.sections.values()],
        "health": validation,
    }

