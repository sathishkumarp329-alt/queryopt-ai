from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from backend.tools.sql_parser import ParsedQuery
from backend.tools.schema_tool import SchemaInfo, has_index_on

@dataclass
class RuleFinding:
    rule_id: str
    severity: str
    category: str
    title: str
    description: str
    evidence: str
    location: str

def rule_r001_select_star(parsed: ParsedQuery, schema: SchemaInfo) -> Optional[RuleFinding]:
    """R001: SELECT * detected"""
    if parsed.is_select_star:
        return RuleFinding(
            rule_id="R001",
            severity="medium",
            category="Column Selection",
            title="SELECT * Antipattern Detected",
            description="Query uses SELECT * which retrieves all columns. Specify explicit column names to minimize I/O.",
            evidence="SELECT *",
            location="SELECT"
        )
    return None

def rule_r002_missing_where(parsed: ParsedQuery, schema: SchemaInfo) -> Optional[RuleFinding]:
    """R002: Missing WHERE clause on table with >100 rows"""
    if not parsed.where_conditions and parsed.tables:
        for t in parsed.tables:
            row_count = schema.tables[t].row_count if schema and t in schema.tables else 0
            if row_count > 100 or row_count == 0:
                return RuleFinding(
                    rule_id="R002",
                    severity="high",
                    category="Filtering",
                    title=f"Missing WHERE Filter on Table '{t}'",
                    description=f"Query has no WHERE filter on table '{t}' ({row_count} rows), resulting in a full table scan.",
                    evidence=f"No WHERE clause for {t}",
                    location=f"FROM {t}"
                )
    return None

def rule_r003_function_on_column(parsed: ParsedQuery, schema: SchemaInfo) -> Optional[RuleFinding]:
    """R003: Function applied to column in WHERE (non-sargable)"""
    if parsed.has_functions_on_columns:
        first = parsed.has_functions_on_columns[0]
        return RuleFinding(
            rule_id="R003",
            severity="high",
            category="SARGability",
            title=f"Non-Sargable Function on '{first['column']}'",
            description=f"Function {first['function']} applied to indexed column prevents index seek.",
            evidence=first['expression'],
            location="WHERE"
        )
    return None

def rule_r004_join_missing_index(parsed: ParsedQuery, schema: SchemaInfo) -> Optional[RuleFinding]:
    """R004: JOIN column missing index"""
    if schema and parsed.joins:
        for join in parsed.joins:
            tbl = join.get("table", "").lower()
            cond = join.get("condition", "").lower()
            if tbl in schema.tables:
                for c in schema.tables[tbl].columns:
                    c_name = c.name.lower()
                    if c_name in cond and not has_index_on(schema, tbl, [c_name]) and not c.is_pk:
                        return RuleFinding(
                            rule_id="R004",
                            severity="high",
                            category="Joins",
                            title=f"JOIN Column '{tbl}.{c_name}' Missing Index",
                            description=f"Join condition references unindexed column '{tbl}.{c_name}'.",
                            evidence=f"JOIN {tbl} ON {cond}",
                            location=f"JOIN {tbl}"
                        )
    return None

def rule_r005_where_missing_index(parsed: ParsedQuery, schema: SchemaInfo) -> Optional[RuleFinding]:
    """R005: WHERE column missing index"""
    if schema and parsed.where_columns and parsed.tables:
        for w in parsed.where_columns:
            for t in parsed.tables:
                if t in schema.tables:
                    col_names = [c.name.lower() for c in schema.tables[t].columns]
                    if w.lower() in col_names and not has_index_on(schema, t, [w]):
                        return RuleFinding(
                            rule_id="R005",
                            severity="medium",
                            category="Indexing",
                            title=f"Filtered Column '{t}.{w}' Has No Index",
                            description=f"Filtering on unindexed column '{w}' forces table scan.",
                            evidence=f"WHERE contains {w}",
                            location="WHERE"
                        )
    return None

