import json
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.db_models import QueryAnalysis

router = APIRouter(prefix="/api/report", tags=["Reports"])

@router.get("/{analysis_id}")
def export_report(
    analysis_id: str,
    format: str = Query("json", regex="^(json|html)$"),
    db: Session = Depends(get_db)
):
    """Export analysis report as JSON or styled standalone HTML document."""
    record = db.query(QueryAnalysis).filter(QueryAnalysis.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    report_data = record.full_report_json or {}

    if format == "json":
        return report_data

    # Generate standalone responsive HTML report
    html_content = generate_html_report(record.id, report_data)
    return Response(content=html_content, media_type="text/html")

def generate_html_report(analysis_id: str, data: dict) -> str:
    summary = data.get("query_summary", {})
    findings = data.get("findings", [])
    opt = data.get("optimization", {})
    indexes = data.get("index_recommendations", [])
    verif = data.get("verification", {})
    
    findings_html = "".join([
        f"""<div style="background:#1e293b; border-left:4px solid {'#ef4444' if f.get('severity')=='critical' else '#f97316' if f.get('severity')=='high' else '#eab308'}; padding:12px; margin-bottom:12px; border-radius:4px;">
            <strong style="color:#f8fafc;">[{f.get('severity','').upper()}] {f.get('title','')}</strong>
            <p style="color:#94a3b8; margin:6px 0;">{f.get('description','')}</p>
            <code style="background:#0f172a; color:#38bdf8; padding:4px 8px; border-radius:4px; display:block; margin-top:4px;">{f.get('evidence','')}</code>
        </div>""" for f in findings
    ])

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>QueryOpt AI Report — {analysis_id[:8]}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 24px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .card {{ background: #1e293b; border-radius: 8px; padding: 20px; margin-bottom: 20px; border: 1px solid #334155; }}
        .score {{ font-size: 28px; font-weight: bold; color: #10b981; }}
        pre {{ background: #090d16; padding: 16px; border-radius: 6px; overflow-x: auto; color: #38bdf8; font-family: monospace; }}
    </style>
</head>
<body>
<div class="container">
    <h1>🚀 QueryOpt AI Analysis Report</h1>
    <div style="color: #94a3b8; margin-bottom: 20px;">Analysis ID: {analysis_id} | Database: {summary.get('database','sqlite')}</div>

    <div class="card">
        <h2>Overall Score</h2>
        <div style="display:flex; gap:30px;">
            <div>SQL Quality: <span class="score">{data.get('sql_score', 0)}/100</span></div>
            <div>Performance: <span class="score">{data.get('performance_score', 0)}/100</span></div>
            <div>Potential: <span style="font-size:24px; color:#f59e0b;">{data.get('optimization_potential', 'N/A')}</span></div>
        </div>
    </div>

    <div class="card">
        <h2>Identified Issues ({len(findings)})</h2>
        {findings_html or "<p style='color:#10b981;'>No structural or performance issues detected.</p>"}
    </div>

    <div class="card">
        <h2>SQL Optimization Comparison</h2>
        <h3>Original SQL</h3>
        <pre>{opt.get('original_sql','')}</pre>
        <h3>Optimized SQL</h3>
        <pre style="color:#4ade80;">{opt.get('optimized_sql','')}</pre>
        <p><strong>Status:</strong> {verif.get('status','')} (Improvement: {verif.get('improvement_pct', 0)}%)</p>
    </div>
</div>
</body>
</html>"""
