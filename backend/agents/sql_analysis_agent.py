import time
from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.tools.sql_parser import parse_sql, ParsedQuery
from backend.tools.schema_tool import SchemaInfo

class SQLAnalysisAgent(BaseAgent):
    """
    Agent 1: SQL Analysis Agent
    Parses SQL structure, extracts tables/columns/joins/filters/aggregations,
    and identifies structural antipatterns.
    """
    def __init__(self):
        super().__init__(name="SQL Analysis Agent")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        start = time.perf_counter()
        sql: str = context.get("sql", "")
        schema: SchemaInfo = context.get("schema_info")

        # 1. Parse SQL AST
        parsed: ParsedQuery = parse_sql(sql)
        parse_dur = (time.perf_counter() - start) * 1000.0

        if parsed.parse_error:
            self.log(
                action="parse_sql_structure",
                tool_used="sqlglot",
                input_summary=sql[:80],
                result_summary=f"Parse error: {parsed.parse_error}",
                finding="Invalid SQL Syntax",
                confidence=1.0,
                duration_ms=parse_dur
            )
            context["parsed_query"] = parsed
            context["sql_findings"] = [{
                "severity": "critical",
                "category": "Syntax",
                "title": "SQL Syntax Error",
                "description": f"Query could not be parsed: {parsed.parse_error}",
                "evidence": parsed.parse_error,
                "location": "Root query"
            }]
            return context

        self.log(
            action="parse_sql_structure",
            tool_used="sqlglot",
            input_summary=sql[:80],
            result_summary=f"Parsed {parsed.query_type} query with {len(parsed.tables)} table(s), {len(parsed.joins)} join(s), {len(parsed.where_conditions)} filter(s)",
            confidence=1.0,
            duration_ms=parse_dur
        )

        findings: List[Dict[str, Any]] = []

        # Issue 1: SELECT * Detection
        if parsed.is_select_star:
            col_hint = ""
            if schema and parsed.tables:
                t = parsed.tables[0]
                if t in schema.tables:
                    col_names = [c.name for c in schema.tables[t].columns[:4]]
                    col_hint = f" (e.g. {', '.join(col_names)}...)"
            
            f = {
                "severity": "medium",
                "category": "Column Selection",
                "title": "Unnecessary SELECT * Detected",
                "description": f"Retrieving all columns increases network payload, memory usage, and prevents covering index optimizations. Specify explicit columns{col_hint}.",
                "evidence": "SELECT * used in root projection",
                "location": "SELECT clause"
            }
            findings.append(f)
            self.log(
                action="detect_select_star",
                result_summary="SELECT * detected",
                finding="Wildcard projection detected",
                confidence=0.95
            )

        # Issue 2: Missing WHERE clause on large tables
        if not parsed.where_conditions and parsed.tables:
            for t in parsed.tables:
                row_count = 0
                if schema and t in schema.tables:
                    row_count = schema.tables[t].row_count
                
                if row_count > 100 or row_count == 0:
                    findings.append({
                        "severity": "high",
                        "category": "Filtering",
                        "title": f"Unbounded Query Missing WHERE Filter on '{t}'",
                        "description": f"Query has no WHERE clause and will scan all rows in table '{t}' ({row_count} rows).",
                        "evidence": f"No WHERE clause present for table '{t}'",
                        "location": f"FROM {t}"
                    })
                    self.log(
                        action="detect_missing_where",
                        result_summary=f"Table {t} ({row_count} rows) accessed without filter",
                        finding=f"Unbounded table scan on {t}",
                        confidence=0.90
                    )

        # Issue 3: Functions applied on columns in WHERE clause (Non-Sargable)
        for func_info in parsed.has_functions_on_columns:
            fn = func_info["function"]
            col = func_info["column"]
            expr = func_info["expression"]
            findings.append({
                "severity": "high",
                "category": "Index SARGability",
                "title": f"Non-Sargable Function '{fn}' on Column '{col}'",
                "description": f"Wrapping column '{col}' in function '{fn}' prevents the database engine from using indexes on '{col}'. Rewrite as a range comparison or constant expression.",
                "evidence": f"Expression: {expr}",
                "location": "WHERE clause"
            })
            self.log(
                action="detect_non_sargable_functions",
                result_summary=f"Found function {fn} on {col}",
                finding=f"Non-sargable predicate {expr}",
                confidence=0.95
            )

        # Issue 4: Leading wildcard in LIKE pattern
        for like_info in parsed.has_leading_wildcard_like:
            col = like_info["column"]
            pattern = like_info["pattern"]
            findings.append({
                "severity": "medium",
                "category": "Index Efficiency",
                "title": f"Leading Wildcard in LIKE Condition on '{col}'",
                "description": f"Condition {col} LIKE {pattern} starts with a wildcard '%', forcing a full table scan since standard B-Tree indexes cannot be used for suffix matching.",
                "evidence": f"{col} LIKE {pattern}",
                "location": "WHERE clause"
            })
            self.log(
                action="detect_leading_wildcards",
                result_summary=f"Found leading wildcard on {col}",
                finding=f"Index-invalidating LIKE pattern {pattern}",
                confidence=0.90
            )

        # Issue 5: Unnecessary DISTINCT with GROUP BY
        if parsed.has_distinct and parsed.group_by:
            findings.append({
                "severity": "low",
                "category": "Redundant Operations",
                "title": "Redundant DISTINCT with GROUP BY",
                "description": "GROUP BY already groups rows into unique sets. Combining DISTINCT with GROUP BY incurs an extra sorting/hashing pass with no effect.",
                "evidence": f"DISTINCT present alongside GROUP BY {', '.join(parsed.group_by)}",
                "location": "SELECT DISTINCT"
            })

        # Issue 6: ORDER BY without LIMIT on large queries
        if parsed.order_by and not parsed.limit and not parsed.where_conditions:
            findings.append({
                "severity": "medium",
                "category": "Sorting Overhead",
                "title": "Unbounded Sorting (ORDER BY without LIMIT)",
                "description": f"Sorting entire dataset by {', '.join(parsed.order_by)} without a LIMIT requires a full memory/disk sort buffer.",
                "evidence": f"ORDER BY {', '.join(parsed.order_by)}",
                "location": "ORDER BY clause"
            })

        # Issue 7: Multiple Joins Cartesian Risk
        is_cartesian = (len(parsed.tables) > 1 and len(parsed.joins) == 0) or any(
            j.get("condition") == "None" or j.get("type") == "CROSS" for j in parsed.joins
        )
        if is_cartesian:
            findings.append({
                "severity": "critical",
                "category": "Cartesian Product",
                "title": "Cartesian Product (CROSS JOIN) Detected",
                "description": f"Multiple tables ({', '.join(parsed.tables)}) queried without explicit JOIN ON conditions produces an M x N Cartesian product.",
                "evidence": f"Tables: {', '.join(parsed.tables)} without ON conditions / CROSS JOIN",
                "location": "FROM clause"
            })

        context["parsed_query"] = parsed
        context["sql_findings"] = findings
        return context
