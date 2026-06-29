"""SQLite migrations for the Catalyst Core kernel."""
from __future__ import annotations

import sqlite3


SCHEMA_VERSION = 1


def migrate(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    _create_tables(conn)
    _create_indexes(conn)
    _create_fts(conn)
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    conn.commit()


def _create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS events (
          id TEXT PRIMARY KEY,
          type TEXT NOT NULL,
          project TEXT NOT NULL,
          aggregate_id TEXT,
          aggregate_type TEXT,
          payload_json TEXT NOT NULL,
          metadata_json TEXT NOT NULL,
          idempotency_key TEXT,
          created_at TEXT NOT NULL
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_events_idempotency
        ON events(project, type, idempotency_key)
        WHERE idempotency_key IS NOT NULL AND idempotency_key != '';

        CREATE TABLE IF NOT EXISTS artifacts (
          id TEXT PRIMARY KEY,
          project TEXT NOT NULL,
          uri TEXT NOT NULL,
          kind TEXT NOT NULL,
          metadata_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS evidence_items (
          id TEXT PRIMARY KEY,
          project TEXT NOT NULL,
          content TEXT NOT NULL,
          source TEXT NOT NULL,
          source_type TEXT NOT NULL,
          scope TEXT,
          audience TEXT,
          task_type TEXT,
          artifact_id TEXT,
          source_strength REAL NOT NULL,
          metadata_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS cognitive_objects (
          id TEXT PRIMARY KEY,
          type TEXT NOT NULL,
          content TEXT NOT NULL,
          scope TEXT,
          project TEXT NOT NULL,
          audience TEXT,
          task_type TEXT,
          confidence REAL NOT NULL,
          source_strength REAL NOT NULL,
          evidence_ids_json TEXT NOT NULL,
          version INTEGER NOT NULL,
          status TEXT NOT NULL,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          usage_count INTEGER NOT NULL,
          success_count INTEGER NOT NULL,
          failure_count INTEGER NOT NULL,
          memory_family TEXT,
          parent_ids_json TEXT NOT NULL,
          embedding_id TEXT,
          eval_ids_json TEXT NOT NULL,
          metadata_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS object_edges (
          id TEXT PRIMARY KEY,
          project TEXT NOT NULL,
          from_id TEXT NOT NULL,
          to_id TEXT NOT NULL,
          type TEXT NOT NULL,
          confidence REAL NOT NULL,
          metadata_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS engine_runs (
          id TEXT PRIMARY KEY,
          engine_id TEXT NOT NULL,
          project TEXT NOT NULL,
          status TEXT NOT NULL,
          input_ids_json TEXT NOT NULL,
          proposed_mutation_ids_json TEXT NOT NULL,
          committed_event_ids_json TEXT NOT NULL,
          warnings_json TEXT NOT NULL,
          started_at TEXT NOT NULL,
          finished_at TEXT NOT NULL,
          metadata_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS proposed_mutations (
          id TEXT PRIMARY KEY,
          type TEXT NOT NULL,
          event_type TEXT NOT NULL,
          project TEXT NOT NULL,
          aggregate_id TEXT,
          aggregate_type TEXT,
          engine_id TEXT,
          payload_json TEXT NOT NULL,
          metadata_json TEXT NOT NULL,
          idempotency_key TEXT,
          committed_event_id TEXT,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS retrieval_runs (
          id TEXT PRIMARY KEY,
          project TEXT NOT NULL,
          task TEXT NOT NULL,
          query_json TEXT NOT NULL,
          candidates_json TEXT NOT NULL,
          selected_object_ids_json TEXT NOT NULL,
          excluded_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agent_packets (
          id TEXT PRIMARY KEY,
          project TEXT NOT NULL,
          task TEXT NOT NULL,
          task_type TEXT,
          audience TEXT,
          scope TEXT,
          retrieval_run_id TEXT,
          object_ids_json TEXT NOT NULL,
          eval_check_ids_json TEXT NOT NULL,
          sections_json TEXT NOT NULL,
          packet TEXT NOT NULL,
          trace_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS eval_checks (
          id TEXT PRIMARY KEY,
          project TEXT NOT NULL,
          object_id TEXT,
          name TEXT NOT NULL,
          check_type TEXT NOT NULL,
          content TEXT NOT NULL,
          failure_terms_json TEXT NOT NULL,
          severity TEXT NOT NULL,
          metadata_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS eval_results (
          id TEXT PRIMARY KEY,
          project TEXT NOT NULL,
          packet_id TEXT NOT NULL,
          task TEXT NOT NULL,
          output TEXT NOT NULL,
          verdict TEXT NOT NULL,
          score REAL NOT NULL,
          passed_check_ids_json TEXT NOT NULL,
          failed_check_ids_json TEXT NOT NULL,
          violated_object_ids_json TEXT NOT NULL,
          issues_json TEXT NOT NULL,
          metadata_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS feedback_events (
          id TEXT PRIMARY KEY,
          project TEXT NOT NULL,
          packet_id TEXT,
          eval_result_id TEXT,
          task TEXT NOT NULL,
          output TEXT NOT NULL,
          feedback TEXT NOT NULL,
          feedback_type TEXT NOT NULL,
          metadata_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS proof_records (
          id TEXT PRIMARY KEY,
          project TEXT NOT NULL,
          before_packet_id TEXT,
          feedback_event_id TEXT,
          after_packet_id TEXT,
          eval_result_id TEXT,
          created_object_ids_json TEXT NOT NULL,
          updated_object_ids_json TEXT NOT NULL,
          claim TEXT NOT NULL,
          metadata_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS object_scores (
          object_id TEXT PRIMARY KEY,
          project TEXT NOT NULL,
          confidence REAL NOT NULL,
          retrieval_weight REAL NOT NULL,
          source_strength REAL NOT NULL,
          success_count INTEGER NOT NULL,
          failure_count INTEGER NOT NULL,
          last_used_at TEXT,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS object_versions (
          id TEXT PRIMARY KEY,
          object_id TEXT NOT NULL,
          project TEXT NOT NULL,
          version INTEGER NOT NULL,
          event_id TEXT,
          snapshot_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        """
    )


def _create_indexes(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_events_project_type ON events(project, type, created_at);
        CREATE INDEX IF NOT EXISTS idx_evidence_project ON evidence_items(project, created_at);
        CREATE INDEX IF NOT EXISTS idx_objects_project_type ON cognitive_objects(project, type, status);
        CREATE INDEX IF NOT EXISTS idx_objects_memory ON cognitive_objects(project, memory_family);
        CREATE INDEX IF NOT EXISTS idx_edges_project_type ON object_edges(project, type);
        CREATE INDEX IF NOT EXISTS idx_edges_from ON object_edges(project, from_id);
        CREATE INDEX IF NOT EXISTS idx_edges_to ON object_edges(project, to_id);
        CREATE INDEX IF NOT EXISTS idx_packets_project ON agent_packets(project, created_at);
        CREATE INDEX IF NOT EXISTS idx_feedback_project ON feedback_events(project, created_at);
        CREATE INDEX IF NOT EXISTS idx_eval_project ON eval_results(project, created_at);
        CREATE INDEX IF NOT EXISTS idx_proof_project ON proof_records(project, created_at);
        """
    )


def _create_fts(conn: sqlite3.Connection) -> None:
    try:
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS cognitive_fts
            USING fts5(object_id UNINDEXED, kind UNINDEXED, project UNINDEXED, content)
            """
        )
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS evidence_fts
            USING fts5(evidence_id UNINDEXED, project UNINDEXED, content)
            """
        )
    except sqlite3.OperationalError:
        # Some custom SQLite builds omit FTS5. The retrieval planner has a
        # deterministic lexical fallback, so this is not fatal.
        pass

