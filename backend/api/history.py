from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database import get_db
from backend.models.db_models import QueryAnalysis
from backend.models.schemas import HistoryResponse, HistoryItem

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("", response_model=HistoryResponse)
def get_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve paginated analysis history."""
    total = db.query(QueryAnalysis).count()
    offset = (page - 1) * per_page
    records = (
        db.query(QueryAnalysis)
        .order_by(desc(QueryAnalysis.created_at))
        .offset(offset)
        .limit(per_page)
        .all()
    )

    items = [
        HistoryItem(
            id=r.id,
            created_at=r.created_at or "",
            database_type=r.database_type or "sqlite",
            schema_name=r.schema_name or "demo",
            original_sql=r.original_sql,
            status=r.status or "completed",
            sql_score=r.sql_score,
            performance_score=r.performance_score,
            optimization_potential=r.optimization_potential,
            duration_seconds=r.duration_seconds
        )
        for r in records
    ]

    return HistoryResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/{analysis_id}")
def get_analysis_by_id(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieve full analysis report by ID."""
    record = db.query(QueryAnalysis).filter(QueryAnalysis.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {
        "analysis_id": record.id,
        "status": record.status,
        "report": record.full_report_json
    }

@router.delete("/{analysis_id}")
def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Delete an analysis record."""
    record = db.query(QueryAnalysis).filter(QueryAnalysis.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    db.delete(record)
    db.commit()
    return {"success": True, "deleted_id": analysis_id}
