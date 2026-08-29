import sqlite3
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
from backend.tools.sql_parser import is_destructive

@dataclass
class ExecutionResult:
    rows: List[Dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    columns: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    error: Optional[str] = None

def execute_safe(
    sql: str,
    db_path: str,
    max_rows: int = 1000,
    timeout_seconds: int = 10
) -> ExecutionResult:
    """Execute a read-only query safely with timeout and row limit."""
    res = ExecutionResult()
    
    if is_destructive(sql):
        res.error = "Security violation: Non-read-only / destructive SQL statements are strictly rejected."
        return res

    start_time = time.perf_counter()
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=timeout_seconds)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Fetch columns
        if cursor.description:
            res.columns = [col[0] for col in cursor.description]
        
        fetched = cursor.fetchmany(max_rows)
        res.rows = [dict(row) for row in fetched]
        res.row_count = len(res.rows)
        
        conn.close()
    except Exception as e:
        res.error = str(e)
    
    end_time = time.perf_counter()
    res.execution_time_ms = round((end_time - start_time) * 1000.0, 2)
    return res

def execute_and_time(sql: str, db_path: str, runs: int = 3) -> Tuple[ExecutionResult, float]:
    """Execute query multiple times to get an accurate average execution time in milliseconds."""
    times = []
    last_res = ExecutionResult()
    
    for _ in range(max(1, runs)):
        res = execute_safe(sql, db_path)
        last_res = res
        if res.error:
            return res, 0.0
        times.append(res.execution_time_ms)
        
    avg_time = round(sum(times) / len(times), 2)
    return last_res, avg_time

def check_result_equivalence(
    sql1: str,
    sql2: str,
    db_path: str,
    sample_size: int = 100
) -> Tuple[bool, str]:
    """Verify if two SQL queries return equivalent result sets."""
    if not sql2 or not sql2.strip():
        return False, "Optimized query is empty"

    res1 = execute_safe(sql1, db_path, max_rows=sample_size)
    if res1.error:
        return False, f"Original query execution error: {res1.error}"

    res2 = execute_safe(sql2, db_path, max_rows=sample_size)
    if res2.error:
        return False, f"Optimized query execution error: {res2.error}"

    # If row count is noticeably different (for sample)
    if res1.row_count != res2.row_count:
        return False, f"Row count mismatch: Original returned {res1.row_count} rows, optimized returned {res2.row_count} rows."

    # Compare column values after sorting if columns match or subset
    # Normalize rows by sorting keys and converting values to string
    try:
        # Check if same number of rows returned
        if res1.row_count == 0 and res2.row_count == 0:
            return True, "Both queries returned 0 rows (equivalent empty set)."

        # Check column overlap
        cols1 = set(res1.columns)
        cols2 = set(res2.columns)
        
        # If columns are completely different
        common_cols = cols1.intersection(cols2)
        if not common_cols and cols1 and cols2:
            return False, f"Column mismatch: Original has columns {res1.columns}, optimized has {res2.columns}"

        # If SELECT * was optimized into explicit columns, check that the explicit columns match original values
        sample_len = min(len(res1.rows), len(res2.rows), 20)
        for i in range(sample_len):
            r1 = res1.rows[i]
            r2 = res2.rows[i]
            for col in common_cols:
                v1 = str(r1.get(col, ""))
                v2 = str(r2.get(col, ""))
                if v1 != v2:
                    return False, f"Value mismatch in row {i+1}, column '{col}': '{v1}' != '{v2}'"

        return True, f"Verified: Results match on {sample_len} sample rows across columns {list(common_cols)}."
    except Exception as e:
        return False, f"Comparison error: {str(e)}"
