export interface Finding {
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  category: string;
  title: string;
  description: string;
  evidence: string;
  location: string;
}

export interface IndexRecommendation {
  table_name: string;
  columns: string[];
  index_type: string;
  create_statement: string;
  reason: string;
  expected_impact: string;
}

export interface OptimizationResult {
  original_sql: string;
  optimized_sql: string;
  changes: string[];
  explanation: string;
}

export interface QueryPlanNode {
  node_id: number;
  parent_id: number;
  detail: string;
  is_full_scan: boolean;
  table: string | null;
  index_used: string | null;
}

export interface ExplainResult {
  nodes: QueryPlanNode[];
  has_full_table_scan: boolean;
  tables_scanned: string[];
  indexes_used: string[];
  tables_with_full_scan: string[];
  summary: string;
}

export interface VerificationResult {
  syntax_valid: boolean;
  tables_valid: boolean;
  is_equivalent: boolean;
  equivalence_explanation: string;
  original_time_ms: number;
  optimized_time_ms: number;
  improvement_pct: number;
  status: 'VERIFIED' | 'UNCERTAIN' | 'FAILED';
  confidence: number;
}

export interface AgentTrajectoryEntry {
  agent_name: string;
  action: string;
  tool_used: string | null;
  input_summary: string;
  result_summary: string;
  finding: string | null;
  confidence: number;
  duration_ms: number;
  timestamp: string;
}

export interface QuerySummary {
  database: string;
  query_type: string;
  tables: string[];
  joins: number;
  complexity: string;
}

export interface FinalReport {
  query_summary: QuerySummary;
  sql_score: number;
  performance_score: number;
  optimization_potential: 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE';
  findings: Finding[];
  optimization: OptimizationResult;
  index_recommendations: IndexRecommendation[];
  verification: VerificationResult;
  trajectory: AgentTrajectoryEntry[];
  explain_result: ExplainResult;
  exec_time_ms: number;
}

export interface AnalyzeResponse {
  analysis_id: string;
  status: string;
  report: FinalReport;
}

export interface HistoryItem {
  id: string;
  created_at: string;
  database_type: string;
  schema_name: string;
  original_sql: string;
  status: string;
  sql_score: number | null;
  performance_score: number | null;
  optimization_potential: string | null;
  duration_seconds: number | null;
}

export interface EvaluationMetrics {
  precision: number;
  recall: number;
  f1_score: number;
  false_positive_rate: number;
  optimization_correctness: number;
  avg_time_ms: number;
  total_cases: number;
  mode: string;
}

export interface BaselineVsAgenticComparison {
  baseline: EvaluationMetrics;
  agentic: EvaluationMetrics;
  improvement: {
    precision_delta: number;
    recall_delta: number;
    f1_delta: number;
    correctness_delta: number;
  };
}
