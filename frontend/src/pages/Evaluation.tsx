import { useEffect, useState } from 'react';
import { Play, BarChart2 } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid
} from 'recharts';
import { getEvaluation, runEvaluation } from '../services/api';

export default function Evaluation() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const fetchMetrics = () => {
    setLoading(true);
    getEvaluation()
      .then((res) => setData(res))
      .catch((err) => console.error('Error fetching evaluation data:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const handleRunEval = async () => {
    setRunning(true);
    try {
      await runEvaluation();
      fetchMetrics();
    } catch (err: any) {
      alert(`Evaluation failed: ${err.message}`);
    } finally {
      setRunning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-400">Loading benchmark evaluation data...</p>
      </div>
    );
  }

  const baseline = data?.baseline || {};
  const agentic = data?.agentic || {};
  const cases = data?.cases || [];

  const chartData = [
    {
      metric: 'Precision (%)',
      Baseline: baseline.precision || 0,
      'QueryOpt AI': agentic.precision || 0
    },
    {
      metric: 'Recall (%)',
      Baseline: baseline.recall || 0,
      'QueryOpt AI': agentic.recall || 0
    },
    {
      metric: 'F1 Score (%)',
      Baseline: baseline.f1_score || 0,
      'QueryOpt AI': agentic.f1_score || 0
    },
    {
      metric: 'Opt Correctness (%)',
      Baseline: baseline.optimization_correctness || 0,
      'QueryOpt AI': agentic.optimization_correctness || 0
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-100 flex items-center gap-2">
            <BarChart2 className="w-7 h-7 text-emerald-400" />
            Baseline vs QueryOpt AI Evaluation
          </h1>
          <p className="text-gray-400 mt-1">
            Empirical benchmark metrics measured across 20 representative SQL test cases covering all major optimization challenges.
          </p>
        </div>

        <button
          onClick={handleRunEval}
          disabled={running}
          className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl flex items-center gap-2 shadow-lg shadow-emerald-950 transition"
        >
          <Play className="w-4 h-4" />
          {running ? 'Benchmarking 20 Test Cases...' : 'Re-run Benchmark Suite'}
        </button>
      </div>

      {/* Metrics Comparison Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-gray-800">
          <h2 className="text-base font-semibold text-gray-200">System Performance & Accuracy Metrics</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-300">
            <thead className="bg-gray-950 text-gray-400 uppercase text-xs">
              <tr>
                <th className="py-3 px-4">Evaluation Metric</th>
                <th className="py-3 px-4">Baseline Rule Engine</th>
                <th className="py-3 px-4">QueryOpt AI (6-Agent)</th>
                <th className="py-3 px-4">Net Improvement</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              <tr>
                <td className="py-3.5 px-4 font-medium text-gray-200">Problem Detection Precision</td>
                <td className="py-3.5 px-4">{baseline.precision}%</td>
                <td className="py-3.5 px-4 text-emerald-400 font-semibold">{agentic.precision}%</td>
                <td className="py-3.5 px-4 text-emerald-400">
                  +{(agentic.precision - baseline.precision).toFixed(1)}%
                </td>
              </tr>
              <tr>
                <td className="py-3.5 px-4 font-medium text-gray-200">Problem Detection Recall</td>
                <td className="py-3.5 px-4">{baseline.recall}%</td>
                <td className="py-3.5 px-4 text-emerald-400 font-semibold">{agentic.recall}%</td>
                <td className="py-3.5 px-4 text-emerald-400">
                  +{(agentic.recall - baseline.recall).toFixed(1)}%
                </td>
              </tr>
              <tr>
                <td className="py-3.5 px-4 font-medium text-gray-200">F1 Score</td>
                <td className="py-3.5 px-4">{baseline.f1_score}%</td>
                <td className="py-3.5 px-4 text-emerald-400 font-semibold">{agentic.f1_score}%</td>
                <td className="py-3.5 px-4 text-emerald-400">
                  +{(agentic.f1_score - baseline.f1_score).toFixed(1)}%
                </td>
              </tr>
              <tr>
                <td className="py-3.5 px-4 font-medium text-gray-200">Optimization Correctness Rate</td>
                <td className="py-3.5 px-4">{baseline.optimization_correctness}% (No rewrites)</td>
                <td className="py-3.5 px-4 text-yellow-400 font-semibold">{agentic.optimization_correctness}% (Verified)</td>
                <td className="py-3.5 px-4 text-gray-400">Verification Gate Active</td>
              </tr>
              <tr>
                <td className="py-3.5 px-4 font-medium text-gray-200">False Positive Rate</td>
                <td className="py-3.5 px-4">{baseline.false_positive_rate}%</td>
                <td className="py-3.5 px-4 text-emerald-400 font-semibold">{agentic.false_positive_rate}%</td>
                <td className="py-3.5 px-4 text-emerald-400">
                  -{(baseline.false_positive_rate - agentic.false_positive_rate).toFixed(1)}%
                </td>
              </tr>
              <tr>
                <td className="py-3.5 px-4 font-medium text-gray-200">Average Execution Latency</td>
                <td className="py-3.5 px-4">{baseline.avg_time_ms} ms</td>
                <td className="py-3.5 px-4 text-emerald-400 font-semibold">{agentic.avg_time_ms} ms</td>
                <td className="py-3.5 px-4 text-emerald-400">
                  {(baseline.avg_time_ms - agentic.avg_time_ms).toFixed(2)} ms faster
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Bar Chart Visualization */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-4">
        <h2 className="text-base font-semibold text-gray-200">Comparative Accuracy Chart</h2>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="metric" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" domain={[0, 100]} />
              <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#f3f4f6' }} />
              <Legend />
              <Bar dataKey="Baseline" fill="#6b7280" radius={[4, 4, 0, 0]} />
              <Bar dataKey="QueryOpt AI" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Test Cases Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-gray-800">
          <h2 className="text-base font-semibold text-gray-200">Benchmark Test Cases ({cases.length})</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-300">
            <thead className="bg-gray-950 text-gray-400 uppercase">
              <tr>
                <th className="py-3 px-4">ID</th>
                <th className="py-3 px-4">Scenario Name</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Target SQL</th>
                <th className="py-3 px-4">Expected Problems</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800 font-mono">
              {cases.map((c: any) => (
                <tr key={c.id} className="hover:bg-gray-800/40">
                  <td className="py-3 px-4 font-bold text-emerald-400">{c.id}</td>
                  <td className="py-3 px-4 font-sans text-gray-200">{c.name}</td>
                  <td className="py-3 px-4 font-sans text-gray-400">{c.category}</td>
                  <td className="py-3 px-4 text-gray-400 truncate max-w-xs">{c.sql}</td>
                  <td className="py-3 px-4 font-sans text-yellow-300">
                    {c.expected_problems?.join(', ') || 'None (Optimal)'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