def rule_r006_unbounded_order_by(parsed: ParsedQuery, schema: SchemaInfo) -> Optional[RuleFinding]:
    """R006: ORDER BY without LIMIT"""
    if parsed.order_by and not parsed.limit and not parsed.where_conditions:
        return RuleFinding(
            rule_id="R006",
            severity="medium",
            category="Sorting",
            title="ORDER BY Without LIMIT",
            description="Sorting unbounded query results requires full memory sort buffer.",
            evidence=f"ORDER BY {', '.join(parsed.order_by)}",
            location="ORDER BY"
        )
    return None

def rule_r007_leading_wildcard(parsed: ParsedQuery, schema: SchemaInfo) -> Optional[RuleFinding]:
    """R007: LIKE with leading wildcard (%value%)"""
    if parsed.has_leading_wildcard_like:
        first = parsed.has_leading_wildcard_like[0]
        return RuleFinding(
            rule_id="R007",
            severity="medium",
            category="Indexing",
            title="Leading Wildcard in LIKE Pattern",
            description=f"Pattern {first['pattern']} on column {first['column']} cannot utilize B-Tree index.",
            evidence=f"LIKE {first['pattern']}",
            location="WHERE"
        )
    return None

def rule_r008_redundant_distinct(parsed: ParsedQuery, schema: SchemaInfo) -> Optional[RuleFinding]:
    """R008: DISTINCT redundant with GROUP BY"""
    if parsed.has_distinct and parsed.group_by:
        return RuleFinding(
            rule_id="R008",
            severity="low",
            category="Redundant Operations",
            title="Redundant DISTINCT with GROUP BY",
            description="GROUP BY already eliminates duplicate groups.",
            evidence="DISTINCT + GROUP BY",
            location="SELECT"
        )
    return None

def rule_r009_cartesian_join(parsed: ParsedQuery, schema: SchemaInfo) -> Optional[RuleFinding]:
    """R009: Cartesian cross join detected"""
    is_cartesian = (len(parsed.tables) > 1 and len(parsed.joins) == 0) or any(
        j.get("condition") == "None" or j.get("type") == "CROSS" for j in parsed.joins
    )
    if is_cartesian:
        return RuleFinding(
            rule_id="R009",
            severity="critical",
            category="Joins",
            title="Cartesian Product (Missing JOIN ON)",
            description=f"Multiple tables queried without explicit JOIN ON condition: {', '.join(parsed.tables)}.",
            evidence="Multiple FROM tables with no ON condition / CROSS JOIN",
            location="FROM"
        )
    return None

def rule_r010_subquery_count(parsed: ParsedQuery, schema: SchemaInfo) -> Optional[RuleFinding]:
    """R010: Heavy subqueries detected"""
    if parsed.subqueries >= 2:
        return RuleFinding(
            rule_id="R010",
            severity="medium",
            category="Subqueries",
            title="Multiple Nested Subqueries",
            description="Multiple subqueries may cause repeated subquery execution. Consider JOINs or CTEs.",
            evidence=f"{parsed.subqueries} subqueries detected",
            location="Subqueries"
        )
    return None

ALL_RULES = [
    rule_r001_select_star,
    rule_r002_missing_where,
    rule_r003_function_on_column,
    rule_r004_join_missing_index,
    rule_r005_where_missing_index,
    rule_r006_unbounded_order_by,
    rule_r007_leading_wildcard,
    rule_r008_redundant_distinct,
    rule_r009_cartesian_join,
    rule_r010_subquery_count
]

def run_rules(parsed: ParsedQuery, schema: SchemaInfo) -> List[RuleFinding]:
    """Run all deterministic baseline rules against the parsed query."""
    findings = []
    for rule in ALL_RULES:
        try:
            res = rule(parsed, schema)
            if res:
                findings.append(res)
        except Exception:
            pass
    return findings
