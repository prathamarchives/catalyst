import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalyst_core import packet
from tests.conftest import seed_file


def test_packet_full_includes_core_sections_and_contract(temp_brain):
    seed_file(temp_brain, "identity.md", "builder, raw voice")
    seed_file(temp_brain, "standards.md", "no hype, specific only")
    seed_file(temp_brain, "judgment.md", "reject pitch-sounding text")
    pkt = packet.build_context_packet("demo-flow-test", "write a launch post", "full", outputs_root=temp_brain["outputs_root"])
    for need in ["# Catalyst Context Packet", "## identity/context summary", "## standards to apply",
                 "## judgment/rejection rules", "## agent judgment contract", "## required evaluation after output",
                 "outputs/demo-flow-test/catalyst-brain/identity.md"]:
        assert need in pkt, need


def test_packet_auto_full_for_high_stakes(temp_brain):
    pkt = packet.build_context_packet("demo-flow-test", "draft the investor update", "auto", outputs_root=temp_brain["outputs_root"])
    assert "mode full" in pkt


def test_packet_quick_marks_unfilled(temp_brain):
    pkt = packet.build_context_packet("demo-flow-test", "write a dm reply", "quick", outputs_root=temp_brain["outputs_root"])
    assert "task_type: reply/dm" in pkt
    assert "unfilled" in pkt or "placeholder" in pkt
