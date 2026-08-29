import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class QueryAnalysis(Base):
    __tablename__ = "query_analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    database_type = Column(String, default="sqlite")
    schema_name = Column(String, default="demo")
    original_sql = Column(Text, nullable=False)
    status = Column(String, default="completed")  # pending, completed, failed
    sql_score = Column(Integer, nullable=True)
    performance_score = Column(Integer, nullable=True)
    optimization_potential = Column(String, nullable=True)  # HIGH, MEDIUM, LOW, NONE
    duration_seconds = Column(Float, nullable=True)
    full_report_json = Column(JSON, nullable=True)

    findings = relationship("FindingRecord", back_populates="analysis", cascade="all, delete-orphan")
    optimizations = relationship("OptimizationRecord", back_populates="analysis", cascade="all, delete-orphan")
    index_recommendations = relationship("IndexRecommendationRecord", back_populates="analysis", cascade="all, delete-orphan")
    trajectories = relationship("AgentTrajectoryRecord", back_populates="analysis", cascade="all, delete-orphan")

class FindingRecord(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("query_analyses.id", ondelete="CASCADE"), nullable=False)
    severity = Column(String, nullable=False)  # critical, high, medium, low, info
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    location = Column(String, nullable=True)

    analysis = relationship("QueryAnalysis", back_populates="findings")

class OptimizationRecord(Base):
    __tablename__ = "optimizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("query_analyses.id", ondelete="CASCADE"), nullable=False)
    original_sql = Column(Text, nullable=False)
    optimized_sql = Column(Text, nullable=False)
    changes_description = Column(JSON, nullable=True)  # List of strings
    explanation = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    equivalence_status = Column(String, default="UNCERTAIN")
    original_exec_time_ms = Column(Float, nullable=True)
    optimized_exec_time_ms = Column(Float, nullable=True)
    improvement_pct = Column(Float, nullable=True)

    analysis = relationship("QueryAnalysis", back_populates="optimizations")

class IndexRecommendationRecord(Base):
    __tablename__ = "index_recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("query_analyses.id", ondelete="CASCADE"), nullable=False)
    table_name = Column(String, nullable=False)
    columns = Column(JSON, nullable=False)  # List of column names
    index_type = Column(String, default="BTREE")
    create_statement = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    expected_impact = Column(String, nullable=False)

    analysis = relationship("QueryAnalysis", back_populates="index_recommendations")

class AgentTrajectoryRecord(Base):
    __tablename__ = "agent_trajectories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("query_analyses.id", ondelete="CASCADE"), nullable=False)
    agent_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    tool_used = Column(String, nullable=True)
    input_summary = Column(Text, nullable=True)
    result_summary = Column(Text, nullable=True)
    finding = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    duration_ms = Column(Float, default=0.0)
    timestamp = Column(String, default=lambda: datetime.utcnow().isoformat())

    analysis = relationship("QueryAnalysis", back_populates="trajectories")

class EvaluationRecord(Base):
    __tablename__ = "evaluation_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    mode = Column(String, nullable=False)  # baseline, agentic
    test_case_id = Column(String, nullable=False)
    detected_problems = Column(JSON, nullable=False)
    expected_problems = Column(JSON, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1 = Column(Float, nullable=False)
    optimization_correct = Column(Boolean, default=False)
    exec_time_ms = Column(Float, nullable=False)
