import time
from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.tools.explain_tool import run_explain, ExplainResult
from backend.tools.query_executor import execute_and_time
from backend.tools.schema_tool import SchemaInfo
from backend.tools.sql_parser import ParsedQuery

class PerformanceAgent(BaseAgent):
    """
    Agent 2: Performance Analysis Agent
    Executes EXPLAIN QUERY PLAN to obtain physical query execution plans,
    detects full table scans, index scans, join costs, and measures execution runtime.
    """
    def __init__(self):
        super().__init__(name="Performance Agent")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        sql: str = context.get("sql", "")
        db_path: str = context.get("db_path", "")
        schema: SchemaInfo = context.get("schema_info")
        parsed: ParsedQuery = context.get("parsed_query")

        # 1. Run EXPLAIN QUERY PLAN
        start = time.perf_counter()
        explain_res: ExplainResult = run_explain(sql, db_path)
        explain_dur = (time.perf_counter() - start) * 1000.0

        self.log(
            action="execute_explain_query_plan",
            tool_used="EXPLAIN QUERY PLAN",
            input_summary=sql[:80],
            result_summary=explain_res.summary,
            finding=f"{len(explain_res.tables_with_full_scan)} full table scans found" if explain_res.has_full_table_scan else "Index search utilized",
            confidence=0.98,
            duration_ms=explain_dur
        )

        # 2. Benchmark actual execution time
        exec_res, avg_exec_time_ms = execute_and_time(sql, db_path, runs=2)
        self.log(
            action="benchmark_execution_time",
            tool_used="sqlite3",
            input_summary=f"Run SQL against {db_path}",
            result_summary=f"Avg execution time: {avg_exec_time_ms} ms across returned {exec_res.row_count} rows",
            confidence=0.95,
            duration_ms=avg_exec_time_ms
        )

        findings: List[Dict[str, Any]] = []

        # Analyze full table scans from physical plan
        if explain_res.has_full_table_scan:
            for tbl in explain_res.tables_with_full_scan:
                row_count = 0
                if schema and tbl in schema.tables:
                    row_count = schema.tables[tbl].row_count

                findings.append({
                    "severity": "high" if row_count > 500 else "medium",
                    "category": "Physical Execution",
                    "title": f"Full Table Scan on '{tbl}' ({row_count} rows)",
                    "description": f"The query optimizer must inspect every row in table '{tbl}' because no suitable index was matched.",
                    "evidence": f"EXPLAIN output: SCAN TABLE {tbl} ({row_count} rows scanned)",
                    "location": f"Table: {tbl}"
                })

        # Check if high latency observed
        if avg_exec_time_ms > 100.0:
            findings.append({
                "severity": "high",
                "category": "Execution Latency",
                "title": f"Elevated Execution Latency ({avg_exec_time_ms} ms)",
                "description": "Query execution time exceeds optimal OLTP latency targets (< 50ms).",
                "evidence": f"Measured average execution time: {avg_exec_time_ms} ms",
                "location": "Runtime"
            })

        context["explain_result"] = explain_res
        context["exec_time_ms"] = avg_exec_time_ms
        context["performance_findings"] = findings
        return context
