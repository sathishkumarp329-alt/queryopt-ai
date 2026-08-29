import time
from typing import Dict, Any, List
from baseline.rule_engine import run_rules, RuleFinding
from backend.tools.sql_parser import parse_sql
from backend.tools.schema_tool import get_schema
from backend.tools.explain_tool import run_explain
from backend.tools.query_executor import execute_and_time
from backend.config import settings

class BaselineAnalyzer:
    """
    Traditional rule-based baseline query analyzer without agentic orchestration,
    deep query verification, or LLM-driven reasoning.
    """
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DEMO_DB_PATH

    def analyze(self, sql: str) -> Dict[str, Any]:
        start = time.perf_counter()
        
        parsed = parse_sql(sql)
        schema = get_schema(self.db_path)
        rule_findings: List[RuleFinding] = run_rules(parsed, schema)
        explain_res = run_explain(sql, self.db_path)
        _, exec_time_ms = execute_and_time(sql, self.db_path, runs=1)

        # Baseline score calculation
        sql_score = 100
        for rf in rule_findings:
            if rf.severity == "critical":
                sql_score -= 25
            elif rf.severity == "high":
                sql_score -= 15
            elif rf.severity == "medium":
                sql_score -= 8
            else:
                sql_score -= 3
        sql_score = max(10, min(100, sql_score))

        perf_score = 70 if explain_res.has_full_table_scan else 95

        findings_dicts = [
            {
                "severity": rf.severity,
                "category": rf.category,
                "title": rf.title,
                "description": rf.description,
                "evidence": rf.evidence,
                "location": rf.location,
            } for rf in rule_findings
        ]

        # Simple baseline index recommendations
        index_recs = []
        if schema and parsed.where_columns and parsed.tables:
            t = parsed.tables[0]
            w = parsed.where_columns[0]
            index_recs.append({
                "table_name": t,
                "columns": [w],
                "index_type": "BTREE",
                "create_statement": f"CREATE INDEX idx_{t}_{w} ON {t}({w});",
                "reason": f"Baseline rule: Index suggested for WHERE column '{w}' on table '{t}'.",
                "expected_impact": "Medium"
            })

        duration = round(time.perf_counter() - start, 3)

        return {
            "query_summary": {
                "database": "sqlite",
                "query_type": parsed.query_type,
                "tables": parsed.tables,
                "joins": len(parsed.joins),
                "complexity": "Simple" if len(parsed.joins) == 0 else "Moderate"
            },
            "sql_score": sql_score,
            "performance_score": perf_score,
            "optimization_potential": "HIGH" if sql_score < 75 else "MEDIUM",
            "findings": findings_dicts,
            "optimization": {
                "original_sql": sql,
                "optimized_sql": sql,  # Baseline does not rewrite complex SQL
                "changes": ["Baseline: No automated SQL rewrite engine available."],
                "explanation": "Rule-based baseline analyzer does not generate verified query rewrites."
            },
            "index_recommendations": index_recs,
            "verification": {
                "syntax_valid": True,
                "tables_valid": True,
                "is_equivalent": True,
                "equivalence_explanation": "Baseline uses original query without modifications.",
                "original_time_ms": exec_time_ms,
                "optimized_time_ms": exec_time_ms,
                "improvement_pct": 0.0,
                "status": "UNCERTAIN",
                "confidence": 0.5
            },
            "trajectory": [
                {
                    "agent_name": "Baseline Rule Engine",
                    "action": "execute_rule_checks",
                    "tool_used": "rules",
                    "input_summary": sql[:60],
                    "result_summary": f"Executed 10 rules, found {len(rule_findings)} issue(s)",
                    "finding": None,
                    "confidence": 0.70,
                    "duration_ms": duration * 1000.0,
                    "timestamp": ""
                }
            ],
            "explain_result": {
                "nodes": [],
                "has_full_table_scan": explain_res.has_full_table_scan,
                "tables_scanned": explain_res.tables_scanned,
                "indexes_used": explain_res.indexes_used,
                "tables_with_full_scan": explain_res.tables_with_full_scan,
                "summary": explain_res.summary
            },
            "exec_time_ms": exec_time_ms,
            "total_pipeline_duration_seconds": duration
        }
