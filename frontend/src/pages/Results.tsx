import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft, Download, FileCode, CheckCircle, ShieldAlert,
  Sliders, Activity, Cpu, Sparkles, Database
} from 'lucide-react';
import { getAnalysis } from '../services/api';
import { FinalReport } from '../types';
import ScoreCard from '../components/ScoreCard';
import FindingCard from '../components/FindingCard';
import QueryDiff from '../components/QueryDiff';
import AgentTimeline from '../components/AgentTimeline';
import QueryPlanView from '../components/QueryPlanView';
import IndexRecommendationCard from '../components/IndexRecommendationCard';
import VerificationBadge from '../components/VerificationBadge';

export default function Results() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<FinalReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'optimization' | 'plan' | 'indexes' | 'trajectory'>('overview');

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getAnalysis(id)
      .then((res) => {
        setReport(res.report);
      })
      .catch((err) => {
        console.error('Error fetching analysis report:', err);
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-400">Loading analysis results...</p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center space-y-4">
        <ShieldAlert className="w-12 h-12 text-red-400 mx-auto" />
        <h2 className="text-xl font-bold text-gray-200">Analysis Not Found</h2>
        <p className="text-gray-400">The requested query analysis record does not exist or was deleted.</p>
        <Link to="/analyzer" className="inline-block px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium">
          Run New Analysis
        </Link>
      </div>
    );
  }

  const findings = report.findings || [];

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <Link to="/analyzer" className="text-xs text-gray-400 hover:text-gray-200 flex items-center gap-1 mb-2">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Analyzer
          </Link>
          <h1 className="text-2xl font-bold text-gray-100 flex items-center gap-2">
            Analysis Report
            <span className="text-xs font-normal text-gray-400 font-mono bg-gray-900 border border-gray-800 px-2 py-1 rounded">
              ID: {id?.slice(0, 8)}
            </span>
          </h1>
        </div>

        {/* Action / Export Buttons */}
        <div className="flex items-center gap-2">
          <a
            href={`/api/report/${id}?format=html`}
            target="_blank"
            rel="noreferrer"
            className="px-3 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-medium rounded-lg flex items-center gap-1.5 transition"
          >
            <Download className="w-4 h-4" /> Export HTML
          </a>
          <a
            href={`/api/report/${id}?format=json`}
            target="_blank"
            rel="noreferrer"
            className="px-3 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-medium rounded-lg flex items-center gap-1.5 transition"
          >
            <FileCode className="w-4 h-4" /> Export JSON
          </a>
        </div>
      </div>

      {/* Score Summary Card */}
      <ScoreCard
        sqlScore={report.sql_score}
        performanceScore={report.performance_score}
        potential={report.optimization_potential}
      />

      {/* Tabs Navigation */}
      <div className="flex border-b border-gray-800 space-x-2">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition flex items-center gap-2 ${
            activeTab === 'overview'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          <Sliders className="w-4 h-4" />
          Findings & Verification ({findings.length})
        </button>

        <button
          onClick={() => setActiveTab('optimization')}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition flex items-center gap-2 ${
            activeTab === 'optimization'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          SQL Optimization & Diff
        </button>

        <button
          onClick={() => setActiveTab('plan')}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition flex items-center gap-2 ${
            activeTab === 'plan'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          <Cpu className="w-4 h-4" />
          Physical Query Plan
        </button>

        <button
          onClick={() => setActiveTab('indexes')}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition flex items-center gap-2 ${
            activeTab === 'indexes'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          <Database className="w-4 h-4" />
          Index Recommendations ({report.index_recommendations?.length || 0})
        </button>

        <button
          onClick={() => setActiveTab('trajectory')}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition flex items-center gap-2 ${
            activeTab === 'trajectory'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          <Activity className="w-4 h-4" />
          Agent Activity Trajectory ({report.trajectory?.length || 0})
        </button>
      </div>

      {/* Tab 1: Findings & Verification */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <h3 className="text-base font-semibold text-gray-200">Detected Issues ({findings.length})</h3>
            {findings.length === 0 ? (
              <div className="bg-gray-900 border border-emerald-800/40 rounded-xl p-6 text-center text-emerald-400">
                <CheckCircle className="w-8 h-8 mx-auto mb-2" />
                No structural or performance antipatterns detected!
              </div>
            ) : (
              findings.map((f, idx) => <FindingCard key={idx} finding={f} />)
            )}
          </div>

          <div className="space-y-4">
            <h3 className="text-base font-semibold text-gray-200">Verification Status</h3>
            <VerificationBadge verification={report.verification} />
          </div>
        </div>
      )}

      {/* Tab 2: Optimization Diff */}
      {activeTab === 'optimization' && (
        <div className="space-y-6">
          <QueryDiff
            original={report.optimization?.original_sql || ''}
            optimized={report.optimization?.optimized_sql || ''}
          />

          {/* Changes list & Explanation */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
            <h3 className="text-sm font-semibold text-gray-200 uppercase tracking-wider">Applied Optimizations</h3>
            <ul className="list-disc list-inside space-y-1.5 text-sm text-gray-300">
              {report.optimization?.changes?.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
            {report.optimization?.explanation && (
              <div className="pt-3 border-t border-gray-800 text-xs text-gray-400">
                <strong>Rationale:</strong> {report.optimization.explanation}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Query Plan */}
      {activeTab === 'plan' && (
        <div className="space-y-4">
          <QueryPlanView explainResult={report.explain_result} execTimeMs={report.exec_time_ms} />
        </div>
      )}

      {/* Tab 4: Index Recommendations */}
      {activeTab === 'indexes' && (
        <div className="space-y-4">
          <IndexRecommendationCard recommendations={report.index_recommendations || []} />
        </div>
      )}

      {/* Tab 5: Agent Trajectory Timeline */}
      {activeTab === 'trajectory' && (
        <div className="space-y-4">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <h3 className="text-base font-semibold text-gray-200 mb-1">Multi-Agent Execution Trajectory</h3>
            <p className="text-xs text-gray-400">
              Full step-by-step audit record of each specialized agent's actions, tools used, findings, and confidence ratings.
            </p>
          </div>
          <AgentTimeline trajectory={report.trajectory || []} />
        </div>
      )}
    </div>
  );
}
