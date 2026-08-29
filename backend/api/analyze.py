import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.schemas import AnalyzeRequest, AnalyzeResponse, FinalReport
from backend.models.db_models import (
    QueryAnalysis, FindingRecord, OptimizationRecord,
    IndexRecommendationRecord, AgentTrajectoryRecord
)
from backend.orchestrator.orchestrator import AgentOrchestrator
from baseline.baseline_analyzer import BaselineAnalyzer
from backend.tools.sql_parser import is_destructive

router = APIRouter(prefix="/api", tags=["Analysis"])

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_query(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """Analyze a SQL query using the full 6-agent pipeline."""
    if is_destructive(request.sql):
        raise HTTPException(
            status_code=400,
            detail="Security violation: Destructive / Data Modification SQL queries are blocked in read-only mode."
        )

    orchestrator = AgentOrchestrator()
    result = orchestrator.run(
        sql=request.sql,
        database_type=request.database_type,
        schema_name=request.schema_name
    )

    final_report = result["final_report"]
    analysis_id = str(uuid.uuid4())

    # Save to Database for persistence & history
    try:
        analysis_record = QueryAnalysis(
            id=analysis_id,
            database_type=request.database_type,
            schema_name=request.schema_name,
            original_sql=request.sql,
            status="completed",
            sql_score=final_report.get("sql_score"),
            performance_score=final_report.get("performance_score"),
            optimization_potential=final_report.get("optimization_potential"),
            duration_seconds=result.get("duration_seconds", 0.0),
            full_report_json=final_report
        )
        db.add(analysis_record)

        # Save findings
        for f in final_report.get("findings", []):
            finding_rec = FindingRecord(
                analysis_id=analysis_id,
                severity=f.get("severity", "info"),
                category=f.get("category", "General"),
                title=f.get("title", ""),
                description=f.get("description", ""),
                evidence=f.get("evidence", ""),
                location=f.get("location", "")
            )
            db.add(finding_rec)

        # Save optimizations
        opt = final_report.get("optimization", {})
        verif = final_report.get("verification", {})
        if opt:
            opt_rec = OptimizationRecord(
                analysis_id=analysis_id,
                original_sql=opt.get("original_sql", request.sql),
                optimized_sql=opt.get("optimized_sql", request.sql),
                changes_description=opt.get("changes", []),
                explanation=opt.get("explanation", ""),
                is_verified=verif.get("status") == "VERIFIED",
                equivalence_status=verif.get("status", "UNCERTAIN"),
                original_exec_time_ms=verif.get("original_time_ms"),
                optimized_exec_time_ms=verif.get("optimized_time_ms"),
                improvement_pct=verif.get("improvement_pct")
            )
            db.add(opt_rec)

        # Save index recommendations
        for idx in final_report.get("index_recommendations", []):
            idx_rec = IndexRecommendationRecord(
                analysis_id=analysis_id,
                table_name=idx.get("table_name", ""),
                columns=idx.get("columns", []),
                index_type=idx.get("index_type", "BTREE"),
                create_statement=idx.get("create_statement", ""),
                reason=idx.get("reason", ""),
                expected_impact=idx.get("expected_impact", "")
            )
            db.add(idx_rec)

        # Save trajectories
        for t in result.get("trajectory", []):
            traj_rec = AgentTrajectoryRecord(
                analysis_id=analysis_id,
                agent_name=t.get("agent_name", ""),
                action=t.get("action", ""),
                tool_used=t.get("tool_used"),
                input_summary=t.get("input_summary"),
                result_summary=t.get("result_summary"),
                finding=t.get("finding"),
                confidence=t.get("confidence", 1.0),
                duration_ms=t.get("duration_ms", 0.0),
                timestamp=t.get("timestamp", "")
            )
            db.add(traj_rec)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error persisting analysis to app db: {e}")

    return AnalyzeResponse(
        analysis_id=analysis_id,
        status="completed",
        report=final_report
    )

@router.post("/analyze/baseline", response_model=AnalyzeResponse)
def analyze_baseline(request: AnalyzeRequest):
    """Analyze a SQL query using the traditional Baseline rule engine."""
    if is_destructive(request.sql):
        raise HTTPException(
            status_code=400,
            detail="Security violation: Destructive / Data Modification SQL queries are blocked."
        )

    baseline = BaselineAnalyzer()
    report = baseline.analyze(sql=request.sql)
    analysis_id = str(uuid.uuid4())

    return AnalyzeResponse(
        analysis_id=analysis_id,
        status="completed",
        report=report
    )
