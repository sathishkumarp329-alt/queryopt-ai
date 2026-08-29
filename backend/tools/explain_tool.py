import sqlite3
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class QueryPlanNode:
    node_id: int
    parent_id: int
    not_used: int
    detail: str
    is_full_scan: bool = False
    table: Optional[str] = None
    index_used: Optional[str] = None

@dataclass
class ExplainResult:
    nodes: List[QueryPlanNode] = field(default_factory=list)
    has_full_table_scan: bool = False
    tables_scanned: List[str] = field(default_factory=list)
    indexes_used: List[str] = field(default_factory=list)
    tables_with_full_scan: List[str] = field(default_factory=list)
    summary: str = ""
    error: Optional[str] = None

def run_explain(sql: str, db_path: str) -> ExplainResult:
    """Run EXPLAIN QUERY PLAN on SQLite and parse the plan tree."""
    result = ExplainResult()
    
    # Strip any trailing semicolons
    cleaned_sql = sql.strip().rstrip(";")
    explain_sql = f"EXPLAIN QUERY PLAN {cleaned_sql}"

    try:
        conn = sqlite3.connect(db_path, timeout=5)
        cursor = conn.cursor()
        cursor.execute(explain_sql)
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        result.error = str(e)
        result.summary = f"EXPLAIN execution failed: {str(e)}"
        return result

    # SQLite returns: (id, parent, notused, detail)
    for row in rows:
        node_id = row[0]
        parent_id = row[1]
        not_used = row[2]
        detail = row[3]
        
        is_scan = "SCAN " in detail.upper() or "SCAN TABLE" in detail.upper()
        
        # Parse table name from detail like "SCAN TABLE customers" or "SEARCH customers USING INDEX idx_name"
        table_name = None
        index_name = None
        
        words = detail.split()
        for i, w in enumerate(words):
            if w.upper() in ("TABLE", "SCAN", "SEARCH") and i + 1 < len(words):
                candidate = words[i+1].rstrip(",")
                if candidate.upper() not in ("TABLE", "USING", "INDEX", "COVERING"):
                    table_name = candidate.lower()
            if w.upper() == "INDEX" and i + 1 < len(words):
                index_name = words[i+1].rstrip(")")

        if is_scan and table_name:
            result.has_full_table_scan = True
            if table_name not in result.tables_with_full_scan:
                result.tables_with_full_scan.append(table_name)
        
        if table_name and table_name not in result.tables_scanned:
            result.tables_scanned.append(table_name)
            
        if index_name and index_name not in result.indexes_used:
            result.indexes_used.append(index_name)

        node = QueryPlanNode(
            node_id=node_id,
            parent_id=parent_id,
            not_used=not_used,
            detail=detail,
            is_full_scan=is_scan,
            table=table_name,
            index_used=index_name
        )
        result.nodes.append(node)

    # Build human summary
    if result.has_full_table_scan:
        result.summary = f"Full table scan detected on: {', '.join(result.tables_with_full_scan)}. "
    else:
        result.summary = "All table accesses utilize index searches. "
        
    if result.indexes_used:
        result.summary += f"Indexes used: {', '.join(result.indexes_used)}."
    else:
        result.summary += "No secondary indexes were used in execution."

    return result

def compare_plans(original: ExplainResult, optimized: ExplainResult) -> Dict[str, Any]:
    """Compare query plans of original vs optimized query."""
    return {
        "original_full_scans": original.tables_with_full_scan,
        "optimized_full_scans": optimized.tables_with_full_scan,
        "scans_eliminated": [t for t in original.tables_with_full_scan if t not in optimized.tables_with_full_scan],
        "original_indexes": original.indexes_used,
        "optimized_indexes": optimized.indexes_used,
        "is_plan_improved": len(optimized.tables_with_full_scan) < len(original.tables_with_full_scan) or (not original.indexes_used and bool(optimized.indexes_used))
    }
