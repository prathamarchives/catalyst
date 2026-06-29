"""Canonical SQLite store for Catalyst Core Layer 2."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterable

from catalyst_core.domain.base import dump_model, from_json, new_id, now_iso, to_json
from catalyst_core.domain.engines import EngineRunRecord
from catalyst_core.domain.events import CoreEvent
from catalyst_core.domain.evidence import EvidenceItem
from catalyst_core.domain.evals import EvalCheck, EvalResult
from catalyst_core.domain.feedback import FeedbackEvent
from catalyst_core.domain.graph import ObjectEdge
from catalyst_core.domain.mutations import ProposedMutation
from catalyst_core.domain.objects import CognitiveObject
from catalyst_core.domain.packets import AgentPacket
from catalyst_core.domain.proof import ProofRecord
from catalyst_core.domain.retrieval import RetrievalRunRecord

from .migrations import migrate


class SQLiteStore:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else Path(".catalyst") / "core" / "catalyst-core.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            migrate(conn)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextmanager
    def transaction(self):
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def fetch_all(self, sql: str, params: Iterable = ()) -> list[dict]:
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(sql, tuple(params)).fetchall()]

    def fetch_one(self, sql: str, params: Iterable = ()) -> dict | None:
        with self.connect() as conn:
            row = conn.execute(sql, tuple(params)).fetchone()
            return dict(row) if row else None

    def append_event(self, conn: sqlite3.Connection, event: CoreEvent | dict) -> dict:
        data = dump_model(event)
        data.setdefault("id", new_id("evt"))
        data.setdefault("created_at", now_iso())
        conn.execute(
            """
            INSERT OR IGNORE INTO events
            (id, type, project, aggregate_id, aggregate_type, payload_json, metadata_json, idempotency_key, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data["type"],
                data.get("project") or "default",
                data.get("aggregate_id") or "",
                data.get("aggregate_type") or "",
                to_json(data.get("payload")),
                to_json(data.get("metadata")),
                data.get("idempotency_key") or "",
                data["created_at"],
            ),
        )
        return data

    def record_proposed_mutation(self, conn: sqlite3.Connection, mutation: ProposedMutation | dict,
                                 event_id: str) -> dict:
        data = dump_model(mutation)
        data.setdefault("id", new_id("mut"))
        conn.execute(
            """
            INSERT OR REPLACE INTO proposed_mutations
            (id, type, event_type, project, aggregate_id, aggregate_type, engine_id,
             payload_json, metadata_json, idempotency_key, committed_event_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data["type"],
                data["event_type"],
                data.get("project") or "default",
                data.get("aggregate_id") or "",
                data.get("aggregate_type") or "",
                data.get("engine_id") or "",
                to_json(data.get("payload")),
                to_json(data.get("metadata")),
                data.get("idempotency_key") or "",
                event_id,
                now_iso(),
            ),
        )
        return data

    def upsert_evidence(self, conn: sqlite3.Connection, evidence: EvidenceItem | dict) -> dict:
        data = dump_model(evidence)
        data.setdefault("id", new_id("ev"))
        data.setdefault("created_at", now_iso())
        conn.execute(
            """
            INSERT OR REPLACE INTO evidence_items
            (id, project, content, source, source_type, scope, audience, task_type, artifact_id,
             source_strength, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data.get("project") or "default",
                data.get("content") or "",
                data.get("source") or "manual",
                data.get("source_type") or "text",
                data.get("scope") or "",
                data.get("audience") or "",
                data.get("task_type") or "",
                data.get("artifact_id") or "",
                float(data.get("source_strength") or 0.6),
                to_json(data.get("metadata")),
                data["created_at"],
            ),
        )
        self._insert_fts(conn, "evidence_fts", ("evidence_id", "project", "content"),
                         (data["id"], data.get("project") or "default", data.get("content") or ""))
        return data

    def upsert_object(self, conn: sqlite3.Connection, obj: CognitiveObject | dict, event_id: str = "") -> dict:
        data = dump_model(obj)
        now = now_iso()
        data.setdefault("id", new_id("obj"))
        data.setdefault("created_at", now)
        data.setdefault("updated_at", now)
        existing = conn.execute("SELECT version, created_at FROM cognitive_objects WHERE id = ?", (data["id"],)).fetchone()
        if existing:
            data["version"] = int(data.get("version") or existing["version"] + 1)
            data["created_at"] = data.get("created_at") or existing["created_at"]
        conn.execute(
            """
            INSERT INTO cognitive_objects
            (id, type, content, scope, project, audience, task_type, confidence, source_strength,
             evidence_ids_json, version, status, created_at, updated_at, usage_count, success_count,
             failure_count, memory_family, parent_ids_json, embedding_id, eval_ids_json, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              type=excluded.type, content=excluded.content, scope=excluded.scope,
              project=excluded.project, audience=excluded.audience, task_type=excluded.task_type,
              confidence=excluded.confidence, source_strength=excluded.source_strength,
              evidence_ids_json=excluded.evidence_ids_json, version=excluded.version,
              status=excluded.status, updated_at=excluded.updated_at,
              usage_count=excluded.usage_count, success_count=excluded.success_count,
              failure_count=excluded.failure_count, memory_family=excluded.memory_family,
              parent_ids_json=excluded.parent_ids_json, embedding_id=excluded.embedding_id,
              eval_ids_json=excluded.eval_ids_json, metadata_json=excluded.metadata_json
            """,
            (
                data["id"],
                data["type"],
                data.get("content") or "",
                data.get("scope") or "",
                data.get("project") or "default",
                data.get("audience") or "",
                data.get("task_type") or "",
                float(data.get("confidence") or 0.0),
                float(data.get("source_strength") or 0.0),
                to_json(data.get("evidence_ids") or []),
                int(data.get("version") or 1),
                data.get("status") or "active",
                data["created_at"],
                now,
                int(data.get("usage_count") or 0),
                int(data.get("success_count") or 0),
                int(data.get("failure_count") or 0),
                data.get("memory_family") or "",
                to_json(data.get("parent_ids") or []),
                data.get("embedding_id") or "",
                to_json(data.get("eval_ids") or []),
                to_json(data.get("metadata")),
            ),
        )
        version_id = new_id("ver")
        conn.execute(
            """
            INSERT INTO object_versions
            (id, object_id, project, version, event_id, snapshot_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                version_id,
                data["id"],
                data.get("project") or "default",
                int(data.get("version") or 1),
                event_id,
                to_json(data),
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO object_scores
            (object_id, project, confidence, retrieval_weight, source_strength,
             success_count, failure_count, last_used_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(object_id) DO UPDATE SET
              confidence=excluded.confidence,
              source_strength=excluded.source_strength,
              success_count=excluded.success_count,
              failure_count=excluded.failure_count,
              updated_at=excluded.updated_at
            """,
            (
                data["id"],
                data.get("project") or "default",
                float(data.get("confidence") or 0.0),
                0.0,
                float(data.get("source_strength") or 0.0),
                int(data.get("success_count") or 0),
                int(data.get("failure_count") or 0),
                "",
                now,
            ),
        )
        self._insert_fts(conn, "cognitive_fts", ("object_id", "kind", "project", "content"),
                         (data["id"], data["type"], data.get("project") or "default", data.get("content") or ""))
        return data

    def insert_edge(self, conn: sqlite3.Connection, edge: ObjectEdge | dict) -> dict:
        data = dump_model(edge)
        data.setdefault("id", new_id("edge"))
        data.setdefault("created_at", now_iso())
        conn.execute(
            """
            INSERT OR IGNORE INTO object_edges
            (id, project, from_id, to_id, type, confidence, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data.get("project") or "default",
                data.get("from_id") or "",
                data.get("to_id") or "",
                data.get("type") or "supports",
                float(data.get("confidence") or 0.7),
                to_json(data.get("metadata")),
                data["created_at"],
            ),
        )
        return data

    def insert_engine_run(self, conn: sqlite3.Connection, run: EngineRunRecord | dict) -> dict:
        data = dump_model(run)
        data.setdefault("id", new_id("engrun"))
        data.setdefault("started_at", now_iso())
        data.setdefault("finished_at", now_iso())
        conn.execute(
            """
            INSERT OR REPLACE INTO engine_runs
            (id, engine_id, project, status, input_ids_json, proposed_mutation_ids_json,
             committed_event_ids_json, warnings_json, started_at, finished_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data.get("engine_id") or "",
                data.get("project") or "default",
                data.get("status") or "ok",
                to_json(data.get("input_ids") or []),
                to_json(data.get("proposed_mutation_ids") or []),
                to_json(data.get("committed_event_ids") or []),
                to_json(data.get("warnings") or []),
                data["started_at"],
                data["finished_at"],
                to_json(data.get("metadata")),
            ),
        )
        return data

    def insert_retrieval_run(self, conn: sqlite3.Connection, run: RetrievalRunRecord | dict) -> dict:
        data = dump_model(run)
        data.setdefault("id", new_id("ret"))
        data.setdefault("created_at", now_iso())
        conn.execute(
            """
            INSERT OR REPLACE INTO retrieval_runs
            (id, project, task, query_json, candidates_json, selected_object_ids_json, excluded_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data.get("project") or "default",
                data.get("task") or "",
                to_json(data.get("query")),
                to_json(data.get("candidates") or []),
                to_json(data.get("selected_object_ids") or []),
                to_json(data.get("excluded") or []),
                data["created_at"],
            ),
        )
        return data

    def insert_packet(self, conn: sqlite3.Connection, packet: AgentPacket | dict) -> dict:
        data = dump_model(packet)
        data.setdefault("id", new_id("packet"))
        data.setdefault("created_at", now_iso())
        conn.execute(
            """
            INSERT OR REPLACE INTO agent_packets
            (id, project, task, task_type, audience, scope, retrieval_run_id, object_ids_json,
             eval_check_ids_json, sections_json, packet, trace_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data.get("project") or "default",
                data.get("task") or "",
                data.get("task_type") or "",
                data.get("audience") or "",
                data.get("scope") or "",
                data.get("retrieval_run_id") or "",
                to_json(data.get("object_ids") or []),
                to_json(data.get("eval_check_ids") or []),
                to_json(data.get("sections") or []),
                data.get("packet") or "",
                to_json(data.get("trace") or []),
                data["created_at"],
            ),
        )
        return data

    def upsert_eval_check(self, conn: sqlite3.Connection, check: EvalCheck | dict) -> dict:
        data = dump_model(check)
        data.setdefault("id", new_id("check"))
        data.setdefault("created_at", now_iso())
        conn.execute(
            """
            INSERT OR REPLACE INTO eval_checks
            (id, project, object_id, name, check_type, content, failure_terms_json, severity, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data.get("project") or "default",
                data.get("object_id") or "",
                data.get("name") or "",
                data.get("check_type") or "text_rule",
                data.get("content") or "",
                to_json(data.get("failure_terms") or []),
                data.get("severity") or "medium",
                to_json(data.get("metadata")),
                data["created_at"],
            ),
        )
        self._insert_fts(conn, "cognitive_fts", ("object_id", "kind", "project", "content"),
                         (data["id"], "eval_check", data.get("project") or "default", data.get("content") or ""))
        return data

    def insert_eval_result(self, conn: sqlite3.Connection, result: EvalResult | dict) -> dict:
        data = dump_model(result)
        data.setdefault("id", new_id("eval"))
        data.setdefault("created_at", now_iso())
        conn.execute(
            """
            INSERT OR REPLACE INTO eval_results
            (id, project, packet_id, task, output, verdict, score, passed_check_ids_json,
             failed_check_ids_json, violated_object_ids_json, issues_json, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data.get("project") or "default",
                data.get("packet_id") or "",
                data.get("task") or "",
                data.get("output") or "",
                data.get("verdict") or "ask",
                float(data.get("score") or 0.0),
                to_json(data.get("passed_check_ids") or []),
                to_json(data.get("failed_check_ids") or []),
                to_json(data.get("violated_object_ids") or []),
                to_json(data.get("issues") or []),
                to_json(data.get("metadata")),
                data["created_at"],
            ),
        )
        return data

    def insert_feedback_event(self, conn: sqlite3.Connection, feedback: FeedbackEvent | dict) -> dict:
        data = dump_model(feedback)
        data.setdefault("id", new_id("fb"))
        data.setdefault("created_at", now_iso())
        conn.execute(
            """
            INSERT OR REPLACE INTO feedback_events
            (id, project, packet_id, eval_result_id, task, output, feedback, feedback_type, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data.get("project") or "default",
                data.get("packet_id") or "",
                data.get("eval_result_id") or "",
                data.get("task") or "",
                data.get("output") or "",
                data.get("feedback") or "",
                data.get("feedback_type") or "rejection",
                to_json(data.get("metadata")),
                data["created_at"],
            ),
        )
        return data

    def insert_proof_record(self, conn: sqlite3.Connection, proof: ProofRecord | dict) -> dict:
        data = dump_model(proof)
        data.setdefault("id", new_id("proof"))
        data.setdefault("created_at", now_iso())
        conn.execute(
            """
            INSERT OR REPLACE INTO proof_records
            (id, project, before_packet_id, feedback_event_id, after_packet_id, eval_result_id,
             created_object_ids_json, updated_object_ids_json, claim, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data.get("project") or "default",
                data.get("before_packet_id") or "",
                data.get("feedback_event_id") or "",
                data.get("after_packet_id") or "",
                data.get("eval_result_id") or "",
                to_json(data.get("created_object_ids") or []),
                to_json(data.get("updated_object_ids") or []),
                data.get("claim") or "",
                to_json(data.get("metadata")),
                data["created_at"],
            ),
        )
        return data

    def update_object_score(self, conn: sqlite3.Connection, object_id: str, project: str,
                            confidence_delta: float = 0.0, retrieval_weight_delta: float = 0.0,
                            success_delta: int = 0, failure_delta: int = 0,
                            mark_used: bool = False) -> None:
        now = now_iso()
        row = conn.execute("SELECT * FROM object_scores WHERE object_id = ?", (object_id,)).fetchone()
        if row:
            confidence = max(0.0, min(1.0, float(row["confidence"]) + confidence_delta))
            retrieval_weight = float(row["retrieval_weight"]) + retrieval_weight_delta
            success = int(row["success_count"]) + success_delta
            failure = int(row["failure_count"]) + failure_delta
        else:
            confidence = max(0.0, min(1.0, 0.5 + confidence_delta))
            retrieval_weight = retrieval_weight_delta
            success = max(0, success_delta)
            failure = max(0, failure_delta)
        conn.execute(
            """
            INSERT INTO object_scores
            (object_id, project, confidence, retrieval_weight, source_strength, success_count,
             failure_count, last_used_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(object_id) DO UPDATE SET
              confidence=excluded.confidence,
              retrieval_weight=excluded.retrieval_weight,
              success_count=excluded.success_count,
              failure_count=excluded.failure_count,
              last_used_at=excluded.last_used_at,
              updated_at=excluded.updated_at
            """,
            (object_id, project, confidence, retrieval_weight, 0.5, success, failure, now if mark_used else "", now),
        )
        conn.execute(
            """
            UPDATE cognitive_objects
            SET confidence = ?, usage_count = usage_count + ?, success_count = success_count + ?,
                failure_count = failure_count + ?, updated_at = ?
            WHERE id = ?
            """,
            (confidence, 1 if mark_used else 0, success_delta, failure_delta, now, object_id),
        )

    def list_objects(self, project: str = "default", status: str | None = "active") -> list[dict]:
        sql = "SELECT * FROM cognitive_objects WHERE project = ?"
        params: list = [project]
        if status:
            sql += " AND status = ?"
            params.append(status)
        rows = self.fetch_all(sql + " ORDER BY updated_at DESC", params)
        return [self._decode_object(r) for r in rows]

    def get_object(self, object_id: str) -> dict | None:
        row = self.fetch_one("SELECT * FROM cognitive_objects WHERE id = ?", (object_id,))
        return self._decode_object(row) if row else None

    def get_packet(self, packet_id: str) -> dict | None:
        row = self.fetch_one("SELECT * FROM agent_packets WHERE id = ?", (packet_id,))
        return self._decode_packet(row) if row else None

    def list_packets(self, project: str = "default", limit: int = 20) -> list[dict]:
        rows = self.fetch_all(
            "SELECT * FROM agent_packets WHERE project = ? ORDER BY created_at DESC LIMIT ?",
            (project, limit),
        )
        return [self._decode_packet(r) for r in rows]

    def list_edges(self, project: str = "default") -> list[dict]:
        rows = self.fetch_all("SELECT * FROM object_edges WHERE project = ? ORDER BY created_at", (project,))
        return [self._decode_json_columns(r, ["metadata_json"]) for r in rows]

    def list_eval_checks(self, project: str = "default") -> list[dict]:
        rows = self.fetch_all("SELECT * FROM eval_checks WHERE project = ? ORDER BY created_at DESC", (project,))
        return [self._decode_eval_check(r) for r in rows]

    def list_feedback(self, project: str = "default", limit: int = 50) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM feedback_events WHERE project = ? ORDER BY created_at DESC LIMIT ?",
            (project, limit),
        )

    def list_proofs(self, project: str = "default", limit: int = 50) -> list[dict]:
        rows = self.fetch_all(
            "SELECT * FROM proof_records WHERE project = ? ORDER BY created_at DESC LIMIT ?",
            (project, limit),
        )
        return [self._decode_proof(r) for r in rows]

    def list_events(self, project: str = "default", limit: int = 200) -> list[dict]:
        rows = self.fetch_all(
            "SELECT * FROM events WHERE project = ? ORDER BY created_at DESC LIMIT ?",
            (project, limit),
        )
        return [self._decode_json_columns(r, ["payload_json", "metadata_json"]) for r in rows]

    def get_event_count(self, project: str = "default") -> int:
        row = self.fetch_one("SELECT COUNT(*) AS n FROM events WHERE project = ?", (project,))
        return int(row["n"] if row else 0)

    def search_fts(self, project: str, query: str, limit: int = 20) -> list[dict]:
        tokens = [t for t in _tokens(query) if len(t) > 2]
        if not tokens:
            return []
        expr = " OR ".join(tokens[:12])
        try:
            return self.fetch_all(
                """
                SELECT object_id, kind, project, content, bm25(cognitive_fts) AS rank
                FROM cognitive_fts
                WHERE cognitive_fts MATCH ? AND project = ?
                LIMIT ?
                """,
                (expr, project, limit),
            )
        except sqlite3.OperationalError:
            return []

    def export_state(self, project: str = "default") -> dict:
        return {
            "events": self.list_events(project, 10000),
            "objects": self.list_objects(project, status=None),
            "edges": self.list_edges(project),
            "packets": self.list_packets(project, 10000),
            "eval_checks": self.list_eval_checks(project),
            "feedback": self.list_feedback(project, 10000),
            "proofs": self.list_proofs(project, 10000),
        }

    def _insert_fts(self, conn: sqlite3.Connection, table: str, columns: tuple[str, ...], values: tuple) -> None:
        try:
            placeholders = ", ".join("?" for _ in values)
            conn.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", values)
        except sqlite3.OperationalError:
            pass

    def _decode_object(self, row: dict) -> dict:
        data = dict(row)
        for old, new, default in [
            ("evidence_ids_json", "evidence_ids", []),
            ("parent_ids_json", "parent_ids", []),
            ("eval_ids_json", "eval_ids", []),
            ("metadata_json", "metadata", {}),
        ]:
            data[new] = from_json(data.pop(old, ""), default)
        return data

    def _decode_packet(self, row: dict) -> dict:
        data = dict(row)
        for old, new, default in [
            ("object_ids_json", "object_ids", []),
            ("eval_check_ids_json", "eval_check_ids", []),
            ("sections_json", "sections", []),
            ("trace_json", "trace", []),
        ]:
            data[new] = from_json(data.pop(old, ""), default)
        return data

    def _decode_eval_check(self, row: dict) -> dict:
        data = dict(row)
        data["failure_terms"] = from_json(data.pop("failure_terms_json", ""), [])
        data["metadata"] = from_json(data.pop("metadata_json", ""), {})
        return data

    def _decode_proof(self, row: dict) -> dict:
        data = dict(row)
        data["created_object_ids"] = from_json(data.pop("created_object_ids_json", ""), [])
        data["updated_object_ids"] = from_json(data.pop("updated_object_ids_json", ""), [])
        data["metadata"] = from_json(data.pop("metadata_json", ""), {})
        return data

    def _decode_json_columns(self, row: dict, cols: list[str]) -> dict:
        data = dict(row)
        for col in cols:
            new = col.removesuffix("_json")
            data[new] = from_json(data.pop(col, ""), {})
        return data


def _tokens(text: str) -> list[str]:
    token = ""
    out: list[str] = []
    for ch in (text or "").lower():
        if ch.isalnum():
            token += ch
        elif token:
            out.append(token)
            token = ""
    if token:
        out.append(token)
    return out

