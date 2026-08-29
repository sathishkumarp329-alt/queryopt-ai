from fastapi import APIRouter, HTTPException
from backend.models.schemas import (
    QueryValidateRequest, QueryExplainRequest,
    QueryExecuteRequest, ExplainResultModel
)
from backend.tools.sql_parser import parse_sql, is_destructive
from backend.tools.explain_tool import run_explain
from backend.tools.query_executor import execute_safe
from backend.tools.schema_tool import get_schema
from backend.config import settings

router = APIRouter(prefix="/api/query", tags=["Query Utilities"])

@router.post("/validate")
def validate_query(request: QueryValidateRequest):
    """Validate query syntax and security constraints."""
    destructive = is_destructive(request.sql)
    parsed = parse_sql(request.sql)

    return {
        "valid": parsed.parse_error is None and not destructive,
        "is_destructive": destructive,
        "query_type": parsed.query_type,
        "tables": parsed.tables,
        "error": "Destructive query not allowed in read-only sandbox" if destructive else parsed.parse_error
    }

@router.post("/explain")
def explain_query(request: QueryExplainRequest):
    """Execute EXPLAIN QUERY PLAN and return parsed physical plan tree."""
    if is_destructive(request.sql):
        raise HTTPException(status_code=400, detail="Cannot explain destructive query.")

    explain_res = run_explain(request.sql, settings.DEMO_DB_PATH)
    return {
        "nodes": [
            {
                "node_id": n.node_id,
                "parent_id": n.parent_id,
                "detail": n.detail,
                "is_full_scan": n.is_full_scan,
                "table": n.table,
                "index_used": n.index_used
            } for n in explain_res.nodes
        ],
        "has_full_table_scan": explain_res.has_full_table_scan,
        "tables_scanned": explain_res.tables_scanned,
        "indexes_used": explain_res.indexes_used,
        "tables_with_full_scan": explain_res.tables_with_full_scan,
        "summary": explain_res.summary,
        "error": explain_res.error
    }

@router.post("/execute")
def execute_query(request: QueryExecuteRequest):
    """Safely execute a read-only query on the demo database."""
    if is_destructive(request.sql):
        raise HTTPException(status_code=400, detail="Destructive execution prohibited.")

    res = execute_safe(
        sql=request.sql,
        db_path=settings.DEMO_DB_PATH,
        max_rows=min(request.max_rows, settings.MAX_QUERY_ROWS)
    )

    if res.error:
        raise HTTPException(status_code=400, detail=res.error)

    return {
        "rows": res.rows,
        "row_count": res.row_count,
        "columns": res.columns,
        "execution_time_ms": res.execution_time_ms
    }

@router.get("/schema/{schema_name}")
def get_schema_metadata(schema_name: str = "demo"):
    """Get metadata for demo database schema (tables, columns, indexes, row counts)."""
    schema = get_schema(settings.DEMO_DB_PATH)
    out = {}
    for tbl, t_info in schema.tables.items():
        out[tbl] = {
            "row_count": t_info.row_count,
            "columns": [{"name": c.name, "type": c.type, "is_pk": c.is_pk} for c in t_info.columns],
            "indexes": [{"name": i.name, "columns": i.columns} for i in t_info.indexes]
        }
    return {"schema": schema_name, "tables": out}
