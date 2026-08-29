import axios from 'axios';
import type {
  AnalyzeResponse,
  ExplainResult,
  HistoryItem,
  BaselineVsAgenticComparison,
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 120_000,
});

// Response interceptor for error normalisation
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err?.response?.data?.detail ||
      err?.response?.data?.message ||
      err?.message ||
      'Unknown error';
    return Promise.reject(new Error(message));
  },
);

/** Analyse a SQL query with the full agentic pipeline */
export async function analyzeQuery(
  sql: string,
  databaseType: string,
  schemaName: string,
): Promise<AnalyzeResponse> {
  const { data } = await api.post<AnalyzeResponse>('/analyze', {
    sql,
    database_type: databaseType,
    schema_name: schemaName,
  });
  return data;
}

/** Analyse a SQL query with the baseline (non-agentic) approach */
export async function analyzeBaseline(
  sql: string,
  schemaName: string,
): Promise<unknown> {
  const { data } = await api.post('/analyze/baseline', {
    sql,
    schema_name: schemaName,
  });
  return data;
}

/** Validate SQL syntax */
export async function validateQuery(
  sql: string,
): Promise<{ valid: boolean; error: string; is_destructive: boolean; query_type: string }> {
  const { data } = await api.post('/validate', { sql });
  return data;
}

/** Explain / query plan for a SQL query */
export async function explainQuery(
  sql: string,
  schemaName: string,
): Promise<ExplainResult> {
  const { data } = await api.post<ExplainResult>('/explain', {
    sql,
    schema_name: schemaName,
  });
  return data;
}

/** Paginated analysis history */
export async function getHistory(
  page: number,
  perPage: number,
): Promise<{ items: HistoryItem[]; total: number }> {
  const { data } = await api.get<{ items: HistoryItem[]; total: number }>('/history', {
    params: { page, per_page: perPage },
  });
  return data;
}

/** Retrieve a single analysis by ID */
export async function getAnalysis(id: string): Promise<AnalyzeResponse> {
  const { data } = await api.get<AnalyzeResponse>(`/analysis/${id}`);
  return data;
}

/** Delete an analysis by ID */
export async function deleteAnalysis(id: string): Promise<{ success: boolean }> {
  const { data } = await api.delete<{ success: boolean }>(`/analysis/${id}`);
  return data;
}

/** Export a report in JSON or HTML format */
export async function getReport(
  id: string,
  format: 'json' | 'html',
): Promise<unknown> {
  const { data } = await api.get(`/analysis/${id}/report`, {
    params: { format },
    responseType: format === 'html' ? 'text' : 'json',
  });
  return data;
}

/** Get latest baseline-vs-agentic evaluation results */
export async function getEvaluation(): Promise<BaselineVsAgenticComparison> {
  const { data } = await api.get<BaselineVsAgenticComparison>('/evaluation');
  return data;
}

/** Trigger a full evaluation run */
export async function runEvaluation(): Promise<{ status: string }> {
  const { data } = await api.post<{ status: string }>('/evaluation/run');
  return data;
}

/** Health check */
export async function getHealth(): Promise<{ status: string }> {
  const { data } = await api.get<{ status: string }>('/health');
  return data;
}

export default api;
