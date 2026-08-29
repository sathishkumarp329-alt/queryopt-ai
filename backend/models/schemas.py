from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Request Models
class AnalyzeRequest(BaseModel):
    sql: str = Field(..., description="The SQL query to analyze")
    database_type: str = Field("sqlite", description="Database dialect (sqlite, mysql, postgresql)")
    schema_name: str = Field("demo", description="Target database schema name")

class QueryValidateRequest(BaseModel):
    sql: str

class QueryExplainRequest(BaseModel):
    sql: str
    schema_name: str = "demo"

class QueryExecuteRequest(BaseModel):
    sql: str
    schema_name: str = "demo"
    max_rows: int = 100

# Inner Structures
class FindingModel(BaseModel):
    severity: str  # critical, high, medium, low, info
    category: str
    title: str
    description: str
    evidence: Optional[str] = None
    location: Optional[str] = None

class IndexRecommendationModel(BaseModel):
    table_name: str
    columns: List[str]
    index_type: str = "BTREE"
    create_statement: str
    reason: str
    expected_impact: str

class OptimizationModel(BaseModel):
    original_sql: str
    optimized_sql: str
    changes: List[str] = []
    explanation: str = ""

class QueryPlanNodeModel(BaseModel):
    node_id: int
    parent_id: int
    detail: str
    is_full_scan: bool = False
    table: Optional[str] = None
    index_used: Optional[str] = None

class ExplainResultModel(BaseModel):
    nodes: List[QueryPlanNodeModel] = []
    has_full_table_scan: bool = False
    tables_scanned: List[str] = []
    indexes_used: List[str] = []
    tables_with_full_scan: List[str] = []
    summary: str = ""

class VerificationResultModel(BaseModel):
    syntax_valid: bool = True
    tables_valid: bool = True
    is_equivalent: bool = False
    equivalence_explanation: str = ""
    original_time_ms: float = 0.0
    optimized_time_ms: float = 0.0
    improvement_pct: float = 0.0
    status: str = "UNCERTAIN"  # VERIFIED, UNCERTAIN, FAILED
    confidence: float = 0.5

class AgentTrajectoryModel(BaseModel):
    agent_name: str
    action: str
    tool_used: Optional[str] = None
    input_summary: Optional[str] = None
    result_summary: Optional[str] = None
    finding: Optional[str] = None
    confidence: float = 1.0
    duration_ms: float = 0.0
    timestamp: str = ""

class QuerySummaryModel(BaseModel):
    database: str = "sqlite"
    query_type: str = "SELECT"
    tables: List[str] = []
    joins: int = 0
    complexity: str = "Simple"

class FinalReport(BaseModel):
    query_summary: QuerySummaryModel
    sql_score: int
    performance_score: int
    optimization_potential: str  # HIGH, MEDIUM, LOW, NONE
    findings: List[FindingModel] = []
    optimization: OptimizationModel
    index_recommendations: List[IndexRecommendationModel] = []
    verification: VerificationResultModel
    trajectory: List[AgentTrajectoryModel] = []
    explain_result: Optional[ExplainResultModel] = None
    exec_time_ms: float = 0.0

# API Responses
class AnalyzeResponse(BaseModel):
    analysis_id: str
    status: str
    report: FinalReport

class HistoryItem(BaseModel):
    id: str
    created_at: str
    database_type: str
    schema_name: str
    original_sql: str
    status: str
    sql_score: Optional[int] = None
    performance_score: Optional[int] = None
    optimization_potential: Optional[str] = None
    duration_seconds: Optional[float] = None

class HistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int
    page: int
    per_page: int

class EvaluationMetricsModel(BaseModel):
    mode: str
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    optimization_correctness: float
    avg_time_ms: float
    total_cases: int

class BaselineVsAgenticComparison(BaseModel):
    baseline: EvaluationMetricsModel
    agentic: EvaluationMetricsModel
    improvement: Dict[str, float]
    cases: List[Dict[str, Any]] = []
