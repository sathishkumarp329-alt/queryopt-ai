from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.tools.sql_parser import ParsedQuery
from backend.tools.explain_tool import ExplainResult

class ReportAgent(BaseAgent):
    """
    Agent 6: Final Report Agent
    Aggregates findings across all agent trajectories, computes standardized
    SQL Quality & Performance scores, assigns optimization potential rating,
    and produces the comprehensive final analysis payload.
    """
    def __init__(self):
        super().__init__(name="Final Report Agent")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        sql: str = context.get("sql", "")
        database_type: str = context.get("database_type", "sqlite")
        parsed: ParsedQuery = context.get("parsed_query")
        explain_res: ExplainResult = context.get("explain_result")
        sql_findings: List[Dict[str, Any]] = context.get("sql_findings", [])
        perf_findings: List[Dict[str, Any]] = context.get("performance_findings", [])
        index_recs: List[Dict[str, Any]] = context.get("index_recommendations", [])
        verif: Dict[str, Any] = context.get("verification_result", {})
        opt_sql: str = context.get("optimized_sql", sql)
        opt_changes: List[str] = context.get("optimization_changes", [])
        opt_expl: str = context.get("optimization_explanation", "")
        exec_time_ms: float = context.get("exec_time_ms", 0.0)

        # Merge findings
        all_findings = sql_findings + perf_findings

        # 1. Compute SQL Quality Score (100 base)
        # Critical: -25, High: -15, Medium: -8, Low: -3, Info: -1
        sql_score = 100
        for f in all_findings:
            sev = f.get("severity", "info").lower()
            if sev == "critical":
                sql_score -= 25
            elif sev == "high":
                sql_score -= 15
            elif sev == "medium":
                sql_score -= 8
            elif sev == "low":
                sql_score -= 3
            elif sev == "info":
                sql_score -= 1
        sql_score = max(5, min(100, sql_score))

        # 2. Compute Performance Score (100 base)
        perf_score = 100
        if explain_res and explain_res.has_full_table_scan:
            perf_score -= 30 * len(explain_res.tables_with_full_scan)
        if exec_time_ms > 100.0:
            perf_score -= 20
        elif exec_time_ms > 50.0:
            perf_score -= 10
        perf_score = max(10, min(100, perf_score))

        # 3. Determine Optimization Potential
        if sql_score < 70 or (explain_res and explain_res.has_full_table_scan) or len(index_recs) > 0:
            potential = "HIGH"
        elif sql_score < 85 or len(opt_changes) > 0:
            potential = "MEDIUM"
        elif len(all_findings) > 0:
            potential = "LOW"
        else:
            potential = "NONE"

        # 4. Complexity determination
        joins_count = len(parsed.joins) if parsed else 0
        tables_count = len(parsed.tables) if parsed else 1
        where_count = len(parsed.where_conditions) if parsed else 0
        
        if joins_count >= 3 or (parsed and parsed.subqueries > 0):
            complexity = "Complex"
        elif joins_count >= 1 or where_count >= 2:
            complexity = "Moderate"
        else:
            complexity = "Simple"

        # 5. Build Final Report Structure
        report = {
            "query_summary": {
                "database": database_type,
                "query_type": parsed.query_type if parsed else "SELECT",
                "tables": parsed.tables if parsed else [],
                "joins": joins_count,
                "complexity": complexity
            },
            "sql_score": sql_score,
            "performance_score": perf_score,
            "optimization_potential": potential,
            "findings": all_findings,
            "optimization": {
                "original_sql": sql,
                "optimized_sql": opt_sql,
                "changes": opt_changes,
                "explanation": opt_expl
            },
            "index_recommendations": index_recs,
            "verification": verif,
            "explain_result": {
                "nodes": [
                    {
                        "node_id": n.node_id,
                        "parent_id": n.parent_id,
                        "detail": n.detail,
                        "is_full_scan": n.is_full_scan,
                        "table": n.table,
                        "index_used": n.index_used
                    } for n in explain_res.nodes
                ] if explain_res else [],
                "has_full_table_scan": explain_res.has_full_table_scan if explain_res else False,
                "tables_scanned": explain_res.tables_scanned if explain_res else [],
                "indexes_used": explain_res.indexes_used if explain_res else [],
                "tables_with_full_scan": explain_res.tables_with_full_scan if explain_res else [],
                "summary": explain_res.summary if explain_res else ""
            },
            "exec_time_ms": exec_time_ms
        }

        self.log(
            action="compile_final_report",
            result_summary=f"Report generated with SQL Score: {sql_score}/100, Performance: {perf_score}/100, Potential: {potential}",
            finding=f"Synthesized {len(all_findings)} finding(s) and {len(index_recs)} index recommendation(s)",
            confidence=0.98
        )

        context["final_report"] = report
        return context
